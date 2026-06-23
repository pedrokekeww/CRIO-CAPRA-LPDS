import cv2
import time
import os
import asyncio
from datetime import datetime
from services.inference import infer_frame
from database import SessionLocal
from crud import get_ppe_rules_by_area, create_violation, create_metrics
from schemas import ViolationCreate, DetectionMetrics
from config import settings
from main import manager
from .sources.base import BaseSource

def calculate_iou(boxA, boxB):
    xA = max(boxA[0] - boxA[2]/2, boxB[0] - boxB[2]/2)
    yA = max(boxA[1] - boxA[3]/2, boxB[1] - boxB[3]/2)
    xB = min(boxA[0] + boxA[2]/2, boxB[0] + boxB[2]/2)
    yB = min(boxA[1] + boxA[3]/2, boxB[1] + boxB[3]/2)
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

async def process_video_stream(source_id: int, area_id: int, source: BaseSource, stop_event: asyncio.Event):
    print(f"Starting generic stream processing for source {source_id}")
    source.start()
    
    frame_count = 0
    
    while not stop_event.is_set():
        ret, frame = source.get_frame()
        
        if not ret:
            status = source.get_status()
            if status == "ended":
                # Video file ended, we can stop the task
                break
            elif status == "waiting_for_frames":
                # Passive source waiting
                await asyncio.sleep(0.5)
                continue
            else:
                # Connection error or something
                print(f"Source {source_id} failed to get frame. Retrying in 2s...")
                await asyncio.sleep(2)
                source.start() # try reconnecting
                continue
                
        frame_count += 1
        
        if frame_count % settings.FRAME_SKIP != 0:
            await asyncio.sleep(0.01)
            continue
            
        # Run inference
        results = await asyncio.to_thread(infer_frame, frame)
        if not results or "predictions" not in results:
            continue
            
        predictions = results["predictions"]
        
        db = SessionLocal()
        
        conform = 0
        non_conform = 0
        violations_batch = []
        people = [p for p in predictions if p["class"].lower() == "person" and p["confidence"] >= settings.CONFIDENCE_THRESHOLD / 100.0]
        
        if area_id:
            rules = get_ppe_rules_by_area(db, area_id)
            required_ppe = [r.ppe_name.lower() for r in rules]
            ppes = [p for p in predictions if p["class"].lower() in required_ppe and p["confidence"] >= settings.CONFIDENCE_THRESHOLD / 100.0]
            
            for person in people:
                p_box = [person["x"], person["y"], person["width"], person["height"]]
                person_ppes = []
                
                for ppe in ppes:
                    ppe_box = [ppe["x"], ppe["y"], ppe["width"], ppe["height"]]
                    iou = calculate_iou(p_box, ppe_box)
                    if iou > 0.05:
                        person_ppes.append(ppe["class"].lower())
                        
                missing_ppe = [ppe for ppe in required_ppe if ppe not in person_ppes]
                
                if missing_ppe:
                    non_conform += 1
                    for missing in missing_ppe:
                        violations_batch.append((missing, person["confidence"]))
                else:
                    conform += 1
        else:
            # If no area is linked, assume everyone is conforming just for counting
            conform = len(people)
                
        # Handle violations
        if non_conform > 0:
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_dir = os.path.join(settings.STORAGE_PATH, date_str)
            os.makedirs(save_dir, exist_ok=True)
            filename = f"source_{source_id}_{int(time.time())}.jpg"
            filepath = os.path.join(save_dir, filename)
            cv2.imwrite(filepath, frame)
            
            for violation_type, conf in violations_batch:
                v = ViolationCreate(
                    source_id=source_id,
                    area_id=area_id, # Can be None
                    violation_type=f"no_{violation_type}",
                    confidence=conf,
                    image_path=filepath
                )
                db_v = create_violation(db, v)
                
                alert = {
                    "type": "new_violation",
                    "data": {
                        "id": db_v.id,
                        "source_id": source_id,
                        "area_id": area_id,
                        "violation_type": db_v.violation_type,
                        "timestamp": db_v.timestamp.isoformat(),
                        "image_path": filepath
                    }
                }
                asyncio.create_task(manager.broadcast(alert))
                
        live_stats = {
            "type": "live_stats",
            "data": {
                "source_id": source_id,
                "people": len(people),
                "conform": conform,
                "non_conform": non_conform,
                "source_status": source.get_status()
            }
        }
        asyncio.create_task(manager.broadcast(live_stats))
        
        from services.source_manager import source_manager
        
        # Draw bounding boxes for preview
        preview_frame = frame.copy()
        for p in predictions:
            color = (0, 255, 0) if p["class"].lower() == "person" else (255, 0, 0)
            x, y, w, h = int(p["x"]), int(p["y"]), int(p["width"]), int(p["height"])
            cv2.rectangle(preview_frame, (x - w//2, y - h//2), (x + w//2, y + h//2), color, 2)
            cv2.putText(preview_frame, p["class"], (x - w//2, y - h//2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        _, buffer = cv2.imencode('.jpg', preview_frame)
        source_manager.latest_frames[source_id] = buffer.tobytes()
        
        if len(people) > 0:
            m = DetectionMetrics(
                source_id=source_id,
                timestamp=datetime.utcnow(),
                total_people=len(people),
                total_conform=conform,
                total_non_conform=non_conform
            )
            create_metrics(db, m)
            
        db.close()
        
    source.stop()
    print(f"Stopped stream for source {source_id}")
