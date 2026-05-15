"""Policy guardrails for compliant automation."""

from dataclasses import dataclass

PROHIBITED_AUTOMATIONS = {
    "mass_unsolicited_dm",
    "fake_engagement",
    "ban_evasion",
    "credential_harvesting",
    "private_scraping",
    "spam_invites",
}


@dataclass(frozen=True)
class SafetyDecision:
    """Decision returned by the automation safety guard."""

    allowed: bool
    reason: str


class AutomationSafetyGuard:
    """Blocks automations that would violate Telegram policies or community trust."""

    def validate_growth_action(self, action_type: str, metadata: dict | None = None) -> SafetyDecision:
        """Validate a growth automation before it is queued or executed."""
        metadata = metadata or {}
        if action_type in PROHIBITED_AUTOMATIONS:
            return SafetyDecision(False, f"Blocked prohibited automation: {action_type}")
        if metadata.get("requires_user_consent") is False:
            return SafetyDecision(False, "Blocked action without explicit user/admin consent")
        if metadata.get("messages_per_minute", 0) > 20:
            return SafetyDecision(False, "Blocked unsafe outbound message rate")
        return SafetyDecision(True, "Allowed compliant automation")
