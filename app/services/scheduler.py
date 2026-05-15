"""Adaptive posting scheduler."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent


class AdaptiveScheduler:
    """Chooses posting windows from historical engagement while avoiding spammy frequency."""

    def __init__(self, session: AsyncSession, timezone_name: str = "UTC") -> None:
        self.session = session
        self.timezone = ZoneInfo(timezone_name)

    async def best_hours(self, limit: int = 3) -> list[int]:
        """Return best UTC hours from reaction/comment/share events."""
        rows = await self.session.execute(
            select(extract("hour", AnalyticsEvent.created_at), func.count())
            .where(AnalyticsEvent.event_type.in_(["reaction", "comment", "share", "click"]))
            .group_by(extract("hour", AnalyticsEvent.created_at))
            .order_by(func.count().desc())
            .limit(limit)
        )
        hours = [int(row[0]) for row in rows.all()]
        return hours or [9, 13, 18]

    async def next_slot(self, minimum_gap_minutes: int = 90) -> datetime:
        """Return the next compliant posting slot."""
        now = datetime.now(UTC)
        for hour in await self.best_hours():
            candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if candidate <= now + timedelta(minutes=minimum_gap_minutes):
                candidate += timedelta(days=1)
            if candidate > now:
                return candidate
        return now + timedelta(minutes=minimum_gap_minutes)
