# RESQ AGENT: Security & Compliance Specification

## 1. Threat Model & Principles
RESQ AGENT coordinates high-stakes emergency disaster responses. In an emergency, service integrity, availability, and non-repudiation are paramount.

### Core Safeguards:
- **Human-in-the-Loop Constraint**: AI components operate via constrained tools and can never trigger real-world actions autonomously.
- **Fail-Closed Permissions**: Endpoints deny access unless explicitly granted through roles or permissions.
- **Defense in Depth**: Security controls operate at the network, gateway, application middleware, database, and cryptographic layers.

---

## 2. Authentication & Session Security
- **Algorithm**: HMAC-SHA256 (JWT).
- **Dual-Token Lifecycle**:
  - `Access Token`: 30-minute lifespan, claims include `sub`, `roles`, `permissions`, and `org_id`.
  - `Refresh Token`: 7-day lifespan, contains unique cryptographic `jti` (JWT ID).
- **Token Rotation**: Every refresh rotates the refresh token. The previous token is revoked immediately in the database (`revoked_tokens`).
- **Deterministic Logout**: Calling `/api/v1/auth/logout` places the active token JTI onto the revocation blacklist, invalidating the session immediately.
- **Password Storage**: Directly salted and hashed using Bcrypt (cost factor 12) with a 72-byte truncation boundary to avoid buffer overflow vulnerabilities.

---

## 3. Role-Based Access Control (RBAC) Matrix

| Operational Role | Scope | Key Permissions |
|---|---|---|
| **SUPER_ADMIN** | System-wide | Unrestricted bypass, system configuration, global audits |
| **ORG_ADMIN** | Organization | User creation, role assignment within org, org details |
| **EMERGENCY_COORDINATOR** | Tactical Command | Incident triage, AI recommendation approval/override, resource dispatch |
| **INCIDENT_OFFICER** | Incident Management | Ground report verification, incident updates, resource requests |
| **FIELD_RESPONDER** | On-Scene Response | Update status (En Route, On Scene, Cleared) |
| **MEDICAL_OFFICER** | Medical Sector | Hospital capacity updates, triage updates, ambulance requests |
| **RESOURCE_MANAGER** | Logistics | Equipment registry, fleet status, shelter management |
| **ANALYST** | Intelligence | Read-only analytics, incident aggregation, post-incident reporting |
| **READ_ONLY_VIEWER** | Public/Auditor | Scoped read-only access |

---

## 4. Cryptographic Tamper-Evident Audit Logging
Every sensitive event computes an HMAC-SHA256 checksum:
$$\text{Checksum} = \text{HMAC-SHA256}\Big(K_{\text{secret}}, \text{actor\_id} \parallel \text{action} \parallel \text{entity\_type} \parallel \text{entity\_id} \parallel \text{timestamp} \parallel \text{changes\_json}\Big)$$

The checksum is verified on-demand via `GET /api/v1/audit-logs/{id}/verify`. Any modification to the database table produces an immediate signature mismatch.

---

## 5. Network & HTTP Security
- **HTTP Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy: default-src 'self'`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Error Sanitization**: Centralized exception handlers catch all internal errors and format them into standard error envelopes without leaking database queries, table names, or stack traces.
