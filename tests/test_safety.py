"""Safety guardrail tests."""

from app.services.safety import AutomationSafetyGuard


def test_blocks_ban_evasion() -> None:
    decision = AutomationSafetyGuard().validate_growth_action("ban_evasion")
    assert decision.allowed is False


def test_allows_consent_based_referral() -> None:
    decision = AutomationSafetyGuard().validate_growth_action(
        "referral_link",
        {"requires_user_consent": True, "messages_per_minute": 0},
    )
    assert decision.allowed is True
