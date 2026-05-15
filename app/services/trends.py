"""Trend discovery service using compliant public sources and configured feeds."""

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class TrendFact:
    """A normalized trend candidate."""

    title: str
    url: str
    source: str
    score: float


class TrendService:
    """Fetch and rank public trend candidates without scraping private surfaces."""

    async def fetch_public_trends(self) -> list[TrendFact]:
        """Fetch trend-like public items from Hacker News as a safe default source."""
        async with httpx.AsyncClient(timeout=10) as client:
            ids = (await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")).json()[:20]
            items: list[TrendFact] = []
            for story_id in ids[:10]:
                data = (await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")).json()
                if data and data.get("title"):
                    items.append(
                        TrendFact(
                            title=data["title"],
                            url=data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                            source="hackernews",
                            score=float(data.get("score", 0)),
                        )
                    )
        return sorted(items, key=lambda item: item.score, reverse=True)
