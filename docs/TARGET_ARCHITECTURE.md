# Nexus Mind — Target Enterprise Architecture (Production Vision)

## 1. High-Level Enterprise Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PRIMARY FRONTEND                                │
│                     Flutter 3 Enterprise Client                             │
│       (Riverpod + GoRouter + Dio + Material 3 + WebSockets + Drift)         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Mobile (iOS / Android)  │  Tablet / iPad  │  Desktop (macOS / Win)     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Web Client (SVG Live Force Graph, Kanban, Gantt, Analytics, Copilot)  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / WSS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API & SECURITY GATEWAY                             │
│                     FastAPI v1 API Gateway (/api/v1)                        │
│   - Rate Limiting (SlowAPI / Redis Token Bucket)                            │
│   - Request Correlation ID Injection & Structured JSON Logging              │
│   - JWT + Refresh Token Rotation + MFA (TOTP) + Session Tracker             │
│   - RBAC & Fine-Grained Permission Enforcement Middleware                   │
│   - AI Prompt Injection & Data Leakage Shield                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
         ┌─────────────────────────────┴─────────────────────────────┐
         ▼                                                           ▼
┌───────────────────────────────────────────┐   ┌───────────────────────────────────────────┐
│              CORE SERVICES                │   │         AI & INTELLIGENCE SERVICES        │
│  ├── Project Service (CRUD, Milestones)   │   │  ├── Agent Orchestrator (Multi-Agent)     │
│  ├── Task Service (Graph, Dependencies)   │   │  │   ├── PM Agent (Milestones, Forecast)  │
│  ├── User & Team Intelligence Service     │   │  │   ├── Developer Agent (Decomposition)  │
│  ├── Notification & Push Service (FCM)    │   │  │   ├── Security Agent (Audit, Anomaly)  │
│  ├── Meeting Intelligence Service (Jitsi) │   │  │   ├── Knowledge Agent (RAG, Citations) │
│  ├── Cybersecurity & Audit Service        │   │  │   └── Analytics Agent (KPIs, Trends)   │
│  ├── Engineering & GitHub/GitLab Service  │   │  ├── RAG Engine (Chunking, pgvector, Hyb) │
│  └── Analytics & Forecasting Service      │   │  ├── ML Risk Engine (XGBoost/RF + SHAP)   │
│                                           │   │  └── "What-If" Project Simulation Engine  │
└─────────────────────┬─────────────────────┘   └─────────────────────┬─────────────────────┘
                      │                                               │
         ┌────────────┴───────────────────────────────┬───────────────┴──────────┐
         ▼                                            ▼                          ▼
┌─────────────────────────────────┐   ┌───────────────────────────────┐   ┌─────────────────────────────────┐
│      POSTGRESQL 16 ENTERPRISE   │   │        REDIS 7 DISTRIBUTED    │   │     OBSERVABILITY & DEVOPS      │
│  - Transactional Core Tables    │   │  - Response Cache             │   │  - OpenTelemetry Tracing        │
│  - pgvector (Embeddings & RAG)  │   │  - Real-time Pub/Sub WSS      │   │  - Prometheus /metrics          │
│  - Immutable Security Audit Logs│   │  - Distributed Task Queues    │   │  - Structured JSON Logs         │
│  - Multi-Tenant Organization IDs│   │  - User Online Presence Hub   │   │  - Docker Compose & K8s Manifest│
└─────────────────────────────────┘   └───────────────────────────────┘   └─────────────────────────────────┘
```

---

## 2. Micro-Modules & Subsystem Contracts

### 2.1 Multi-Agent AI Swarm & Safe Tool Calling
* **Agentic Orchestrator**: Inspects user queries, routes to specialized sub-agents (`ProjectManagerAgent`, `DeveloperAgent`, `SecurityAgent`, `KnowledgeAgent`, `AnalyticsAgent`).
* **Tool Calling Guard**: Strict tool manifests with JSON schema validation and permission checking.
* **Human-in-the-Loop Proposal Protocol**: All state-mutating actions (reassigning tasks, creating milestones, modifying deadlines) output structured proposed action diffs requiring explicit user confirmation before commit.

### 2.2 RAG Knowledge & Document Engine
* **Document Formats**: PDF, Markdown, Plain Text, DOCX.
* **Chunking**: Recursive character chunking (500 tokens, 10% overlap).
* **Embeddings**: Local fast hashed vectors + optional OpenAI/Anthropic/HuggingFace embeddings stored in `pgvector`.
* **Hybrid Retrieval**: Dense semantic vector similarity + Sparse BM25 keyword matching + metadata filtering.
* **Citations**: Returns exact document source filename, section, and page reference.

### 2.3 Machine Learning & Explainable Risk Analysis
* **Model**: Trained classifier (Random Forest / XGBoost / Logistic Regression) trained on project history, dependency graph topology, assignee overload, deadline proximity, and reassignment count.
* **Explainability (XAI)**: Feature importance vectors providing human-readable explanations (e.g. `[+45% dependency blocked hazard, +30% capacity overload]`).
* **"What-If" Project Simulator**: Simulates developer absence, milestone scope shifts, and addition of engineering resources, yielding delta completion dates and bottleneck shift alerts.

### 2.4 Cybersecurity Center & Audit Engine
* **MFA**: TOTP RFC 6238 time-based one-time password generation & validation.
* **Audit Trail**: Immutable event stream with user actor, IP address, user agent, request ID, target entity, and before/after diffs.
* **Anomaly Detection**: Statistical & Isolation Forest outlier detection for abnormal login rates, brute-force attempts, and unauthorized access patterns.
