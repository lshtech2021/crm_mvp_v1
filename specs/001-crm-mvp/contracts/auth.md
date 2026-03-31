# Auth API Contracts

**Base path:** `/api/auth`

**Auth:** All endpoints require `Authorization: Bearer <access_token>` except `POST /login` and `POST /refresh`. `POST /logout` and `GET /me` require a valid Bearer token.

**Rate limits:** `POST /login` — 10 requests/minute per client identity (e.g. IP + email bucket). `POST /refresh` — 5 requests/minute per client identity.

**Standard errors (when applicable):**

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or invalid request syntax |
| 401 | Unauthenticated or invalid credentials / token |
| 403 | Authenticated but action forbidden |
| 404 | Resource not found (rare on auth routes) |
| 409 | Conflict (rare on auth routes) |
| 422 | Validation / semantic errors |
| 429 | Rate limit exceeded |

---

## POST /api/auth/login

**Description:** Exchange credentials for access and refresh tokens.

| Request body | Type | Required |
|--------------|------|----------|
| `email` | string | yes |
| `password` | string | yes |

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "admin",
    "tenant_id": "uuid"
  }
}
```

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or missing required fields |
| 401 | Invalid email or password |
| 422 | Validation failed (e.g. invalid email format) |
| 429 | Rate limit exceeded (login) |

**Roles:** Unauthenticated (public).

---

## POST /api/auth/refresh

**Description:** Obtain a new access token (and rotated refresh token) using a refresh token.

| Request body | Type | Required |
|--------------|------|----------|
| `refresh_token` | string | yes |

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "bmV3IHJlZnJlc2ggdG9rZW4..."
}
```

| Status | Condition |
|--------|-----------|
| 400 | Malformed JSON or missing `refresh_token` |
| 401 | Invalid, expired, or revoked refresh token |
| 422 | Validation failed |
| 429 | Rate limit exceeded (refresh) |

**Roles:** Unauthenticated (public; token in body).

---

## POST /api/auth/logout

**Description:** Invalidate the current session / refresh token for the caller.

**Request body:** None.

**Response:** `204 No Content`

| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid Bearer token |
| 403 | Token valid but logout not permitted for subject (rare) |

**Roles:** Authenticated user.

---

## GET /api/auth/me

**Description:** Return the current authenticated user profile.

**Query / body:** None.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "rep",
  "tenant_id": "uuid"
}
```

| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid Bearer token |
| 403 | Authenticated but user disabled or tenant access denied |

**Roles:** Authenticated user (any role).
