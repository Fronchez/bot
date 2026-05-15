"""Content queue models."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContentStatus(StrEnum):
    """Lifecycle states for generated content."""

    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"


class ContentType(StrEnum):
    """Supported content formats."""

    POST = "post"
    POLL = "poll"
    MEME = "meme"
    GIVEAWAY = "giveaway"
    AD = "ad"


class ContentItem(Base):
    """A generated item in the autonomous content queue."""

    __tablename__ = "content_items"
    __table_args__ = (
        Index("ix_content_status_scheduled", "status", "scheduled_at"),
        Index("uq_content_hash", "dedupe_hash", unique=True),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), default=ContentType.POST)
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    title: Mapped[str] = mapped_column(String(240))
    body_markdown: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    dedupe_hash: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(default=0.0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    telegram_message_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
