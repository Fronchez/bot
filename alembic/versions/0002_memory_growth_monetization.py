"""Memory, growth and monetization schema.

Revision ID: 0002_memory_growth
Revises: 0001_initial
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_memory_growth"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create memory, referral, gamification and monetization tables."""
    memory_kind = postgresql.ENUM(
        "AUDIENCE_INTEREST",
        "STYLE_RULE",
        "WINNING_HOOK",
        "BLOCKED_PATTERN",
        "CONTENT_LEARNING",
        name="memorykind",
    )
    trend_source = postgresql.ENUM(
        "HACKERNEWS",
        "REDDIT",
        "YOUTUBE_RSS",
        "NEWS_RSS",
        "TELEGRAM_PUBLIC",
        "MANUAL",
        name="trendsource",
    )
    referral_status = postgresql.ENUM("PENDING", "VERIFIED", "REJECTED", name="referralstatus")
    campaign_status = postgresql.ENUM("DRAFT", "ACTIVE", "PAUSED", "COMPLETED", name="campaignstatus")
    for enum in (memory_kind, trend_source, referral_status, campaign_status):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "memory_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", memory_kind, nullable=False),
        sa.Column("key", sa.String(length=240), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kind", "key", name="uq_memory_kind_key"),
    )
    op.create_index("ix_memory_kind_score", "memory_items", ["kind", "score"])
    op.create_index(op.f("ix_memory_items_kind"), "memory_items", ["kind"])

    op.create_table(
        "trend_signals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", trend_source, nullable=False),
        sa.Column("external_id", sa.String(length=240), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trend_source_score", "trend_signals", ["source", "score"])
    op.create_index(op.f("ix_trend_signals_source"), "trend_signals", ["source"])
    op.create_index(op.f("ix_trend_signals_collected_at"), "trend_signals", ["collected_at"])

    op.create_table(
        "referral_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("telegram_invite_link", sa.String(length=2048), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column("verified_joins", sa.Integer(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["telegram_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_referral_code"),
    )
    op.create_table(
        "referral_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("referral_link_id", sa.Uuid(), nullable=False),
        sa.Column("referred_user_id", sa.Uuid(), nullable=True),
        sa.Column("status", referral_status, nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["referral_link_id"], ["referral_links.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referred_user_id"], ["telegram_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_referral_status_created", "referral_events", ["status", "created_at"])

    op.create_table(
        "activity_scores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["telegram_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_user_created", "activity_scores", ["user_id", "created_at"])

    op.create_table(
        "monetization_campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("status", campaign_status, nullable=False),
        sa.Column("disclosure", sa.String(length=500), nullable=False),
        sa.Column("landing_url", sa.String(length=2048), nullable=True),
        sa.Column("budget_cents", sa.Integer(), nullable=False),
        sa.Column("target_topics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("creative_brief", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop memory, referral, gamification and monetization tables."""
    op.drop_table("monetization_campaigns")
    op.drop_index("ix_activity_user_created", table_name="activity_scores")
    op.drop_table("activity_scores")
    op.drop_index("ix_referral_status_created", table_name="referral_events")
    op.drop_table("referral_events")
    op.drop_table("referral_links")
    op.drop_index(op.f("ix_trend_signals_collected_at"), table_name="trend_signals")
    op.drop_index(op.f("ix_trend_signals_source"), table_name="trend_signals")
    op.drop_index("ix_trend_source_score", table_name="trend_signals")
    op.drop_table("trend_signals")
    op.drop_index(op.f("ix_memory_items_kind"), table_name="memory_items")
    op.drop_index("ix_memory_kind_score", table_name="memory_items")
    op.drop_table("memory_items")
    for name in ("campaignstatus", "referralstatus", "trendsource", "memorykind"):
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
