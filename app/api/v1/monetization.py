"""Monetization campaign endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_session
from app.models.growth import CampaignStatus, MonetizationCampaign
from app.services.monetization import MonetizationService

SessionDep = Annotated[AsyncSession, Depends(get_session)]
router = APIRouter(prefix="/monetization", tags=["monetization"], dependencies=[Depends(require_admin)])


class CampaignCreate(BaseModel):
    """Create monetization campaign request."""

    name: str = Field(min_length=2, max_length=240)
    status: CampaignStatus = CampaignStatus.DRAFT
    disclosure: str = "Реклама / партнёрский материал"
    landing_url: str | None = None
    budget_cents: int = Field(default=0, ge=0)
    target_topics: list[str] = Field(default_factory=list)
    creative_brief: str = ""
    starts_at: datetime | None = None
    ends_at: datetime | None = None


@router.post("/campaigns", response_model=dict)
async def create_campaign(payload: CampaignCreate, session: SessionDep) -> dict[str, str]:
    """Create a sponsorship/affiliate/subscription campaign."""
    campaign = MonetizationCampaign(**payload.model_dump())
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    return {"id": str(campaign.id), "name": campaign.name, "status": campaign.status.value}


@router.post("/campaigns/{campaign_id}/generate-ad", response_model=dict)
async def generate_ad(campaign_id: UUID, session: SessionDep) -> dict[str, str]:
    """Generate a disclosed sponsored content draft."""
    item = await MonetizationService(session).generate_sponsored_post(campaign_id)
    return {"content_id": str(item.id), "status": item.status.value}
