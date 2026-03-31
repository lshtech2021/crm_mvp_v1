from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler  # type: ignore[import-untyped]
from slowapi.errors import RateLimitExceeded  # type: ignore[import-untyped]
from sqlalchemy import text

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.middleware import TenantContextMiddleware
from app.modules.auth.router import limiter as auth_limiter
from app.modules.auth.router import router as auth_router
from app.modules.audit.router import router as audit_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("CRM backend starting up")
    yield
    logger.info("CRM backend shutting down")


app = FastAPI(
    title="CRM MVP",
    version="0.1.0",
    lifespan=lifespan,
)

# --- Rate limiter state ---
app.state.limiter = auth_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# --- Middleware (order matters: last added = first executed) ---
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantContextMiddleware)  # type: ignore[arg-type]


# --- Exception handlers ---
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# --- Routers ---
app.include_router(auth_router)
app.include_router(audit_router)


# --- Health endpoints ---
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def readiness() -> dict[str, str]:
    from app.db.session import engine

    errors: list[str] = []

    # Check DB
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        errors.append("database")

    # Check Redis
    try:
        import redis.asyncio as aioredis  # type: ignore[import-untyped]

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
    except Exception:
        errors.append("redis")

    if errors:
        return {"status": "degraded", "failing": ", ".join(errors)}
    return {"status": "ok"}
