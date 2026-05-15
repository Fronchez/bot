"""Referral and gamification services."""

import secrets
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.growth import ActivityScore, ReferralEvent, ReferralLink, ReferralStatus
from app.models.user import TelegramUser
from app.services.safety import AutomationSafetyGuard


class ReferralService:
    """Tracks compliant referrals, points and leaderboard state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.guard = AutomationSafetyGuard()

    async def create_link(self, owner_user_id: UUID | None, telegram_invite_link: str | None = None) -> ReferralLink:
        """Create a referral code. Telegram invite creation remains explicit/admin-controlled."""
        decision = self.guard.validate_growth_action("referral_link", {"requires_user_consent": True})
        if not decision.allowed:
            raise ValueError(decision.reason)
        link = ReferralLink(
            owner_user_id=owner_user_id,
            code=secrets.token_urlsafe(8),
            telegram_invite_link=telegram_invite_link,
        )
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def record_join(
        self,
        referral_link_id: UUID,
        referred_user_id: UUID | None,
        metadata: dict | None = None,
    ) -> ReferralEvent:
        """Record and validate a referral join event with simple anti-fraud checks."""
        status = ReferralStatus.VERIFIED if referred_user_id else ReferralStatus.PENDING
        event = ReferralEvent(
            referral_link_id=referral_link_id,
            referred_user_id=referred_user_id,
            status=status,
            reason="verified_join" if referred_user_id else "awaiting_user_match",
            metadata_json=metadata or {},
        )
        link = await self.session.get(ReferralLink, referral_link_id)
        if link and status == ReferralStatus.VERIFIED:
            link.verified_joins += 1
            if link.owner_user_id:
                self.session.add(ActivityScore(user_id=link.owner_user_id, points=10, reason="verified_referral"))
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def leaderboard(self, limit: int = 10) -> list[dict[str, str | int]]:
        """Return the activity leaderboard."""
        rows = await self.session.execute(
            select(TelegramUser.telegram_id, TelegramUser.username, func.coalesce(func.sum(ActivityScore.points), 0))
            .join(ActivityScore, ActivityScore.user_id == TelegramUser.id)
            .group_by(TelegramUser.telegram_id, TelegramUser.username)
            .order_by(desc(func.coalesce(func.sum(ActivityScore.points), 0)))
            .limit(limit)
        )
        return [
            {"telegram_id": row[0], "username": row[1] or "", "points": int(row[2])}
            for row in rows.all()
        ]
