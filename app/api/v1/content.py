"""Content admin endpoints."""

import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_session
from app.models.content import ContentItem, ContentStatus
from app.repositories.content import ContentRepository
from app.schemas.content import ContentCreate, ContentRead
from app.services.content_engine import ContentEngine

SessionDep = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter(prefix="/content", tags=["content"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[ContentRead])
async def list_content(session: SessionDep) -> list[ContentItem]:
    """List recent content queue items."""
    return await ContentRepository(session).list_recent()


@router.post("", response_model=ContentRead)
async def create_content(
    payload: ContentCreate, session: SessionDep
) -> ContentItem:
    """Create content manually."""
    body_hash = hashlib.sha256(f"{payload.title}\n{payload.body_markdown}".encode()).hexdigest()
    item = ContentItem(
        **payload.model_dump(),
        dedupe_hash=body_hash,
        status=ContentStatus.SCHEDULED if payload.scheduled_at else ContentStatus.DRAFT,
    )
    return await ContentRepository(session).add(item)


@router.post("/generate", response_model=ContentRead)
async def generate_content(session: SessionDep) -> ContentItem:
    """Generate a post from the autonomous AI content engine."""
    return await ContentEngine(session).generate_next_post()


@router.post("/{item_id}/approve", response_model=ContentRead)
async def approve_content(item_id: UUID, session: SessionDep) -> ContentItem:
    """Approve a draft for scheduling."""
    item = await ContentRepository(session).get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Content not found")
    item.status = ContentStatus.SCHEDULED
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
