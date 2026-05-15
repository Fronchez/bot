"""Initial schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial tables."""
    content_status = postgresql.ENUM("DRAFT", "APPROVED", "SCHEDULED", "PUBLISHED", "REJECTED", name="contentstatus")
    content_type = postgresql.ENUM("POST", "POLL", "MEME", "GIVEAWAY", "AD", name="contenttype")
    content_status.create(op.get_bind(), checkfirst=True)
    content_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "content_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content_type", content_type, nullable=False),
        sa.Column("status", content_status, nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=2048), nullable=True),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("dedupe_hash", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("telegram_message_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_status_scheduled", "content_items", ["status", "scheduled_at"])
    op.create_index("uq_content_hash", "content_items", ["dedupe_hash"], unique=True)
    op.create_table(
        "telegram_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("reputation", sa.Integer(), nullable=False),
        sa.Column("invite_count", sa.Integer(), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_telegram_users_telegram_id"), "telegram_users", ["telegram_id"], unique=True)
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=128), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analytics_events_event_type"), "analytics_events", ["event_type"])
    op.create_index(op.f("ix_analytics_events_subject_id"), "analytics_events", ["subject_id"])
    op.create_index(op.f("ix_analytics_events_created_at"), "analytics_events", ["created_at"])
    op.create_table(
        "reputation_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["telegram_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "giveaways",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("prize", sa.String(length=240), nullable=False),
        sa.Column("conditions", sa.String(length=1000), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("winner_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["winner_user_id"], ["telegram_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "giveaway_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("giveaway_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("referral_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["giveaway_id"], ["giveaways.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["telegram_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("giveaway_id", "user_id", name="uq_giveaway_user"),
    )


def downgrade() -> None:
    """Drop initial tables."""
    op.drop_table("giveaway_participants")
    op.drop_table("giveaways")
    op.drop_table("reputation_events")
    op.drop_index(op.f("ix_analytics_events_created_at"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_subject_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_event_type"), table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_index(op.f("ix_telegram_users_telegram_id"), table_name="telegram_users")
    op.drop_table("telegram_users")
    op.drop_index("uq_content_hash", table_name="content_items")
    op.drop_index("ix_content_status_scheduled", table_name="content_items")
    op.drop_table("content_items")
    postgresql.ENUM(name="contentstatus").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="contenttype").drop(op.get_bind(), checkfirst=True)
