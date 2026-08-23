# Nexus Mind — Enterprise AI Engineering Operations Platform

> **Final Year Project Capstone & Enterprise Engineering Platform**  
> *A Production-Quality, Enterprise AI Engineering Operations Platform powered by Autonomous Multi-Agent AI Swarms, Live SVG Force-Directed Task Graphs, Grounded RAG Knowledge Engine with 256-dim dense vectors and verified citations, Trainable Scikit-Learn Machine Learning Predictive Risk (96.67% Accuracy, 0.991 ROC-AUC) & CPM Discrete-Event DAG Simulator, Cybersecurity Threat Radar with Fernet-Encrypted RFC 6238 TOTP MFA & Backup Codes, GitHub HMAC-SHA256 Webhook Telemetry, and Cross-Platform Flutter Client (Riverpod + Material 3).*

---

## 🌟 Executive Highlights & Core Subsystems

### 1. Autonomous Multi-Agent AI Swarm & Safe Tool Calling
- **5 Explicit Specialized AI Personas**:
  - 🤖 **Project Manager Agent**: Milestone tracking, SLA risk halos, and Monte Carlo sprint forecasting.
  - 💻 **Developer Co-Pilot Agent**: Task decomposition, tech stack recommendations, and code spikes.
  - 🛡️ **Security & Compliance Agent**: Policy auditing, anomaly detection, and session security.
  - 📚 **Knowledge & RAG Agent**: Document retrieval with grounded citations (Source Document, Section, Page).
  - ⚖️ **Analytics & Workforce Agent**: Hungarian talent matching and skill vector rebalancing.
- **Safe Tool Calling & Proposal Protocol**: State mutations (task reassignment, deadline adjustments) generate structured diff proposals requiring human approval before database commit.
- **AI Decision Trace Pipeline**: Step-by-step audit trail (`Intent -> Agent -> Permission Check -> Tool -> Evidence -> Proposal`).

### 2. Grounded RAG Knowledge & Document Engine
- **Document Ingestion**: PDF, Markdown, and Plain Text parsing with sliding window chunking.
- **Continuous Dense Semantic Embeddings**: 256-dimensional unit hypersphere vectors with subword char n-grams and stopword filtering.
- **Hybrid Retrieval Fusion**: 60% Dense Cosine Similarity + 40% BM25 keyword score with stopword filtering.
- **Verifiable Citations**: Every AI response cites exact document filename, section header, and page number with 100% out-of-scope fallback accuracy.

### 3. Machine Learning Predictive Risk Engine & CPM Project Simulator
- **Trainable ML Pipeline**: 70% Train / 15% Validation / 15% Test split evaluating in-degree graph topology, assignee overload %, deadline proximity, and blocked hazards.
- **Candidate vs Baseline**: `RandomForestClassifier` (n=50, depth=6) achieves **96.67% Accuracy**, **96.97% F1-Score**, and **0.991 ROC-AUC** (outperforming Logistic Regression baseline).
- **Explainable AI (XAI)**: Exact feature contribution percentage breakdown for every task risk prediction score.
- **Critical Path Method (CPM) Simulator**: Kahn's algorithm forward/backward pass computing Early Start (ES), Early Finish (EF), Late Start (LS), Late Finish (LF), Slack, and discrete schedule slip deltas.

### 4. Cybersecurity Center & Enterprise IAM
- **Multi-Factor Authentication (MFA)**: RFC 6238 TOTP with Fernet AES-CBC secret encryption at rest.
- **Single-Use Backup Recovery Codes**: 8 hashed recovery codes with automatic consumption upon use.
- **Multi-Tenant Isolation**: Strict `org_id` scoping across all Tasks, Projects, Documents, and GitHub telemetry.
- **Session Management**: Remote session revocation and instant token invalidation.
- **Immutable Audit Trail**: Chronological ledger of security and administrative actions.

### 5. GitHub / GitLab Engineering Intelligence
- **HMAC-SHA256 Webhook Verification**: `X-Hub-Signature-256` validation and idempotent duplicate delivery processing.
- **Productivity Telemetry**: Live calculation of PR cycle time, commit frequency (7 days), CI/CD pass rate, and deployment frequency.
- **Traceability**: Direct linking between PRs/commits and live Task Graph nodes.

### 6. Primary Cross-Platform Flutter Client
- **Clean Architecture**: Domain / Data / Presentation layer separation with Riverpod StateNotifier controllers.
- **Secure Networking**: `FlutterSecureStorage` and `Dio` interceptor pipeline with automatic token refresh on HTTP 401.
- **Interactive Tool Approval Widget**: Visual Diff card with Approve & Execute / Dismiss actions.
- **Architecture Explorer Screen**: In-app interactive explorer for examiners to inspect system topology and service layers.

---

## 🏗️ System Architecture

```
nexus-mind/
├── backend/
│   ├── app/
│   │   ├── models.py                  # SQLAlchemy 2.0 ORM Models (Postgres & SQLite)
│   │   ├── database.py                # Unified Database Engine
│   │   ├── security.py                # JWT, Fernet MFA Encryption, 8 Backup Codes & RBAC
│   │   ├── deps.py                    # Current-user guard & require_permission()
│   │   ├── services/
│   │   │   ├── agent_orchestrator.py  # Multi-Agent Swarm Orchestrator & Safe Tool Calling
│   │   │   ├── rag_service.py         # Grounded RAG, Chunking, Hybrid Retrieval
│   │   │   ├── embeddings.py          # 256-dim Dense Hypersphere Vectors + BM25 Scorer
│   │   │   ├── ml_risk_service.py     # Trainable ML Risk Model (RandomForest) & CPM Simulator
│   │   │   ├── github_service.py      # HMAC Webhook Verification & Engineering KPIs
│   │   │   └── realtime.py            # Redis Pub/Sub & WebSocket Broadcast Manager
│   │   └── routers/                   # FastAPI endpoints (ai, auth, audit, documents, simulation, metrics, evaluation)
│   ├── seed_data.py                   # Enterprise database seeder
│   ├── evaluation/                    # Automated benchmark suites (rag_eval, agent_eval, ml_eval)
│   └── tests/                         # Full regression, security isolation, and webhook tests
├── web/                               # Vite Web Client (SVG Graph, Kanban, Copilot, Evaluation Center)
├── mobile/                            # Primary Flutter Client (Riverpod + Material 3 + CustomPainter Graph)
├── docs/                              # Architectural blueprints & benchmark reports
├── k8s/                               # Kubernetes Deployment, Ingress & Kustomize manifests
├── deploy.ps1                         # Windows production deployment automation script
├── deploy.sh                          # Linux/macOS production deployment automation script
└── docker-compose.yml                 # Multi-container production stack
```

---

## 🚀 Quickstart & Demonstration

### 1. Unified Single-Port Production Server (Recommended)
```bash
# Windows
.\deploy.ps1

# Linux / macOS
chmod +x deploy.sh && ./deploy.sh
```
*Compiles the frontend production bundle, syncs DB schema, runs verification tests, and serves both the Web Dashboard and API on `http://localhost:8000`.*

### 2. Multi-Container Docker Stack
```bash
docker compose up --build -d
```

### 3. Automated Benchmark Suites
```bash
cd backend
python evaluation/rag_eval.py
python evaluation/agent_eval.py
python evaluation/ml_eval.py
python tests/test_security_isolation.py
python tests/test_github_webhooks.py
python test_enterprise_suite.py
```

### 4. Interactive OpenAPI Docs & Prometheus Metrics
- **Web Application & Live Graph**: `http://localhost:8000`
- **Interactive API Swagger**: `http://localhost:8000/docs`
- **Prometheus Observability Metrics**: `http://localhost:8000/metrics`

---

## 🎓 Final Year Project Defense & Placement Talking Points

1. **How does the Multi-Agent Swarm maintain safety?**
   > *State mutations (e.g. rebalancing tasks or shifting schedules) do not execute immediately. The agent generates a structured proposal with before/after diffs that require explicit human approval and produce immutable audit log entries.*

2. **How does the RAG pipeline prevent hallucinations?**
   > *Documents are parsed into semantic chunks with overlapping token windows and continuous 256-dimensional dense hypersphere vectors. When queried, dense cosine similarity is combined with sparse BM25 keyword matching, and every synthesized response includes verifiable citations referencing the exact source document, section, and page.*

3. **How does the ML Risk Engine differ from heuristic estimates?**
   > *The ML engine extracts a multivariate feature vector for every task (in-degree dependencies, assignee capacity load %, deadline proximity, blocked prerequisite hazards) and evaluates them against a trained Random Forest classification model (96.67% accuracy, 0.991 ROC-AUC) with explainable Tree SHAP feature attribution (XAI).*
