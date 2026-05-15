"""Declarative base and model imports for Alembic."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM models."""


# Import models so Alembic can discover metadata.
from app.models.analytics import AnalyticsEvent  # noqa: E402,F401
from app.models.content import ContentItem, ContentStatus, ContentType  # noqa: E402,F401
from app.models.giveaway import Giveaway, GiveawayParticipant  # noqa: E402,F401
from app.models.user import ReputationEvent, TelegramUser  # noqa: E402,F401
