# Reporting API Contracts

**Base path:** `/api/reporting`

**Auth:** All endpoints require `Authorization: Bearer <access_token>`. Metrics are **tenant-wide** for the token’s `tenant_id`.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Invalid request |
| 401 | Missing or invalid Bearer token |
| 403 | Not allowed for tenant |
| 404 | Snapshot or resource not found (if keyed routes added later) |
| 409 | Conflict (if applicable) |
| 422 | Invalid optional parameters |

---

## GET /api/reporting/dashboard

**Description:** Precomputed dashboard snapshot for the tenant.

**Query params:** None (or optional `as_of` if implementation supports historical snapshots — not required for MVP).

**Response:** `200 OK`

```json
{
  "computed_at": "2026-03-31T12:00:00Z",
  "contacts_count": 1250,
  "deals_by_stage": [
    { "stage": "qualification", "count": 10, "total_value": 250000 },
    { "stage": "proposal", "count": 5, "total_value": 180000 }
  ],
  "open_pipeline_value": 430000,
  "overdue_tasks_count": 7
}
```

| Status | Condition |
|--------|-----------|
| 400 | Invalid optional query parameters |
| 401 | Unauthenticated |
| 403 | Unauthorized for tenant |
| 422 | Invalid query values |

**Roles:** All authenticated roles (`admin`, `manager`, `rep`) — tenant-wide read.
