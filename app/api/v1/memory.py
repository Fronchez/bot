"""AI memory admin endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_session
from app.models.memory import MemoryItem, MemoryKind
from app.services.memory import MemoryService

SessionDep = Annotated[AsyncSession, Depends(get_session)]
router = APIRouter(prefix="/memory", tags=["memory"], dependencies=[Depends(require_admin)])


class MemoryWrite(BaseModel):
    """Memory write request."""

    kind: MemoryKind
    key: str = Field(min_length=1, max_length=240)
    text: str = Field(min_length=1)
    score_delta: float = 1.0
    metadata: dict = Field(default_factory=dict)


class MemorySearch(BaseModel):
    """Memory retrieval request."""

    query: str = Field(min_length=1)
    kinds: list[MemoryKind] | None = None
    limit: int = Field(default=5, ge=1, le=25)


@router.post("", response_model=dict)
async def remember(payload: MemoryWrite, session: SessionDep) -> dict[str, str]:
    """Store or update memory."""
    item = await MemoryService(session).remember(
        payload.kind,
        payload.key,
        payload.text,
        payload.score_delta,
        payload.metadata,
    )
    return {"id": str(item.id), "kind": item.kind.value, "key": item.key}


@router.post("/search", response_model=list[dict])
async def search(payload: MemorySearch, session: SessionDep) -> list[dict]:
    """Search semantic memory."""
    items: list[MemoryItem] = await MemoryService(session).retrieve(payload.query, payload.kinds, payload.limit)
    return [
        {"id": str(item.id), "kind": item.kind.value, "key": item.key, "text": item.text, "score": item.score}
        for item in items
    ]
