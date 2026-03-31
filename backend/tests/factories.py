from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.auth.models import Tenant, User

_DEFAULT_PASSWORD_HASH = hash_password("password123")


async def create_tenant(
    session: AsyncSession,
    *,
    name: str | None = None,
    slug: str | None = None,
    status: str = "active",
) -> Tenant:
    _id = uuid.uuid4()
    tenant = Tenant(
        id=_id,
        name=name or f"Tenant-{_id.hex[:8]}",
        slug=slug or f"tenant-{_id.hex[:8]}",
        status=status,
    )
    session.add(tenant)
    await session.flush()
    return tenant


async def create_user(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    email: str | None = None,
    password: str = "password123",
    first_name: str = "Test",
    last_name: str = "User",
    role: str = "rep",
    status: str = "active",
) -> User:
    _id = uuid.uuid4()
    pw_hash = _DEFAULT_PASSWORD_HASH if password == "password123" else hash_password(password)
    user = User(
        id=_id,
        email=email or f"user-{_id.hex[:8]}@test.com",
        password_hash=pw_hash,
        first_name=first_name,
        last_name=last_name,
        role=role,
        tenant_id=tenant_id,
        status=status,
    )
    session.add(user)
    await session.flush()
    return user
