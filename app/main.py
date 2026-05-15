"""FastAPI application entrypoint."""

from fastapi import FastAPI
from prometheus_client import make_asgi_app
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])
app = FastAPI(title=settings.app_name, version="0.1.0")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(api_router)
app.mount("/metrics", make_asgi_app())


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request, exc: RateLimitExceeded) -> JSONResponse:  # type: ignore[no-untyped-def]
    """Return a JSON response for rate limit errors."""
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok", "environment": settings.environment}
