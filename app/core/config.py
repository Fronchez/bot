"""Application configuration."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "local"
    app_name: str = "Autonomous Telegram AI Bot"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://bot:bot@localhost:5432/bot"
    redis_url: str = "redis://localhost:6379/0"
    telegram_bot_token: str = ""
    telegram_channel_id: str = ""
    telegram_admin_ids: list[int] = Field(default_factory=list)
    openai_api_key: str = ""
    openai_text_model: str = "gpt-4.1-mini"
    openai_image_model: str = "gpt-image-1"
    jwt_secret: str = "change-me"
    rate_limit_per_minute: Annotated[int, Field(ge=1, le=300)] = 60
    posting_timezone: str = "UTC"
    safe_mode: bool = True

    @field_validator("telegram_admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> list[int]:
        """Parse comma-separated admin ids from env."""
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [int(item) for item in value]
        raise TypeError("telegram_admin_ids must be a CSV string or list")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
