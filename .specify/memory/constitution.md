<!--
Sync Impact Report
- Version change: 2.0.0 → 2.1.0
- Modified principles:
  - I. Code Quality & Maintainable Architecture — added async/background job justification rule
  - VII. Spec-Driven Development & Incremental Delivery — added frontend-backend spec alignment rule
- Added sections:
  - Non-Functional Standards: Asynchronous Infrastructure bullet
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md — ✅ updated (Constitution Check: async justification + cross-layer alignment)
  - .specify/templates/spec-template.md — ✅ no change (already covers cross-layer requirements)
  - .specify/templates/tasks-template.md — ✅ no change (async justification is plan-level, not task-level)
  - .specify/templates/checklist-template.md — ✅ no change (generic)
  - .specify/templates/agent-file-template.md — ✅ no change (generic)
  - .specify/templates/commands/*.md — ⚠ not present (no files to update)
- Follow-up TODOs: None
-->

# CRM MVP Constitution

## Core Principles

### I. Code Quality & Maintainable Architecture

- All merged code MUST pass the project's linting and formatting gates;
  CI MUST reject violations.
- Public surfaces and critical paths MUST follow established naming,
  structure, and error-handling conventions; new patterns MUST include
  a short rationale in the plan or PR.
- Dead code, commented-out features, and disabled behavior MUST NOT
  land on the default branch without a tracked removal issue.
- New abstractions MUST be justified when they add indirection; use
  the plan's Complexity Tracking when a gate would otherwise be
  violated.
- Architecture MUST remain modular: clear separation between layers
  (API, service, data access, presentation) with explicit dependency
  direction. Circular dependencies MUST NOT be introduced.
- Shared utilities and cross-cutting concerns MUST be extracted into
  well-defined modules rather than duplicated across features.
- Asynchronous workflows and background job infrastructure MUST NOT
  be introduced without documented product or operational
  justification in the plan or PR; synchronous request-response
  MUST be the default execution model.

**Rationale**: Predictable structure, enforced style, and modular
architecture reduce defects, review load, and onboarding cost as the
CRM scales across tenants and teams. Defaulting to synchronous
execution keeps the system debuggable and prevents premature
infrastructure complexity.

### II. Testing Rigor

- All critical user flows MUST have unit, integration, and end-to-end
  test coverage appropriate to risk and architectural boundaries.
- Behavior tied to acceptance criteria MUST be covered by automated
  tests; untested acceptance criteria MUST NOT be considered complete.
- Regressions MUST be reproduced with a failing test before the fix
  merges, when feasible.
- Pure logic MUST favor fast unit tests; I/O and integration
  boundaries MUST have integration or contract tests when the feature
  crosses them.
- End-to-end tests MUST cover the primary happy path and critical
  error paths for each user-facing flow.
- Test names MUST describe behavior, not implementation; flaky tests
  MUST be fixed or explicitly quarantined with an owner and deadline.

**Rationale**: Multi-layered test coverage encodes expectations at
every boundary, prevents repeat failures, and catches the integration
defects that unit tests alone miss.

### III. Multi-Tenant Isolation

- Every data query and mutation MUST be scoped to the current tenant
  context; unscoped queries against tenant-owned data MUST NOT exist
  in application code.
- Tenant context MUST be established at the request boundary (e.g.,
  middleware or gateway) and propagated through the call chain without
  relying on application code to manually attach it per query.
- Cross-tenant data access MUST be impossible through normal API
  operations; any administrative cross-tenant capability MUST require
  explicit super-admin authorization and audit logging.
- Background jobs, scheduled tasks, and event handlers MUST carry and
  enforce tenant context with the same rigor as synchronous request
  paths.
- Tenant-specific configuration, feature flags, and resource limits
  MUST be isolated; one tenant's settings MUST NOT affect another.

**Rationale**: In a multi-tenant SaaS, data leakage between tenants
is a critical security and compliance failure. Systematic isolation
at the architecture level prevents accidental cross-tenant exposure
regardless of individual developer awareness.

### IV. Security & Role-Based Authorization

- Every protected operation (API endpoint, service method, UI action)
  MUST enforce role-based authorization checks; authorization MUST NOT
  be bypassed by direct URL access, API manipulation, or client-side
  guards alone.
- Authentication MUST be required for all non-public endpoints;
  session and token management MUST follow current best practices
  (secure cookies, short-lived tokens, refresh rotation).
- All user input MUST be validated and sanitized at the boundary;
  parameterized queries or equivalent MUST prevent injection attacks.
- Secrets, API keys, and credentials MUST NOT appear in source code,
  logs, or client-side bundles; they MUST be managed through
  environment configuration or a secrets manager.
- Dependency vulnerability scanning MUST be part of the CI pipeline;
  known critical or high-severity vulnerabilities MUST be addressed
  before merge or explicitly risk-accepted with justification.

**Rationale**: A CRM holds sensitive customer data across multiple
tenants. Defense-in-depth — authentication, authorization, input
validation, and dependency hygiene — is mandatory to protect against
both external attacks and internal mistakes.

### V. Accessibility & Predictable UX

- User-facing flows MUST reuse established patterns for navigation,
  forms, feedback (success, warning, error), empty states, and
  loading — unless the specification documents a deliberate deviation.
- User-visible errors MUST be actionable and consistent in tone;
  destructive actions MUST require confirmation using the product's
  standard confirmation pattern.
- Interactive UI MUST be keyboard-operable with logical focus order;
  controls MUST use semantic HTML (or platform equivalent). Target
  WCAG 2.1 Level AA for all applicable criteria.
- Color MUST NOT be the sole means of conveying information; contrast
  ratios MUST meet AA thresholds.
- Screen reader compatibility MUST be verified for critical flows;
  ARIA attributes MUST be used correctly when native semantics are
  insufficient.

**Rationale**: Consistency reduces training cost and support burden.
Accessibility is a legal and ethical obligation that prevents
exclusion of users who rely on assistive technology.

### VI. Auditability

- Key business actions (create, update, delete of business entities;
  permission changes; authentication events; tenant administration)
  MUST produce an immutable audit record including: actor identity,
  tenant, timestamp, action performed, and outcome.
- Audit records MUST NOT be deletable or modifiable through normal
  application operations; retention policy MUST be documented.
- Audit logging MUST NOT record secrets, passwords, or unnecessary
  PII; when PII is required for audit context, it MUST be identified
  and handled per the project's data-handling policy.
- Audit entries MUST be queryable by tenant, actor, time range, and
  action type to support compliance and incident investigation.

**Rationale**: A SaaS CRM managing customer data across tenants MUST
provide verifiable records of who did what and when for compliance,
dispute resolution, and security incident investigation.

### VII. Spec-Driven Development & Incremental Delivery

- Every feature MUST begin with a version-controlled specification
  that includes testable user scenarios, functional requirements, and
  measurable success criteria before implementation starts.
- Specifications MUST be stored alongside code in the repository
  (under `specs/`) and versioned through the same review process as
  source code.
- Features MUST be decomposed into independently testable increments
  (user stories) that each deliver demonstrable value; an increment
  MUST be verifiable without requiring completion of subsequent
  increments.
- CI quality gates MUST enforce: linting, formatting, type checking
  (where applicable), automated test passage, and build success.
  Merges to the default branch MUST NOT bypass these gates without
  explicit documented justification.
- Plans and task lists MUST trace back to specification requirements;
  implementation work without a corresponding spec requirement MUST
  be flagged and justified.
- Frontend and backend implementation changes MUST remain aligned
  with the approved specification; cross-layer deviations (e.g.,
  API contract changes without spec update, UI behavior diverging
  from acceptance scenarios) MUST be reconciled before merge.

**Rationale**: Spec-driven development prevents scope creep, ensures
shared understanding before investment, and creates a verifiable
chain from requirement to implementation. Requiring cross-layer
alignment prevents frontend and backend from drifting apart.
Incremental delivery reduces risk and enables early feedback.

### VIII. AI-Assisted Implementation Discipline

- AI-assisted implementation MUST operate within bounded task scopes
  defined by the current specification and task list; tasks MUST NOT
  expand beyond their stated scope without explicit approval.
- AI-generated code MUST preserve the project's architectural
  patterns, naming conventions, and dependency direction; deviations
  MUST be flagged for human review before merge.
- AI-assisted work MUST NOT invent requirements, features, or
  behaviors not present in the specification; if a gap is identified,
  it MUST be raised as a clarification rather than silently filled.
- AI-generated changes MUST be subject to the same review, testing,
  and CI gate standards as human-authored code; AI authorship MUST
  NOT lower the quality bar.

**Rationale**: AI accelerates implementation but can introduce drift
from specifications, architectural inconsistency, and phantom
requirements if not constrained. Bounded scopes and human oversight
keep AI contributions aligned with project intent.

## Non-Functional Standards

- **Linting & Formatting**: Enforce one agreed style per language in
  the codebase; CI MUST fail on violations.
- **Performance**: Each feature's plan and specification MUST state
  measurable performance targets (latency percentiles, throughput,
  time-to-interactive, or resource budgets) where user-facing or
  latency-sensitive behavior is involved. Merged changes MUST NOT
  regress documented targets without explicit approval and a
  migration plan.
- **Observability**: Errors and critical operations MUST emit
  structured, searchable logs suitable for production debugging
  without logging secrets or PII unnecessarily.
- **Dependencies**: New dependencies MUST be justified (security,
  maintenance, license impact) in the plan or PR when they materially
  affect the stack.
- **Data Integrity**: Database migrations MUST be backward-compatible
  or include a documented rollback strategy; data loss MUST NOT occur
  during schema changes.
- **Asynchronous Infrastructure**: Background job queues, event buses,
  and scheduled tasks MUST NOT be introduced unless the plan or PR
  documents a concrete product or operational need (e.g., long-running
  report generation, webhook delivery). When used, jobs MUST carry
  tenant context per Principle III and produce audit records per
  Principle VI where applicable.

## Development Workflow & Quality Gates

- **Specification**: Feature specs MUST include testable user
  scenarios, functional requirements, and measurable success criteria;
  UX, performance, security, tenant isolation, and auditability
  expectations MUST be stated where applicable.
- **Planning**: `plan.md` MUST include a Constitution Check before
  Phase 0 and MUST be re-checked after Phase 1 design; violations
  MUST use Complexity Tracking with justification.
- **Implementation**: Tasks MUST be grouped by user story with
  independent verification paths; test tasks MUST appear when the
  constitution or spec requires automated coverage. Tenant isolation,
  security authorization, and audit logging tasks MUST be included
  for features touching protected data or operations.
- **Review**: Reviewers MUST verify alignment with all Core Principles
  for the scope of the change, including tenant isolation, security
  enforcement, and auditability where applicable.
- **CI Gates**: The CI pipeline MUST enforce lint, format, type check,
  test suite passage, and dependency vulnerability scan. Merges MUST
  NOT proceed when gates fail.

## Governance

- This constitution supersedes informal or undocumented practices
  when they conflict.
- **Amendments**: Propose changes via pull request with rationale,
  updated version and dates, and synchronized updates to dependent
  templates under `.specify/templates/` where principles affect gates
  or task types.
- **Versioning**: `MAJOR` for incompatible governance or
  removal/redefinition of principles; `MINOR` for new principles or
  materially expanded guidance; `PATCH` for clarifications and
  non-semantic edits.
- **Compliance**: Feature plans, specifications, and task lists MUST
  remain consistent with this document; periodic review MUST occur
  before major releases or when tenant/security requirements change.
- **AI Compliance**: AI-assisted workflows MUST be audited against
  this constitution with the same rigor as human-driven workflows;
  AI-specific deviations MUST be documented and reviewed.

**Version**: 2.1.0 | **Ratified**: 2026-03-31 | **Last Amended**: 2026-03-31
