from __future__ import annotations

from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "development"

    DATABASE_URL: str | None = None
    DATABASE_PATH: str | None = "/data/app.db"

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_PUBLIC_ENDPOINT: str | None = None
    MINIO_USE_SECURE: bool = False
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "bandai-hobby"

    DATA_DIR: str = "/data/import"

    JWT_SECRET: str = "change_me"
    JWT_EXPIRES_IN: int = 86400

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_ROLE: str = "admin"


class VersionInfo(BaseModel):
    name: str = "modellion-admin"
    version: str = "0.1.0"
    env: str = "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
