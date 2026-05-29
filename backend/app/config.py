import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medicine_delivery")
    SQLITE_URL: str = "sqlite:///./medicine_delivery.db"
    
    # JWT Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-medicine-delivery-key-92837423984")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440  # 24 hours
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
