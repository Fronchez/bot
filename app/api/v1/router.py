"""API router composition."""

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.content import router as content_router
from app.api.v1.growth import router as growth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(content_router)
api_router.include_router(analytics_router)
api_router.include_router(growth_router)
