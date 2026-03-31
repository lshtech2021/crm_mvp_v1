"""Seed script for the CRM database.

Usage:
    python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.modules.auth.models import Tenant, User

_TENANTS = [
    {"name": "Acme Corp", "slug": "acme"},
    {"name": "Globex Inc", "slug": "globex"},
]
_ROLES = ["admin", "manager", "rep", "viewer"]


async def _get_or_create_tenant(
    session: AsyncSession,
    name: str,
    slug: str,
) -> Tenant:
    result = await session.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()
    if tenant is not None:
        print(f"  Tenant '{slug}' already exists — skipping")
        return tenant

    tenant = Tenant(id=uuid.uuid4(), name=name, slug=slug, status="active")
    session.add(tenant)
    await session.flush()
    print(f"  Created tenant '{slug}'")
    return tenant


async def _get_or_create_user(
    session: AsyncSession,
    *,
    email: str,
    password_hash: str,
    first_name: str,
    last_name: str,
    role: str,
    tenant_id: uuid.UUID,
) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        print(f"  User '{email}' already exists — skipping")
        return user

    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        role=role,
        tenant_id=tenant_id,
        status="active",
    )
    session.add(user)
    await session.flush()
    print(f"  Created user '{email}' (role={role})")
    return user


async def seed() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    pw_hash = hash_password("password123")

    print("Seeding database…")
    async with factory() as session:
        for td in _TENANTS:
            tenant = await _get_or_create_tenant(session, td["name"], td["slug"])
            for role in _ROLES:
                email = f"{role}@{td['slug']}.com"
                await _get_or_create_user(
                    session,
                    email=email,
                    password_hash=pw_hash,
                    first_name=role.title(),
                    last_name=td["name"].split()[0],
                    role=role,
                    tenant_id=tenant.id,
                )
        await session.commit()

    await engine.dispose()
    print("\nSeed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
