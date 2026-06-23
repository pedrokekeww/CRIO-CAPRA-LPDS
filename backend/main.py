from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import asyncio
import os
import shutil
import time
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.source_manager import source_manager
    db = next(get_db())
    active_sources = crud.get_sources(db)
    for source in active_sources:
        if source.is_active:
            await source_manager.start_source(source.id, source)
    db.close()
    yield
    await source_manager.stop_all()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- AREAS & RULES ---
@app.get("/api/areas/", response_model=List[schemas.Area])
def read_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_areas(db, skip=skip, limit=limit)

@app.post("/api/areas/", response_model=schemas.Area)
def create_area(area: schemas.AreaCreate, db: Session = Depends(get_db)):
    return crud.create_area(db=db, area=area)

@app.delete("/api/areas/{area_id}")
def delete_area(area_id: int, db: Session = Depends(get_db)):
    crud.delete_area(db, area_id)
    return {"message": "deleted"}

@app.post("/api/areas/{area_id}/rules/", response_model=schemas.PPERule)
def create_rule(area_id: int, rule: schemas.PPERuleCreate, db: Session = Depends(get_db)):
    return crud.create_ppe_rule(db=db, area_id=area_id, rule=rule)

@app.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    crud.delete_ppe_rule(db, rule_id)
    return {"message": "deleted"}

# --- SOURCES ---
@app.get("/api/sources/", response_model=List[schemas.VideoSource])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sources(db, skip=skip, limit=limit)

@app.post("/api/sources/", response_model=schemas.VideoSource)
async def create_source(source: schemas.VideoSourceCreate, db: Session = Depends(get_db)):
    db_source = crud.create_source(db=db, source=source)
    if db_source.is_active and db_source.source_type not in ["VIDEO_FILE", "IMAGE"]: 
        # Video and Image need upload first before starting
        from services.source_manager import source_manager
        await source_manager.start_source(db_source.id, db_source)
    return db_source

@app.put("/api/sources/{source_id}", response_model=schemas.VideoSource)
async def update_source(source_id: int, source: schemas.VideoSourceCreate, db: Session = Depends(get_db)):
    db_source = crud.update_source(db, source_id, source)
    from services.source_manager import source_manager
    if db_source.is_active:
        await source_manager.start_source(db_source.id, db_source)
    else:
        await source_manager.stop_source(db_source.id)
    return db_source

@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    from services.source_manager import source_manager
    await source_manager.stop_source(source_id)
    crud.delete_source(db, source_id)
    return {"message": "deleted"}

# --- UPLOADS FOR SOURCES ---
@app.post("/api/sources/{source_id}/upload_video")
async def upload_video(source_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_source = crud.get_source(db, source_id)
    if not db_source or db_source.source_type != "VIDEO_FILE":
        raise HTTPException(status_code=400, detail="Invalid source")
        
    save_dir = "./storage/videos"
    os.makedirs(save_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(save_dir, f"source_{source_id}_{int(time.time())}{file_ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_source.file_path = file_path
    db.commit()
    
    if db_source.is_active:
        from services.source_manager import source_manager
        await source_manager.start_source(db_source.id, db_source)
        
    return {"message": "uploaded", "file_path": file_path}

@app.post("/api/sources/{source_id}/upload_image")
async def upload_image(source_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_source = crud.get_source(db, source_id)
    if not db_source or db_source.source_type != "IMAGE":
        raise HTTPException(status_code=400, detail="Invalid source")
        
    save_dir = "./storage/images"
    os.makedirs(save_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(save_dir, f"source_{source_id}_{int(time.time())}{file_ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_source.image_path = file_path
    db.commit()
    
    # Push image to passive source queue
    from services.source_manager import source_manager
    if db_source.is_active:
        await source_manager.start_source(db_source.id, db_source)
        import cv2
        frame = cv2.imread(file_path)
        source_impl = source_manager.get_source(source_id)
        if source_impl and hasattr(source_impl, "push_frame"):
            source_impl.push_frame(frame)
            
    return {"message": "uploaded", "file_path": file_path}

# --- SCREEN SHARE WEBSOCKET ---
@app.websocket("/ws/stream/{source_id}")
async def screen_stream(websocket: WebSocket, source_id: int):
    await websocket.accept()
    from services.source_manager import source_manager
    import cv2
    import numpy as np
    import base64
    
    try:
        while True:
            data = await websocket.receive_text()
            # Expecting base64 image data like "data:image/jpeg;base64,..."
            if "," in data:
                b64_data = data.split(",")[1]
                img_bytes = base64.b64decode(b64_data)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                source_impl = source_manager.get_source(source_id)
                if source_impl and hasattr(source_impl, "push_frame"):
                    source_impl.push_frame(frame)
    except WebSocketDisconnect:
        print(f"Screen stream disconnected for source {source_id}")

# --- METRICS & VIOLATIONS ---
@app.get("/api/violations/", response_model=List[schemas.Violation])
def read_violations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_violations(db, skip=skip, limit=limit)

@app.get("/api/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    import datetime
    today = datetime.date.today()
    
    sources = crud.get_sources(db)
    active_sources = len([s for s in sources if s.is_active])
    
    violations = crud.get_violations(db, limit=1000)
    today_violations = [v for v in violations if v.timestamp.date() == today]
    
    metrics = crud.get_metrics(db, limit=1000)
    today_metrics = [m for m in metrics if m.timestamp.date() == today]
    
    total_people = sum([m.total_people for m in today_metrics])
    total_conform = sum([m.total_conform for m in today_metrics])
    
    return {
        "active_cameras": active_sources, # Kept key name for frontend compatibility
        "total_people_detected": total_people,
        "total_conformity": total_conform,
        "total_non_conformity": len(today_violations),
        "compliance_rate": (total_conform / total_people * 100) if total_people > 0 else 100
    }
