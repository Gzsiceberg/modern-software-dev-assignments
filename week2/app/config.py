from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Action Item Extractor"
    debug: bool = False

    ollama_model: str = "llama3.1:8b"
    ollama_host: str = "http://localhost:11434"

    db_path: str = "week2/data/app.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()


def get_db_path() -> Path:
    return Path(settings.db_path)


def get_data_dir() -> Path:
    return get_db_path().parent
