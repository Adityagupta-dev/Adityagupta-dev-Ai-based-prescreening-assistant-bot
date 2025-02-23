# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional, Dict
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY", None)
    
    # Model Settings
    USE_GEMINI: bool = True
    GEMINI_MODEL: str = "models/gemini-pro"
    HUGGINGFACE_MODEL: str = "google/flan-t5-base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    
    # ChromaDB Settings
    CHROMA_DB_PATH: str = "./data/chroma_db"
    COLLECTION_NAME: str = "question_bank"
    
    # Complexity Settings
    MIN_COMPLEXITY: int = 1
    MAX_COMPLEXITY: int = 3
    COMPLEXITY_STEP: float = 0.5

    # Error Messages
    ERROR_MESSAGES: Dict[str, str] = {
        "model_unavailable": "Primary model unavailable, switching to backup model",
        "invalid_role": "Selected role is not available",
        "no_questions": "No questions available for the selected complexity",
        "db_connection": "Error connecting to the database",
        "evaluation_error": "Error evaluating answer",
        "model_error": "Error initializing the language model"
    }

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

# Make ERROR_MESSAGES easily accessible
ERROR_MESSAGES = get_settings().ERROR_MESSAGES

import os

RECRUITER_EMAIL = os.getenv("RECRUITER_EMAIL", "recruiter@company.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-specific-password")