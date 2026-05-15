"""FastAPI dependencies."""

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Protect admin endpoints with a simple deploy-time token."""
    settings = get_settings()
    if x_admin_token != settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
