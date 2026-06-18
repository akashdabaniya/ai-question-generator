"""Application configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Central configuration for the AI Question Generator backend."""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_questions.db"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # NLP Model
    MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Text processing limits
    MAX_TEXT_LENGTH: int = 50_000
    MIN_TEXT_LENGTH: int = 50

    # Question generation defaults
    DEFAULT_QUESTION_COUNT: int = 5
    MAX_QUESTION_COUNT: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
