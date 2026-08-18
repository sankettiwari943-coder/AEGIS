import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AEGIS — AI Emergency & Geospatial Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CORS_ORIGINS: List[str] = ["*"]
    SIMULATION_MODE_LABEL: str = "SIMULATION / DEMONSTRATION DATA"
    DEFAULT_SCENARIO: str = "Monsoon Flood — River Basin District"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
