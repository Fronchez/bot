"""AI-assisted moderation service."""

import re
from dataclasses import dataclass

from app.services.ai_client import AIClient
from app.services.prompts import MODERATION_PROMPT

SPAM_PATTERNS = [
    re.compile(r"(?i)free\s+crypto|airdrop|guaranteed\s+profit"),
    re.compile(r"(?i)подписывайтесь\s+на\s+мой\s+канал"),
    re.compile(r"https?://\S+", re.IGNORECASE),
]


@dataclass(frozen=True)
class ModerationDecision:
    """Normalized moderation result."""

    action: str
    categories: list[str]
    confidence: float
    explanation: str


class ModerationService:
    """Combines deterministic filters, reputation and optional LLM moderation."""

    def __init__(self, ai: AIClient | None = None) -> None:
        self.ai = ai or AIClient()

    async def classify(self, message: str, user_reputation: int = 0) -> ModerationDecision:
        """Classify a message and recommend an action."""
        if len(message) > 2000:
            return ModerationDecision("delete", ["flood"], 0.95, "Message is too long")
        if self._looks_like_spam(message) and user_reputation < 10:
            return ModerationDecision("delete", ["spam"], 0.9, "Low-reputation link or spam pattern")
        result = await self.ai.generate_json(MODERATION_PROMPT.format(message=message[:1500]))
        return ModerationDecision(
            action=str(result.get("action", "allow")),
            categories=list(result.get("categories", [])),
            confidence=float(result.get("confidence", 0.5)),
            explanation=str(result.get("explanation", "AI moderation")),
        )

    @staticmethod
    def _looks_like_spam(message: str) -> bool:
        links = len(re.findall(r"https?://", message, flags=re.IGNORECASE))
        return links >= 2 or any(pattern.search(message) for pattern in SPAM_PATTERNS)
