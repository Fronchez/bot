"""Pydantic schemas for content."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.content import ContentStatus, ContentType


class ContentCreate(BaseModel):
    """Request to create content manually or from AI."""

    content_type: ContentType = ContentType.POST
    title: str = Field(min_length=3, max_length=240)
    body_markdown: str = Field(min_length=10)
    image_url: str | None = None
    source_url: str | None = None
    scheduled_at: datetime | None = None


class ContentRead(ContentCreate):
    """Content item API response."""

    id: UUID
    status: ContentStatus
    score: float
    telegram_message_id: int | None = None
    published_at: datetime | None = None

    class Config:
        from_attributes = True
