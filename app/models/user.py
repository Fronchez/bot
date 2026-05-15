"""Telegram user and reputation models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TelegramUser(Base):
    """Known Telegram user participating in the community."""

    __tablename__ = "telegram_users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reputation: Mapped[int] = mapped_column(default=0)
    invite_count: Mapped[int] = mapped_column(default=0)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReputationEvent(Base):
    """An immutable reputation adjustment record."""

    __tablename__ = "reputation_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("telegram_users.id", ondelete="CASCADE"))
    reason: Mapped[str] = mapped_column(String(120))
    delta: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
