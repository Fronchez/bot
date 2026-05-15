"""Long-term AI memory and lightweight semantic retrieval."""

import hashlib
import math
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryItem, MemoryKind
from app.services.ai_client import AIClient


class MemoryService:
    """Stores audience, style and performance memory for autonomous decisions."""

    def __init__(self, session: AsyncSession, ai: AIClient | None = None) -> None:
        self.session = session
        self.ai = ai or AIClient()

    async def remember(
        self,
        kind: MemoryKind,
        key: str,
        text: str,
        score_delta: float = 1.0,
        metadata: dict | None = None,
    ) -> MemoryItem:
        """Upsert a memory item and refresh its embedding."""
        item = await self.session.scalar(select(MemoryItem).where(MemoryItem.kind == kind, MemoryItem.key == key))
        embedding = await self.ai.embed_text(text)
        if item is None:
            item = MemoryItem(
                kind=kind,
                key=key,
                text=text,
                score=score_delta,
                embedding=embedding,
                metadata_json=metadata or {},
            )
        else:
            item.text = text
            item.score += score_delta
            item.embedding = embedding
            item.metadata_json = {**item.metadata_json, **(metadata or {})}
            item.last_seen_at = datetime.now(UTC)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def retrieve(self, query: str, kinds: list[MemoryKind] | None = None, limit: int = 5) -> list[MemoryItem]:
        """Return memory items ranked by cosine similarity and score."""
        query_embedding = await self.ai.embed_text(query)
        stmt = select(MemoryItem)
        if kinds:
            stmt = stmt.where(MemoryItem.kind.in_(kinds))
        items = list(await self.session.scalars(stmt.limit(500)))
        ranked = sorted(
            items,
            key=lambda item: self._cosine(query_embedding, item.embedding or []) + item.score / 100.0,
            reverse=True,
        )
        return ranked[:limit]

    async def style_context(self) -> str:
        """Build a compact style context for post generation prompts."""
        items = await self.retrieve(
            "Telegram winning hooks style audience preferences",
            [MemoryKind.STYLE_RULE, MemoryKind.WINNING_HOOK, MemoryKind.AUDIENCE_INTEREST],
            limit=8,
        )
        return "\n".join(f"- {item.kind.value}: {item.text}" for item in items)

    @staticmethod
    def deterministic_embedding(text: str, dimensions: int = 64) -> list[float]:
        """Create a stable local embedding for development and tests."""
        vector = [0.0] * dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            idx = int.from_bytes(digest[:2], "big") % dimensions
            vector[idx] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        return sum(left[i] * right[i] for i in range(size))
