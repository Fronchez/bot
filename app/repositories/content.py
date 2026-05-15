"""Content repository."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ContentItem, ContentStatus


class ContentRepository:
    """Persistence operations for content queue."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: ContentItem) -> ContentItem:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get(self, item_id: UUID) -> ContentItem | None:
        return await self.session.get(ContentItem, item_id)

    async def list_recent(self, limit: int = 50) -> list[ContentItem]:
        result = await self.session.scalars(
            select(ContentItem).order_by(ContentItem.created_at.desc()).limit(limit)
        )
        return list(result)

    async def due_for_publication(self, limit: int = 5) -> list[ContentItem]:
        result = await self.session.scalars(
            select(ContentItem)
            .where(ContentItem.status == ContentStatus.SCHEDULED)
            .where(ContentItem.scheduled_at <= datetime.now(UTC))
            .order_by(ContentItem.scheduled_at.asc())
            .limit(limit)
        )
        return list(result)
