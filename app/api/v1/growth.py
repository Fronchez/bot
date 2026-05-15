"""Growth endpoints."""

from fastapi import APIRouter, Depends

from app.api.deps import require_admin
from app.services.growth import GrowthEngine, GrowthExperiment

router = APIRouter(prefix="/growth", tags=["growth"], dependencies=[Depends(require_admin)])


@router.get("/experiments")
async def experiments() -> list[GrowthExperiment]:
    """List safe growth experiments."""
    return GrowthEngine().propose_experiments()
