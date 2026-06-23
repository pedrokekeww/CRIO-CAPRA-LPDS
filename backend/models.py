from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Area(Base):
    __tablename__ = "areas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    video_sources = relationship("VideoSource", back_populates="area")
    ppe_rules = relationship("PPERule", back_populates="area", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="area")

class VideoSource(Base):
    __tablename__ = "video_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    source_type = Column(String) # RTSP, WEBCAM, VIDEO_FILE, SCREEN_SHARE, IMAGE
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    status = Column(String, default="offline")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Polymorphic fields (can be null depending on type)
    rtsp_url = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    device_index = Column(Integer, nullable=True)
    file_path = Column(String, nullable=True)
    loop_enabled = Column(Boolean, default=False)
    playback_speed = Column(Float, default=1.0)
    session_id = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    is_test_image = Column(Boolean, default=False)

    area = relationship("Area", back_populates="video_sources")
    violations = relationship("Violation", back_populates="video_source")

class PPERule(Base):
    __tablename__ = "area_required_ppe"
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    ppe_name = Column(String)

    area = relationship("Area", back_populates="ppe_rules")

class Violation(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("video_sources.id"))
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    violation_type = Column(String)
    confidence = Column(Float)
    image_path = Column(String)
    status_review = Column(String, default="pending")

    video_source = relationship("VideoSource", back_populates="violations")
    area = relationship("Area", back_populates="violations")

class DetectionMetrics(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("video_sources.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_people = Column(Integer, default=0)
    total_conform = Column(Integer, default=0)
    total_non_conform = Column(Integer, default=0)
