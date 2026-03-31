from __future__ import annotations

import asyncio
import os
import uuid

# ── Environment (must precede ANY app import) ──────────────────────────────
_TEST_DB = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://crm:crm@localhost:5432/crm_test",
)
os.environ["DATABASE_URL"] = _TEST_DB
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-do-not-use-in-prod")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_ALWAYS_EAGER", "true")

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.dependencies import get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.auth.models import Tenant, User  # noqa: E402
from app.modules.auth.service import create_access_token  # noqa: E402
from app.workers.celery_app import celery_app  # noqa: E402

# ── Celery eager mode ──────────────────────────────────────────────────────
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)

# ── Test engine / session factory ──────────────────────────────────────────
test_engine = create_async_engine(_TEST_DB, echo=False, pool_pre_ping=True)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── Seed configuration ────────────────────────────────────────────────────
_TENANTS = [
    {"name": "Acme Corp", "slug": "acme"},
    {"name": "Globex Inc", "slug": "globex"},
]
_ROLES = ["admin", "manager", "rep", "viewer"]
_PASSWORD_HASH = hash_password("password123")


async def _seed() -> None:
    """Insert two tenants with four users each."""
    async with TestSessionFactory() as session:
        for t in _TENANTS:
            existing = (
                await session.execute(select(Tenant).where(Tenant.slug == t["slug"]))
            ).scalar_one_or_none()
            if existing:
                continue

            tenant = Tenant(
                id=uuid.uuid4(),
                name=t["name"],
                slug=t["slug"],
                status="active",
            )
            session.add(tenant)
            await session.flush()

            for role in _ROLES:
                user = User(
                    id=uuid.uuid4(),
                    email=f"{role}@{t['slug']}.com",
                    password_hash=_PASSWORD_HASH,
                    first_name=role.title(),
                    last_name=t["name"].split()[0],
                    role=role,
                    tenant_id=tenant.id,
                    status="active",
                )
                session.add(user)

        await session.commit()


# ── Session-scoped DB lifecycle (sync wrapper around async) ────────────────
@pytest.fixture(scope="session", autouse=False)
def _setup_database():
    """Create all tables, seed data, yield, then drop everything."""

    async def _up() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        await _seed()
        # Dispose pool so test event loops get fresh connections
        await test_engine.dispose()

    async def _down() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()

    asyncio.run(_up())
    yield
    asyncio.run(_down())


# ── Function-scoped fixtures ──────────────────────────────────────────────
@pytest_asyncio.fixture
async def db_session(_setup_database: None) -> AsyncSession:
    """Yield a fresh async session for direct DB access in tests."""
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(_setup_database: None) -> AsyncClient:
    """HTTPX client wired to the FastAPI app with the test DB."""

    async def _override_get_db():  # noqa: ANN202
        async with TestSessionFactory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def users(_setup_database: None) -> dict[str, User]:
    """All seeded users keyed by email."""
    async with TestSessionFactory() as session:
        result = await session.execute(select(User))
        return {u.email: u for u in result.scalars().all()}


@pytest_asyncio.fixture
async def tenants(_setup_database: None) -> dict[str, Tenant]:
    """All seeded tenants keyed by slug."""
    async with TestSessionFactory() as session:
        result = await session.execute(select(Tenant))
        return {t.slug: t for t in result.scalars().all()}


@pytest.fixture
def auth_headers() -> object:
    """Return a callable: auth_headers(user) → {"Authorization": "Bearer <jwt>"}."""

    def _make(user: User) -> dict[str, str]:
        token = create_access_token(user)
        return {"Authorization": f"Bearer {token}"}

    return _make
