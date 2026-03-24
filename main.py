import shutil
import os
import cv2
import numpy as np
import base64
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from inference import get_model
import supervision as sv

import database
import schemas

app = FastAPI(title="YOLO Inference Manager")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Models ---
@app.post("/models/", response_model=schemas.ModelConfig)
def create_model(model: schemas.ModelConfigCreate, db: Session = Depends(get_db)):
    db_model = database.ModelConfig(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@app.get("/models/", response_model=List[schemas.ModelConfig])
def read_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(database.ModelConfig).offset(skip).limit(limit).all()

@app.delete("/models/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    db_model = db.query(database.ModelConfig).filter(database.ModelConfig.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    db.delete(db_model)
    db.commit()
    return {"message": "Model deleted"}

# --- Folders ---
@app.post("/folders/", response_model=schemas.Folder)
def create_folder(folder: schemas.FolderCreate, db: Session = Depends(get_db)):
    db_folder = database.Folder(name=folder.name)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

@app.get("/folders/", response_model=List[schemas.Folder])
def read_folders(db: Session = Depends(get_db)):
    folders = db.query(database.Folder).all()
    # Add analysis count
    for folder in folders:
        folder.analysis_count = db.query(database.Analysis).filter(database.Analysis.folder_id == folder.id).count()
    return folders

@app.delete("/folders/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    db_folder = db.query(database.Folder).filter(database.Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    db.delete(db_folder)
    db.commit()
    return {"message": "Folder deleted"}

# --- Analysis ---
@app.post("/analyze/{model_db_id}")
async def analyze_image(
    model_db_id: int, 
    file: UploadFile = File(...), 
    analysis_name: str = Form(...),
    folder_id: int = Form(0), # 0 means no folder
    db: Session = Depends(get_db)
):
    # 1. Get model from DB
    db_model_config = db.query(database.ModelConfig).filter(database.ModelConfig.id == model_db_id).first()
    if not db_model_config:
        raise HTTPException(status_code=404, detail="Model config not found")

    # 2. Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 3. Load YOLO model
    try:
        yolo_model = get_model(model_id=db_model_config.model_id, api_key=db_model_config.api_key)
        results = yolo_model.infer(image)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    # 4. Annotate
    detections = sv.Detections.from_inference(results)
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    labels = [f"{p.class_name} {p.confidence:.2f}" for p in results.predictions]
    annotated_image = box_annotator.annotate(scene=image.copy(), detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)

    # 5. Convert to base64
    _, buffer = cv2.imencode('.jpg', annotated_image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    image_url = f"data:image/jpeg;base64,{image_base64}"

    # 6. Prepare metadata for frontend
    class_names = [p.class_name for p in results.predictions]
    metadata = {
        "detections_count": len(detections),
        "classes": class_names,
        "confidences": detections.confidence.tolist() if detections.confidence is not None else [],
        "model_name": db_model_config.name
    }

    # 7. Save to DB (only if folder_id is provided)
    analysis_id = None
    if folder_id > 0:
        import json
        new_analysis = database.Analysis(
            name=analysis_name,
            folder_id=folder_id,
            image_url=image_url,
            detections=len(detections),
            results_json=json.dumps(metadata)
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        analysis_id = new_analysis.id

    return {
        "id": analysis_id,
        "image": image_url,
        "metadata": metadata
    }

@app.get("/folders/{folder_id}/metrics")
def get_folder_metrics(folder_id: int, db: Session = Depends(get_db)):
    analyses = db.query(database.Analysis).filter(database.Analysis.folder_id == folder_id).all()
    if not analyses:
        return {
            "total_images": 0,
            "total_detections": 0,
            "avg_confidence": 0,
            "class_distribution": {}
        }

    import json
    total_detections = 0
    all_confidences = []
    class_counts = {}

    for analysis in analyses:
        total_detections += analysis.detections
        if analysis.results_json:
            data = json.loads(analysis.results_json)
            all_confidences.extend(data.get("confidences", []))
            for cls in data.get("classes", []):
                class_counts[cls] = class_counts.get(cls, 0) + 1

    avg_conf = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    
    # Calculate percentages
    total_classes = sum(class_counts.values())
    class_dist = {cls: (count / total_classes) * 100 for cls, count in class_counts.items()} if total_classes > 0 else {}

    return {
        "total_images": len(analyses),
        "total_detections": total_detections,
        "avg_confidence": round(avg_conf, 4),
        "class_distribution": class_dist,
        "class_counts": class_counts
    }

@app.get("/folders/{folder_id}/analyses", response_model=List[schemas.Analysis])
def read_folder_analyses(folder_id: int, db: Session = Depends(get_db)):
    return db.query(database.Analysis).filter(database.Analysis.folder_id == folder_id).all()

@app.get("/")
def read_root():
    return {"message": "API is running. Access /static/index.html for the UI."}

@app.get("/design")
def read_design():
    return FileResponse("static/design.html")
