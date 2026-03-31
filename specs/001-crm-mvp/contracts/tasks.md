# Tasks API Contracts

**Base path:** `/api/tasks`

**Auth:** All endpoints require `Authorization: Bearer <access_token>`. All operations are scoped to the token’s `tenant_id`.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or invalid request syntax |
| 401 | Missing or invalid Bearer token |
| 403 | Wrong role or rep not assignee (SEC-008 on update) |
| 404 | Task or reference not found in tenant |
| 409 | Conflict if applicable |
| 422 | Validation / unprocessable entity |

---

## POST /api/tasks

**Description:** Create a task.

| Request body | Type | Required | Notes |
|--------------|------|----------|--------|
| `title` | string | yes | |
| `assignee_id` | string (uuid) | no | User in tenant |
| `status` | string | no | Default per workflow |
| `priority` | string | no | |
| `due_date` | string (date/datetime) | no | |
| `contact_id` | string (uuid) | no | |
| `deal_id` | string (uuid) | no | |
| … | | | Per data model |

**Response:** `201 Created` — task resource.

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "title": "Follow up",
  "assignee_id": "uuid",
  "status": "open",
  "priority": "normal",
  "due_date": "2026-04-01",
  "contact_id": null,
  "deal_id": "uuid",
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
| 403 | Role not allowed |
| 404 | Referenced contact, deal, or assignee not in tenant |
| 422 | Validation failed |

**Roles:** `admin`, `manager`, `rep` (per tenant policy).

---

## GET /api/tasks

**Description:** List tasks with filters and pagination.

| Query param | Type | Required | Notes |
|-------------|------|----------|--------|
| `assignee_id` | uuid | no | |
| `status` | string | no | |
| `priority` | string | no | |
| `due_date_from` | string | no | Inclusive |
| `due_date_to` | string | no | Inclusive |
| `contact_id` | uuid | no | |
| `deal_id` | uuid | no | |
| `archived` | boolean | no | |
| `overdue` | boolean | no | When `true`, filter to tasks past `due_date` and not in terminal “done” state (exact semantics per implementation) |
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
| 422 | Invalid filter or date range |

**Roles:** `admin`, `manager`, `rep`.

---

## GET /api/tasks/:id

**Description:** Get a single task.

**Path params:** `id` (uuid).

**Response:** `200 OK` — task object.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Access denied |
| 404 | Task not found |

**Roles:** `admin`, `manager`, `rep`.

---

## PUT /api/tasks/:id

**Description:** Update a task. **SEC-008:** `rep` may update only if current user is the **assignee** (`assignee_id`).

**Path params:** `id` (uuid).

| Request body | Type | Required |
|--------------|------|----------|
| … | | Partial update per data model |

**Response:** `200 OK` — updated task.

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON |
| 401 | Unauthenticated |
| 403 | Wrong role or rep not assignee |
| 404 | Task not found |
| 422 | Validation failed |

**Roles:** `admin`, `manager`; `rep` if assignee per SEC-008.

---

## POST /api/tasks/:id/status

**Description:** Change task status. **Free movement** between all defined statuses.

**Path params:** `id` (uuid).

| Request body | Type | Required |
|--------------|------|----------|
| `status` | string | yes | |

**Response:** `200 OK` — task with new `status`.

| Status | Condition |
|--------|-----------|
| 400 | Missing `status` |
| 401 | Unauthenticated |
| 403 | Not allowed to change this task |
| 404 | Task not found |
| 422 | Unknown or invalid `status` value |

**Roles:** Per tenant policy (typically same as update: admin, manager; rep if assignee).

---

## POST /api/tasks/:id/archive

**Description:** Archive a task.

**Path params:** `id` (uuid).

**Request body:** None (or empty object).

**Response:** `200 OK` — archived task.

| Status | Condition |
|--------|-----------|
| 401 | Unauthenticated |
| 403 | Not admin or manager |
| 404 | Task not found |
| 422 | Already archived |

**Roles:** `admin`, `manager` only.
