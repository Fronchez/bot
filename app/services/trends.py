"""Trend discovery service using compliant public sources and configured feeds."""

from dataclasses import dataclass
from xml.etree import ElementTree

import httpx


@dataclass(frozen=True)
class TrendFact:
    """A normalized trend candidate."""

    title: str
    url: str
    source: str
    score: float
    summary: str | None = None


class TrendService:
    """Fetch and rank public trend candidates without scraping private surfaces."""

    async def fetch_public_trends(self) -> list[TrendFact]:
        """Fetch trend-like public items from several compliant public endpoints."""
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "autonomous-telegram-ai-bot/0.1"}) as client:
            results = await self._safe_collect(client)
        return sorted(results, key=lambda item: item.score, reverse=True)

    async def _safe_collect(self, client: httpx.AsyncClient) -> list[TrendFact]:
        collectors = [
            self._fetch_hackernews(client),
            self._fetch_reddit_public_json(client, "technology"),
            self._fetch_reddit_public_json(client, "ArtificialInteligence"),
            self._fetch_youtube_rss(client, "UCXuqSBlHAE6Xw-yeJA0Tunw"),
            self._fetch_news_rss(client, "https://hnrss.org/frontpage"),
        ]
        results: list[TrendFact] = []
        for collector in collectors:
            try:
                results.extend(await collector)
            except (httpx.HTTPError, ValueError, ElementTree.ParseError, KeyError, TypeError):
                continue
        return self._dedupe(results)

    async def _fetch_hackernews(self, client: httpx.AsyncClient) -> list[TrendFact]:
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
        return items

    async def _fetch_reddit_public_json(self, client: httpx.AsyncClient, subreddit: str) -> list[TrendFact]:
        data = (await client.get(f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10")).json()
        children = data.get("data", {}).get("children", [])
        return [
            TrendFact(
                title=child["data"].get("title", ""),
                url="https://reddit.com" + child["data"].get("permalink", ""),
                source=f"reddit:{subreddit}",
                score=float(child["data"].get("score", 0)),
                summary=child["data"].get("selftext") or None,
            )
            for child in children
            if child.get("data", {}).get("title")
        ]

    async def _fetch_youtube_rss(self, client: httpx.AsyncClient, channel_id: str) -> list[TrendFact]:
        xml = (await client.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")).text
        root = ElementTree.fromstring(xml)
        ns = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}
        items: list[TrendFact] = []
        for entry in root.findall("atom:entry", ns)[:10]:
            title = entry.findtext("atom:title", default="", namespaces=ns)
            link = entry.find("atom:link", ns)
            url = link.attrib.get("href", "") if link is not None else ""
            items.append(TrendFact(title=title, url=url, source="youtube_rss", score=50.0))
        return items

    async def _fetch_news_rss(self, client: httpx.AsyncClient, feed_url: str) -> list[TrendFact]:
        xml = (await client.get(feed_url)).text
        root = ElementTree.fromstring(xml)
        items: list[TrendFact] = []
        for item in root.findall("./channel/item")[:10]:
            title = item.findtext("title", default="")
            url = item.findtext("link", default="")
            items.append(TrendFact(title=title, url=url, source="news_rss", score=25.0))
        return items

    @staticmethod
    def _dedupe(items: list[TrendFact]) -> list[TrendFact]:
        seen: set[str] = set()
        unique: list[TrendFact] = []
        for item in items:
            key = item.url or item.title.lower()
            if key and key not in seen:
                seen.add(key)
                unique.append(item)
        return unique
