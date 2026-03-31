# Audit API Contracts

**Base path:** `/api/audit`

**Auth:** All endpoints require `Authorization: Bearer <access_token>`.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Malformed or invalid query parameters |
| 401 | Missing or invalid Bearer token |
| 403 | Not `admin` |
| 404 | Single-entry route not found (if added later) |
| 409 | Conflict (if applicable) |
| 422 | Invalid date range or filter values |

---

## GET /api/audit

**Description:** Paginated audit log for the tenant. **Admin only.**

| Query param | Type | Required | Notes |
|-------------|------|----------|--------|
| `actor_id` | uuid | no | User who performed the action |
| `entity_type` | string | no | e.g. `contact`, `deal` |
| `entity_id` | uuid | no | |
| `action_type` | string | no | e.g. `create`, `update`, `delete` |
| `from_date` | string (ISO 8601) | no | Inclusive start |
| `to_date` | string (ISO 8601) | no | Inclusive end |
| `page` | integer | no | 1-based |
| `page_size` | integer | no | |

**Response:** `200 OK` — paginated list envelope with audit entries as `items`.

```json
{
  "items": [
    {
      "id": "uuid",
      "tenant_id": "uuid",
      "actor_id": "uuid",
      "entity_type": "deal",
      "entity_id": "uuid",
      "action_type": "update",
      "metadata": {},
      "created_at": "2026-03-31T11:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

| Status | Condition |
|--------|-----------|
| 400 | Malformed or invalid query parameters |
| 401 | Unauthenticated |
| 403 | Not `admin` |
| 422 | Invalid date range or filter values |

**Roles:** `admin` only.
