# Feature Specification: CRM MVP

**Feature Branch**: `001-crm-mvp`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Build a custom multi-tenant CRM for an internal
business team. The product should allow authenticated users to manage contacts,
companies, deals in a sales pipeline, tasks, and basic reporting dashboards.
The CRM must support role-based access with at least admin, manager, rep, and
viewer roles. Every business record must belong to exactly one tenant, and
users must never be able to access data from another tenant."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Authentication & Tenant-Scoped Foundation (Priority: P1)

An internal team member opens the CRM, authenticates with email and password,
and lands on a tenant-scoped dashboard. The system establishes the user's
tenant context and role for the duration of the session. All subsequent data
access is automatically scoped to that tenant. Unauthenticated requests are
redirected to the login page. Users with different roles see the same login
flow but receive role-appropriate capabilities once inside.

**Why this priority**: Every other story depends on authenticated, tenant-
scoped sessions. Without this, no data access is safe or meaningful.

**Independent Test**: Can be verified by logging in as users from two
different tenants and confirming each sees only their own data (or an empty
state for a new tenant). Role assignment is visible on the user profile.

**Acceptance Scenarios**:

1. **Given** a registered user with valid credentials, **When** they submit
   the login form, **Then** the system authenticates them, establishes tenant
   context, and redirects to the dashboard.
2. **Given** an unauthenticated visitor, **When** they attempt to access any
   protected route, **Then** the system redirects to the login page with a
   return-URL preserved.
3. **Given** a user belonging to Tenant A, **When** they are authenticated,
   **Then** all API responses contain only Tenant A data; no Tenant B records
   are returned regardless of query parameters or URL manipulation.
4. **Given** a user with the "rep" role, **When** they access the system,
   **Then** they can perform rep-level actions but receive a 403 for
   admin-only operations.
5. **Given** an authenticated session, **When** the session token expires,
   **Then** the next request returns 401 and the UI redirects to login.

---

### User Story 2 — Contact Management (Priority: P2)

A sales rep creates a new contact with name, email, phone, company
association, and optional notes. They can later search for contacts by name
or email, filter by company or archive status, edit contact details, and
archive contacts they no longer need. Contacts can be associated with one
company and linked to deals. The contact list shows an empty state when no
contacts exist, loading indicators during fetch, and actionable error messages
on failure.

**Why this priority**: Contacts are the foundational entity in any CRM.
Every subsequent feature (companies, deals, tasks) relates back to contacts.

**Independent Test**: Can be verified by creating, searching, editing, and
archiving contacts as a rep; confirming list/detail views render correctly
including empty, loading, and error states.

**Acceptance Scenarios**:

1. **Given** an authenticated rep on the contacts page with no contacts,
   **When** the page loads, **Then** the system displays an empty state with
   a prompt to create the first contact.
2. **Given** the contact creation form, **When** the rep submits valid data
   (first name, last name, email), **Then** the system persists the contact
   scoped to the current tenant and displays a success notification.
3. **Given** a contact creation form, **When** the rep submits without a
   required field (first name or last name), **Then** the system displays
   inline validation errors and does not submit.
4. **Given** 50+ contacts exist, **When** the rep types a search query,
   **Then** the system filters results by name or email within 300ms of the
   last keystroke (debounced).
5. **Given** a contact detail view, **When** the rep clicks "Edit" and
   changes the email, **Then** the system validates the new email format,
   persists the change, and shows a success notification.
6. **Given** a contact detail view, **When** the rep clicks "Archive",
   **Then** the system prompts for confirmation, archives the contact on
   confirm, and removes it from the default list view (visible under an
   "Archived" filter).
7. **Given** a contact, **When** the rep associates it with a company,
   **Then** the contact's detail view shows the linked company and the
   company's detail view shows the contact.

---

### User Story 3 — Company Management (Priority: P3)

A sales rep creates a company with name, industry, website, and optional
notes. They can search companies by name, filter by industry, edit details,
and view all contacts and deals associated with a company. Companies cannot
be deleted if they have active deals; they can be archived.

**Why this priority**: Companies provide organizational context for contacts
and deals. Deals require a company association, so company management must
precede deal management.

**Independent Test**: Can be verified by creating companies, associating
contacts, and confirming the bidirectional association renders correctly.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the companies page with no companies,
   **When** the page loads, **Then** the system displays an empty state with
   a prompt to create the first company.
2. **Given** the company creation form, **When** the rep submits valid data
   (company name), **Then** the system persists the company scoped to the
   current tenant and displays a success notification.
3. **Given** a company with three associated contacts, **When** the user
   views the company detail page, **Then** all three contacts appear in an
   "Associated Contacts" section.
4. **Given** a company with an active (non-closed) deal, **When** the user
   attempts to archive, **Then** the system blocks the action and displays
   a message explaining active deals must be closed first.
5. **Given** the companies list, **When** the user filters by industry,
   **Then** only companies matching the selected industry are displayed.

---

### User Story 4 — Deal Pipeline Management (Priority: P4)

A sales rep creates a deal with a name, value, expected close date, and
associates it with a company and a primary contact. The deal is assigned to
an owner (defaults to the creating rep). Deals move through defined pipeline
stages: Qualification → Proposal → Negotiation → Closed Won / Closed Lost.
Reps can drag deals between stages on a pipeline board view or change stage
from the deal detail page. Closing a deal as won or lost requires
confirmation and records the close date.

**Why this priority**: The deal pipeline is the core revenue-driving workflow.
It depends on contacts and companies already existing.

**Independent Test**: Can be verified by creating a deal, moving it through
each stage, and closing it. Pipeline board shows correct stage groupings.

**Acceptance Scenarios**:

1. **Given** the deal creation form, **When** the rep submits valid data
   (deal name, value, company, primary contact), **Then** the system creates
   the deal in "Qualification" stage, assigns the rep as owner, scopes it to
   the current tenant, and displays a success notification.
2. **Given** a deal in "Qualification" stage, **When** the rep moves it to
   "Proposal" (via board drag or detail page), **Then** the system updates
   the stage and records the stage-change timestamp.
3. **Given** a deal in "Negotiation" stage, **When** the rep closes it as
   "Won", **Then** the system prompts for confirmation, records the close
   date, sets status to "Closed Won", and the deal is no longer draggable
   on the board.
4. **Given** a deal in any open stage, **When** the rep closes it as "Lost",
   **Then** the system prompts for confirmation with an optional loss reason
   field, records the close date, and sets status to "Closed Lost".
5. **Given** the pipeline board view, **When** the page loads, **Then** deals
   are grouped by stage in columns; empty stages show a placeholder; the
   total value per stage is displayed in the column header.
6. **Given** a deal detail view, **When** the user views it, **Then** the
   associated company, primary contact, owner, current stage, value, and
   expected close date are all visible.

---

### User Story 5 — Task Management (Priority: P5)

A user creates a task with a title, description, due date, and priority.
Tasks can be assigned to any user within the same tenant. Tasks can be linked
to a contact or a deal (or both). Tasks have statuses: To Do → In Progress →
Done. Users can view their assigned tasks, filter by status or due date, and
mark tasks complete. Overdue tasks are visually flagged.

**Why this priority**: Tasks drive operational follow-up on contacts and
deals. They depend on the existence of contacts, companies, and deals but
are independently valuable for team coordination.

**Independent Test**: Can be verified by creating tasks, assigning them,
changing status, and confirming overdue visual indicators appear correctly.

**Acceptance Scenarios**:

1. **Given** the task creation form, **When** the user submits valid data
   (title, due date, assignee), **Then** the system persists the task scoped
   to the current tenant with status "To Do" and displays a success
   notification.
2. **Given** a task in "To Do" status, **When** the assignee changes it to
   "In Progress", **Then** the status updates and the change is visible in
   the task list.
3. **Given** a task with a due date in the past and status not "Done",
   **When** the task list loads, **Then** the task displays a visual overdue
   indicator (e.g., red badge or highlighted row).
4. **Given** a task linked to a deal, **When** the user views the deal
   detail page, **Then** the task appears in a "Related Tasks" section.
5. **Given** the task list, **When** the user filters by "assigned to me"
   and status "To Do", **Then** only matching tasks are displayed.
6. **Given** a task in "In Progress", **When** the user marks it "Done",
   **Then** the system records the completion timestamp and removes the
   overdue indicator if present.

---

### User Story 6 — Reporting Dashboard (Priority: P6)

A manager or admin views an MVP reporting dashboard that shows summary
metrics for their tenant: total contacts created (with a trend indicator
for the current period), deals grouped by pipeline stage with total value
per stage, total open pipeline value, and a count of overdue tasks. The
dashboard auto-refreshes or provides a manual refresh action. Viewers can
see the dashboard but cannot modify data from it.

**Why this priority**: Reporting provides visibility into CRM health but
depends on all prior entities (contacts, companies, deals, tasks) being
populated. It is the least blocking feature.

**Independent Test**: Can be verified by seeding data and confirming
dashboard metrics match expected counts and values. Empty-state dashboard
renders correctly with zero data.

**Acceptance Scenarios**:

1. **Given** an authenticated manager with tenant data, **When** they
   navigate to the dashboard, **Then** the system displays: contacts created
   count, deals by stage with values, open pipeline total, and overdue task
   count.
2. **Given** a new tenant with no data, **When** a user views the dashboard,
   **Then** each widget shows a zero-state (e.g., "No contacts yet") rather
   than broken or blank content.
3. **Given** the dashboard is loaded, **When** the user clicks "Refresh",
   **Then** the metrics update to reflect the latest data with a loading
   indicator during fetch.
4. **Given** a viewer-role user, **When** they access the dashboard, **Then**
   they can see all metrics but no "Create" or "Edit" actions are available.
5. **Given** three deals in "Proposal" stage with values $10k, $20k, $30k,
   **When** the dashboard loads, **Then** the "Proposal" stage widget shows
   count: 3, total value: $60,000.

---

### Edge Cases

- What happens when a user's tenant is deactivated mid-session? The system
  MUST terminate the session and return 403 on subsequent requests with a
  clear message.
- What happens when a contact is archived while linked to an open deal? The
  deal retains the association but the contact appears as "(Archived)" in
  deal views. The contact can be un-archived.
- What happens when a user attempts to create a contact with a duplicate
  email within the same tenant? The system MUST reject with a validation
  error identifying the duplicate.
- What happens when a deal's associated company is archived? The system
  blocks company archival if active deals exist (per US3 scenario 4).
- What happens when a task assignee is removed from the tenant? The task
  remains with assignee shown as "(Removed User)"; admins can reassign.
- What happens during concurrent stage changes on the same deal? The system
  MUST use optimistic concurrency (e.g., version field); the second update
  receives a conflict error prompting refresh.
- What happens when the API is unreachable during form submission? The UI
  MUST display an actionable error message ("Unable to save — check your
  connection and try again") and preserve form data.
- What happens when a search query returns zero results? The system MUST
  display a "No results found" message with a suggestion to adjust filters.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to register and authenticate with
  email and password.
- **FR-002**: System MUST establish tenant context from the authenticated
  user's tenant membership at the request boundary (middleware) and
  propagate it to all data-access operations.
- **FR-003**: System MUST support four roles: admin, manager, rep, viewer,
  with permissions enforced server-side on every protected operation.
- **FR-004**: System MUST allow CRUD operations on contacts (create, read,
  update, archive) with fields: first name, last name, email (unique per
  tenant), phone, company association, notes.
- **FR-005**: System MUST allow CRUD operations on companies with fields:
  name, industry, website, notes.
- **FR-006**: System MUST allow CRUD operations on deals with fields: name,
  value (currency), expected close date, pipeline stage, owner (user),
  company association, primary contact association.
- **FR-007**: System MUST enforce pipeline stages in order: Qualification →
  Proposal → Negotiation → Closed Won / Closed Lost. Deals MUST NOT move
  backward from a Closed state.
- **FR-008**: System MUST allow CRUD operations on tasks with fields: title,
  description, due date, priority (low/medium/high), status (to_do,
  in_progress, done), assignee (user), linked contact, linked deal.
- **FR-009**: System MUST display an MVP reporting dashboard with: contact
  count, deals by stage with total values, open pipeline value, overdue
  task count.
- **FR-010**: System MUST support search (by name, email) and filtering
  (by status, company, industry, stage, assignee, date range) on all list
  views.
- **FR-011**: System MUST display appropriate empty states, loading
  indicators, and actionable error messages for all user-facing views.
- **FR-012**: System MUST support association between entities: contacts ↔
  companies (many-to-one), contacts ↔ deals (one primary per deal),
  companies ↔ deals (one per deal), tasks → contacts (optional), tasks →
  deals (optional).
- **FR-013**: Destructive actions (archive, close-as-lost) MUST require
  user confirmation before execution.
- **FR-014**: System MUST support pagination on all list endpoints with a
  configurable page size (default 25, max 100).

### Tenant Isolation Requirements

- **TI-001**: Every business entity (contact, company, deal, task) MUST
  include a non-nullable tenant identifier. All queries MUST filter by the
  current tenant context.
- **TI-002**: Tenant context MUST be resolved from the authenticated user's
  token at the middleware layer; application code MUST NOT manually attach
  tenant IDs to queries.
- **TI-003**: API endpoints MUST NOT accept tenant ID as a client-supplied
  parameter; tenant ID MUST be derived server-side only.
- **TI-004**: Cross-tenant data access MUST be impossible through API
  manipulation, URL parameter injection, or ID enumeration.
- **TI-005**: Background jobs (if introduced) MUST carry explicit tenant
  context; tenant-less job execution MUST be rejected.

### Security & Authorization Requirements

- **SEC-001**: System MUST enforce the following role permissions:

  | Operation | Admin | Manager | Rep | Viewer |
  |-----------|-------|---------|-----|--------|
  | Create any entity | ✅ | ✅ | ✅ (own) | ❌ |
  | Read any entity | ✅ | ✅ | ✅ | ✅ |
  | Update any entity | ✅ | ✅ | ✅ (own) | ❌ |
  | Archive any entity | ✅ | ✅ | ❌ | ❌ |
  | Manage users/roles | ✅ | ❌ | ❌ | ❌ |
  | View reports | ✅ | ✅ | ✅ | ✅ |

- **SEC-002**: Authorization MUST be enforced server-side; client-side
  visibility controls MUST NOT be the sole enforcement mechanism.
- **SEC-003**: All user inputs MUST be validated at the API boundary:
  string length limits, email format, currency format, date format,
  and enumeration values.
- **SEC-004**: All database queries MUST use parameterized statements;
  raw string interpolation in queries MUST NOT exist.
- **SEC-005**: Passwords MUST be hashed with a strong algorithm (bcrypt
  or argon2); plaintext passwords MUST NOT be stored or logged.
- **SEC-006**: Authentication tokens MUST be short-lived (configurable,
  default 15 minutes for access tokens) with refresh token rotation.
- **SEC-007**: API rate limiting MUST be applied to authentication
  endpoints to prevent brute-force attacks.

### Audit Requirements

- **AUD-001**: The following actions MUST produce audit records: contact
  create/update/archive, company create/update/archive, deal
  create/update/stage-change/close, task create/update/status-change,
  user login/logout, role change.
- **AUD-002**: Each audit record MUST include: actor ID, actor role,
  tenant ID, timestamp (UTC), action type, entity type, entity ID,
  and a summary of changed fields (old value → new value for updates).
- **AUD-003**: Audit records MUST be append-only; no application-level
  operation MUST allow deletion or modification of audit entries.
- **AUD-004**: Audit records MUST be queryable by tenant, actor, entity
  type, action type, and time range.
- **AUD-005**: Audit logging MUST NOT include password values, full
  authentication tokens, or other secrets. Email addresses and names
  in audit context are acceptable as they identify the business action.

### Key Entities

- **Tenant**: Represents an isolated organizational unit. Key attributes:
  name, slug (unique), status (active/deactivated), created_at.
- **User**: An authenticated person belonging to exactly one tenant. Key
  attributes: email (unique globally), password hash, first name, last
  name, role (admin/manager/rep/viewer), tenant_id, status (active/
  deactivated).
- **Contact**: A person the business interacts with. Key attributes: first
  name, last name, email (unique per tenant), phone, notes, company_id
  (optional FK), tenant_id, archived (boolean), created_by, updated_at.
- **Company**: A business organization. Key attributes: name, industry,
  website, notes, tenant_id, archived (boolean), created_by, updated_at.
- **Deal**: A sales opportunity. Key attributes: name, value (decimal),
  expected_close_date, stage (enum: qualification/proposal/negotiation/
  closed_won/closed_lost), close_date, loss_reason, owner_id (FK to User),
  company_id (FK), primary_contact_id (FK), tenant_id, created_by,
  version (for optimistic concurrency), updated_at.
- **Task**: A follow-up action item. Key attributes: title, description,
  due_date, priority (low/medium/high), status (to_do/in_progress/done),
  assignee_id (FK to User), contact_id (optional FK), deal_id (optional
  FK), tenant_id, completed_at, created_by, updated_at.
- **AuditLog**: An immutable record of a business action. Key attributes:
  actor_id, actor_role, tenant_id, timestamp, action_type, entity_type,
  entity_id, changes (JSON: old/new values), ip_address.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authenticated user can complete the full contact lifecycle
  (create → search → edit → archive) in under 2 minutes on first use.
- **SC-002**: A rep can create a deal and move it through all pipeline
  stages to "Closed Won" in under 3 minutes.
- **SC-003**: API list endpoints return paginated results within 500ms at
  p95 for datasets up to 10,000 records per tenant.
- **SC-004**: The pipeline board view renders with up to 200 visible deals
  with time-to-interactive under 2 seconds.
- **SC-005**: A user from Tenant A can never retrieve, modify, or infer
  the existence of Tenant B's data through any API operation — verified
  by automated cross-tenant isolation tests.
- **SC-006**: All RBAC rules (SEC-001 matrix) pass automated integration
  tests covering every operation × role combination.
- **SC-007**: Dashboard metrics are accurate within 1 second of the last
  committed transaction when manually refreshed.
- **SC-008**: Empty states, loading indicators, and error messages are
  present on every list view, detail view, and dashboard widget — verified
  by UI test or manual checklist.
- **SC-009**: All interactive elements are keyboard-navigable and critical
  flows pass axe-core automated accessibility checks (WCAG 2.1 AA).
- **SC-010**: Audit log captures all actions listed in AUD-001 with
  complete record structure per AUD-002 — verified by integration tests.

## Assumptions

- Users access the CRM via modern desktop browsers (Chrome, Firefox, Edge,
  Safari — latest two versions). Native mobile app is out of scope for MVP.
- Authentication uses email/password with JWT tokens. SSO/OAuth is deferred
  to a future phase.
- Pipeline stages are system-defined for MVP (Qualification → Proposal →
  Negotiation → Closed Won / Closed Lost). Tenant-configurable stages are
  deferred.
- Currency is displayed in USD for MVP. Multi-currency support is deferred.
- A single-database, shared-schema multi-tenancy model with row-level
  tenant scoping is assumed (tenant_id on every business table). Schema-
  per-tenant is not required for MVP scale.
- User registration and tenant provisioning are admin-only operations for
  MVP (no self-service signup).
- File attachments (e.g., on contacts or deals) are out of scope for MVP.
- Email integration (sending/receiving from within the CRM) is out of scope.
- Notification system (in-app or email notifications for task assignments,
  deal changes) is out of scope for MVP.
- The system will be deployed as a single web application (monolith or
  modular monolith); microservice decomposition is deferred.
- Data import/export (CSV, bulk operations) is out of scope for MVP.
- Audit log viewer UI is out of scope for MVP; logs are queryable via API
  or direct database access for administrators.
