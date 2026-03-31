# Implementation Plan: CRM MVP

**Branch**: `001-crm-mvp` | **Date**: 2026-03-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-crm-mvp/spec.md`

## Summary

Build a production-grade multi-tenant CRM MVP with a decoupled
architecture: a Python/FastAPI backend with PostgreSQL + Redis, a
Next.js/React/TypeScript frontend with Tailwind CSS, and Celery for
two justified async workflows (audit log dispatch and dashboard metric
precomputation). The system manages contacts, companies, deals (pipeline),
tasks, and a reporting dashboard — all scoped by tenant with role-based
authorization enforced on every protected API operation. Implementation
proceeds incrementally: platform foundation → contacts & companies →
deals & pipeline → tasks & reporting → hardening.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI 0.110+, SQLAlchemy 2.x (async),
Pydantic v2, Alembic, Celery 5.x, Next.js 14 (App Router), React 18,
Tailwind CSS 3.x
**Storage**: PostgreSQL 16 (primary), Redis 7 (cache + Celery broker)
**Testing**: pytest + httpx (backend), Vitest + React Testing Library
(frontend), Playwright (E2E)
**Target Platform**: Linux server (Docker), modern desktop browsers
**Project Type**: Web application (decoupled backend API + frontend SPA)
**Performance Goals**: API p95 < 500ms for list endpoints at 10k
records/tenant (SC-003); pipeline board TTI < 2s at 200 deals (SC-004);
dashboard refresh < 500ms p95 (SC-007)
**Constraints**: Shared-schema multi-tenancy (row-level `tenant_id`);
offset-based pagination; DB-level search (ILIKE); manual-refresh UI
**Scale/Scope**: Up to 10k records per tenant per entity; 4 roles;
7 entity types; 18+ API endpoint groups; ~15 frontend pages/views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Align with `.specify/memory/constitution.md` (CRM MVP v2.1.0). Verify:

- **Code Quality & Maintainable Architecture**: ✅ PASS
  - Backend: Ruff for linting + formatting; CI rejects violations.
  - Frontend: ESLint + Prettier; CI rejects violations.
  - Modular layer separation: `router → service → models/db` (backend);
    `pages → features → lib/api` (frontend). Dependency direction
    enforced by import structure.
  - Async justification: Two background workflows documented with
    concrete product need (FR-017 audit dispatch, FR-018 dashboard
    precompute). All other operations synchronous.
  - No unjustified abstractions. Complexity Tracking empty.

- **Testing Rigor**: ✅ PASS
  - Backend: pytest unit tests for services/domain logic; httpx API
    integration tests for every endpoint; tenant isolation + RBAC matrix
    coverage (SC-005, SC-006).
  - Frontend: Vitest + RTL for component behavior; integration tests
    for feature flows.
  - E2E: Playwright covering 6 critical user journeys (one per user
    story). Covers happy path + key error paths.
  - Audit log integration tests (SC-010).

- **Multi-Tenant Isolation**: ✅ PASS
  - `tenant_id` on every business table (TI-001).
  - FastAPI middleware resolves tenant from JWT, injects into
    SQLAlchemy session via `execution_options` — all queries auto-
    filtered (TI-002).
  - No client-supplied tenant IDs accepted (TI-003).
  - Automated cross-tenant tests attempt access with Tenant B
    credentials against Tenant A records (SC-005, TI-004).
  - Celery tasks receive `tenant_id` as required parameter;
    rejected without it (TI-005).

- **Security & Role-Based Authorization**: ✅ PASS
  - RBAC enforced via FastAPI dependency that checks `current_user.role`
    against operation + ownership rules (SEC-001, SEC-008).
  - Server-side enforcement; UI hides controls for UX but does not
    rely on client-side checks (SEC-002).
  - Pydantic v2 schemas validate all inputs at API boundary (SEC-003).
  - SQLAlchemy parameterized queries exclusively (SEC-004).
  - bcrypt password hashing (SEC-005).
  - JWT access (15 min) + refresh rotation (SEC-006).
  - Rate limiting on auth endpoints via `slowapi` (SEC-007).

- **Accessibility & Predictable UX**: ✅ PASS
  - Shared component library: Button, Input, Select, Modal,
    DataTable, Pagination, EmptyState, LoadingSpinner, ErrorBanner,
    Toast, ConfirmDialog.
  - All components use semantic HTML; ARIA attributes where needed.
  - WCAG 2.1 AA: keyboard navigation, focus management, color
    contrast, no color-only indicators.
  - axe-core integrated into Playwright E2E runs (SC-009).
  - Consistent patterns for empty/loading/error across all views
    (FR-011, SC-008).

- **Auditability**: ✅ PASS
  - Audit service produces records for all actions in AUD-001.
  - Schema: actor_id, actor_role, tenant_id, timestamp, action_type,
    entity_type, entity_id, changes (JSON), ip_address (AUD-002).
  - Dispatched async via Celery (FR-017); graceful degradation if
    queue unavailable.
  - Append-only AuditLog table; no delete/update endpoints (AUD-003).
  - Queryable by tenant, actor, entity, action, time range (AUD-004).
  - No secrets in audit payloads (AUD-005).

- **Spec-Driven Development & Incremental Delivery**: ✅ PASS
  - Spec exists at `specs/001-crm-mvp/spec.md` with 6 user stories,
    18 FRs, 10 SCs, all testable.
  - Work decomposes into 5 phases, each independently testable.
  - CI gates: lint, format, type check (mypy + tsc), pytest,
    vitest, playwright, dependency audit.
  - Task list traces to spec FRs and user stories.
  - Frontend-backend alignment enforced: typed API client generated
    from Pydantic schemas; contract tests verify sync.

- **AI-Assisted Implementation Discipline**: ✅ PASS
  - Tasks are bounded to specific files and spec requirements.
  - Architectural patterns documented in this plan; AI must follow.
  - No requirement invention; gaps raised as clarifications.
  - Same CI gates apply to AI-authored code.

## Project Structure

### Documentation (this feature)

```text
specs/001-crm-mvp/
├── plan.md              # This file
├── data-model.md        # Entity definitions, relationships, indexes
├── quickstart.md        # Local development setup guide
├── contracts/
│   ├── auth.md          # Auth API endpoints
│   ├── contacts.md      # Contact API endpoints
│   ├── companies.md     # Company API endpoints
│   ├── deals.md         # Deal API endpoints
│   ├── tasks.md         # Task API endpoints
│   ├── reporting.md     # Reporting API endpoints
│   └── audit.md         # Audit API endpoints
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── alembic/
│   ├── versions/               # Migration files
│   └── env.py
├── app/
│   ├── core/
│   │   ├── config.py           # pydantic-settings: DB, Redis, JWT, etc.
│   │   ├── security.py         # JWT encode/decode, password hashing
│   │   ├── dependencies.py     # get_db, get_current_user, require_role()
│   │   ├── middleware.py        # TenantContextMiddleware
│   │   ├── permissions.py      # RBAC policy: role × operation × ownership
│   │   └── exceptions.py       # App-level exception hierarchy
│   ├── db/
│   │   ├── base.py             # DeclarativeBase, metadata
│   │   ├── session.py          # async engine, session factory
│   │   └── mixins.py           # TenantMixin, TimestampMixin, SoftDeleteMixin
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── router.py       # POST /auth/login, /auth/refresh, /auth/logout
│   │   │   ├── schemas.py      # LoginRequest, TokenResponse, UserResponse
│   │   │   ├── service.py      # authenticate, create_tokens, rotate_refresh
│   │   │   └── models.py       # User, Tenant
│   │   ├── contacts/
│   │   │   ├── router.py       # CRUD + search/filter/archive
│   │   │   ├── schemas.py      # ContactCreate, ContactUpdate, ContactResponse
│   │   │   ├── service.py      # Business logic, ownership checks
│   │   │   └── models.py       # Contact
│   │   ├── companies/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── models.py       # Company
│   │   ├── deals/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py      # Stage transitions, optimistic concurrency
│   │   │   └── models.py       # Deal
│   │   ├── tasks/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── models.py       # Task
│   │   ├── reporting/
│   │   │   ├── router.py       # GET /reporting/dashboard
│   │   │   ├── schemas.py      # DashboardResponse
│   │   │   ├── service.py      # Read precomputed snapshot
│   │   │   └── models.py       # DashboardSnapshot
│   │   └── audit/
│   │       ├── router.py       # GET /audit (admin-only query)
│   │       ├── schemas.py
│   │       ├── service.py      # emit_audit_event (dispatches to Celery)
│   │       ├── models.py       # AuditLog
│   │       └── tasks.py        # Celery: write_audit_record
│   ├── workers/
│   │   ├── celery_app.py       # Celery config (Redis broker/backend)
│   │   └── scheduled.py        # Celery Beat: precompute_dashboard_metrics
│   └── main.py                 # FastAPI app, router registration, startup
├── tests/
│   ├── conftest.py             # Fixtures: test DB, test client, test users
│   ├── factories.py            # Factory Boy factories for entities
│   ├── unit/                   # Service logic, permissions, validators
│   ├── integration/            # DB-dependent service tests
│   └── api/                    # httpx AsyncClient API tests
├── pyproject.toml
├── Dockerfile
└── .env.example

frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout: AuthProvider, AppShell
│   │   ├── page.tsx            # Redirect to /dashboard or /login
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── contacts/
│   │   │   ├── page.tsx        # Contact list
│   │   │   ├── new/page.tsx    # Create contact
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Contact detail + edit
│   │   ├── companies/
│   │   │   ├── page.tsx
│   │   │   ├── new/page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── deals/
│   │   │   ├── page.tsx        # Pipeline board view
│   │   │   ├── new/page.tsx
│   │   │   └── [id]/page.tsx
│   │   └── tasks/
│   │       ├── page.tsx
│   │       ├── new/page.tsx
│   │       └── [id]/page.tsx
│   ├── components/
│   │   ├── ui/                 # Button, Input, Select, Modal, Badge, Card
│   │   ├── layout/             # AppShell, Sidebar, TopNav, PageHeader
│   │   ├── data/               # DataTable, Pagination, SearchInput, FilterBar
│   │   └── feedback/           # EmptyState, LoadingSpinner, ErrorBanner,
│   │                           # Toast, ConfirmDialog
│   ├── features/
│   │   ├── auth/               # LoginForm, AuthProvider, useAuth
│   │   ├── contacts/           # ContactForm, ContactList, ContactDetail
│   │   ├── companies/          # CompanyForm, CompanyList, CompanyDetail
│   │   ├── deals/              # DealForm, DealDetail, PipelineBoard,
│   │   │                       # PipelineColumn, DealCard, CloseDialog
│   │   ├── tasks/              # TaskForm, TaskList, TaskDetail
│   │   └── dashboard/          # MetricCard, PipelineSummary, OverdueBadge
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts       # Base fetch: auth headers, error handling
│   │   │   ├── auth.ts
│   │   │   ├── contacts.ts
│   │   │   ├── companies.ts
│   │   │   ├── deals.ts
│   │   │   ├── tasks.ts
│   │   │   ├── reporting.ts
│   │   │   └── types.ts        # Shared API types (PaginatedResponse, etc.)
│   │   ├── auth/
│   │   │   ├── context.tsx      # AuthContext, AuthProvider
│   │   │   └── tokens.ts       # Token storage, refresh logic
│   │   └── hooks/
│   │       ├── use-debounce.ts
│   │       ├── use-pagination.ts
│   │       └── use-confirm.ts
│   └── types/
│       └── index.ts            # Domain types (Contact, Company, Deal, etc.)
├── tests/
│   ├── components/             # Vitest + RTL
│   ├── integration/            # Feature-level tests
│   └── e2e/                    # Playwright
│       ├── auth.spec.ts
│       ├── contacts.spec.ts
│       ├── companies.spec.ts
│       ├── deals.spec.ts
│       ├── tasks.spec.ts
│       └── dashboard.spec.ts
├── playwright.config.ts
├── vitest.config.ts
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── Dockerfile
└── .env.example

docker-compose.yml              # PostgreSQL, Redis, backend, frontend, celery worker, celery beat
```

**Structure Decision**: Decoupled web application with separate `backend/`
and `frontend/` directories at repository root. Backend is a Python/FastAPI
modular monolith with domain modules. Frontend is a Next.js App Router
application. Docker Compose orchestrates all services for local development.

## Architecture Decisions

### Backend Layer Separation

Every domain module follows: `router.py → service.py → models.py`.

- **Router** (`router.py`): FastAPI route definitions. Handles HTTP
  concerns (path params, query params, status codes). Calls service
  methods. Depends on `get_current_user`, `get_db`, `require_role()`.
- **Service** (`service.py`): Business logic. Receives a DB session and
  tenant context. Performs validation, authorization (ownership checks),
  state transitions, and entity operations. Calls `audit.service.emit_audit_event`
  for auditable actions.
- **Models** (`models.py`): SQLAlchemy ORM models. Use `TenantMixin`,
  `TimestampMixin`, `SoftDeleteMixin` from `db/mixins.py`.
- **Schemas** (`schemas.py`): Pydantic v2 models for request validation
  and response serialization. Enforce field constraints (string lengths,
  email format, enums).

Services MUST NOT import from routers. Models MUST NOT import from
services. Routers are the only layer aware of HTTP.

### Tenant Isolation Strategy

1. `TenantContextMiddleware` extracts `tenant_id` from the decoded JWT
   on every request and stores it in request state.
2. `get_db` dependency creates an async SQLAlchemy session with
   `execution_options(tenant_id=...)`.
3. `TenantMixin` adds a class-level `__tenant_filter__` event listener
   that appends `WHERE tenant_id = :tid` to all queries on models that
   use the mixin.
4. On `INSERT`, `TenantMixin` auto-sets `tenant_id` from session options.
5. This makes tenant scoping automatic and invisible to service code,
   satisfying TI-002 ("application code MUST NOT manually attach tenant
   IDs").

### RBAC Enforcement

1. `require_role(*allowed_roles)` is a FastAPI dependency factory. It
   checks `current_user.role in allowed_roles` and raises 403 if not.
2. For write operations, routers call `permissions.check_ownership(user,
   entity)` which resolves ownership per SEC-008 (owner_id for deals,
   assignee_id for tasks, created_by for contacts/companies).
3. Admins and managers bypass ownership checks.

### Background Job Justification (Constitution Principle I)

Two async workflows are justified per FR-017 and FR-018:

| Workflow | Justification | Pattern |
|----------|--------------|---------|
| Audit log dispatch (FR-017) | Removes audit write latency (~5-10ms) from every mutating API call; graceful degradation if queue unavailable | Celery task `write_audit_record` dispatched via `apply_async` |
| Dashboard precompute (FR-018) | Aggregation queries across 5 tables would add 100-300ms to dashboard load at scale; precomputed snapshot serves in <50ms | Celery Beat scheduled task every 5 minutes |

All other operations are synchronous request-response.

### Frontend Patterns

- **Data fetching**: Server-side fetch on page load (Next.js App Router
  server components where possible, client-side fetch for interactive
  lists with search/filter/pagination).
- **State management**: React Context for auth state; component-local
  state for forms/lists; no global state library needed for MVP.
- **API client**: Typed wrapper around `fetch()` in `lib/api/client.ts`.
  Adds Authorization header, handles 401 (redirect to login), 403
  (show permission error), 409 (conflict/retry), 422 (validation
  errors), and network errors. Returns typed responses.
- **Component patterns**:
  - Lists: `DataTable` + `SearchInput` + `FilterBar` + `Pagination`
  - Detail views: Card layout with entity data, related entities tabs
  - Forms: Controlled Pydantic-aligned forms with inline validation
  - Pipeline board: Columns per stage with draggable `DealCard`
  - Dashboard: Grid of `MetricCard` widgets reading precomputed data

## Testing Strategy

### Backend Tests (pytest)

| Layer | Scope | Tools | Coverage Target |
|-------|-------|-------|-----------------|
| Unit | Service logic, validators, permissions, domain rules | pytest, unittest.mock | All business rules: stage transitions, ownership checks, archive constraints |
| Integration | DB operations via service layer | pytest, test PostgreSQL (Docker) | CRUD + search + filter + pagination for each entity |
| API | Full HTTP request/response cycle | httpx AsyncClient, test DB | Every endpoint × success + validation error + auth error + 404 |
| Cross-tenant | Tenant isolation verification | httpx, two test tenants | SC-005: Tenant A user cannot access Tenant B data on any endpoint |
| RBAC matrix | Permission enforcement | httpx, users per role | SC-006: Every operation × role combination tested |
| Audit | Audit record creation | pytest, Celery eager mode | SC-010: All AUD-001 actions produce correct AUD-002 records |

### Frontend Tests (Vitest + RTL)

| Layer | Scope | Tools | Coverage Target |
|-------|-------|-------|-----------------|
| Component | Shared UI components render correctly | Vitest, RTL | Button, Input, Modal, DataTable, EmptyState, ErrorBanner, Toast |
| Feature | Feature components with mocked API | Vitest, RTL, MSW | ContactForm validation, PipelineBoard stage grouping, TaskList filtering |
| Integration | Page-level flows with API mocking | Vitest, RTL, MSW | Login flow, contact CRUD flow, deal stage change |

### End-to-End Tests (Playwright)

| Test | User Story | Critical Path |
|------|-----------|--------------|
| `auth.spec.ts` | US1 | Login → dashboard → logout → protected redirect |
| `contacts.spec.ts` | US2 | Create → search → edit → archive → verify archived filter |
| `companies.spec.ts` | US3 | Create → associate contact → verify bidirectional link |
| `deals.spec.ts` | US4 | Create → move stages → close won → verify board |
| `tasks.spec.ts` | US5 | Create → assign → change status → verify overdue indicator |
| `dashboard.spec.ts` | US6 | Verify metrics match seeded data → refresh → empty state |

All Playwright tests include axe-core accessibility checks (SC-009).

### CI Quality Gates

```text
Pipeline: GitHub Actions

1. backend-lint:     ruff check + ruff format --check
2. backend-types:    mypy --strict
3. backend-tests:    pytest (unit + integration + API) with PostgreSQL service
4. frontend-lint:    eslint + prettier --check
5. frontend-types:   tsc --noEmit
6. frontend-tests:   vitest run
7. e2e-tests:        playwright (against docker-compose stack)
8. security-audit:   pip-audit (backend) + npm audit (frontend)

All gates MUST pass before merge. No gate bypasses without documented
justification per constitution Principle VII.
```

## Incremental Delivery Phases

### Phase Mapping (plan ↔ tasks.md)

| Plan Phase | tasks.md Phase(s) | User Story | Scope |
|------------|-------------------|------------|-------|
| Phase 0 | Phase 1 + Phase 2 | US1 | Setup + auth + tenant foundation |
| Phase 1 | Phase 3 + Phase 4 | US2 + US3 | Contacts + companies |
| Phase 2 | Phase 5 | US4 | Deals + pipeline |
| Phase 3 | Phase 6 + Phase 7 | US5 + US6 | Tasks + reporting dashboard |
| Phase 4 | Phase 8 | — | Hardening + deployment readiness |

### Phase 0: Platform Foundation

**Goal**: Authenticated users can log in, see an app shell with navigation,
and encounter proper empty states. Tenant isolation and RBAC infrastructure
are in place. CI pipeline is green.

**Delivers**: US1 (Authentication & Tenant-Scoped Foundation)

**Backend scope**:
- Project scaffold: `pyproject.toml`, FastAPI app, Docker setup
- PostgreSQL + Alembic: initial migration with `tenants` and `users` tables
- Redis connection setup
- `core/config.py`: pydantic-settings for all env vars
- `core/security.py`: JWT encode/decode, bcrypt hash/verify
- `core/middleware.py`: TenantContextMiddleware
- `core/dependencies.py`: `get_db`, `get_current_user`, `require_role()`
- `core/permissions.py`: RBAC policy engine
- `core/exceptions.py`: AppError hierarchy with HTTP status mapping
- `db/`: base, session, mixins (TenantMixin, TimestampMixin, SoftDeleteMixin)
- `modules/auth/`: login, refresh, logout, user-me endpoints
- `modules/audit/`: AuditLog model, service, Celery task
- Celery app + worker config (Redis broker)
- Seed script: create test tenants + users (all 4 roles)
- Tests: auth API tests, tenant isolation tests, RBAC matrix smoke tests

**Frontend scope**:
- Project scaffold: Next.js, TypeScript, Tailwind, ESLint, Prettier
- `lib/api/client.ts`: typed fetch wrapper with auth + error handling
- `lib/auth/`: AuthProvider, token management, login/logout hooks
- `components/ui/`: Button, Input, Select, Modal, Badge, Card
- `components/layout/`: AppShell, Sidebar (nav links), TopNav (user menu)
- `components/feedback/`: EmptyState, LoadingSpinner, ErrorBanner, Toast,
  ConfirmDialog
- `app/login/page.tsx`: Login form
- `app/layout.tsx`: Root layout with AuthProvider + AppShell
- `app/page.tsx`: Redirect to /dashboard
- `app/dashboard/page.tsx`: Empty dashboard shell with placeholder widgets
- Tests: LoginForm component test, AuthProvider integration test

**CI scope**:
- GitHub Actions workflow with all 8 gates
- Docker Compose: postgres, redis, backend, frontend, celery-worker

**Checkpoint**: A user can log in, see the app shell with sidebar navigation,
and land on an empty dashboard. A second user from a different tenant sees
only their own (empty) data. RBAC prevents viewers from creating entities.
CI pipeline passes.

---

### Phase 1: Contacts & Companies

**Goal**: Full CRUD for contacts and companies with search, filtering,
pagination, archival, and entity associations.

**Delivers**: US2 (Contact Management) + US3 (Company Management)

**Backend scope**:
- Migration: `contacts` and `companies` tables
- `modules/contacts/`: router, schemas, service, models
  - CRUD: create, get, list (search + filter + paginate), update, archive
  - Search: ILIKE on first_name, last_name, email
  - Filters: company_id, archived status
  - Ownership enforcement (SEC-008: created_by)
  - Duplicate email validation (per tenant)
  - Audit events for create/update/archive
- `modules/companies/`: router, schemas, service, models
  - CRUD: create, get, list (search + filter + paginate), update, archive
  - Search: ILIKE on name
  - Filters: industry, archived status
  - Archive blocked if active deals exist
  - Audit events for create/update/archive
- Tests: full API tests for both modules, ownership tests, search/filter
  tests, archive-with-active-deals test

**Frontend scope**:
- `components/data/`: DataTable, SearchInput, FilterBar, Pagination
- `features/contacts/`: ContactForm, ContactList, ContactDetail
- `features/companies/`: CompanyForm, CompanyList, CompanyDetail
- `lib/api/contacts.ts`, `lib/api/companies.ts`
- Contact pages: list, new, [id] detail/edit
- Company pages: list, new, [id] detail/edit
- Bidirectional association rendering (company detail shows contacts,
  contact detail shows company)
- Tests: ContactForm validation, list rendering with empty/loading/error
  states

**E2E**: `contacts.spec.ts`, `companies.spec.ts`

**Checkpoint**: Users can create, search, edit, and archive contacts and
companies. Associations render bidirectionally. Archived entities are
filtered from default views. All states (empty, loading, error) render
correctly.

---

### Phase 2: Deals & Pipeline

**Goal**: Full deal lifecycle with pipeline board (drag-and-drop), stage
transitions, close flows, and optimistic concurrency.

**Delivers**: US4 (Deal Pipeline Management)

**Backend scope**:
- Migration: `deals` table with `version` column
- `modules/deals/`: router, schemas, service, models
  - CRUD: create (defaults to Qualification, owner = current user),
    get, list, update, archive
  - Stage transition: free movement among open stages; closed stages
    terminal (FR-007)
  - Close flow: closed_won / closed_lost with close_date and
    optional loss_reason
  - Optimistic concurrency: `version` field checked on update;
    409 Conflict on mismatch
  - Ownership enforcement (SEC-008: owner_id)
  - Associations: company_id, primary_contact_id
  - Audit events for create/update/stage-change/close
  - Pipeline query: grouped by stage with value sums
- Tests: stage transition validation (forward skip, backward, closed
  terminal), optimistic concurrency conflict test, pipeline grouping,
  ownership transfer

**Frontend scope**:
- `features/deals/`: DealForm, DealDetail, PipelineBoard, PipelineColumn,
  DealCard, CloseDialog (won/lost with loss reason)
- `lib/api/deals.ts`
- Deal pages: pipeline board (list), new, [id] detail/edit
- Drag-and-drop: `@dnd-kit/core` for pipeline column reordering
- Conflict handling: 409 response shows "Deal was modified — refresh
  to see latest"
- Tests: PipelineBoard stage grouping, DealCard rendering, CloseDialog

**E2E**: `deals.spec.ts`

**Checkpoint**: Users can create deals, drag them across pipeline stages,
close as won/lost with confirmation. Pipeline board shows stage columns
with value totals. Optimistic concurrency prevents conflicting updates.

---

### Phase 3: Tasks & Reporting

**Goal**: Task management with assignment, status tracking, overdue
indicators. Dashboard with precomputed metrics.

**Delivers**: US5 (Task Management) + US6 (Reporting Dashboard)

**Backend scope**:
- Migration: `tasks` table, `dashboard_snapshots` table
- `modules/tasks/`: router, schemas, service, models
  - CRUD: create (defaults to to_do), get, list, update, archive
  - Status: free movement between to_do/in_progress/done (FR-008)
  - completed_at set when status → done, cleared when reopened
  - Ownership enforcement (SEC-008: assignee_id)
  - Links to contact_id, deal_id (optional)
  - Overdue query: due_date < now AND status ≠ done
  - Audit events for create/update/status-change
- `modules/reporting/`: router, schemas, service, models
  - `DashboardSnapshot` model: tenant_id, computed_at, data (JSON)
  - `GET /reporting/dashboard`: reads latest snapshot for tenant
  - Tests: snapshot read, empty tenant
- `workers/scheduled.py`: Celery Beat task `precompute_dashboard_metrics`
  - Iterates active tenants
  - Computes: contact_count, deals_by_stage (count + total value),
    open_pipeline_value, overdue_task_count
  - Writes DashboardSnapshot per tenant
  - Runs every 5 minutes (configurable)
- Tests: task API tests, overdue query, dashboard precompute correctness

**Frontend scope**:
- `features/tasks/`: TaskForm, TaskList, TaskDetail
- `features/dashboard/`: MetricCard, PipelineSummary, OverdueTasksBadge
- `lib/api/tasks.ts`, `lib/api/reporting.ts`
- Task pages: list (with "assigned to me" filter), new, [id] detail/edit
- Overdue visual indicator on task list rows
- Dashboard page: metric widgets reading precomputed snapshot, Refresh
  button
- Related tasks section on deal detail page, contact detail page
- Tests: TaskList filtering, overdue indicator rendering, MetricCard
  zero-state

**E2E**: `tasks.spec.ts`, `dashboard.spec.ts`

**Checkpoint**: Users can create, assign, and manage tasks. Overdue tasks
are visually flagged. Dashboard displays accurate precomputed metrics with
proper zero-states. Refresh button loads latest snapshot.

---

### Phase 4: Hardening & Deployment Readiness

**Goal**: Cross-cutting quality passes, performance verification,
accessibility audit, security hardening, and deployment configuration.

**Delivers**: SC-001 through SC-010 verification

**Scope**:
- **Tenant isolation audit**: Review all queries for unscoped access;
  run cross-tenant test suite (SC-005)
- **RBAC matrix test**: Full operation × role matrix (SC-006)
- **Audit log verification**: All AUD-001 actions produce AUD-002
  records; integration test suite (SC-010)
- **Performance verification**: Load test list endpoints at 10k
  records (SC-003); measure pipeline board TTI (SC-004); measure
  dashboard refresh latency (SC-007)
- **Accessibility pass**: axe-core on all pages; keyboard navigation
  walkthrough; screen reader verification on critical flows (SC-009)
- **UX consistency pass**: Empty states, loading indicators, error
  messages on every view (SC-008); destructive action confirmations
  (FR-013)
- **Security hardening**: Rate limiting verification (SEC-007); input
  validation audit (SEC-003); dependency vulnerability scan
- **Spec traceability check**: All tasks map to spec FRs; no
  unspecified work
- **Deployment config**: Production Dockerfiles, docker-compose
  (production profile), environment variable documentation, health
  check endpoints (`/health`, `/ready`)
- **Documentation**: README with setup instructions, architecture
  overview, development workflow

**Checkpoint**: All 10 success criteria (SC-001 through SC-010) verified.
CI pipeline green. System deployable via Docker Compose.

## Complexity Tracking

> No Constitution Check violations requiring justification.
> All gates pass. Background jobs justified per FR-017, FR-018.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
