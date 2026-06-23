from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PPERuleBase(BaseModel):
    ppe_name: str

class PPERuleCreate(PPERuleBase):
    pass

class PPERule(PPERuleBase):
    id: int
    area_id: int

    class Config:
        from_attributes = True

class AreaBase(BaseModel):
    name: str
    description: Optional[str] = None

class AreaCreate(AreaBase):
    pass

class Area(AreaBase):
    id: int
    created_at: datetime
    ppe_rules: List[PPERule] = []

    class Config:
        from_attributes = True

class VideoSourceBase(BaseModel):
    name: str
    source_type: str
    area_id: Optional[int] = None
    is_active: bool = True
    
    rtsp_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    device_index: Optional[int] = None
    file_path: Optional[str] = None
    loop_enabled: bool = False
    playback_speed: float = 1.0
    session_id: Optional[str] = None
    image_path: Optional[str] = None
    is_test_image: bool = False

class VideoSourceCreate(VideoSourceBase):
    pass

class VideoSource(VideoSourceBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ViolationBase(BaseModel):
    source_id: int
    area_id: Optional[int] = None
    violation_type: str
    confidence: float
    image_path: str

class ViolationCreate(ViolationBase):
    pass

class Violation(ViolationBase):
    id: int
    timestamp: datetime
    status_review: str

    class Config:
        from_attributes = True

class DetectionMetrics(BaseModel):
    source_id: int
    timestamp: datetime
    total_people: int
    total_conform: int
    total_non_conform: int

    class Config:
        from_attributes = True
