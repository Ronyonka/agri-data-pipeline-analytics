"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API, pipeline, and dashboard."""

    database_url: str = Field(..., alias="DATABASE_URL")
    open_meteo_base_url: str = Field(
        "https://archive-api.open-meteo.com/v1",
        alias="OPEN_METEO_BASE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
