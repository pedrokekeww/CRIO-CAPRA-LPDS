from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ppe_monitor.db"
    ROBOFLOW_API_KEY: str = "5QaqrsR4nedevUxjLzbq"
    ROBOFLOW_MODEL_ID: str = "ppe-vum8g/2"
    ROBOFLOW_API_URL: str = "https://detect.roboflow.com"
    CONFIDENCE_THRESHOLD: int = 40 # 0-100 percentage
    STORAGE_PATH: str = "./storage/violations"
    FRAME_SKIP: int = 15 # Run inference every N frames

    class Config:
        env_file = ".env"

settings = Settings()
