# Nexus Mind — Current Architecture Specification (Phase 0)

## 1. Architectural Overview

```
                      ┌────────────────────────────────────────┐
                      │             CLIENT LAYER               │
                      │  - Web SPA (Vite + Vanilla ES6 + CSS)  │
                      │  - Mobile App (Flutter Basic)          │
                      └───────────────────┬────────────────────┘
                                          │  HTTP REST / WebSocket
                                          ▼
                      ┌────────────────────────────────────────┐
                      │            API GATEWAY LAYER           │
                      │          FastAPI (Uvicorn ASGI)        │
                      │   - JWT Bearer Auth (python-jose)      │
                      │   - CORS Middleware & Static Routing   │
                      └───────────────────┬────────────────────┘
                                          │
                  ┌───────────────────────┴────────────────────────┐
                  ▼                                                ▼
┌───────────────────────────────────┐            ┌───────────────────────────────────┐
│           ROUTER LAYER            │            │          REALTIME SERVICE         │
│  - /api/auth    - /api/tasks      │            │  - ConnectionManager              │
│  - /api/users   - /api/meetings   │            │  - Redis Pub/Sub listener         │
│  - /api/projects- /api/ai         │            │  - WebSocket /ws?token=...        │
│  - /api/policies- /api/bootstrap  │            └─────────────────┬─────────────────┘
└─────────────────┬─────────────────┘                              │
                  │                                                │
                  ▼                                                │
┌───────────────────────────────────┐                              │
│           SERVICE LAYER           │                              │
│  - ai_service.py (Monte Carlo,    │                              │
│    Decomposition, Rebalancing)    │                              │
│  - embeddings.py (Bag-of-words)   │                              │
│  - push.py (FCM Tokens)           │                              │
└─────────────────┬─────────────────┘                              │
                  │                                                │
                  ▼                                                ▼
┌───────────────────────────────────┐            ┌───────────────────────────────────┐
│          DATABASE LAYER           │            │           CACHE & PUB/SUB         │
│  - PostgreSQL 16 / SQLite 3       │            │  - Redis 7                        │
│  - SQLAlchemy 2.0 ORM Models      │            │  - Cross-process event broadcast  │
│  - Alembic 1.13 Migrations        │            │                                   │
└───────────────────────────────────┘            └───────────────────────────────────┘
```

---

## 2. Component Analysis

### 2.1 Backend Routing & Dependency Injection
- **`app/database.py`**: Provides session generator `get_db()` with `autocommit=False, autoflush=False`. Supports `check_same_thread=False` for SQLite and connection pooling for PostgreSQL.
- **`app/deps.py`**: Extracts `token` from `Authorization: Bearer <JWT>`, decodes payload with `python-jose`, and loads current active `User` model.
- **`app/routers/`**:
  - `tasks.py`: Task CRUD, status updates, drag position persistence, assignment, and dependency manipulation.
  - `ai.py`: Task decomposition, Monte Carlo sprint forecasting, and capacity rebalancing.
  - `bootstrap.py`: Unified aggregation payload delivering tasks, projects, users, policies, alerts, meetings, and activity logs in a single round-trip.
  - `ws.py`: Realtime WebSocket endpoint validating authentication token on handshake.

### 2.2 Data Layer & Entity Relationships
- **User** 1-to-N **Task** (as assignee)
- **User** 1-to-N **PushToken** (for mobile push)
- **Project** 1-to-N **Task**
- **Task** 1-to-N **TaskHistory** (audit events)
- **Task** 1-to-N **Alert** (risk notifications)
- **Task.depends_on**: Stored as JSON array of prerequisite task ID strings.

### 2.3 AI & Intelligence Services
- **Monte Carlo Forecast**: Runs 500 stochastic iterations using random normal SLA delay sampling conditioned on task priority, blocked dependencies, and assignee overload.
- **Workload Rebalancer**: Computes cosine similarity between task keyword vectors and user skill vectors, combining Hungarian matching with capacity limits.
- **Task Decomposition**: Formats prompt for Anthropic Claude 3.5 Sonnet / 3.7 Sonnet with deterministic heuristic fallback when API key is unset.

### 2.4 Realtime Synchronization
- Mutations (task status change, reassignments, alerts) trigger `manager.broadcast_json(...)`.
- `ConnectionManager` publishes to Redis channel `nexusmind:events`.
- Dedicated background Redis listener loop receives events and sends WebSocket frames to connected clients.
