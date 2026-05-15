"""Moderation tests."""

import pytest

from app.services.moderation import ModerationService


@pytest.mark.asyncio
async def test_spam_link_deleted_for_low_reputation() -> None:
    decision = await ModerationService().classify("free crypto http://a.test http://b.test", 0)
    assert decision.action == "delete"
    assert "spam" in decision.categories
