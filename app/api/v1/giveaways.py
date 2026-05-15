"""Giveaway admin endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_session
from app.models.giveaway import Giveaway
from app.services.giveaways import GiveawayService

SessionDep = Annotated[AsyncSession, Depends(get_session)]
router = APIRouter(prefix="/giveaways", tags=["giveaways"], dependencies=[Depends(require_admin)])


class GiveawayCreate(BaseModel):
    """Create giveaway request."""

    title: str = Field(min_length=3, max_length=240)
    prize: str = Field(min_length=1, max_length=240)
    conditions: str = Field(min_length=3, max_length=1000)
    starts_at: datetime
    ends_at: datetime


@router.post("", response_model=dict)
async def create_giveaway(payload: GiveawayCreate, session: SessionDep) -> dict[str, str]:
    """Create a giveaway."""
    giveaway = Giveaway(**payload.model_dump())
    session.add(giveaway)
    await session.commit()
    await session.refresh(giveaway)
    return {"id": str(giveaway.id), "title": giveaway.title}


@router.post("/{giveaway_id}/participants/{user_id}", response_model=dict)
async def enter_giveaway(giveaway_id: UUID, user_id: UUID, session: SessionDep) -> dict[str, str]:
    """Enter a participant into a giveaway."""
    participant = await GiveawayService(session).enter(giveaway_id, user_id)
    return {"id": str(participant.id), "giveaway_id": str(participant.giveaway_id)}


@router.post("/{giveaway_id}/pick-winner", response_model=dict)
async def pick_winner(giveaway_id: UUID, session: SessionDep) -> dict[str, str]:
    """Pick and persist a giveaway winner."""
    giveaway = await GiveawayService(session).pick_winner(giveaway_id)
    return {"giveaway_id": str(giveaway.id), "winner_user_id": str(giveaway.winner_user_id)}
