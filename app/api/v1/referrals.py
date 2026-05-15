"""Referral and gamification endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_session
from app.services.referrals import ReferralService

SessionDep = Annotated[AsyncSession, Depends(get_session)]
router = APIRouter(prefix="/referrals", tags=["referrals"], dependencies=[Depends(require_admin)])


class ReferralLinkCreate(BaseModel):
    """Create referral link request."""

    owner_user_id: UUID | None = None
    telegram_invite_link: str | None = None


@router.post("/links", response_model=dict)
async def create_link(payload: ReferralLinkCreate, session: SessionDep) -> dict[str, str | None]:
    """Create a tracked referral link."""
    link = await ReferralService(session).create_link(payload.owner_user_id, payload.telegram_invite_link)
    return {"id": str(link.id), "code": link.code, "telegram_invite_link": link.telegram_invite_link}


@router.post("/links/{link_id}/joins", response_model=dict)
async def record_join(link_id: UUID, session: SessionDep) -> dict[str, str]:
    """Record a pending referral join."""
    event = await ReferralService(session).record_join(link_id, None)
    return {"id": str(event.id), "status": event.status.value}


@router.get("/leaderboard", response_model=list[dict])
async def leaderboard(session: SessionDep) -> list[dict[str, str | int]]:
    """Return gamification leaderboard."""
    return await ReferralService(session).leaderboard()
