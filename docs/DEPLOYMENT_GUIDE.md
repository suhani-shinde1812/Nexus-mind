# NEXUS MIND — ENTERPRISE DEPLOYMENT GUIDE

**Version**: 2.0.0 (Production-Ready)  
**Target Environments**: Bare-Metal VM, Local Container, Multi-Container Docker Compose, Kubernetes Cluster (EKS/GKE/AKS/Minikube), and Cloud Providers (AWS/GCP/Azure/Render/Railway).

---

## 1. Architecture Deployment Overview

Nexus Mind is designed with a cloud-native, horizontally scalable 12-factor architecture:

```
                          [ Client Layer ]
              (Web Dashboard SPA / Flutter Mobile & Desktop)
                                     │
                                     ▼
                      [ Ingress / Nginx Proxy ]
                      (SSL/TLS, Gzip, WebSockets)
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
       [ FastAPI REST & WS Nodes ]             [ Background Celery/Async Workers ]
     (RAG Engine, Swarm, ML Risk)              (Model Training, Telemetry Polls)
                 │                                       │
                 ├───────────────────┬───────────────────┤
                 ▼                   ▼                   ▼
       [ PostgreSQL 16 DB ]     [ Redis 7 ]     [ Persistent Storage ]
        (pgvector, JSONB)      (Pub/Sub, Cache)  (PDF Knowledge Vault)
```

---

## 2. Deployment Option 1: Unified Single-Port Deployment (Fastest)

Nexus Mind supports a **Unified Single-Port Deployment** where FastAPI serves both the production React/Vite SPA and backend REST/WebSockets from a single port (`8000`).

### Automated Script (Windows PowerShell):
```powershell
.\deploy.ps1
```

### Automated Script (Linux / macOS):
```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual Step-by-Step:
1. **Build Web Production Bundle**:
   ```bash
   cd web
   npm install
   npm run build
   ```
2. **Synchronize & Seed Database**:
   ```bash
   cd ../backend
   python seed_data.py
   ```
3. **Launch Production Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

**Access Points**:
- **Application Dashboard**: `http://localhost:8000`
- **Swagger API Docs**: `http://localhost:8000/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

---

## 3. Deployment Option 2: Docker Compose Multi-Container Stack

For complete enterprise isolation with dedicated PostgreSQL 16 and Redis 7 containers:

```bash
docker compose up --build -d
```

### Services Initialized:
- `postgres`: PostgreSQL 16 Alpine on port `5432` with healthcheck
- `redis`: Redis 7 Alpine on port `6379`
- `backend`: FastAPI Python 3.12 container on port `8000`
- `web`: Nginx Alpine reverse-proxying frontend on port `5173` (or `80`)

### Verification & Logs:
```bash
docker compose ps
docker compose logs -f backend
```

---

## 4. Deployment Option 3: Kubernetes Cluster Deployment

Production-grade Kubernetes manifests with namespaces, resource limits, secrets, and ingress:

### 1. Create Secrets:
```bash
kubectl create namespace nexusmind

kubectl create secret generic nexusmind-secrets \
  --namespace nexusmind \
  --from-literal=database-url="postgresql+psycopg2://nexus:YOUR_SECRET@postgres:5432/nexusmind" \
  --from-literal=jwt-secret-key="YOUR_PRODUCTION_JWT_SECRET_HEX" \
  --from-literal=encryption-key="YOUR_FERNET_32_BYTE_SECRET" \
  --from-literal=github-webhook-secret="YOUR_GITHUB_WEBHOOK_SECRET"
```

### 2. Apply Kustomize Manifests:
```bash
kubectl apply -k k8s/
```

### 3. Verify Pods & Services:
```bash
kubectl get pods -n nexusmind
kubectl get svc -n nexusmind
kubectl get ingress -n nexusmind
```

---

## 5. Deployment Option 4: Cloud Platform Deployment

### A. AWS (App Runner / ECS Fargate)
1. Push `backend` and `web` images to AWS ECR.
2. Deploy backend service connecting to AWS RDS Aurora PostgreSQL and ElastiCache Redis.
3. Configure environment variables in AWS Secrets Manager.

### B. Render / Railway
1. Connect GitHub repository to Render/Railway.
2. Create Managed PostgreSQL and Redis instances.
3. Set `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, and `ENCRYPTION_KEY`.
4. Deploy web as Static Site (`dist` output directory) or use the unified single-port Dockerfile.

---

## 6. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Environment mode (`development`, `production`) |
| `DEMO_MODE` | `false` | When true, skips strict MFA requirements for evaluation |
| `DATABASE_URL` | `postgresql+psycopg2://...` | PostgreSQL connection string (SQLite fallback in local dev) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching & WebSocket pub/sub connection string |
| `JWT_SECRET_KEY` | *(Generated random hex)* | 256-bit cryptographic signing key for JWT tokens |
| `ENCRYPTION_KEY` | *(Generated random hex)* | Fernet encryption key for MFA secrets at rest |
| `GITHUB_WEBHOOK_SECRET` | *(Generated random hex)* | HMAC-SHA256 verification secret for GitHub webhooks |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins (comma-separated) |
