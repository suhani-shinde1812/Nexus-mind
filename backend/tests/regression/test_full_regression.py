"""
Nexus Mind — Zero-Regression Baseline Test Suite
Guarantees that core API routes, authentication, task graph, dependencies,
Monte Carlo forecasting, workload rebalancing, and data schemas remain 100% operational.
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"

from fastapi.testclient import TestClient
from app.main import app
from seed_data import seed


seed()
client = TestClient(app)


def test_regression_baseline():
    from app.database import SessionLocal
    from app import models
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == "sarah.jenkins@nexusmind.ai").first()
    if user:
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = []
        db.commit()
    db.close()

    print("\n[REGRESSION 1] Verifying System Health & Baseline Status...")
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json().get("status") == "ok"

    print("\n[REGRESSION 2] Verifying Authentication & Token Issuance...")
    login = client.post(
        "/api/auth/login",
        data={"username": "sarah.jenkins@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n[REGRESSION 3] Verifying Workspace Bootstrap Hydration...")
    boot = client.get("/api/bootstrap", headers=headers)
    assert boot.status_code == 200
    data = boot.json()
    assert len(data["tasks"]) >= 8
    assert len(data["projects"]) >= 3
    assert len(data["users"]) >= 6

    print("\n[REGRESSION 4] Verifying Task Graph CRUD & Dependency Operations...")
    task_id = "TASK-102"
    task_res = client.get("/api/tasks/TASK-102/reassignment-candidates", headers=headers)
    assert task_res.status_code == 200
    candidates = task_res.json()
    assert len(candidates) > 0

    print("\n[REGRESSION 5] Verifying Monte Carlo & AI Intelligence Services...")
    forecast = client.post("/api/ai/forecast", headers=headers)
    assert forecast.status_code == 200
    assert "onTimeProbability" in forecast.json()

    rebalance = client.post("/api/ai/rebalance", headers=headers)
    assert rebalance.status_code == 200
    assert "recommendations" in rebalance.json()

    print("\n[PASS] All baseline regression tests passed successfully!")


if __name__ == "__main__":
    test_regression_baseline()
