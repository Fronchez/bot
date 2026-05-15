"""Analytics and strategy adaptation service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent


class AnalyticsService:
    """Records events and computes content strategy signals."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(self, event_type: str, subject_id: str | None, payload: dict) -> AnalyticsEvent:
        """Append an analytics event."""
        event = AnalyticsEvent(event_type=event_type, subject_id=subject_id, payload=payload)
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def engagement_summary(self) -> dict[str, float]:
        """Return aggregate metrics used by the decision engine."""
        result = await self.session.execute(
            select(AnalyticsEvent.event_type, func.count()).group_by(AnalyticsEvent.event_type)
        )
        counts = {str(row[0]): float(row[1]) for row in result.all()}
        impressions = max(counts.get("impression", 0.0), 1.0)
        reactions = counts.get("reaction", 0.0) + counts.get("comment", 0.0) + counts.get("share", 0.0)
        return {"engagement_rate": reactions / impressions, "events": sum(counts.values())}
