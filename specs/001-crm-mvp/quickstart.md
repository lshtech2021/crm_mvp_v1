# Local development quickstart

Multi-tenant CRM MVP: FastAPI + SQLAlchemy 2 (async) + Alembic + Celery, PostgreSQL 16, Redis 7, Next.js 14 (App Router).

## Prerequisites

- Docker and Docker Compose v2
- Python 3.12+ (optional: run backend without Docker)
- Node.js 20+ and pnpm (optional: run frontend without Docker)

## Quick Start (Docker Compose)

```bash
git clone <repository-url>
cd crm
cp .env.example .env
docker compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- OpenAPI (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

## Manual Setup (without Docker)

Ensure PostgreSQL 16 and Redis 7 are running and reachable from your machine.

### Backend

1. Create a virtualenv and install deps from `pyproject.toml`.
2. Copy `.env.example` to `.env` and configure `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`.
3. Run migrations: `alembic upgrade head`
4. Start the API: `python -m app.main`
5. Start a worker: `celery -A app.workers.celery_app worker --loglevel=info`
6. Start the scheduler: `celery -A app.workers.celery_app beat --loglevel=info`

### Frontend

1. `pnpm install`
2. Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. `pnpm dev` — dev server at [http://localhost:3000](http://localhost:3000)

## Seed Data

```bash
python -m scripts.seed
```

Creates:

- 2 tenants: Acme Corp, Globex Inc
- 4 users per tenant (admin, manager, rep, viewer), password `password123`

## Running Tests

### Backend

```bash
pytest                           # all tests
pytest tests/unit/               # unit only
pytest tests/api/                # API integration
```

### Frontend

```bash
pnpm test                        # Vitest + RTL
pnpm test:e2e                    # Playwright (stack should be up)
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Async SQLAlchemy URL (e.g. `postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis connection URL |
| `JWT_SECRET_KEY` | Secret for signing JWTs |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL (default: `15`) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL (default: `7`) |
| `CELERY_BROKER_URL` | Celery broker (typically Redis) |
| `DASHBOARD_PRECOMPUTE_INTERVAL_SECONDS` | Dashboard precompute cadence (default: `300`) |
| `CORS_ORIGINS` | Allowed browser origins (comma-separated or as documented in app config) |

## Useful Commands

| Area | Command |
|------|---------|
| Backend lint | `ruff check . && ruff format --check .` |
| Backend types | `mypy app/` |
| Frontend lint | `pnpm lint` |
| Frontend types | `pnpm typecheck` |
