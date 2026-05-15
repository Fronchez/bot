"""Analytics endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_session
from app.services.analytics import AnalyticsService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(require_admin)])


@router.get("/summary")
async def summary(session: SessionDep) -> dict[str, float]:
    """Return engagement summary."""
    return await AnalyticsService(session).engagement_summary()
