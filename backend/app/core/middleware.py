from __future__ import annotations

import logging
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.security import decode_token

logger = logging.getLogger(__name__)

_PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/api/auth/login",
        "/api/auth/refresh",
        "/health",
        "/ready",
        "/docs",
        "/openapi.json",
    }
)


class TenantContextMiddleware:
    """Pure ASGI middleware that extracts tenant/user context from JWT."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        path = request.url.path

        if path in _PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            await self.app(scope, receive, send)
            return

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = JSONResponse(
                status_code=401, content={"detail": "Missing or invalid authorization header"}
            )
            await response(scope, receive, send)
            return

        token = auth_header.removeprefix("Bearer ")
        try:
            payload: dict[str, Any] = decode_token(token)
        except Exception:
            response = JSONResponse(
                status_code=401, content={"detail": "Invalid or expired token"}
            )
            await response(scope, receive, send)
            return

        scope.setdefault("state", {})
        scope["state"]["tenant_id"] = payload.get("tenant_id")
        scope["state"]["user_id"] = payload.get("sub")

        await self.app(scope, receive, send)
