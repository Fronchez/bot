"""Self-improving autonomous decision loop."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics import AnalyticsService
from app.services.content_engine import ContentEngine


class DecisionEngine:
    """Adapts strategy based on analytics and keeps the queue healthy."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.analytics = AnalyticsService(session)
        self.content = ContentEngine(session)

    async def run_cycle(self) -> dict[str, float | str]:
        """Run one autonomous optimization cycle."""
        summary = await self.analytics.engagement_summary()
        target_queue_items = 6 if summary["engagement_rate"] >= 0.05 else 4
        created = await self.content.generate_next_post()
        return {
            "action": "generated_content",
            "content_id": str(created.id),
            "target_queue_items": float(target_queue_items),
            **summary,
        }
