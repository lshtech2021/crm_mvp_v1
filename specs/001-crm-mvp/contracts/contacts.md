# Contacts API Contracts

**Base path:** `/api/contacts`

**Auth:** All endpoints require `Authorization: Bearer <access_token>`. All operations are scoped to the token’s `tenant_id`.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or invalid request syntax |
| 401 | Missing or invalid Bearer token |
| 403 | Wrong role or not resource owner (SEC-008 for rep) |
| 404 | Resource not found or not in tenant |
| 409 | Conflict (e.g. duplicate unique field, if enforced) |
| 422 | Validation / unprocessable entity |

---

## POST /api/contacts

**Description:** Create a contact in the current tenant.

| Request body | Type | Required | Notes |
|--------------|------|----------|--------|
| `first_name` | string | yes | |
| `last_name` | string | yes | |
| `email` | string | no | |
| `phone` | string | no | |
| `company_id` | string (uuid) | no | Must belong to same tenant |
| … | | | Additional fields per data model |

**Response:** `201 Created` — created contact resource (JSON object including `id`, `tenant_id`, `created_by`, timestamps, etc.).

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "first_name": "Alex",
  "last_name": "Rivera",
  "email": "alex@example.com",
  "phone": null,
  "company_id": "uuid",
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
| 404 | Referenced `company_id` not found in tenant |
| 422 | Validation failed |

**Roles:** `admin`, `manager`, `rep`.

---

## GET /api/contacts

**Description:** List contacts with search, filters, and pagination.

| Query param | Type | Required | Notes |
|-------------|------|----------|--------|
| `q` | string | no | Search (implementation-defined fields) |
| `company_id` | uuid | no | Filter by company |
| `archived` | boolean | no | Default: exclude archived unless `true` |
| `page` | integer | no | 1-based; default 1 |
| `page_size` | integer | no | Default and max per implementation |

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
| 422 | Invalid filter or pagination values |

**Roles:** `admin`, `manager`, `rep`, `viewer` (tenant-scoped).

---

## GET /api/contacts/:id

**Description:** Get a single contact by ID within the tenant.

**Path params:** `id` (uuid).

**Response:** `200 OK` — contact object (same shape as create response).

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Wrong tenant or role denied |
| 404 | Contact not found |

**Roles:** `admin`, `manager`, `rep`, `viewer`.

---

## PUT /api/contacts/:id

**Description:** Update a contact. **SEC-008:** `rep` may update only if `created_by` equals current user ID.

**Path params:** `id` (uuid).

| Request body | Type | Required |
|--------------|------|----------|
| … | | Partial update fields per data model |

**Response:** `200 OK` — updated contact object.

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON |
| 401 | Unauthenticated |
| 403 | Role not allowed, or rep not owner (`created_by`) |
| 404 | Contact not found |
| 422 | Validation failed |

**Roles:** `admin`, `manager`; `rep` if owner per SEC-008.

---

## POST /api/contacts/:id/archive

**Description:** Archive a contact (soft archive).

**Path params:** `id` (uuid).

**Request body:** None (or empty object).

**Response:** `200 OK` — archived contact representation.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Not admin or manager |
| 404 | Contact not found |
| 422 | Already archived or invalid state transition |

**Roles:** `admin`, `manager` only.

---

## POST /api/contacts/:id/unarchive

**Description:** Restore an archived contact.

**Path params:** `id` (uuid).

**Request body:** None (or empty object).

**Response:** `200 OK` — unarchived contact.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Not admin or manager |
| 404 | Contact not found |
| 422 | Not archived |

**Roles:** `admin`, `manager` only.
