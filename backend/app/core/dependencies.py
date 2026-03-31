from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ForbiddenError
from app.db.session import async_session_factory
from app.modules.auth.models import User


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    tenant_id: str | None = getattr(request.state, "tenant_id", None)
    execution_options: dict[str, Any] = {}
    if tenant_id is not None:
        execution_options["tenant_id"] = tenant_id

    async with async_session_factory() as session:
        if execution_options:
            session = session.execution_options(**execution_options)  # type: ignore[assignment]
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id: str | None = getattr(request.state, "user_id", None)
    if user_id is None:
        raise AppError(status_code=401, detail="Not authenticated")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise AppError(status_code=401, detail="User not found")
    return user


def require_role(*roles: str) -> Callable[..., Any]:
    async def _dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(detail="Insufficient permissions")
        return current_user

    return _dependency
