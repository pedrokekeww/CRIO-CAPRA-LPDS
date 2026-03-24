from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ModelConfigBase(BaseModel):
    name: str
    model_id: str
    api_key: str

class ModelConfigCreate(ModelConfigBase):
    pass

class ModelConfig(ModelConfigBase):
    id: int

    class Config:
        from_attributes = True

class FolderBase(BaseModel):
    name: str

class FolderCreate(FolderBase):
    pass

class Folder(FolderBase):
    id: int
    created_at: datetime
    analysis_count: Optional[int] = 0

    class Config:
        from_attributes = True

class AnalysisBase(BaseModel):
    name: str
    folder_id: int

class AnalysisCreate(AnalysisBase):
    image_url: str
    detections: int
    results_json: Optional[str] = None

class Analysis(AnalysisCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
