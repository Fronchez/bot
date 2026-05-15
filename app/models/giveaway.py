"""Giveaway models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Giveaway(Base):
    """A scheduled community giveaway."""

    __tablename__ = "giveaways"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(240))
    prize: Mapped[str] = mapped_column(String(240))
    conditions: Mapped[str] = mapped_column(String(1000))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    winner_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("telegram_users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GiveawayParticipant(Base):
    """A user entry in a giveaway."""

    __tablename__ = "giveaway_participants"
    __table_args__ = (UniqueConstraint("giveaway_id", "user_id", name="uq_giveaway_user"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    giveaway_id: Mapped[UUID] = mapped_column(ForeignKey("giveaways.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("telegram_users.id", ondelete="CASCADE"))
    referral_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
