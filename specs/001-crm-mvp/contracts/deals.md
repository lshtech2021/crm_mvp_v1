# Deals API Contracts

**Base path:** `/api/deals`

**Auth:** All endpoints require `Authorization: Bearer <access_token>`. All operations are scoped to the token’s `tenant_id`.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or invalid request syntax |
| 401 | Missing or invalid Bearer token |
| 403 | Wrong role or not permitted on resource |
| 404 | Deal or reference not found in tenant |
| 409 | Optimistic concurrency conflict, illegal stage/close transition |
| 422 | Validation / unprocessable entity |

---

## POST /api/deals

**Description:** Create a deal. **Default:** stage = Qualification; **owner** = current authenticated user.

| Request body | Type | Required | Notes |
|--------------|------|----------|--------|
| `name` | string | yes | Deal name |
| `company_id` | string (uuid) | yes | FK to companies; tenant-scoped |
| `primary_contact_id` | string (uuid) | yes | FK to contacts; tenant-scoped |
| `value` | number | yes | Decimal, USD |
| … | | | Other fields per data model; `stage` / `owner_id` may be ignored or rejected if set |

**Response:** `201 Created` — deal resource including `version` (optimistic concurrency).

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "Enterprise license",
  "stage": "qualification",
  "value": 50000,
  "currency": "USD",
  "company_id": "uuid",
  "primary_contact_id": "uuid",
  "owner_id": "uuid",
  "archived": false,
  "version": 1,
  "created_at": "2026-03-31T12:00:00Z",
  "updated_at": "2026-03-31T12:00:00Z"
}
```

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON |
| 401 | Unauthenticated |
| 403 | Role not allowed |
| 404 | Referenced company or contact not in tenant |
| 422 | Validation failed |

**Roles:** Per tenant policy (typically `admin`, `manager`, `rep`).

---

## GET /api/deals

**Description:** List deals with filters and pagination.

| Query param | Type | Required | Notes |
|-------------|------|----------|--------|
| `stage` | string | no | Pipeline stage |
| `owner_id` | uuid | no | Filter by owner |
| `company_id` | uuid | no | Filter by company |
| `archived` | boolean | no | |
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
| 403 | Unauthorized |
| 422 | Invalid filters |

**Roles:** `admin`, `manager`, `rep` (tenant-scoped).

---

## GET /api/deals/:id

**Description:** Get a single deal with **embedded** company, primary contact, and owner details.

**Path params:** `id` (uuid).

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "Enterprise license",
  "stage": "proposal",
  "value": 50000,
  "company": { "id": "uuid", "name": "Acme Corp" },
  "primary_contact": { "id": "uuid", "first_name": "Alex", "last_name": "Rivera", "email": "alex@example.com" },
  "owner": { "id": "uuid", "email": "owner@example.com", "first_name": "Jane", "last_name": "Doe" },
  "version": 3,
  "archived": false,
  "created_at": "2026-03-31T12:00:00Z",
  "updated_at": "2026-03-31T12:05:00Z"
}
```

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Access denied |
| 404 | Deal not found |

**Roles:** `admin`, `manager`, `rep`.

---

## PUT /api/deals/:id

**Description:** Update a deal. **Requires `version`** for optimistic concurrency; mismatch returns **409**.

**Path params:** `id` (uuid).

| Request body | Type | Required |
|--------------|------|----------|
| `version` | integer | yes | Expected current version |
| … | | | Other updatable fields |

**Response:** `200 OK` — updated deal (incremented `version`).

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or missing `version` |
| 401 | Unauthenticated |
| 403 | Not allowed to update this deal |
| 404 | Deal not found |
| 409 | Version conflict (stale `version`) |
| 422 | Validation failed |

**Roles:** Per SEC-008 / tenant rules (admin, manager; rep if owner where applicable).

---

## POST /api/deals/:id/stage

**Description:** Change pipeline stage. **Open stages:** free movement among non-terminal open stages. **Closed stages (won/lost):** terminal — no further stage changes via this endpoint.

**Path params:** `id` (uuid).

| Request body | Type | Required |
|--------------|------|----------|
| `stage` | string | yes | Target stage |
| `version` | integer | yes | Optimistic concurrency |

**Response:** `200 OK` — deal with new `stage` and `version`.

| Status | Condition |
|--------|-----------|
| 400 | Missing `stage` or `version` |
| 401 | Unauthenticated |
| 403 | Not allowed |
| 404 | Deal not found |
| 409 | Version conflict or illegal transition (e.g. from terminal closed stage) |
| 422 | Unknown stage or invalid transition |

**Roles:** Per tenant policy.

---

## POST /api/deals/:id/close

**Description:** Close the deal as won or lost.

**Path params:** `id` (uuid).

| Request body | Type | Required | Notes |
|--------------|------|----------|--------|
| `outcome` | string | yes | `won` \| `lost` |
| `loss_reason` | string | no | Typically required when `outcome` is `lost` |
| `version` | integer | yes | Optimistic concurrency |

**Response:** `200 OK` — closed deal (terminal stage, outcome fields set).

| Status | Condition |
|--------|-----------|
| 400 | Malformed body |
| 401 | Unauthenticated |
| 403 | Not allowed |
| 404 | Deal not found |
| 409 | Version conflict or already closed |
| 422 | Invalid outcome or missing `loss_reason` when required |

**Roles:** Per tenant policy.

---

## POST /api/deals/:id/archive

**Description:** Archive a deal.

**Path params:** `id` (uuid).

**Request body:** None or optional `version` if implementation requires consistency.

**Response:** `200 OK` — archived deal.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Not admin or manager |
| 404 | Deal not found |
| 422 | Invalid archive state |

**Roles:** `admin`, `manager` only.

---

## GET /api/deals/pipeline

**Description:** Deals grouped by stage with **count** and **sum of values** per stage (tenant scope). Each stage group includes the deal rows used for aggregation (same fields as list items or a documented summary shape).

**Query params:** Optional filters aligned with list endpoint (implementation may support subset).

**Response:** `200 OK`

```json
{
  "by_stage": [
    {
      "stage": "qualification",
      "count": 2,
      "total_value": 100000,
      "items": [
        { "id": "uuid", "name": "Deal A", "value": 60000, "stage": "qualification" }
      ]
    },
    {
      "stage": "proposal",
      "count": 1,
      "total_value": 50000,
      "items": [
        { "id": "uuid", "name": "Deal B", "value": 50000, "stage": "proposal" }
      ]
    }
  ]
}
```

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Unauthorized |

**Roles:** `admin`, `manager`, `rep`.
