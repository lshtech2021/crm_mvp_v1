# Tasks: CRM MVP

**Input**: Design documents from `/specs/001-crm-mvp/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md,
contracts/, quickstart.md

**Tests**: Constitution Principle II requires multi-layer coverage for all
critical user flows. Backend API tests, frontend component tests, and
Playwright E2E tests are included per the testing strategy in plan.md.

**Cross-Cutting**: Tenant isolation (Principle III), RBAC authorization
(Principle IV), and audit logging (Principle VI) tasks are included in
every phase that touches protected data.

**Organization**: Tasks are grouped by user story (US1–US6) to enable
independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Root**: `docker-compose.yml`, `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffold, dependency management, Docker setup, CI pipeline

- [ ] T001 Create root `docker-compose.yml` with postgres, redis, backend, frontend, celery-worker, celery-beat services
- [ ] T002 [P] Initialize backend project: `backend/pyproject.toml` with FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, Celery, httpx, pytest, ruff, mypy deps
- [ ] T003 [P] Initialize frontend project: `frontend/package.json` with Next.js 14, React 18, TypeScript, Tailwind CSS, ESLint, Prettier, Vitest, Playwright, @dnd-kit/core deps
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

**Checkpoint**: Both projects scaffold, Docker Compose starts all services, CI pipeline runs (tests will fail until code exists).

---

## Phase 2: Foundational / US1 — Authentication & Tenant-Scoped Foundation (Priority: P1)

**Goal**: Authenticated users can log in, see an app shell with navigation, and encounter proper empty states. Tenant isolation and RBAC infrastructure enforce security on every request. CI pipeline is green.

**Independent Test**: Log in as users from two different tenants and confirm each sees only their own data. Verify RBAC by attempting admin operations as a rep (expect 403).

### Backend Core Infrastructure

- [ ] T014 Implement app config in `backend/app/core/config.py` using pydantic-settings (DB URL, Redis URL, JWT settings, CORS origins, Celery broker)
- [ ] T015 Implement DB engine and async session factory in `backend/app/db/session.py` (async SQLAlchemy, session-scoped tenant_id via execution_options)
- [ ] T016 Implement SQLAlchemy declarative base in `backend/app/db/base.py`
- [ ] T017 Implement DB mixins in `backend/app/db/mixins.py`: TenantMixin (auto-filter + auto-set tenant_id), TimestampMixin (created_at, updated_at), SoftDeleteMixin (archived flag, default-exclude filter)
- [ ] T018 Implement app exception hierarchy in `backend/app/core/exceptions.py` (NotFoundError, ForbiddenError, ConflictError, ValidationError with HTTP status mapping)
- [ ] T019 Implement JWT encode/decode and bcrypt hash/verify in `backend/app/core/security.py`
- [ ] T020 Implement tenant context middleware in `backend/app/core/middleware.py` (extract tenant_id from JWT, store in request state)
- [ ] T021 Implement FastAPI dependencies in `backend/app/core/dependencies.py`: get_db (tenant-scoped session), get_current_user (JWT decode + user lookup), require_role() factory
- [ ] T022 Implement RBAC permission engine in `backend/app/core/permissions.py`: role × operation matrix (SEC-001), check_ownership per entity (SEC-008)
- [ ] T023 Implement Celery app configuration in `backend/app/workers/celery_app.py` (Redis broker, eager mode for tests)

### Backend Auth Module

- [ ] T024 Implement Tenant and User SQLAlchemy models in `backend/app/modules/auth/models.py` per data-model.md (tables: tenants, users)
- [ ] T025 Create Alembic initial migration in `backend/alembic/versions/` for tenants and users tables with enums and indexes
- [ ] T026 Implement auth Pydantic schemas in `backend/app/modules/auth/schemas.py` (LoginRequest, TokenResponse, UserResponse, RefreshRequest)
- [ ] T027 Implement auth service in `backend/app/modules/auth/service.py` (authenticate, create_tokens, rotate_refresh, get_user_by_id)
- [ ] T028 Implement auth router in `backend/app/modules/auth/router.py` per contracts/auth.md (POST /login, /refresh, /logout; GET /me) with rate limiting via slowapi

### Backend Audit Module

- [ ] T029 Implement AuditLog SQLAlchemy model in `backend/app/modules/audit/models.py` per data-model.md (no FKs, append-only)
- [ ] T030 Create Alembic migration for audit_logs table in `backend/alembic/versions/`
- [ ] T031 Implement audit service in `backend/app/modules/audit/service.py` (emit_audit_event dispatches to Celery; graceful fallback per FR-017)
- [ ] T032 Implement Celery audit task in `backend/app/modules/audit/tasks.py` (write_audit_record with tenant context per TI-005)
- [ ] T033 Implement audit query router in `backend/app/modules/audit/router.py` per contracts/audit.md (GET /audit, admin-only, paginated)
- [ ] T034 Implement audit Pydantic schemas in `backend/app/modules/audit/schemas.py`

### Backend App Entry Point

- [ ] T035 Implement FastAPI app in `backend/app/main.py` (register routers, middleware, CORS, exception handlers, startup/shutdown, /health and /ready endpoints)

### Backend Test Infrastructure & Tests

- [ ] T036 Implement test fixtures in `backend/tests/conftest.py` (test DB, async client, test tenants A+B, test users per role)
- [ ] T037 [P] Implement entity factories in `backend/tests/factories.py` (TenantFactory, UserFactory using Factory Boy)
- [ ] T038 [P] Implement unit tests for security utils in `backend/tests/unit/test_security.py` (JWT encode/decode, password hash/verify)
- [ ] T039 [P] Implement unit tests for permissions engine in `backend/tests/unit/test_permissions.py` (role × operation matrix, ownership checks)
- [ ] T040 Implement auth API tests in `backend/tests/api/test_auth.py` (login success/failure, refresh, logout, /me, token expiry)
- [ ] T041 Implement tenant isolation API tests in `backend/tests/api/test_tenant_isolation.py` (Tenant A user cannot see Tenant B data via any endpoint; SC-005)
- [ ] T042 Implement RBAC smoke API tests in `backend/tests/api/test_rbac_smoke.py` (viewer cannot create; rep cannot archive; admin can manage users)

### Backend Seed Script

- [ ] T043 Implement seed script in `backend/scripts/seed.py` (create 2 tenants, 4 users per tenant with all roles, password "password123")

### Frontend Core Infrastructure

- [ ] T044 Implement shared API types in `frontend/src/types/index.ts` (Contact, Company, Deal, Task, User, PaginatedResponse, ApiError)
- [ ] T045 Implement base API client in `frontend/src/lib/api/client.ts` (typed fetch wrapper: auth headers, 401 redirect, 403/409/422 error handling, network error)
- [ ] T046 Implement auth API functions in `frontend/src/lib/api/auth.ts` (login, refresh, logout, getMe)
- [ ] T047 Implement token storage and refresh logic in `frontend/src/lib/auth/tokens.ts`
- [ ] T048 Implement AuthContext and AuthProvider in `frontend/src/lib/auth/context.tsx` (login/logout state, token refresh, role access)

### Frontend Shared UI Components

- [ ] T049 [P] Implement Button component in `frontend/src/components/ui/button.tsx` (variants: primary, secondary, destructive, ghost; sizes; disabled state; keyboard accessible)
- [ ] T050 [P] Implement Input component in `frontend/src/components/ui/input.tsx` (label, error state, required indicator, ARIA attributes)
- [ ] T051 [P] Implement Select component in `frontend/src/components/ui/select.tsx` (label, options, error state, ARIA)
- [ ] T052 [P] Implement Modal component in `frontend/src/components/ui/modal.tsx` (accessible dialog, focus trap, escape to close)
- [ ] T053 [P] Implement Badge component in `frontend/src/components/ui/badge.tsx` (variants for status/priority/stage colors)
- [ ] T054 [P] Implement Card component in `frontend/src/components/ui/card.tsx` (header, body, footer slots)

### Frontend Feedback Components

- [ ] T055 [P] Implement EmptyState component in `frontend/src/components/feedback/empty-state.tsx` (icon, title, description, action button)
- [ ] T056 [P] Implement LoadingSpinner component in `frontend/src/components/feedback/loading-spinner.tsx` (full-page and inline variants)
- [ ] T057 [P] Implement ErrorBanner component in `frontend/src/components/feedback/error-banner.tsx` (actionable message, retry button)
- [ ] T058 [P] Implement Toast notification system in `frontend/src/components/feedback/toast.tsx` (success, error, warning variants; auto-dismiss)
- [ ] T059 [P] Implement ConfirmDialog component in `frontend/src/components/feedback/confirm-dialog.tsx` (confirmation before destructive actions per FR-013)

### Frontend Layout Components

- [ ] T060 [P] Implement Sidebar in `frontend/src/components/layout/sidebar.tsx` (nav links: Dashboard, Contacts, Companies, Deals, Tasks; active state; role-aware visibility)
- [ ] T061 [P] Implement TopNav in `frontend/src/components/layout/top-nav.tsx` (user menu: name, role, logout)
- [ ] T062 Implement AppShell in `frontend/src/components/layout/app-shell.tsx` (Sidebar + TopNav + main content area)
- [ ] T063 [P] Implement PageHeader in `frontend/src/components/layout/page-header.tsx` (title, breadcrumb, action buttons)

### Frontend Auth Pages & App Shell

- [ ] T064 Implement LoginForm in `frontend/src/features/auth/login-form.tsx` (email + password form, validation, error display)
- [ ] T065 Implement login page in `frontend/src/app/login/page.tsx` (LoginForm, redirect on success)
- [ ] T066 Implement root layout in `frontend/src/app/layout.tsx` (AuthProvider, conditional AppShell for authenticated routes)
- [ ] T067 Implement root page redirect in `frontend/src/app/page.tsx` (redirect to /dashboard if authenticated, /login if not)
- [ ] T068 Implement empty dashboard shell in `frontend/src/app/dashboard/page.tsx` (placeholder metric widgets with EmptyState per US6 zero-state)

### Frontend Tests for US1

- [ ] T069 [P] Implement LoginForm component test in `frontend/tests/components/login-form.test.tsx` (render, validation, submit, error display)
- [ ] T070 [P] Implement AuthProvider integration test in `frontend/tests/integration/auth-provider.test.tsx` (login/logout state, token refresh, redirect)
- [ ] T071 Implement E2E auth test in `frontend/tests/e2e/auth.spec.ts` (login → dashboard → logout → protected redirect; axe-core checks)

**Checkpoint**: Users can log in, see app shell with navigation, land on empty dashboard. Two tenants see only own data. RBAC enforced. CI green.

---

## Phase 3: US2 — Contact Management (Priority: P2)

**Goal**: Full CRUD for contacts with search, filtering, pagination, archival, company association, and duplicate email validation.

**Independent Test**: Create, search, edit, and archive contacts as a rep. Verify list/detail views render with empty, loading, and error states.

### Shared Data Components (first entity CRUD — reused by US3–US6)

- [ ] T072 [P] [US2] Implement SearchInput component in `frontend/src/components/data/search-input.tsx` (debounced input per 300ms, clear button, ARIA)
- [ ] T073 [P] [US2] Implement FilterBar component in `frontend/src/components/data/filter-bar.tsx` (dropdowns for entity-specific filters, active filter badges, clear all)
- [ ] T074 [P] [US2] Implement Pagination component in `frontend/src/components/data/pagination.tsx` (page numbers, prev/next, page size selector; uses offset-based params)
- [ ] T075 [P] [US2] Implement DataTable component in `frontend/src/components/data/data-table.tsx` (sortable columns, row click, loading skeleton, empty state slot)
- [ ] T076 [P] [US2] Implement useDebounce hook in `frontend/src/lib/hooks/use-debounce.ts`
- [ ] T077 [P] [US2] Implement usePagination hook in `frontend/src/lib/hooks/use-pagination.ts` (page state, page_size, total_pages from API)

### Backend Contact Module

- [ ] T078 [US2] Implement Contact SQLAlchemy model in `backend/app/modules/contacts/models.py` per data-model.md (TenantMixin, SoftDeleteMixin, trigram index)
- [ ] T079 [US2] Create Alembic migration for contacts table with partial unique index on (tenant_id, email) and trigram indexes
- [ ] T080 [US2] Implement contact Pydantic schemas in `backend/app/modules/contacts/schemas.py` (ContactCreate, ContactUpdate, ContactResponse, ContactListParams)
- [ ] T081 [US2] Implement contact service in `backend/app/modules/contacts/service.py` (create with duplicate email check, get, list with ILIKE search + filters + pagination, update with ownership check, archive/unarchive, audit events)
- [ ] T082 [US2] Implement contact router in `backend/app/modules/contacts/router.py` per contracts/contacts.md (POST, GET list, GET :id, PUT :id, POST :id/archive, POST :id/unarchive)
- [ ] T083 [US2] Register contacts router in `backend/app/main.py`

### Backend Contact Tests

- [ ] T084 [P] [US2] Implement contact unit tests in `backend/tests/unit/test_contact_service.py` (duplicate email rejection, ownership check, archive logic)
- [ ] T085 [US2] Implement contact API tests in `backend/tests/api/test_contacts.py` (CRUD success, validation errors, 403 for viewer create, 403 for non-owner rep update, search, filter, pagination, archive/unarchive, tenant isolation)

### Frontend Contact Feature

- [ ] T086 [US2] Implement contact API functions in `frontend/src/lib/api/contacts.ts` (create, getById, list, update, archive, unarchive)
- [ ] T087 [US2] Implement ContactForm in `frontend/src/features/contacts/contact-form.tsx` (create/edit mode, company selector, inline validation, submit)
- [ ] T088 [US2] Implement ContactList in `frontend/src/features/contacts/contact-list.tsx` (DataTable + SearchInput + FilterBar + Pagination, archived filter toggle)
- [ ] T089 [US2] Implement ContactDetail in `frontend/src/features/contacts/contact-detail.tsx` (display fields, linked company, edit button, archive button with ConfirmDialog)
- [ ] T090 [US2] Implement contact list page in `frontend/src/app/contacts/page.tsx` (ContactList with empty/loading/error states)
- [ ] T091 [P] [US2] Implement contact create page in `frontend/src/app/contacts/new/page.tsx` (ContactForm in create mode)
- [ ] T092 [US2] Implement contact detail page in `frontend/src/app/contacts/[id]/page.tsx` (ContactDetail with edit mode toggle)

### Frontend Contact Tests

- [ ] T093 [P] [US2] Implement ContactForm component test in `frontend/tests/components/contact-form.test.tsx` (validation, submit, error display)
- [ ] T094 [US2] Implement E2E contacts test in `frontend/tests/e2e/contacts.spec.ts` (create → search → edit → archive → archived filter; empty state; axe-core)

**Checkpoint**: Full contact CRUD operational. Search, filter, paginate work. Archived contacts hidden by default. Ownership enforced for reps. Tenant isolation holds.

---

## Phase 4: US3 — Company Management (Priority: P3)

**Goal**: Full CRUD for companies with search, filtering, pagination, archival (blocked if active deals), and bidirectional contact association.

**Independent Test**: Create companies, associate contacts, verify bidirectional rendering. Attempt to archive a company with active deals (blocked).

### Backend Company Module

- [ ] T095 [US3] Implement Company SQLAlchemy model in `backend/app/modules/companies/models.py` per data-model.md (TenantMixin, SoftDeleteMixin, trigram index on name)
- [ ] T096 [US3] Create Alembic migration for companies table with trigram index
- [ ] T097 [US3] Implement company Pydantic schemas in `backend/app/modules/companies/schemas.py` (CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListParams)
- [ ] T098 [US3] Implement company service in `backend/app/modules/companies/service.py` (create, get with associated contacts/deals, list with ILIKE search + filters + pagination, update with ownership check, archive with active-deal guard, unarchive, audit events)
- [ ] T099 [US3] Implement company router in `backend/app/modules/companies/router.py` per contracts/companies.md
- [ ] T100 [US3] Register companies router in `backend/app/main.py`

### Backend Company Tests

- [ ] T101 [P] [US3] Implement company unit tests in `backend/tests/unit/test_company_service.py` (archive-blocked-by-active-deals, ownership check)
- [ ] T102 [US3] Implement company API tests in `backend/tests/api/test_companies.py` (CRUD, search, filter, pagination, archive blocked with active deal returns 409, tenant isolation)

### Frontend Company Feature

- [ ] T103 [US3] Implement company API functions in `frontend/src/lib/api/companies.ts`
- [ ] T104 [US3] Implement CompanyForm in `frontend/src/features/companies/company-form.tsx` (create/edit, industry dropdown, validation)
- [ ] T105 [US3] Implement CompanyList in `frontend/src/features/companies/company-list.tsx` (DataTable + search + industry filter + pagination)
- [ ] T106 [US3] Implement CompanyDetail in `frontend/src/features/companies/company-detail.tsx` (fields, "Associated Contacts" section, "Associated Deals" section, archive with error handling for active deals)
- [ ] T107 [US3] Implement company pages in `frontend/src/app/companies/` (list page.tsx, new/page.tsx, [id]/page.tsx)
- [ ] T108 [US3] Add company link to ContactDetail in `frontend/src/features/contacts/contact-detail.tsx` (bidirectional association rendering)

### Frontend Company Tests

- [ ] T109 [P] [US3] Implement CompanyForm component test in `frontend/tests/components/company-form.test.tsx`
- [ ] T110 [US3] Implement E2E companies test in `frontend/tests/e2e/companies.spec.ts` (create → associate contact → verify bidirectional link; archive blocked; axe-core)

**Checkpoint**: Full company CRUD. Bidirectional contact ↔ company association renders. Archive blocked when active deals exist. All states correct.

---

## Phase 5: US4 — Deal Pipeline Management (Priority: P4)

**Goal**: Full deal lifecycle with pipeline board (drag-and-drop), free stage movement among open stages, close flows (won/lost), and optimistic concurrency.

**Independent Test**: Create a deal, move through stages via board drag and detail page, close as won. Verify pipeline board grouping with value totals. Trigger optimistic concurrency conflict.

### Backend Deal Module

- [ ] T111 [US4] Implement Deal SQLAlchemy model in `backend/app/modules/deals/models.py` per data-model.md (stage enum, version column, owner_id, company_id, primary_contact_id)
- [ ] T112 [US4] Create Alembic migration for deals table with stage/owner/archived indexes
- [ ] T113 [US4] Implement deal Pydantic schemas in `backend/app/modules/deals/schemas.py` (DealCreate, DealUpdate, DealStageChange, DealClose, DealResponse, PipelineResponse)
- [ ] T114 [US4] Implement deal service in `backend/app/modules/deals/service.py` (create with auto-Qualification + owner=current_user, get, list, update with version check, stage transition with free-open/closed-terminal rules per FR-007, close flow with close_date/loss_reason, pipeline aggregation by stage with value sums, ownership check per SEC-008 owner_id, audit events)
- [ ] T115 [US4] Implement deal router in `backend/app/modules/deals/router.py` per contracts/deals.md (POST, GET list, GET :id, PUT :id, POST :id/stage, POST :id/close, POST :id/archive, GET /pipeline)
- [ ] T116 [US4] Register deals router in `backend/app/main.py`
- [ ] T117 [US4] Add deal factory to `backend/tests/factories.py` (DealFactory with company and contact associations)

### Backend Deal Tests

- [ ] T118 [P] [US4] Implement deal unit tests in `backend/tests/unit/test_deal_service.py` (stage transitions: forward skip, backward move, closed terminal, reopen blocked; optimistic concurrency conflict; ownership transfer)
- [ ] T119 [US4] Implement deal API tests in `backend/tests/api/test_deals.py` (CRUD, stage change, close won/lost, 409 on version conflict, 409 on reopen closed, pipeline aggregation, ownership enforcement, tenant isolation)

### Frontend Deal Feature

- [ ] T120 [US4] Implement deal API functions in `frontend/src/lib/api/deals.ts` (create, getById, list, update, changeStage, close, archive, getPipeline)
- [ ] T121 [US4] Implement DealForm in `frontend/src/features/deals/deal-form.tsx` (name, value, expected close date, company selector, primary contact selector, validation)
- [ ] T122 [US4] Implement DealCard in `frontend/src/features/deals/deal-card.tsx` (compact card for pipeline board: name, value, owner, company; draggable)
- [ ] T123 [US4] Implement PipelineColumn in `frontend/src/features/deals/pipeline-column.tsx` (stage header with count + total value, droppable zone, placeholder for empty stage)
- [ ] T124 [US4] Implement PipelineBoard in `frontend/src/features/deals/pipeline-board.tsx` (@dnd-kit/core drag-and-drop, columns per stage, onDragEnd calls changeStage API, 409 conflict handling)
- [ ] T125 [US4] Implement CloseDialog in `frontend/src/features/deals/close-dialog.tsx` (won/lost selection, optional loss reason field, confirmation per FR-013)
- [ ] T126 [US4] Implement DealDetail in `frontend/src/features/deals/deal-detail.tsx` (all fields, company + contact + owner links, stage indicator, close button, edit mode)
- [ ] T127 [US4] Implement deal pages in `frontend/src/app/deals/` (page.tsx = PipelineBoard, new/page.tsx, [id]/page.tsx = DealDetail)
- [ ] T128 [US4] Add deals section to CompanyDetail in `frontend/src/features/companies/company-detail.tsx` (list deals associated with company)

### Frontend Deal Tests

- [ ] T129 [P] [US4] Implement PipelineBoard component test in `frontend/tests/components/pipeline-board.test.tsx` (stage grouping, value totals, drag interaction)
- [ ] T130 [P] [US4] Implement CloseDialog component test in `frontend/tests/components/close-dialog.test.tsx` (won/lost flow, loss reason)
- [ ] T131 [US4] Implement E2E deals test in `frontend/tests/e2e/deals.spec.ts` (create → move stages → close won → verify board; axe-core)

**Checkpoint**: Full deal lifecycle. Pipeline board shows stage columns with drag-and-drop. Closed deals terminal. Optimistic concurrency handles conflicts. Value totals correct.

---

## Phase 6: US5 — Task Management (Priority: P5)

**Goal**: Task CRUD with assignment, free status transitions, overdue indicators, and links to contacts/deals.

**Independent Test**: Create tasks, assign, change status, verify overdue visual indicator. Filter by "assigned to me" and status.

### Backend Task Module

- [ ] T132 [US5] Implement Task SQLAlchemy model in `backend/app/modules/tasks/models.py` per data-model.md (status enum, priority enum, assignee_id, optional contact_id/deal_id, completed_at)
- [ ] T133 [US5] Create Alembic migration for tasks table with assignee/status index and partial overdue index
- [ ] T134 [US5] Implement task Pydantic schemas in `backend/app/modules/tasks/schemas.py` (TaskCreate, TaskUpdate, TaskStatusChange, TaskResponse, TaskListParams with overdue filter)
- [ ] T135 [US5] Implement task service in `backend/app/modules/tasks/service.py` (create with default to_do, get, list with filters including overdue flag, update with ownership check per SEC-008 assignee_id, status change with free movement + completed_at management, archive, audit events)
- [ ] T136 [US5] Implement task router in `backend/app/modules/tasks/router.py` per contracts/tasks.md
- [ ] T137 [US5] Register tasks router in `backend/app/main.py`
- [ ] T138 [US5] Add task factory to `backend/tests/factories.py` (TaskFactory)

### Backend Task Tests

- [ ] T139 [P] [US5] Implement task unit tests in `backend/tests/unit/test_task_service.py` (status transitions: skip forward, backward, reopen; completed_at set/cleared; overdue query; ownership transfer)
- [ ] T140 [US5] Implement task API tests in `backend/tests/api/test_tasks.py` (CRUD, status change, overdue filter, assignee filter, contact/deal link, ownership enforcement, tenant isolation)

### Frontend Task Feature

- [ ] T141 [US5] Implement task API functions in `frontend/src/lib/api/tasks.ts`
- [ ] T142 [US5] Implement TaskForm in `frontend/src/features/tasks/task-form.tsx` (title, description, due date, priority, assignee selector, optional contact/deal link, validation)
- [ ] T143 [US5] Implement TaskList in `frontend/src/features/tasks/task-list.tsx` (DataTable with overdue row indicator per red badge/highlight, filters: assigned-to-me, status, priority, due date range)
- [ ] T144 [US5] Implement TaskDetail in `frontend/src/features/tasks/task-detail.tsx` (all fields, linked contact/deal, status change buttons, edit mode)
- [ ] T145 [US5] Implement task pages in `frontend/src/app/tasks/` (page.tsx, new/page.tsx, [id]/page.tsx)
- [ ] T146 [US5] Add "Related Tasks" section to DealDetail in `frontend/src/features/deals/deal-detail.tsx`
- [ ] T147 [US5] Add "Related Tasks" section to ContactDetail in `frontend/src/features/contacts/contact-detail.tsx`

### Frontend Task Tests

- [ ] T148 [P] [US5] Implement TaskList component test in `frontend/tests/components/task-list.test.tsx` (overdue indicator rendering, filter behavior)
- [ ] T149 [US5] Implement E2E tasks test in `frontend/tests/e2e/tasks.spec.ts` (create → assign → change status → verify overdue indicator; axe-core)

**Checkpoint**: Full task management. Overdue tasks visually flagged. Related tasks appear on deal and contact detail pages. Free status movement works.

---

## Phase 7: US6 — Reporting Dashboard (Priority: P6)

**Goal**: Dashboard with precomputed metrics (contact count, deals by stage with values, open pipeline value, overdue task count), manual refresh, and proper zero-states.

**Independent Test**: Seed data and verify dashboard metrics match expected counts. Verify empty-state dashboard with new tenant.

### Backend Reporting Module

- [ ] T150 [US6] Implement DashboardSnapshot SQLAlchemy model in `backend/app/modules/reporting/models.py` per data-model.md (tenant_id UNIQUE, computed_at, data JSONB)
- [ ] T151 [US6] Create Alembic migration for dashboard_snapshots table
- [ ] T152 [US6] Implement reporting Pydantic schemas in `backend/app/modules/reporting/schemas.py` (DashboardResponse with contacts_count, deals_by_stage, open_pipeline_value, overdue_tasks_count, computed_at)
- [ ] T153 [US6] Implement reporting service in `backend/app/modules/reporting/service.py` (read latest snapshot for tenant)
- [ ] T154 [US6] Implement reporting router in `backend/app/modules/reporting/router.py` per contracts/reporting.md (GET /reporting/dashboard)
- [ ] T155 [US6] Register reporting router in `backend/app/main.py`
- [ ] T156 [US6] Implement Celery Beat scheduled task in `backend/app/workers/scheduled.py` (precompute_dashboard_metrics: iterate active tenants, compute aggregates, upsert DashboardSnapshot per FR-018)
- [ ] T157 [US6] Configure Celery Beat schedule in `backend/app/workers/celery_app.py` (run precompute every 5 minutes)

### Backend Reporting Tests

- [ ] T158 [P] [US6] Implement dashboard precompute unit test in `backend/tests/unit/test_dashboard_precompute.py` (correct aggregation: contact count, deals by stage with values, open pipeline, overdue tasks)
- [ ] T159 [US6] Implement reporting API tests in `backend/tests/api/test_reporting.py` (dashboard returns snapshot, empty tenant returns zeros, tenant isolation)

### Frontend Dashboard Feature

- [ ] T160 [US6] Implement reporting API functions in `frontend/src/lib/api/reporting.ts` (getDashboard)
- [ ] T161 [US6] Implement MetricCard in `frontend/src/features/dashboard/metric-card.tsx` (label, value, optional trend indicator, zero-state variant)
- [ ] T162 [US6] Implement PipelineSummary in `frontend/src/features/dashboard/pipeline-summary.tsx` (stage bars with count + total value)
- [ ] T163 [US6] Replace empty dashboard shell in `frontend/src/app/dashboard/page.tsx` with full dashboard: MetricCard grid (contacts, open pipeline, overdue tasks), PipelineSummary, Refresh button, computed_at timestamp, zero-states per widget

### Frontend Dashboard Tests

- [ ] T164 [P] [US6] Implement MetricCard component test in `frontend/tests/components/metric-card.test.tsx` (value rendering, zero-state)
- [ ] T165 [US6] Implement E2E dashboard test in `frontend/tests/e2e/dashboard.spec.ts` (verify metrics match seeded data → refresh → empty state; viewer sees metrics but no edit actions; axe-core)

**Checkpoint**: Dashboard displays accurate precomputed metrics. Zero-states render for empty tenants. Refresh loads latest snapshot. All roles can view.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, verification, and deployment readiness per plan Phase 4.

- [ ] T166 [P] Implement full RBAC matrix integration test in `backend/tests/api/test_rbac_matrix.py` (every operation × role combination per SEC-001; SC-006)
- [ ] T167 [P] Implement comprehensive tenant isolation test suite in `backend/tests/api/test_tenant_isolation_full.py` (all entity endpoints: contacts, companies, deals, tasks, reporting, audit; SC-005)
- [ ] T168 [P] Implement audit log verification tests in `backend/tests/integration/test_audit_completeness.py` (all AUD-001 actions produce AUD-002 records; SC-010)
- [ ] T169 [P] Run axe-core accessibility audit on all frontend pages via Playwright and fix violations (SC-009)
- [ ] T170 [P] UX consistency pass: verify empty states, loading indicators, error messages on every list/detail/dashboard view (SC-008)
- [ ] T171 [P] Verify all destructive actions (archive, close-as-lost) show ConfirmDialog (FR-013)
- [ ] T172 [P] Input validation audit: verify SEC-003 constraints (string lengths, email format, currency, date, enum values) on all API endpoints
- [ ] T173 [P] Rate limiting verification on auth endpoints (SEC-007)
- [ ] T174 [P] Dependency vulnerability scan: `pip-audit` (backend) + `npm audit` (frontend)
- [ ] T175 Performance verification: seed 10k records per entity, measure list endpoint p95 (SC-003), pipeline board TTI (SC-004), dashboard refresh (SC-007)
- [ ] T176 Create production Docker Compose profile in `docker-compose.prod.yml` with environment variable documentation
- [ ] T177 Add /health and /ready endpoint tests in `backend/tests/api/test_health.py`
- [ ] T178 Create project README.md with setup instructions, architecture overview, development workflow, and quickstart reference
- [ ] T179 Spec traceability check: verify all tasks map to spec FRs/SCs; no unspecified work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational / US1 (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US2 Contacts (Phase 3)**: Depends on Phase 2 completion
- **US3 Companies (Phase 4)**: Depends on Phase 2; benefits from Phase 3 shared data components but independently testable
- **US4 Deals (Phase 5)**: Depends on Phase 2; requires contacts and companies tables to exist (Phases 3–4)
- **US5 Tasks (Phase 6)**: Depends on Phase 2; optionally links to contacts/deals (Phases 3–5)
- **US6 Dashboard (Phase 7)**: Depends on Phase 2; reads from all entity tables for aggregation (Phases 3–6)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation — no dependencies on other stories
- **US2 (P2)**: Can start after US1 — introduces shared data components (DataTable, Pagination, SearchInput, FilterBar)
- **US3 (P3)**: Can start after US1 — reuses shared data components from US2; companies table needed for contact.company_id FK (can be created independently)
- **US4 (P4)**: Requires contacts + companies tables — start after US2 + US3
- **US5 (P5)**: Can start after US1 for standalone tasks; contact_id/deal_id links require US2 + US4
- **US6 (P6)**: Requires all entity tables populated — start after US4 + US5

### Within Each User Story

- Backend models → backend service → backend router → backend tests
- Frontend API client → frontend components → frontend pages → frontend tests
- Backend and frontend for same story can run in parallel
- E2E tests run last (require both backend and frontend)

### Parallel Opportunities

- All Setup tasks marked [P] run in parallel (T002–T012)
- Backend and frontend foundational work run in parallel (T014–T043 ∥ T044–T068)
- Shared UI components (T049–T063) all run in parallel
- Within each story: backend module and frontend feature can develop in parallel
- US2 and US3 backend modules can develop in parallel (different tables/files)
- All Phase 8 verification tasks marked [P] run in parallel

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational / US1
3. **STOP and VALIDATE**: User can log in, see app shell, RBAC works
4. Deploy/demo if ready

### Incremental Delivery

1. Setup + US1 → Login + app shell + tenant isolation (MVP foundation)
2. Add US2 → Contact management + shared data components
3. Add US3 → Company management + bidirectional associations
4. Add US4 → Deal pipeline with board + drag-and-drop
5. Add US5 → Task management with overdue indicators
6. Add US6 → Reporting dashboard with precomputed metrics
7. Hardening → All SC-001–SC-010 verified, deployment-ready

### Parallel Team Strategy

With multiple developers after Phase 2:
- Developer A: US2 (contacts) → US4 (deals)
- Developer B: US3 (companies) → US5 (tasks)
- Developer C: US6 (dashboard, after entities exist)
- All: Phase 8 (hardening)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable at its checkpoint
- Backend tests use Celery eager mode for synchronous audit writes in test
- E2E tests include axe-core accessibility checks per SC-009
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
