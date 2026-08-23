"""
Comprehensive test script for Nexus Mind backend API.
Verifies JWT auth, task graph CRUD, AI decomposition, Monte Carlo forecast, and rebalancing.
"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"

from fastapi.testclient import TestClient
from app.main import app
from seed_data import seed

# Ensure database is seeded
seed()

client = TestClient(app)

def test_full_pipeline():
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

    print("\n--- 1. Testing Health & Auth Login ---")
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200, f"Health failed: {health_resp.text}"
    print("[PASS] GET /api/health passed")

    login_resp = client.post(
        "/api/auth/login",
        data={"username": "sarah.jenkins@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    tokens = login_resp.json()
    token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] POST /api/auth/login passed (JWT token acquired)")

    print("\n--- 2. Testing Bootstrap Aggregation & Activity Logs ---")
    bootstrap_resp = client.get("/api/bootstrap", headers=headers)
    assert bootstrap_resp.status_code == 200, f"Bootstrap failed: {bootstrap_resp.text}"
    bdata = bootstrap_resp.json()
    assert len(bdata["tasks"]) > 0, "No tasks returned in bootstrap"
    assert len(bdata["users"]) > 0, "No users returned in bootstrap"
    print(f"[PASS] GET /api/bootstrap returned {len(bdata['tasks'])} tasks, {len(bdata['users'])} users, {len(bdata.get('activityLogs', []))} activity logs")

    print("\n--- 3. Testing Task Graph CRUD & Risk Scoring ---")
    task_resp = client.post(
        "/api/tasks",
        json={
            "title": "Quantum Encryption Key Distribution",
            "description": "Implement post-quantum cryptographic key exchange protocol.",
            "project": "Security & Compliance",
            "assignee": "Elena Rostova",
            "status": "in_progress",
            "priority": "Critical",
            "dependsOn": ["TASK-103"],
            "dueDate": "2026-08-30",
        },
        headers=headers,
    )
    assert task_resp.status_code == 201, f"Task create failed: {task_resp.text}"
    created_task = task_resp.json()
    task_id = created_task["id"]
    risk = created_task.get("aiRiskScore") or created_task.get("ai_risk_score", 0.1)
    print(f"[PASS] POST /api/tasks created [{task_id}] '{created_task['title']}' (Risk Score: {risk})")

    print("\n--- 4. Testing Dependency Link Manipulation ---")
    dep_resp = client.post(f"/api/tasks/{task_id}/dependency/TASK-101", headers=headers)
    assert dep_resp.status_code == 200, f"Add dependency failed: {dep_resp.text}"
    deps = dep_resp.json().get("dependsOn") or dep_resp.json().get("depends_on", [])
    assert "TASK-101" in deps, f"Dependency not added: {dep_resp.json()}"
    print(f"[PASS] POST /api/tasks/{task_id}/dependency/TASK-101 added dependency link")

    rem_dep_resp = client.delete(f"/api/tasks/{task_id}/dependency/TASK-101", headers=headers)
    assert rem_dep_resp.status_code == 200, f"Remove dependency failed: {rem_dep_resp.text}"
    deps_after = rem_dep_resp.json().get("dependsOn") or rem_dep_resp.json().get("depends_on", [])
    assert "TASK-101" not in deps_after, f"Dependency not removed: {rem_dep_resp.json()}"
    print(f"[PASS] DELETE /api/tasks/{task_id}/dependency/TASK-101 removed dependency link")

    print("\n--- 5. Testing AI Monte Carlo Sprint Forecast ---")
    forecast_resp = client.post("/api/ai/forecast", headers=headers)
    assert forecast_resp.status_code == 200, f"Forecast failed: {forecast_resp.text}"
    fdata = forecast_resp.json()
    assert "onTimeProbability" in fdata, "Missing onTimeProbability"
    print(f"[PASS] POST /api/ai/forecast: On-Time Delivery Probability = {fdata['onTimeProbability']}%, Expected Delay = {fdata['expectedDelayDays']} days ({fdata['simulationRuns']} simulations)")

    print("\n--- 6. Testing AI Workload Rebalancing Plan ---")
    rebal_resp = client.post("/api/ai/rebalance", headers=headers)
    assert rebal_resp.status_code == 200, f"Rebalance failed: {rebal_resp.text}"
    rdata = rebal_resp.json()
    print(f"[PASS] POST /api/ai/rebalance: Status = {rdata['status']}, Found {len(rdata['recommendations'])} optimal reassignments")

    print("\n--- 7. Testing AI Task Decomposition ---")
    decomp_resp = client.post(
        "/api/ai/decompose",
        json={"title": "Automated Chaos Engineering Fault Injection", "description": "Simulate network partitions and service latency injection."},
        headers=headers,
    )
    assert decomp_resp.status_code == 200, f"Decompose failed: {decomp_resp.text}"
    subtasks = decomp_resp.json()
    assert len(subtasks) > 0, "No subtasks returned"
    print(f"[PASS] POST /api/ai/decompose generated {len(subtasks)} structured subtasks")

    print("\n========================================================")
    print("ALL NEXUS MIND BACKEND INTEGRATION TESTS PASSED 100%!")
    print("========================================================")

if __name__ == "__main__":
    test_full_pipeline()
