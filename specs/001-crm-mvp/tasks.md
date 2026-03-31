# Tasks: CRM MVP

**Input**: Design documents from `/specs/001-crm-mvp/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, quickstart.md

**Tests**: Constitution Principle II requires multi-layer coverage for all
critical user flows. Backend unit + API tests, frontend component tests,
and Playwright E2E tests are included. Each acceptance criterion (AC) is
tagged on the implementation task that delivers it AND the test that
validates it.

**Cross-Cutting**: Tenant isolation (Principle III), RBAC authorization
(Principle IV), and audit logging (Principle VI) are explicit separate
tasks in every module that touches protected data.

**Organization**: Tasks are grouped by user story (US1–US6). Within each
story, backend and frontend are independent streams that can execute in
parallel. Within each stream, tasks follow the dependency order:
- **Backend**: model → migration → schemas → service CRUD → service
  search/filter → service authorization → service audit → router
  endpoints → router auth guards → registration → tests
- **Frontend**: API client → form → list → detail → page shells →
  cross-entity integration → tests

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to user story (US1–US6); absent for setup/foundation/polish
- **AC ref**: `(AC: USx.y)` tags the acceptance scenario this task delivers or validates

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Root**: `docker-compose.yml`, `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffold, dependency management, Docker, CI

- [ ] T001 Create root `docker-compose.yml` with postgres, redis, backend, frontend, celery-worker, celery-beat services
- [ ] T002 [P] Initialize backend project: `backend/pyproject.toml` with FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, Celery, httpx, pytest, ruff, mypy dependencies
- [ ] T003 [P] Initialize frontend project: `frontend/package.json` with Next.js 14, React 18, TypeScript 5, Tailwind CSS, ESLint, Prettier, Vitest, Playwright, @dnd-kit/core dependencies
- [ ] T004 [P] Create `backend/Dockerfile` (Python 3.12, multi-stage build)
- [ ] T005 [P] Create `frontend/Dockerfile` (Node 20, multi-stage build)
- [ ] T006 [P] Create `backend/.env.example` with DATABASE_URL, REDIS_URL, JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS, CELERY_BROKER_URL, CORS_ORIGINS
- [ ] T007 [P] Create `frontend/.env.example` with NEXT_PUBLIC_API_URL
- [ ] T008 [P] Configure Ruff linting and formatting in `backend/pyproject.toml` (ruff section)
- [ ] T009 [P] Configure ESLint + Prettier in `frontend/.eslintrc.json` and `frontend/.prettierrc`
- [ ] T010 [P] Configure Tailwind CSS in `frontend/tailwind.config.ts` with design tokens (colors, spacing, typography)
- [ ] T011 [P] Configure Vitest in `frontend/vitest.config.ts` with jsdom environment and path aliases
- [ ] T012 [P] Configure Playwright in `frontend/playwright.config.ts` with base URL and axe-core integration
- [ ] T013 Create GitHub Actions CI workflow in `.github/workflows/ci.yml` with 8 gates: backend-lint, backend-types, backend-tests, frontend-lint, frontend-types, frontend-tests, e2e-tests, security-audit

**Checkpoint**: Both projects scaffold, Docker Compose starts, CI runs.

---

## Phase 2: Foundational / US1 — Authentication & Tenant-Scoped Foundation (Priority: P1)

**Goal**: Authenticated users log in, see app shell, encounter empty states.
Tenant isolation and RBAC enforce security on every request. CI green.

**Independent Test**: Log in as two tenant users, confirm data isolation.
Rep gets 403 for admin operations. Token expiry redirects to login.

### Backend: Core Infrastructure

- [ ] T014 [P] Implement app config in `backend/app/core/config.py` using pydantic-settings (DB URL, Redis URL, JWT settings, CORS origins, Celery broker)
- [ ] T015 [P] Implement SQLAlchemy declarative base in `backend/app/db/base.py`
- [ ] T016 Implement DB engine and async session factory in `backend/app/db/session.py` (async SQLAlchemy, session-scoped tenant_id via execution_options)
- [ ] T017 Implement DB mixins in `backend/app/db/mixins.py`: TenantMixin (auto-filter queries + auto-set tenant_id on insert), TimestampMixin (created_at, updated_at), SoftDeleteMixin (archived flag, default-exclude from queries)
- [ ] T018 [P] Implement app exception hierarchy in `backend/app/core/exceptions.py` (NotFoundError, ForbiddenError, ConflictError, ValidationError → HTTP status mapping)
- [ ] T019 [P] Implement JWT encode/decode and bcrypt hash/verify in `backend/app/core/security.py`
- [ ] T020 Implement tenant context middleware in `backend/app/core/middleware.py` (extract tenant_id from decoded JWT, store in request state) (AC: US1.3)
- [ ] T021 Implement FastAPI dependencies in `backend/app/core/dependencies.py`: get_db (tenant-scoped session), get_current_user (JWT decode + user lookup), require_role() factory (AC: US1.4)
- [ ] T022 Implement RBAC permission engine in `backend/app/core/permissions.py`: role × operation matrix per SEC-001, check_ownership() dispatcher per SEC-008 entity ownership table (AC: US1.4)
- [ ] T023 [P] Implement Celery app configuration in `backend/app/workers/celery_app.py` (Redis broker/backend, eager mode toggle for tests)

### Backend: Auth Data Layer

- [ ] T024 Implement Tenant and User SQLAlchemy models in `backend/app/modules/auth/models.py` per data-model.md (tenants table, users table with role enum)
- [ ] T025 Create Alembic initial migration in `backend/alembic/versions/` for pg_trgm extension, enums (tenant_status, user_role, user_status, deal_stage, task_priority, task_status), tenants table, users table with indexes

### Backend: Auth Schema Layer

- [ ] T026 [P] Implement auth Pydantic schemas in `backend/app/modules/auth/schemas.py` (LoginRequest, TokenResponse, RefreshRequest, UserResponse with role and tenant_id)

### Backend: Auth Service Layer

- [ ] T027 Implement auth service: authentication in `backend/app/modules/auth/service.py` (authenticate user by email+password, verify hash, raise on invalid credentials) (AC: US1.1)
- [ ] T028 Implement auth service: token management in `backend/app/modules/auth/service.py` (create_access_token, create_refresh_token, rotate_refresh with old-token invalidation) (AC: US1.5)

### Backend: Auth Service — Audit Integration

- [ ] T029 Implement auth audit event integration in `backend/app/modules/auth/service.py`: emit_audit_event on login_success, login_failure, logout, token_refresh with actor_id + tenant_id (AUD-001)

### Backend: Auth API Layer

- [ ] T030 Implement auth router endpoints in `backend/app/modules/auth/router.py` per contracts/auth.md: POST /login, POST /refresh, POST /logout, GET /me (AC: US1.1, US1.2)
- [ ] T031 Implement auth rate limiting in `backend/app/modules/auth/router.py` via slowapi: 10 req/min on /login, 5 req/min on /refresh (SEC-007)

### Backend: Audit Data Layer

- [ ] T032 [P] Implement AuditLog SQLAlchemy model in `backend/app/modules/audit/models.py` per data-model.md (no FKs, append-only)
- [ ] T033 [P] Implement audit Pydantic schemas in `backend/app/modules/audit/schemas.py` (AuditLogResponse, AuditQueryParams)
- [ ] T034 Create Alembic migration for audit_logs table in `backend/alembic/versions/` with tenant+timestamp, tenant+entity, tenant+actor indexes

### Backend: Audit Service + Background Job

- [ ] T035 Implement audit service in `backend/app/modules/audit/service.py`: emit_audit_event() dispatches to Celery task; synchronous fallback if queue unavailable (FR-017)
- [ ] T036 Implement Celery audit task in `backend/app/modules/audit/tasks.py`: write_audit_record receives tenant_id as required param, rejects tenant-less calls (TI-005, AUD-002)

### Backend: Audit API Layer

- [ ] T037 Implement audit query router in `backend/app/modules/audit/router.py` per contracts/audit.md: GET /audit (admin-only, paginated by tenant+actor+entity+time) (AUD-004)
- [ ] T038 Add require_role(admin) guard to audit router in `backend/app/modules/audit/router.py`

### Backend: App Entry Point

- [ ] T039 Implement FastAPI app in `backend/app/main.py`: register auth + audit routers, add TenantContextMiddleware, CORS, exception handlers, /health and /ready endpoints

### Backend: Test Infrastructure

- [ ] T040 Implement test fixtures in `backend/tests/conftest.py` (test DB, async engine, async session, httpx AsyncClient, 2 test tenants, 4 users per tenant with all roles, Celery eager mode)
- [ ] T041 [P] Implement entity factories in `backend/tests/factories.py` (TenantFactory, UserFactory via Factory Boy)

### Backend: Unit Tests

- [ ] T042 [P] Implement security utility tests in `backend/tests/unit/test_security.py` (JWT encode/decode round-trip, bcrypt hash/verify, expired token rejection)
- [ ] T043 [P] Implement RBAC engine unit tests in `backend/tests/unit/test_permissions.py` (role × operation matrix per SEC-001: admin=all, manager=all-except-user-mgmt, rep=own-only-write, viewer=read-only; ownership dispatch per SEC-008)
- [ ] T044 [P] Implement audit service unit tests in `backend/tests/unit/test_audit_service.py` (Celery dispatch called, graceful fallback on queue failure, tenant_id required)

### Backend: API Integration Tests

- [ ] T045 Implement auth API tests in `backend/tests/api/test_auth.py` (login success → tokens returned AC:US1.1, login failure → 401, refresh → new tokens, refresh with invalid token → 401, /me returns user+role+tenant, token expiry → 401 AC:US1.5, verify login/logout produce audit records per AUD-001) 
- [ ] T046 Implement tenant isolation API tests in `backend/tests/api/test_tenant_isolation.py` (Tenant A user GETs → only Tenant A data; query param injection fails; URL ID of Tenant B record → 404; SC-005, AC:US1.3)
- [ ] T047 Implement RBAC smoke API tests in `backend/tests/api/test_rbac_smoke.py` (viewer POST → 403; rep archive → 403; admin manage users → 200; AC:US1.4)

### Backend: Seed Script

- [ ] T048 Implement seed script in `backend/scripts/seed.py` (2 tenants: Acme Corp + Globex Inc, 4 users per tenant for admin/manager/rep/viewer roles, password "password123")

### Frontend: Core API Integration

- [ ] T049 [P] Implement shared domain types in `frontend/src/types/index.ts` (Contact, Company, Deal, Task, User, Tenant, PaginatedResponse<T>, ApiError, role/stage/status enums)
- [ ] T050 Implement base API client in `frontend/src/lib/api/client.ts` (typed fetch wrapper: Authorization header injection, 401 → redirect to login AC:US1.2, 403 → permission error, 409 → conflict message, 422 → validation errors, network error → retry message)
- [ ] T051 [P] Implement auth API functions in `frontend/src/lib/api/auth.ts` (login, refresh, logout, getMe — typed request/response)

### Frontend: Auth State Management

- [ ] T052 Implement token storage and refresh in `frontend/src/lib/auth/tokens.ts` (localStorage for tokens, auto-refresh before expiry, clear on logout)
- [ ] T053 Implement AuthContext and AuthProvider in `frontend/src/lib/auth/context.tsx` (user state, role access, isAuthenticated, login/logout actions, token refresh interval)

### Frontend: Shared UI Components (Tailwind-based)

- [ ] T054 [P] Implement Button in `frontend/src/components/ui/button.tsx` (variants: primary/secondary/destructive/ghost; sizes: sm/md/lg; loading state; disabled; keyboard accessible; Tailwind)
- [ ] T055 [P] Implement Input in `frontend/src/components/ui/input.tsx` (label, placeholder, error message, required indicator, ARIA attributes; Tailwind)
- [ ] T056 [P] Implement Select in `frontend/src/components/ui/select.tsx` (label, options, placeholder, error state, ARIA; Tailwind)
- [ ] T057 [P] Implement Modal in `frontend/src/components/ui/modal.tsx` (accessible dialog, focus trap, Escape to close, backdrop click; Tailwind)
- [ ] T058 [P] Implement Badge in `frontend/src/components/ui/badge.tsx` (color variants for status/priority/stage; Tailwind)
- [ ] T059 [P] Implement Card in `frontend/src/components/ui/card.tsx` (header/body/footer slots; Tailwind)

### Frontend: Feedback Components (Tailwind-based)

- [ ] T060 [P] Implement EmptyState in `frontend/src/components/feedback/empty-state.tsx` (icon, title, description, CTA button; Tailwind) (AC: US2.1, US3.1)
- [ ] T061 [P] Implement LoadingSpinner in `frontend/src/components/feedback/loading-spinner.tsx` (full-page + inline variants; Tailwind)
- [ ] T062 [P] Implement ErrorBanner in `frontend/src/components/feedback/error-banner.tsx` (actionable message, retry button; Tailwind)
- [ ] T063 [P] Implement Toast notification system in `frontend/src/components/feedback/toast.tsx` (success/error/warning variants, auto-dismiss timer, stack; Tailwind) (AC: US2.2)
- [ ] T064 [P] Implement ConfirmDialog in `frontend/src/components/feedback/confirm-dialog.tsx` (title, message, confirm/cancel actions, destructive variant; wraps Modal; Tailwind) (AC: US2.6, FR-013)

### Frontend: Layout Components (Tailwind-based)

- [ ] T065 [P] Implement Sidebar in `frontend/src/components/layout/sidebar.tsx` (nav links: Dashboard/Contacts/Companies/Deals/Tasks; active route indicator; role-aware visibility; Tailwind)
- [ ] T066 [P] Implement TopNav in `frontend/src/components/layout/top-nav.tsx` (user name + role display, logout action; Tailwind)
- [ ] T067 Implement AppShell in `frontend/src/components/layout/app-shell.tsx` (Sidebar + TopNav + main content area; responsive; Tailwind)
- [ ] T068 [P] Implement PageHeader in `frontend/src/components/layout/page-header.tsx` (title, breadcrumb, action buttons slot; Tailwind)

### Frontend: Shared Hooks

- [ ] T069 [P] Implement useDebounce hook in `frontend/src/lib/hooks/use-debounce.ts` (configurable delay, default 300ms)
- [ ] T070 [P] Implement usePagination hook in `frontend/src/lib/hooks/use-pagination.ts` (page, page_size, total_pages state from API response)
- [ ] T071 [P] Implement useConfirm hook in `frontend/src/lib/hooks/use-confirm.ts` (open/close state for ConfirmDialog, promise-based confirm/cancel)

### Frontend: Auth Feature + Page Shells

- [ ] T072 Implement LoginForm in `frontend/src/features/auth/login-form.tsx` (email + password fields, inline validation, submit handler, error display; Tailwind) (AC: US1.1)
- [ ] T073 Implement login page shell in `frontend/src/app/login/page.tsx` (renders LoginForm, redirects to dashboard on success) (AC: US1.1)
- [ ] T074 Implement root layout in `frontend/src/app/layout.tsx` (AuthProvider wrapper, conditional AppShell for authenticated routes)
- [ ] T075 Implement root page redirect in `frontend/src/app/page.tsx` (redirect to /dashboard if authenticated, /login if not) (AC: US1.2)
- [ ] T076 Implement empty dashboard page shell in `frontend/src/app/dashboard/page.tsx` (placeholder MetricCard widgets with EmptyState, "Refresh" button wired to no-op for now)

### Frontend: US1 Tests

- [ ] T077 [P] Implement LoginForm component test in `frontend/tests/components/login-form.test.tsx` (renders fields, validates required, shows API error, calls onSubmit; AC: US1.1)
- [ ] T078 [P] Implement AuthProvider integration test in `frontend/tests/integration/auth-provider.test.tsx` (login sets user state, logout clears, 401 triggers redirect; AC: US1.2, US1.5)
- [ ] T079 Implement E2E auth test in `frontend/tests/e2e/auth.spec.ts` (login → dashboard → logout → protected redirect → token expiry; axe-core checks; AC: US1.1–US1.5)

**Checkpoint**: Login works. App shell renders. Tenants isolated. RBAC enforced. CI green.

---

## Phase 3: US2 — Contact Management (Priority: P2)

**Goal**: Full contact CRUD with search, filter, pagination, archival, company
association, duplicate email validation.

**Independent Test**: Create, search, edit, archive contacts as rep. Verify
empty/loading/error states. Confirm archived filter and duplicate rejection.

### Frontend: Shared Data Components (reused by US3–US6)

- [ ] T080 [P] [US2] Implement SearchInput in `frontend/src/components/data/search-input.tsx` (debounced via useDebounce, clear button, ARIA search role; Tailwind)
- [ ] T081 [P] [US2] Implement FilterBar in `frontend/src/components/data/filter-bar.tsx` (accepts filter config, renders dropdowns, active filter badges, clear-all action; Tailwind)
- [ ] T082 [P] [US2] Implement Pagination in `frontend/src/components/data/pagination.tsx` (page numbers, prev/next, page size selector, total display; offset-based; Tailwind)
- [ ] T083 [P] [US2] Implement DataTable in `frontend/src/components/data/data-table.tsx` (column config, row click handler, loading skeleton, empty state slot, sortable headers; Tailwind)

### Backend: Contact Data Layer

- [ ] T084 [P] [US2] Implement Contact SQLAlchemy model in `backend/app/modules/contacts/models.py` per data-model.md (TenantMixin, TimestampMixin, SoftDeleteMixin, company_id FK, created_by FK)
- [ ] T085 [US2] Create Alembic migration for contacts table in `backend/alembic/versions/` with partial unique index on (tenant_id, email) WHERE email IS NOT NULL, trigram GIN index, tenant+archived index

### Backend: Contact Schema Layer

- [ ] T086 [P] [US2] Implement contact Pydantic schemas in `backend/app/modules/contacts/schemas.py` (ContactCreate with email/name validation, ContactUpdate, ContactResponse, ContactListParams with q/company_id/archived/page/page_size)

### Backend: Contact Service — Core CRUD

- [ ] T087 [US2] Implement contact service core CRUD in `backend/app/modules/contacts/service.py`: create (with duplicate email check per tenant AC:edge-case-3), get_by_id, update, archive, unarchive (AC: US2.2, US2.5, US2.6)

### Backend: Contact Service — Search, Filter, Pagination

- [ ] T088 [US2] Implement contact service list with search/filter/pagination in `backend/app/modules/contacts/service.py`: ILIKE search on first_name+last_name+email, filter by company_id+archived, offset-based pagination with total count (AC: US2.4, FR-010, FR-014)

### Backend: Contact Service — Authorization

- [ ] T089 [US2] Implement contact service authorization enforcement in `backend/app/modules/contacts/service.py`: check_ownership on update (created_by per SEC-008), admin/manager bypass, raise ForbiddenError for non-owner reps

### Backend: Contact Service — Audit Integration

- [ ] T090 [US2] Integrate audit events into contact service in `backend/app/modules/contacts/service.py`: emit_audit_event on create, update, archive, unarchive with entity diff (AUD-001)

### Backend: Contact API Layer — Endpoints

- [ ] T091 [US2] Implement contact router endpoints in `backend/app/modules/contacts/router.py` per contracts/contacts.md: POST /contacts, GET /contacts (list), GET /contacts/:id, PUT /contacts/:id, POST /contacts/:id/archive, POST /contacts/:id/unarchive

### Backend: Contact API Layer — Authorization Guards

- [ ] T092 [US2] Add authorization guards to contact router in `backend/app/modules/contacts/router.py`: require_role(admin, manager, rep) on create/update, require_role(admin, manager) on archive/unarchive, all roles on read (SEC-001)

### Backend: Contact Registration

- [ ] T093 [US2] Register contacts router in `backend/app/main.py`

### Backend: Contact Tests — Unit

- [ ] T094 [P] [US2] Implement contact service unit tests in `backend/tests/unit/test_contact_service.py` (duplicate email rejection AC:edge-3, ownership check: rep-owner passes/rep-non-owner raises, archive sets flag, search ILIKE returns matches)

### Backend: Contact Tests — API Integration

- [ ] T095 [US2] Implement contact API tests in `backend/tests/api/test_contacts.py` (create success AC:US2.2, create missing field → 422 AC:US2.3, create duplicate email → 409, get/list, update success AC:US2.5, update non-owner rep → 403, archive AC:US2.6, search returns matches AC:US2.4, filter by company, paginate, archived filter, viewer create → 403, tenant isolation)
- [ ] T096 [P] [US2] Add ContactFactory to `backend/tests/factories.py`

### Frontend: Contact API Client

- [ ] T097 [P] [US2] Implement typed contact API functions in `frontend/src/lib/api/contacts.ts` (createContact, getContact, listContacts, updateContact, archiveContact, unarchiveContact — typed params and responses)

### Frontend: Contact Form Component

- [ ] T098 [US2] Implement ContactForm in `frontend/src/features/contacts/contact-form.tsx` (create/edit mode prop, fields: first_name/last_name/email/phone/company_id selector/notes, inline validation, onSubmit/onCancel, server error display; Tailwind) (AC: US2.2, US2.3, US2.5)

### Frontend: Contact List Component

- [ ] T099 [US2] Implement ContactList in `frontend/src/features/contacts/contact-list.tsx` (composes DataTable+SearchInput+FilterBar+Pagination, columns: name/email/phone/company/archived, debounced search wired to API, filter by company+archived, pagination state via usePagination; Tailwind) (AC: US2.4)

### Frontend: Contact Detail Component

- [ ] T100 [US2] Implement ContactDetail in `frontend/src/features/contacts/contact-detail.tsx` (read view: all fields + linked company name as link, edit button toggles to ContactForm in edit mode, archive button with ConfirmDialog; role-aware: hide edit/archive for viewers; Tailwind) (AC: US2.5, US2.6, US2.7)

### Frontend: Contact Page Shells

- [ ] T101 [US2] Implement contact list page shell in `frontend/src/app/contacts/page.tsx` (PageHeader with "New Contact" CTA (hidden for viewer role), renders ContactList, EmptyState when no contacts AC:US2.1, LoadingSpinner during fetch, ErrorBanner on failure)
- [ ] T102 [P] [US2] Implement contact create page shell in `frontend/src/app/contacts/new/page.tsx` (PageHeader "New Contact", renders ContactForm in create mode, navigates to detail on success)
- [ ] T103 [US2] Implement contact detail page shell in `frontend/src/app/contacts/[id]/page.tsx` (fetches contact by ID, renders ContactDetail, LoadingSpinner, 404 ErrorBanner)

### Frontend: Contact Tests

- [ ] T104 [P] [US2] Implement ContactForm component test in `frontend/tests/components/contact-form.test.tsx` (renders all fields, validates required first/last name, validates email format, shows server error, calls onSubmit with data; AC: US2.2, US2.3)
- [ ] T105 [P] [US2] Implement ContactList component test in `frontend/tests/components/contact-list.test.tsx` (renders rows, search filters, pagination updates, empty state, loading skeleton)
- [ ] T106 [US2] Implement E2E contacts test in `frontend/tests/e2e/contacts.spec.ts` (create → success toast AC:US2.2 → search by name AC:US2.4 → edit email AC:US2.5 → archive with confirm AC:US2.6 → verify archived filter → empty state AC:US2.1; axe-core)

**Checkpoint**: Full contact CRUD. Search, filter, paginate. Archived hidden by default. Ownership enforced. Tenant isolation holds.

---

## Phase 4: US3 — Company Management (Priority: P3)

**Goal**: Full company CRUD with search, filter, pagination, archival (blocked
by active deals), bidirectional contact association.

**Independent Test**: Create company, associate contacts, verify bidirectional
link. Archive blocked when active deals exist.

### Backend: Company Data Layer

- [ ] T107 [P] [US3] Implement Company SQLAlchemy model in `backend/app/modules/companies/models.py` per data-model.md (TenantMixin, TimestampMixin, SoftDeleteMixin, trigram GIN on name)
- [ ] T108 [US3] Create Alembic migration for companies table in `backend/alembic/versions/` with trigram index, tenant+archived index

### Backend: Company Schema Layer

- [ ] T109 [P] [US3] Implement company Pydantic schemas in `backend/app/modules/companies/schemas.py` (CompanyCreate, CompanyUpdate, CompanyResponse with associated_contacts_count and associated_deals_count, CompanyListParams with q/industry/archived)

### Backend: Company Service — Core CRUD

- [ ] T110 [US3] Implement company service core CRUD in `backend/app/modules/companies/service.py`: create, get_by_id (with eager-load associated contacts/deals), update, archive (guard: reject if non-closed deals exist → ConflictError AC:US3.4), unarchive (AC: US3.2)

### Backend: Company Service — Search, Filter, Pagination

- [ ] T111 [US3] Implement company service list with search/filter/pagination in `backend/app/modules/companies/service.py`: ILIKE on name, filter by industry+archived, offset-based pagination (AC: US3.5)

### Backend: Company Service — Authorization + Audit

- [ ] T112 [US3] Implement company service authorization in `backend/app/modules/companies/service.py`: ownership check (created_by per SEC-008), audit events on create/update/archive/unarchive (AUD-001)

### Backend: Company API Layer

- [ ] T113 [US3] Implement company router endpoints in `backend/app/modules/companies/router.py` per contracts/companies.md: POST, GET list, GET :id, PUT :id, POST :id/archive, POST :id/unarchive
- [ ] T114 [US3] Add authorization guards to company router in `backend/app/modules/companies/router.py`: require_role per SEC-001 (create/update: admin+manager+rep, archive: admin+manager)
- [ ] T115 [US3] Register companies router in `backend/app/main.py`

### Backend: Company Tests

- [ ] T116 [P] [US3] Implement company service unit tests in `backend/tests/unit/test_company_service.py` (archive blocked by active deals AC:US3.4, ownership check, search returns matches)
- [ ] T117 [US3] Implement company API tests in `backend/tests/api/test_companies.py` (create AC:US3.2, get with associated contacts AC:US3.3, search+filter AC:US3.5, archive blocked → 409 AC:US3.4, tenant isolation, RBAC enforcement)
- [ ] T118 [P] [US3] Add CompanyFactory to `backend/tests/factories.py`

### Frontend: Company API Client

- [ ] T119 [P] [US3] Implement typed company API functions in `frontend/src/lib/api/companies.ts`

### Frontend: Company Feature Components

- [ ] T120 [US3] Implement CompanyForm in `frontend/src/features/companies/company-form.tsx` (create/edit mode, fields: name/industry dropdown/website/notes, validation; Tailwind) (AC: US3.2)
- [ ] T121 [US3] Implement CompanyList in `frontend/src/features/companies/company-list.tsx` (DataTable+SearchInput+FilterBar+Pagination, columns: name/industry/website/contacts count; Tailwind) (AC: US3.5)
- [ ] T122 [US3] Implement CompanyDetail in `frontend/src/features/companies/company-detail.tsx` (fields, "Associated Contacts" section with linked names AC:US3.3, "Associated Deals" section, archive button with error handling for active-deal 409 AC:US3.4; Tailwind)

### Frontend: Company Page Shells

- [ ] T123 [US3] Implement company list page shell in `frontend/src/app/companies/page.tsx` (PageHeader with "New Company" CTA hidden for viewer role, CompanyList, EmptyState AC:US3.1, loading/error states)
- [ ] T124 [P] [US3] Implement company create page shell in `frontend/src/app/companies/new/page.tsx`
- [ ] T125 [US3] Implement company detail page shell in `frontend/src/app/companies/[id]/page.tsx`

### Frontend: Cross-Entity Integration

- [ ] T126 [US3] Add linked company display to ContactDetail in `frontend/src/features/contacts/contact-detail.tsx` (company name as clickable link; AC: US2.7)

### Frontend: Company Tests

- [ ] T127 [P] [US3] Implement CompanyForm component test in `frontend/tests/components/company-form.test.tsx` (validates name required, submits, edit pre-fills)
- [ ] T128 [P] [US3] Implement CompanyDetail component test in `frontend/tests/components/company-detail.test.tsx` (renders associated contacts AC:US3.3, shows archive-blocked error)
- [ ] T129 [US3] Implement E2E companies test in `frontend/tests/e2e/companies.spec.ts` (create → associate contact → bidirectional link AC:US3.3 → archive blocked AC:US3.4 → empty state AC:US3.1; axe-core)

**Checkpoint**: Full company CRUD. Bidirectional contact ↔ company renders. Archive blocked with active deals.

---

## Phase 5: US4 — Deal Pipeline Management (Priority: P4)

**Goal**: Full deal lifecycle with pipeline board (drag-and-drop), free stage
movement, close flows (won/lost), optimistic concurrency.

**Independent Test**: Create deal, drag through stages, close as won. Trigger
version conflict. Board shows stage columns with value totals.

### Backend: Deal Data Layer

- [ ] T130 [P] [US4] Implement Deal SQLAlchemy model in `backend/app/modules/deals/models.py` per data-model.md (deal_stage enum, version column, owner_id/company_id/primary_contact_id FKs)
- [ ] T131 [US4] Create Alembic migration for deals table in `backend/alembic/versions/` with tenant+stage, tenant+owner, tenant+archived indexes

### Backend: Deal Schema Layer

- [ ] T132 [P] [US4] Implement deal Pydantic schemas in `backend/app/modules/deals/schemas.py` (DealCreate, DealUpdate with version, DealStageChange with version, DealClose with outcome+loss_reason+version, DealResponse, PipelineStageGroup, PipelineResponse)

### Backend: Deal Service — Core CRUD

- [ ] T133 [US4] Implement deal service core CRUD in `backend/app/modules/deals/service.py`: create (auto-Qualification stage, owner=current_user AC:US4.1), get_by_id (eager-load company+contact+owner), update (with version check → ConflictError on mismatch), archive, unarchive

### Backend: Deal Service — Stage Transitions

- [ ] T134 [US4] Implement deal service stage transitions in `backend/app/modules/deals/service.py`: change_stage (free movement among open stages, reject if currently closed → ConflictError AC:FR-007), close_deal (set closed_won/closed_lost + close_date + optional loss_reason, record stage-change timestamp) (AC: US4.2, US4.3, US4.4)

### Backend: Deal Service — Pipeline Aggregation

- [ ] T135 [US4] Implement deal service pipeline aggregation in `backend/app/modules/deals/service.py`: get_pipeline (GROUP BY stage, count + SUM(value) per stage, exclude archived) (AC: US4.5)

### Backend: Deal Service — Authorization + Audit

- [ ] T136 [US4] Implement deal service authorization in `backend/app/modules/deals/service.py`: ownership check (owner_id per SEC-008), audit events on create/update/stage-change/close (AUD-001)

### Backend: Deal API Layer

- [ ] T137 [US4] Implement deal router endpoints in `backend/app/modules/deals/router.py` per contracts/deals.md: POST, GET list, GET :id, PUT :id, POST :id/stage, POST :id/close, POST :id/archive, POST :id/unarchive, GET /pipeline (AC: US4.6)
- [ ] T138 [US4] Add authorization guards to deal router in `backend/app/modules/deals/router.py` per SEC-001
- [ ] T139 [US4] Register deals router in `backend/app/main.py`

### Backend: Deal Tests

- [ ] T140 [P] [US4] Implement deal service unit tests in `backend/tests/unit/test_deal_service.py` (stage transitions: forward skip OK, backward OK, closed terminal → rejected, version conflict → ConflictError, ownership transfer on reassign; AC: US4.2–US4.4, FR-007)
- [ ] T141 [US4] Implement deal API tests in `backend/tests/api/test_deals.py` (create defaults AC:US4.1, stage change AC:US4.2, close won AC:US4.3, close lost with loss_reason AC:US4.4, 409 on reopen closed, 409 on version conflict, pipeline aggregation AC:US4.5, get detail AC:US4.6, RBAC, tenant isolation)
- [ ] T142 [P] [US4] Add DealFactory to `backend/tests/factories.py`

### Frontend: Deal API Client

- [ ] T143 [P] [US4] Implement typed deal API functions in `frontend/src/lib/api/deals.ts` (createDeal, getDeal, listDeals, updateDeal, changeStage, closeDeal, archiveDeal, getPipeline)

### Frontend: Deal Feature Components

- [ ] T144 [US4] Implement DealForm in `frontend/src/features/deals/deal-form.tsx` (fields: name/value/expected_close_date/company selector/primary contact selector, validation; Tailwind) (AC: US4.1)
- [ ] T145 [P] [US4] Implement DealCard in `frontend/src/features/deals/deal-card.tsx` (compact draggable card: deal name, value formatted as currency, owner name, company name; Tailwind)
- [ ] T146 [P] [US4] Implement PipelineColumn in `frontend/src/features/deals/pipeline-column.tsx` (stage header with count + total value, droppable zone via @dnd-kit, empty-stage placeholder; Tailwind) (AC: US4.5)
- [ ] T147 [US4] Implement PipelineBoard in `frontend/src/features/deals/pipeline-board.tsx` (@dnd-kit DndContext, columns per stage, onDragEnd calls changeStage API, 409 conflict → "Deal modified — refresh" ErrorBanner; Tailwind) (AC: US4.2, US4.5)
- [ ] T148 [US4] Implement CloseDialog in `frontend/src/features/deals/close-dialog.tsx` (won/lost toggle, optional loss_reason textarea for lost, ConfirmDialog wrapper; Tailwind) (AC: US4.3, US4.4, FR-013)
- [ ] T149 [US4] Implement DealDetail in `frontend/src/features/deals/deal-detail.tsx` (all fields, company+contact+owner as links, stage badge, close button, edit mode; Tailwind) (AC: US4.6)

### Frontend: Deal Page Shells

- [ ] T150 [US4] Implement pipeline board page shell in `frontend/src/app/deals/page.tsx` (PageHeader with "New Deal" CTA hidden for viewer role, renders PipelineBoard, LoadingSpinner, ErrorBanner)
- [ ] T151 [P] [US4] Implement deal create page shell in `frontend/src/app/deals/new/page.tsx`
- [ ] T152 [US4] Implement deal detail page shell in `frontend/src/app/deals/[id]/page.tsx`

### Frontend: Cross-Entity Integration

- [ ] T153 [US4] Add "Associated Deals" section to CompanyDetail in `frontend/src/features/companies/company-detail.tsx` (list deals with stage badges)

### Frontend: Deal Tests

- [ ] T154 [P] [US4] Implement PipelineBoard component test in `frontend/tests/components/pipeline-board.test.tsx` (renders columns per stage, value totals, empty-stage placeholder AC:US4.5, drag triggers stage change callback)
- [ ] T155 [P] [US4] Implement CloseDialog component test in `frontend/tests/components/close-dialog.test.tsx` (won flow, lost flow with loss_reason, confirm triggers callback)
- [ ] T156 [US4] Implement E2E deals test in `frontend/tests/e2e/deals.spec.ts` (create deal AC:US4.1 → move stages AC:US4.2 → close won AC:US4.3 → board shows columns AC:US4.5 → detail shows all fields AC:US4.6; axe-core)

**Checkpoint**: Full deal lifecycle. Board with drag-and-drop. Closed deals terminal. Concurrency conflicts handled.

---

## Phase 6: US5 — Task Management (Priority: P5)

**Goal**: Task CRUD with assignment, free status transitions, overdue
indicators, links to contacts/deals.

**Independent Test**: Create task, assign, change status, verify overdue
visual. Filter by "assigned to me" + status.

### Backend: Task Data Layer

- [ ] T157 [P] [US5] Implement Task SQLAlchemy model in `backend/app/modules/tasks/models.py` per data-model.md (task_status/task_priority enums, assignee_id FK, optional contact_id/deal_id FKs, completed_at)
- [ ] T158 [US5] Create Alembic migration for tasks table in `backend/alembic/versions/` with tenant+assignee+status index, partial overdue index (tenant_id, due_date WHERE status != 'done'), tenant+archived index

### Backend: Task Schema Layer

- [ ] T159 [P] [US5] Implement task Pydantic schemas in `backend/app/modules/tasks/schemas.py` (TaskCreate, TaskUpdate, TaskStatusChange, TaskResponse with is_overdue computed field, TaskListParams with assignee_id/status/priority/due_date_from/due_date_to/overdue/contact_id/deal_id)

### Backend: Task Service — Core CRUD + Status

- [ ] T160 [US5] Implement task service core CRUD in `backend/app/modules/tasks/service.py`: create (default to_do AC:US5.1), get, update, archive, unarchive; status change with free movement (AC:US5.2, US5.6, FR-008), completed_at set on transition to done / cleared on reopen

### Backend: Task Service — Search, Filter, Overdue

- [ ] T161 [US5] Implement task service list with filters in `backend/app/modules/tasks/service.py`: filter by assignee_id ("assigned to me" AC:US5.5), status, priority, due_date range, contact_id, deal_id, overdue flag (due_date < now AND status ≠ done AC:US5.3), pagination

### Backend: Task Service — Authorization + Audit

- [ ] T162 [US5] Implement task service authorization in `backend/app/modules/tasks/service.py`: ownership check (assignee_id per SEC-008, ownership transfers on reassign), audit events on create/update/status-change (AUD-001)

### Backend: Task API Layer

- [ ] T163 [US5] Implement task router endpoints in `backend/app/modules/tasks/router.py` per contracts/tasks.md: POST, GET list, GET :id, PUT :id, POST :id/status, POST :id/archive, POST :id/unarchive
- [ ] T164 [US5] Add authorization guards to task router in `backend/app/modules/tasks/router.py` per SEC-001
- [ ] T165 [US5] Register tasks router in `backend/app/main.py`

### Backend: Task Tests

- [ ] T166 [P] [US5] Implement task service unit tests in `backend/tests/unit/test_task_service.py` (free status movement: skip forward/backward/reopen, completed_at management, overdue query logic, ownership transfer on reassign)
- [ ] T167 [US5] Implement task API tests in `backend/tests/api/test_tasks.py` (create AC:US5.1, status change AC:US5.2, overdue filter AC:US5.3, assignee filter AC:US5.5, mark done AC:US5.6, contact/deal link AC:US5.4, RBAC, tenant isolation)
- [ ] T168 [P] [US5] Add TaskFactory to `backend/tests/factories.py`

### Frontend: Task API Client

- [ ] T169 [P] [US5] Implement typed task API functions in `frontend/src/lib/api/tasks.ts`

### Frontend: Task Feature Components

- [ ] T170 [US5] Implement TaskForm in `frontend/src/features/tasks/task-form.tsx` (fields: title/description/due_date/priority selector/assignee selector/optional contact link/optional deal link, validation; Tailwind) (AC: US5.1)
- [ ] T171 [US5] Implement TaskList in `frontend/src/features/tasks/task-list.tsx` (DataTable with overdue row visual: red left-border + Badge "Overdue" AC:US5.3, filters: assigned-to-me/status/priority/due date range, pagination; Tailwind) (AC: US5.5)
- [ ] T172 [US5] Implement TaskDetail in `frontend/src/features/tasks/task-detail.tsx` (all fields, linked contact/deal as links, status change buttons with immediate API call, edit mode; Tailwind) (AC: US5.2, US5.6)

### Frontend: Task Page Shells

- [ ] T173 [US5] Implement task list page shell in `frontend/src/app/tasks/page.tsx` (PageHeader with "New Task" CTA hidden for viewer role, TaskList, empty/loading/error states)
- [ ] T174 [P] [US5] Implement task create page shell in `frontend/src/app/tasks/new/page.tsx`
- [ ] T175 [US5] Implement task detail page shell in `frontend/src/app/tasks/[id]/page.tsx`

### Frontend: Cross-Entity Integration

- [ ] T176 [US5] Add "Related Tasks" section to DealDetail in `frontend/src/features/deals/deal-detail.tsx` (list linked tasks with status+overdue badges; AC: US5.4)
- [ ] T177 [US5] Add "Related Tasks" section to ContactDetail in `frontend/src/features/contacts/contact-detail.tsx`

### Frontend: Task Tests

- [ ] T178 [P] [US5] Implement TaskList component test in `frontend/tests/components/task-list.test.tsx` (overdue indicator on past-due rows AC:US5.3, filter by assigned-to-me AC:US5.5, status filter)
- [ ] T179 [US5] Implement E2E tasks test in `frontend/tests/e2e/tasks.spec.ts` (create AC:US5.1 → assign → status change AC:US5.2 → overdue indicator AC:US5.3 → deal shows related task AC:US5.4 → mark done AC:US5.6; axe-core)

**Checkpoint**: Full task management. Overdue visually flagged. Related tasks on deal/contact detail. Free status movement.

---

## Phase 7: US6 — Reporting Dashboard (Priority: P6)

**Goal**: Dashboard with precomputed metrics, manual refresh, proper zero-states.

**Independent Test**: Seed data, verify dashboard metrics match. Empty tenant shows zero-states.

### Backend: Reporting Data Layer

- [ ] T180 [P] [US6] Implement DashboardSnapshot SQLAlchemy model in `backend/app/modules/reporting/models.py` per data-model.md (tenant_id UNIQUE, computed_at, data JSONB)
- [ ] T181 [US6] Create Alembic migration for dashboard_snapshots table in `backend/alembic/versions/`

### Backend: Reporting Schema Layer

- [ ] T182 [P] [US6] Implement reporting Pydantic schemas in `backend/app/modules/reporting/schemas.py` (DashboardResponse: contacts_count, deals_by_stage list, open_pipeline_value, overdue_tasks_count, computed_at)

### Backend: Reporting Service

- [ ] T183 [US6] Implement reporting service in `backend/app/modules/reporting/service.py`: get_dashboard (read latest DashboardSnapshot for tenant, return zero-state if none exists AC:US6.2)

### Backend: Reporting API Layer

- [ ] T184 [US6] Implement reporting router in `backend/app/modules/reporting/router.py` per contracts/reporting.md: GET /reporting/dashboard (all roles, tenant-wide metrics AC:US6.1, FR-009)
- [ ] T185 [US6] Register reporting router in `backend/app/main.py`

### Backend: Dashboard Precompute Background Job

- [ ] T186 [US6] Implement Celery Beat scheduled task in `backend/app/workers/scheduled.py`: precompute_dashboard_metrics iterates active tenants, computes contact_count + deals_by_stage + open_pipeline_value + overdue_tasks_count, upserts DashboardSnapshot (FR-018)
- [ ] T187 [US6] Configure Celery Beat schedule in `backend/app/workers/celery_app.py`: precompute every 5 minutes (configurable via DASHBOARD_PRECOMPUTE_INTERVAL_SECONDS)

### Backend: Reporting Tests

- [ ] T188 [P] [US6] Implement dashboard precompute unit test in `backend/tests/unit/test_dashboard_precompute.py` (aggregation correctness: contact count, deals by stage with values AC:US6.5, open pipeline value, overdue tasks count; handles empty tenant)
- [ ] T189 [US6] Implement reporting API tests in `backend/tests/api/test_reporting.py` (dashboard returns snapshot AC:US6.1, empty tenant returns zeros AC:US6.2, all roles can access, tenant isolation)

### Frontend: Dashboard API Client

- [ ] T190 [P] [US6] Implement typed reporting API functions in `frontend/src/lib/api/reporting.ts` (getDashboard)

### Frontend: Dashboard Feature Components

- [ ] T191 [P] [US6] Implement MetricCard in `frontend/src/features/dashboard/metric-card.tsx` (label, value, zero-state variant "No data yet"; Tailwind)
- [ ] T192 [P] [US6] Implement PipelineSummary in `frontend/src/features/dashboard/pipeline-summary.tsx` (horizontal stage bars with count + total value per stage, zero-state; Tailwind) (AC: US6.5)

### Frontend: Dashboard Page Shell

- [ ] T193 [US6] Replace placeholder dashboard in `frontend/src/app/dashboard/page.tsx` with full implementation: MetricCard grid (contacts count, open pipeline value, overdue tasks count), PipelineSummary, Refresh button triggers re-fetch, computed_at timestamp, per-widget zero-states AC:US6.2, role-aware: viewers see metrics but no CTA buttons AC:US6.4 (AC: US6.1, US6.3)

### Frontend: Dashboard Tests

- [ ] T194 [P] [US6] Implement MetricCard component test in `frontend/tests/components/metric-card.test.tsx` (renders value, renders zero-state)
- [ ] T195 [P] [US6] Implement PipelineSummary component test in `frontend/tests/components/pipeline-summary.test.tsx` (renders stages with counts+values AC:US6.5, renders zero-state)
- [ ] T196 [US6] Implement E2E dashboard test in `frontend/tests/e2e/dashboard.spec.ts` (metrics match seeded data AC:US6.1 → refresh AC:US6.3 → empty state AC:US6.2 → viewer sees no edit buttons AC:US6.4 → stage values AC:US6.5; axe-core)

**Checkpoint**: Dashboard accurate. Zero-states render. Refresh works. All roles see metrics.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, verification, deployment readiness (plan Phase 4).

### Verification Tests

- [ ] T197 [P] Implement full RBAC matrix test in `backend/tests/api/test_rbac_matrix.py` (every operation × role combination per SEC-001; SC-006)
- [ ] T198 [P] Implement comprehensive tenant isolation suite in `backend/tests/api/test_tenant_isolation_full.py` (all entity endpoints: contacts/companies/deals/tasks/reporting/audit; SC-005)
- [ ] T199 [P] Implement audit completeness tests in `backend/tests/integration/test_audit_completeness.py` (all AUD-001 actions produce AUD-002 records with correct schema; SC-010)
- [ ] T200 [P] Implement input validation audit tests in `backend/tests/api/test_input_validation.py` (SEC-003: string lengths, email format, currency format, date format, enum values on all endpoints)

### Frontend Verification

- [ ] T201 [P] Run axe-core accessibility audit on all pages via Playwright helper in `frontend/tests/e2e/accessibility.spec.ts` and fix violations (SC-009)
- [ ] T202 [P] UX consistency pass in `frontend/tests/e2e/ux-consistency.spec.ts`: verify empty states, loading indicators, error messages on every list/detail/dashboard view (SC-008)
- [ ] T203 [P] Verify all destructive actions trigger ConfirmDialog in `frontend/tests/e2e/confirm-dialog.spec.ts`: archive contact, archive company, close-as-lost deal (FR-013)

### Performance + Security

- [ ] T204 [P] Rate limiting verification: test auth endpoint throttling in `backend/tests/api/test_rate_limiting.py` (SEC-007)
- [ ] T205 [P] Dependency vulnerability scan: `pip-audit` (backend) + `npm audit` (frontend) (SEC pipeline gate)
- [ ] T206 Performance verification: seed 10k records per entity, measure list endpoint p95 < 500ms (SC-003), pipeline board TTI < 2s (SC-004), dashboard refresh < 500ms (SC-007)

### Deployment + Documentation

- [ ] T207 [P] Create production Docker Compose in `docker-compose.prod.yml` with environment variable documentation
- [ ] T208 [P] Add /health and /ready endpoint tests in `backend/tests/api/test_health.py`
- [ ] T209 Create project README.md (setup instructions, architecture overview, development workflow, quickstart reference)
- [ ] T210 Spec traceability check: verify all tasks map to spec FRs/SCs, no unspecified work delivered

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (US1)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US2)**: Depends on Phase 2
- **Phase 4 (US3)**: Depends on Phase 2; benefits from Phase 3 shared data components
- **Phase 5 (US4)**: Requires contacts + companies tables (Phases 3–4)
- **Phase 6 (US5)**: Depends on Phase 2; contact/deal links need Phases 3+5
- **Phase 7 (US6)**: Requires all entity tables (Phases 3–6)
- **Phase 8 (Polish)**: Depends on all user stories complete

### Backend ∥ Frontend Parallelism

Within every user story phase, backend and frontend streams are
independently testable and can execute in parallel:

```text
Phase N backend: model → migration → schemas → service layers → router → tests
                              ∥ (parallel)
Phase N frontend: API client → form → list → detail → page shells → tests
```

E2E tests require both streams complete.

### User Story Dependencies

- **US1**: Foundation — no story deps
- **US2**: After US1 — introduces shared data components
- **US3**: After US1 — reuses shared data components; companies table independent of contacts
- **US4**: After US2 + US3 — deals reference both contacts and companies
- **US5**: After US1 — standalone tasks work; contact/deal links after US2+US4
- **US6**: After US4 + US5 — aggregates across all entities

### Parallel Opportunities

- **Phase 1**: 11 of 13 tasks [P] (all scaffold tasks)
- **Phase 2**: Backend (T014–T048) ∥ Frontend (T049–T079), 20+ [P] within each
- **Phase 3**: Backend (T084–T096) ∥ Frontend (T097–T106), shared components (T080–T083) all [P]
- **Phase 4**: Backend (T107–T118) ∥ Frontend (T119–T129)
- **Phase 5**: Backend (T130–T142) ∥ Frontend (T143–T156)
- **Phase 6**: Backend (T157–T168) ∥ Frontend (T169–T179)
- **Phase 7**: Backend (T180–T189) ∥ Frontend (T190–T196)
- **Phase 8**: All verification tasks [P] (T197–T208)

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup
2. Phase 2: US1 foundation
3. **STOP and VALIDATE**: Login + app shell + tenant isolation + RBAC
4. Deploy/demo if ready

### Incremental Delivery

1. Setup + US1 → Login + app shell (MVP foundation)
2. US2 → Contact management + shared data components
3. US3 → Company management + bidirectional associations
4. US4 → Deal pipeline with drag-and-drop board
5. US5 → Task management with overdue indicators
6. US6 → Reporting dashboard with precomputed metrics
7. Hardening → All SC-001–SC-010 verified, deployment-ready

### Parallel Team Strategy

After Phase 2, with multiple developers:
- Developer A: US2 backend + frontend → US4 backend + frontend
- Developer B: US3 backend + frontend → US5 backend + frontend
- Developer C: Shared data components → US6 (after entities exist)
- All: Phase 8 (hardening)

---

## Notes

- [P] = different files, no dependency on incomplete tasks
- [Story] label maps task to user story for traceability
- (AC: USx.y) tags map to spec acceptance scenarios
- Backend service split: CRUD → search/filter → authorization → audit
- Frontend component split: form → list → detail → page shell
- Backend and frontend streams within each story execute in parallel
- Backend tests use Celery eager mode for synchronous audit writes
- All E2E tests include axe-core accessibility checks (SC-009)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
