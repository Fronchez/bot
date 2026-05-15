"""Long-term AI memory and trend signal models."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MemoryKind(StrEnum):
    """Types of memory records stored by the autonomous agent."""

    AUDIENCE_INTEREST = "audience_interest"
    STYLE_RULE = "style_rule"
    WINNING_HOOK = "winning_hook"
    BLOCKED_PATTERN = "blocked_pattern"
    CONTENT_LEARNING = "content_learning"


class TrendSource(StrEnum):
    """Supported trend source families."""

    HACKERNEWS = "hackernews"
    REDDIT = "reddit"
    YOUTUBE_RSS = "youtube_rss"
    NEWS_RSS = "news_rss"
    TELEGRAM_PUBLIC = "telegram_public"
    MANUAL = "manual"


class MemoryItem(Base):
    """A persistent semantic memory item used for RAG and strategy adaptation."""

    __tablename__ = "memory_items"
    __table_args__ = (
        Index("ix_memory_kind_score", "kind", "score"),
        UniqueConstraint("kind", "key", name="uq_memory_kind_key"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    kind: Mapped[MemoryKind] = mapped_column(Enum(MemoryKind), index=True)
    key: Mapped[str] = mapped_column(String(240))
    text: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding: Mapped[list[float]] = mapped_column(JSONB, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TrendSignal(Base):
    """A normalized trend candidate collected from a compliant source."""

    __tablename__ = "trend_signals"
    __table_args__ = (Index("ix_trend_source_score", "source", "score"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source: Mapped[TrendSource] = mapped_column(Enum(TrendSource), index=True)
    external_id: Mapped[str | None] = mapped_column(String(240), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(2048))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
