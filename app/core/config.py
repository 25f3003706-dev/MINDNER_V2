"""Application configuration management using Pydantic Settings."""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Mindner"
    ENVIRONMENT: str = "development"
    DATABASE_PATH: str = "database/caregiver.db"
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    SECRET_KEY: str = "mindner-dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    @property
    def absolute_db_path(self) -> Path:
        """Returns the absolute path to the SQLite database."""
        db_p = Path(self.DATABASE_PATH)
        if db_p.is_absolute():
            return db_p
        return (BASE_DIR / db_p).resolve()


settings = Settings()
