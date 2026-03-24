from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./yolo_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    model_id = Column(String)
    api_key = Column(String)

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="folder")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"))
    image_url = Column(String)  # Base64 or path
    detections = Column(Integer)
    results_json = Column(String, nullable=True) # Full JSON metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    folder = relationship("Folder", back_populates="analyses")

Base.metadata.create_all(bind=engine)
