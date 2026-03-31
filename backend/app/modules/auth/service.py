from __future__ import annotations

import logging
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import create_token, decode_token, verify_password
from app.modules.auth.models import User

logger = logging.getLogger(__name__)


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        _emit_audit_safe(
            tenant_id=None,
            actor_id=None,
            actor_role=None,
            action_type="login_failure",
            entity_type="user",
            entity_id=None,
        )
        raise AppError(status_code=401, detail="Invalid email or password")

    _emit_audit_safe(
        tenant_id=str(user.tenant_id),
        actor_id=str(user.id),
        actor_role=user.role,
        action_type="login_success",
        entity_type="user",
        entity_id=str(user.id),
    )
    return user


def create_access_token(user: User) -> str:
    settings = get_settings()
    return create_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role,
        },
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user: User) -> str:
    settings = get_settings()
    return create_token(
        data={
            "sub": str(user.id),
            "type": "refresh",
        },
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


async def rotate_refresh(db: AsyncSession, refresh_token: str) -> tuple[str, str]:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise AppError(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise AppError(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AppError(status_code=401, detail="User not found")

    new_access = create_access_token(user)
    new_refresh = create_refresh_token(user)

    _emit_audit_safe(
        tenant_id=str(user.tenant_id),
        actor_id=str(user.id),
        actor_role=user.role,
        action_type="token_refresh",
        entity_type="user",
        entity_id=str(user.id),
    )

    return new_access, new_refresh


def _emit_audit_safe(
    *,
    tenant_id: str | None,
    actor_id: str | None,
    actor_role: str | None,
    action_type: str,
    entity_type: str,
    entity_id: str | None,
    changes: dict[str, object] | None = None,
    ip_address: str | None = None,
) -> None:
    """Fire-and-forget audit event; never break the auth flow."""
    try:
        from app.modules.audit.service import emit_audit_event

        emit_audit_event(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
        )
    except Exception:
        logger.warning("Failed to emit audit event for %s", action_type, exc_info=True)
