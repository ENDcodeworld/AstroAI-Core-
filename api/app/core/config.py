"""
Application configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "AstroAI-Core"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://astroai:password@localhost:5432/astroai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # External APIs
    NASA_API_KEY: str = ""
    ESA_API_KEY: str = ""
    
    # Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_BUCKET: str = "astroai-data"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    
    # ML
    MODEL_PATH: str = "./models"
    DEVICE: str = "cpu"  # or "cuda"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
