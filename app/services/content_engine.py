"""Autonomous content generation and scheduling engine."""

import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ContentItem, ContentStatus
from app.repositories.content import ContentRepository
from app.services.ai_client import AIClient
from app.services.prompts import (
    CONTENT_STRATEGIST_PROMPT,
    IMAGE_PROMPT_TEMPLATE,
    POST_WRITER_PROMPT,
)
from app.services.trends import TrendService


class ContentEngine:
    """Turns trends and strategy memory into publishable Telegram content."""

    def __init__(self, session: AsyncSession, ai: AIClient | None = None) -> None:
        self.session = session
        self.repo = ContentRepository(session)
        self.ai = ai or AIClient()
        self.trends = TrendService()

    async def generate_next_post(self) -> ContentItem:
        """Create, score and enqueue the next autonomous post."""
        facts = await self.trends.fetch_public_trends()
        facts_text = "\n".join(f"- {fact.title} ({fact.source}, score={fact.score})" for fact in facts[:5])
        strategy = await self.ai.generate_json(
            CONTENT_STRATEGIST_PROMPT.format(
                audience_profile="tech-savvy Telegram audience interested in AI automation",
                winning_themes="AI tools, productivity, Telegram growth, practical guides",
                trend_facts=facts_text,
            )
        )
        post = await self.ai.generate_json(
            POST_WRITER_PROMPT.format(
                title=strategy.get("title", "AI-тренд"),
                angle=strategy.get("angle", "практическая польза"),
                format=strategy.get("format", "короткий пост"),
                style_memory="energetic, useful, ethical, no clickbait lies",
            )
        )
        image_url = await self.ai.generate_image_url(
            IMAGE_PROMPT_TEMPLATE.format(subject=post.get("image_prompt", post.get("title")), mood="energetic")
        )
        title = str(post.get("title") or strategy.get("title") or "AI-пост")
        body = str(post.get("body_markdown") or "Что думаете?")
        item = ContentItem(
            title=title[:240],
            body_markdown=body,
            image_url=image_url,
            source_url=facts[0].url if facts else None,
            dedupe_hash=self._hash(title, body),
            score=float(strategy.get("score", 0.75) or 0.75),
            status=ContentStatus.SCHEDULED,
            scheduled_at=self._next_slot(),
            metadata_json={"strategy": strategy, "post": post},
        )
        try:
            return await self.repo.add(item)
        except IntegrityError:
            await self.session.rollback()
            item.dedupe_hash = self._hash(title, body + datetime.now(UTC).isoformat())
            return await self.repo.add(item)

    @staticmethod
    def _hash(title: str, body: str) -> str:
        return hashlib.sha256(f"{title}\n{body}".encode()).hexdigest()

    @staticmethod
    def _next_slot() -> datetime:
        """Simple initial scheduler: next quarter-hour, later optimized by analytics."""
        now = datetime.now(UTC)
        return now.replace(second=0, microsecond=0) + timedelta(minutes=15 - now.minute % 15)
