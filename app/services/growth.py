"""Compliant growth mechanics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GrowthExperiment:
    """A safe growth experiment proposal."""

    name: str
    hypothesis: str
    mechanic: str
    metric: str


class GrowthEngine:
    """Selects growth experiments that avoid spam and platform abuse."""

    def propose_experiments(self) -> list[GrowthExperiment]:
        """Return ready-to-run ethical growth mechanics."""
        return [
            GrowthExperiment(
                name="Referral quest",
                hypothesis="A visible leaderboard increases organic invites.",
                mechanic="Award points for verified invite links and useful comments.",
                metric="invites_per_active_user",
            ),
            GrowthExperiment(
                name="AI prompt battle",
                hypothesis="User-generated AI prompts increase comments and saves.",
                mechanic="Weekly contest; members submit prompts; community votes via poll.",
                metric="comments_per_post",
            ),
            GrowthExperiment(
                name="Partner digest",
                hypothesis="Cross-promotion with aligned admins increases qualified reach.",
                mechanic="Admin-approved partner mentions in useful digest posts.",
                metric="subscriber_growth_rate",
            ),
        ]
