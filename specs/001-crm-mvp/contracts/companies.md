# Companies API Contracts

**Base path:** `/api/companies`

**Auth:** All endpoints require `Authorization: Bearer <access_token>`. All operations are scoped to the token’s `tenant_id`.

**Pattern:** Same CRUD + archive/unarchive pattern as contacts, with industry filter and archive guard when active deals exist.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or invalid request syntax |
| 401 | Missing or invalid Bearer token |
| 403 | Wrong role or not resource owner (SEC-008 for rep) |
| 404 | Resource not found or not in tenant |
| 409 | Archive blocked: active deals exist |
| 422 | Validation / unprocessable entity |

---

## POST /api/companies

**Description:** Create a company in the current tenant.

| Request body | Type | Required | Notes |
|--------------|------|----------|--------|
| `name` | string | yes | |
| `industry` | string | no | |
| … | | | Additional fields per data model |

**Response:** `201 Created` — company resource.

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "Acme Corp",
  "industry": "software",
  "archived": false,
  "created_by": "uuid",
  "created_at": "2026-03-31T12:00:00Z",
  "updated_at": "2026-03-31T12:00:00Z"
}
```

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON |
| 401 | Unauthenticated |
| 403 | Role not admin, manager, or rep |
| 422 | Validation failed |

**Roles:** `admin`, `manager`, `rep`.

---

## GET /api/companies

**Description:** List companies with filters and pagination.

| Query param | Type | Required | Notes |
|-------------|------|----------|--------|
| `q` | string | no | Search |
| `industry` | string | no | Filter by industry |
| `archived` | boolean | no | Filter archived state |
| `page` | integer | no | 1-based |
| `page_size` | integer | no | |

**Response:** `200 OK`

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "total_pages": 0
}
```

| Status | Condition |
|--------|-----------|
| 400 | Invalid query parameters |
| 401 | Unauthenticated |
| 403 | Unauthorized for tenant |
| 422 | Invalid filter or pagination |

**Roles:** `admin`, `manager`, `rep`.

---

## GET /api/companies/:id

**Description:** Get a single company by ID.

**Path params:** `id` (uuid).

**Response:** `200 OK` — company object.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Wrong tenant or role denied |
| 404 | Company not found |

**Roles:** `admin`, `manager`, `rep`.

---

## PUT /api/companies/:id

**Description:** Update a company. **SEC-008:** `rep` may update only if `created_by` equals current user ID.

**Path params:** `id` (uuid).

| Request body | Type | Required |
|--------------|------|----------|
| … | | Partial update per data model |

**Response:** `200 OK` — updated company.

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON |
| 401 | Unauthenticated |
| 403 | Wrong role or rep not owner |
| 404 | Company not found |
| 422 | Validation failed |

**Roles:** `admin`, `manager`; `rep` if owner per SEC-008.

---

## POST /api/companies/:id/archive

**Description:** Archive a company. **Blocked if the company has active (non-closed) deals** — returns 409.

**Path params:** `id` (uuid).

**Request body:** None (or empty object).

**Response:** `200 OK` — archived company.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Not admin or manager |
| 404 | Company not found |
| 409 | Active deals exist for this company |
| 422 | Already archived or invalid state |

**Roles:** `admin`, `manager` only.

---

## POST /api/companies/:id/unarchive

**Description:** Restore an archived company.

**Path params:** `id` (uuid).

**Request body:** None (or empty object).

**Response:** `200 OK` — unarchived company.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Not admin or manager |
| 404 | Company not found |
| 422 | Not archived |

**Roles:** `admin`, `manager` only.
