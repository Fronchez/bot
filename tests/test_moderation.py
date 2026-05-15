"""Moderation tests."""

import asyncio

from app.services.moderation import ModerationService


def test_spam_link_deleted_for_low_reputation() -> None:
    decision = asyncio.run(ModerationService().classify("free crypto http://a.test http://b.test", 0))
    assert decision.action == "delete"
    assert "spam" in decision.categories
