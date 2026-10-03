# RESQ AGENT: API Reference Documentation

## 1. Overview
The RESQ AGENT backend exposes a versioned REST API rooted at `/api/v1/` alongside top-level health and liveness probes.

All endpoints adhere to standardized JSON envelopes and fail-safe error payloads.

---

## 2. Standard Error Format
When an error occurs, the API returns a consistent JSON response:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "details": [
      {
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "type": "value_error"
      }
    ]
  }
}
```

---

## 3. Endpoints

### System Health
- **`GET /health`**: Returns system operational status.
- **`GET /health/live`**: Liveness probe for container orchestrators.
- **`GET /health/ready`**: Readiness probe verifying database and cache connectivity without exposing connection strings.

### Authentication (`/api/v1/auth`)
- **`POST /api/v1/auth/login`**: Authenticate via email & password. Returns access token, refresh token, and expiration.
- **`POST /api/v1/auth/refresh`**: Exchange valid refresh token for rotated tokens.
- **`POST /api/v1/auth/logout`**: Blacklist current token.
- **`GET /api/v1/auth/me`**: Get caller profile, roles, and permissions.

### Organizations (`/api/v1/organizations`)
- **`POST /api/v1/organizations/`**: Create new administrative organization (Requires `org:create`).
- **`GET /api/v1/organizations/`**: List organizations with filters (`admin_level`, `province_id`, `parent_id`).
- **`GET /api/v1/organizations/{id}`**: Get organization by ID.
- **`PUT /api/v1/organizations/{id}`**: Update organization (Requires `org:update`).

### Users & Roles (`/api/v1/users`)
- **`POST /api/v1/users/`**: Create a user account (Requires `user:create`).
- **`GET /api/v1/users/`**: List users with pagination (Requires `user:read`).
- **`GET /api/v1/users/{id}`**: Get user details (Requires `user:read`).
- **`PUT /api/v1/users/{id}`**: Update user profile (Requires `user:update`).
- **`POST /api/v1/users/{id}/roles`**: Assign roles to user (Requires `user:assign_role`).

### Compliance Audit Trail (`/api/v1/audit-logs`)
- **`GET /api/v1/audit-logs/`**: Paginated audit log search (Requires `audit:read`).
- **`GET /api/v1/audit-logs/{id}/verify`**: Cryptographically verify HMAC-SHA256 signature.
