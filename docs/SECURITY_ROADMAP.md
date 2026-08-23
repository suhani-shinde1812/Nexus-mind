# Nexus Mind — Cybersecurity, IAM & Compliance Roadmap

## 1. Authentication & Session Security Architecture

### 1.1 Multi-Factor Authentication (MFA / TOTP)
- Implements RFC 6238 Time-Based One-Time Passwords (`pyotp`).
- Provisioning via `otpauth://` QR codes and backup recovery codes.
- MFA verification step required upon login before issuing long-lived access tokens.

### 1.2 JWT & Refresh Token Rotation
- **Access Tokens**: Short-lived (15–60 minutes) signed with `HS256` / `RS256`.
- **Refresh Tokens**: Cryptographically secure random UUIDs stored as SHA-256 hashes in `user_sessions` table with single-use rotation.
- **Session Revocation**: Remote session termination by user or administrator.

---

## 2. Enterprise Authorization (RBAC & ABAC)

### 2.1 Role-Based Access Control
| Role | Permissions |
| :--- | :--- |
| **Employee** | `task.read`, `task.update_own`, `meeting.read`, `comment.create`, `doc.read` |
| **Team Lead** | `task.*`, `project.read`, `team.rebalance`, `meeting.*`, `doc.read`, `analytics.view` |
| **Project Manager** | `project.*`, `task.*`, `ai.forecast`, `simulation.run`, `analytics.*`, `doc.*` |
| **Security Admin** | `security.*`, `audit.*`, `user.*`, `policy.*`, `session.revoke`, `system.*` |

### 2.2 Attribute-Based Access Control (ABAC)
- Multi-tenant organization isolation (`user.org_id == resource.org_id`).
- Sensitivity clearance levels on SOP security documents (`user.clearance >= doc.classification_level`).

---

## 3. Security Audit Logging & Anomaly Detection

### 3.1 Immutable Audit Log Pipeline
- Captures: `timestamp`, `actor_id`, `actor_email`, `action`, `resource_type`, `resource_id`, `ip_address`, `user_agent`, `status`, `diff_payload`.
- Monitored actions: Authentication attempts, role promotions, task deletions, policy edits, AI tool executions.

### 3.2 Anomaly Detection Engine
- **Heuristic & Statistical Detection**:
  - Failed login velocity (> 5 failed attempts in 2 minutes ➔ Account Lockout + Security Alert).
  - High-frequency API scraping (> 120 req/min from single IP).
  - Privilege escalation attempts.
- **Isolation Forest Model**: Evaluates multivariate vectors (request frequency, time of day, endpoint sensitivity, failed auth ratio) to output an active **Organization Threat Level (0-100)**.
