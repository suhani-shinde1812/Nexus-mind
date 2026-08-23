# Nexus Mind — Database Schema & Migration Plan

## 1. Objectives & Database Strategy
- Support PostgreSQL 16 (production with pgvector) and SQLite 3 (portable local zero-config testing).
- Maintain 100% backward compatibility with existing tables while introducing multi-tenancy, RAG embeddings, comments, security audit logs, sessions, and GitHub integrations.

---

## 2. Target Schema Specification

```
organizations (id PK, name, plan, created_at)
 └── users (id PK, org_id FK, name, email, hashed_password, role, app_role, avatar, capacity, active_tasks, skills, mfa_secret, mfa_enabled, is_active, created_at)
      ├── user_sessions (id PK, user_id FK, refresh_token_hash, user_agent, ip_address, expires_at, created_at)
      ├── push_tokens (id PK, user_id FK, token, platform, created_at)
      ├── audit_logs (id PK, org_id FK, user_id FK, action, target_type, target_id, details JSON, ip_address, created_at)
      └── security_events (id PK, org_id FK, user_id FK, severity, event_type, description, status, created_at)

projects (id PK, org_id FK, name, lead, deadline, progress, created_at)
 └── tasks (id PK, org_id FK, project_id FK, assignee_id FK, title, description, status, priority, depends_on JSON, x, y, due_date, ai_risk_score, risk_reason, created_at, updated_at, completed_at)
      ├── task_comments (id PK, task_id FK, user_id FK, content, created_at, updated_at)
      ├── task_attachments (id PK, task_id FK, filename, file_url, file_size, uploaded_by FK, created_at)
      └── task_history (id PK, task_id FK, event_type, from_value, to_value, actor_id FK, created_at)

documents (id PK, org_id FK, title, filename, file_type, file_size, summary, uploaded_by FK, created_at)
 └── document_chunks (id PK, document_id FK, chunk_index, content, metadata JSON, embedding_vector JSON/vector)

meetings (id PK, org_id FK, title, project, date, time, duration, attendees JSON, agenda, organizer, status, link, ai_summary, action_items JSON, created_at)

github_integrations (id PK, org_id FK, repo_name, repo_url, access_token, webhook_secret, is_active, created_at)
 └── github_events (id PK, integration_id FK, event_type, pr_number, commit_hash, author, status, payload JSON, created_at)
```

---

## 3. Migration Steps & Alembic Scripting

1. **Step 1: Core Table Extensions**
   - Add `mfa_secret` and `mfa_enabled` columns to `users`.
   - Add `ai_summary` and `action_items` to `meetings`.
   - Add `org_id` column with default value `"ORG-GLOBAL"` to ensure zero-breakage on existing datasets.
2. **Step 2: Add New Tables**
   - Create `organizations`
   - Create `user_sessions`
   - Create `task_comments`
   - Create `task_attachments`
   - Create `documents` and `document_chunks`
   - Create `security_events`
   - Create `audit_logs`
   - Create `github_integrations` and `github_events`
3. **Step 3: Indexing & Vector Setup**
   - Indexes on `(tasks.assignee_id)`, `(tasks.project_id)`, `(task_history.task_id)`.
   - B-Tree index on `(audit_logs.created_at)` and `(security_events.severity)`.
   - Full-text and vector cosine distance indexing for RAG retrieval.
