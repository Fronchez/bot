"""Referral, gamification and monetization models."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReferralStatus(StrEnum):
    """Referral validation state."""

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class CampaignStatus(StrEnum):
    """Monetization campaign lifecycle."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ReferralLink(Base):
    """A tracked invite/referral link owned by a user or campaign."""

    __tablename__ = "referral_links"
    __table_args__ = (UniqueConstraint("code", name="uq_referral_code"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("telegram_users.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(64))
    telegram_invite_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    clicks: Mapped[int] = mapped_column(default=0)
    verified_joins: Mapped[int] = mapped_column(default=0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReferralEvent(Base):
    """A single referral attribution event with fraud-review status."""

    __tablename__ = "referral_events"
    __table_args__ = (Index("ix_referral_status_created", "status", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    referral_link_id: Mapped[UUID] = mapped_column(ForeignKey("referral_links.id", ondelete="CASCADE"))
    referred_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("telegram_users.id"), nullable=True)
    status: Mapped[ReferralStatus] = mapped_column(Enum(ReferralStatus), default=ReferralStatus.PENDING)
    reason: Mapped[str | None] = mapped_column(String(240), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ActivityScore(Base):
    """Gamification score ledger for leaderboards, quests and badges."""

    __tablename__ = "activity_scores"
    __table_args__ = (Index("ix_activity_user_created", "user_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("telegram_users.id", ondelete="CASCADE"))
    points: Mapped[int]
    reason: Mapped[str] = mapped_column(String(120))
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MonetizationCampaign(Base):
    """A compliant sponsorship, affiliate or subscription campaign."""

    __tablename__ = "monetization_campaigns"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(240))
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    disclosure: Mapped[str] = mapped_column(String(500), default="Реклама / партнёрский материал")
    landing_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    budget_cents: Mapped[int] = mapped_column(default=0)
    target_topics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    creative_brief: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
