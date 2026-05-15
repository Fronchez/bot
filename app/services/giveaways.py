"""Giveaway orchestration service."""

from datetime import UTC, datetime
from random import SystemRandom
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.giveaway import Giveaway, GiveawayParticipant
from app.models.growth import ActivityScore


class GiveawayService:
    """Creates giveaways, validates entries and selects winners fairly."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.random = SystemRandom()

    async def enter(self, giveaway_id: UUID, user_id: UUID, referral_count: int = 0) -> GiveawayParticipant:
        """Enter a user into a giveaway and award participation points."""
        participant = GiveawayParticipant(
            giveaway_id=giveaway_id,
            user_id=user_id,
            referral_count=max(referral_count, 0),
        )
        self.session.add(participant)
        self.session.add(ActivityScore(user_id=user_id, points=3, reason="giveaway_entry"))
        await self.session.commit()
        await self.session.refresh(participant)
        return participant

    async def pick_winner(self, giveaway_id: UUID) -> Giveaway:
        """Pick a weighted random winner after the giveaway end time."""
        giveaway = await self.session.get(Giveaway, giveaway_id)
        if giveaway is None:
            raise ValueError("Giveaway not found")
        if giveaway.ends_at > datetime.now(UTC):
            raise ValueError("Giveaway has not ended yet")
        participants = list(
            await self.session.scalars(
                select(GiveawayParticipant).where(GiveawayParticipant.giveaway_id == giveaway_id)
            )
        )
        if not participants:
            raise ValueError("Giveaway has no participants")
        weighted: list[GiveawayParticipant] = []
        for participant in participants:
            weighted.extend([participant] * (1 + min(participant.referral_count, 10)))
        winner = self.random.choice(weighted)
        giveaway.winner_user_id = winner.user_id
        self.session.add(giveaway)
        self.session.add(ActivityScore(user_id=winner.user_id, points=50, reason="giveaway_winner"))
        await self.session.commit()
        await self.session.refresh(giveaway)
        return giveaway

    async def active(self) -> list[Giveaway]:
        """List currently active giveaways."""
        now = datetime.now(UTC)
        return list(
            await self.session.scalars(
                select(Giveaway).where(Giveaway.starts_at <= now, Giveaway.ends_at >= now)
            )
        )
