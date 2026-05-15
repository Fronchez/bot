"""API router composition."""

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.content import router as content_router
from app.api.v1.giveaways import router as giveaways_router
from app.api.v1.growth import router as growth_router
from app.api.v1.memory import router as memory_router
from app.api.v1.monetization import router as monetization_router
from app.api.v1.referrals import router as referrals_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(content_router)
api_router.include_router(analytics_router)
api_router.include_router(growth_router)
api_router.include_router(memory_router)
api_router.include_router(giveaways_router)
api_router.include_router(referrals_router)
api_router.include_router(monetization_router)
