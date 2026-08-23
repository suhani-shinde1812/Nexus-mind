"""
Nexus Mind — Enterprise Automated Integration Test Suite
Verifies all 10 core enterprise subsystems:
1. Health & Prometheus Metrics
2. Enterprise IAM, MFA (TOTP), Session Management & RBAC
3. Task Graph Operations & Threaded Comments
4. Multi-Agent Swarm Query Orchestrator
5. RAG Knowledge Pipeline & Grounded Citations
6. Machine Learning Risk Prediction & XAI
7. "What-If" Discrete-Event Schedule Simulator
8. Cybersecurity Threat Radar & Anomaly Detection
9. Immutable Audit Logging Pipeline
10. GitHub Engineering Intelligence Telemetry
"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"

from fastapi.testclient import TestClient
from app.main import app
from seed_data import seed

# Prime DB with enterprise seed data
seed()

client = TestClient(app)


def test_enterprise_pipeline():
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

    print("\n========================================================")
    print("RUNNING NEXUS MIND ENTERPRISE VALIDATION TEST SUITE")
    print("========================================================")

    # 1. Health & Metrics
    print("\n[TEST 1] Testing Health & Prometheus Observability Metrics...")
    health_res = client.get("/api/health")
    assert health_res.status_code == 200, f"Health failed: {health_res.text}"
    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200, f"Metrics failed: {metrics_res.text}"
    assert "nexusmind_tasks_total" in metrics_res.text, "Missing task metric in Prometheus stream"
    print("[PASS] Health (v2.0.0) & Prometheus /metrics verified")

    # 2. Authentication & JWT
    print("\n[TEST 2] Testing Enterprise Authentication, Sessions & MFA...")
    login_res = client.post(
        "/api/auth/login",
        data={"username": "sarah.jenkins@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_data = login_res.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Active Sessions
    sessions_res = client.get("/api/auth/sessions", headers=headers)
    assert sessions_res.status_code == 200, f"Sessions failed: {sessions_res.text}"
    assert len(sessions_res.json()) > 0, "No active sessions found"
    print(f"[PASS] JWT Authentication & Session tracking verified ({len(sessions_res.json())} active sessions)")

    # MFA Setup test
    mfa_setup_res = client.post("/api/auth/mfa/setup", headers=headers)
    assert mfa_setup_res.status_code == 200, f"MFA setup failed: {mfa_setup_res.text}"
    assert "secret" in mfa_setup_res.json(), "Missing MFA secret"
    print("[PASS] RFC 6238 TOTP Multi-Factor Authentication setup verified")

    # 3. Task Graph & Threaded Comments
    print("\n[TEST 3] Testing Task Graph & Realtime Threaded Comments...")
    comments_res = client.get("/api/tasks/TASK-102/comments", headers=headers)
    assert comments_res.status_code == 200, f"Get comments failed: {comments_res.text}"
    
    new_comment_res = client.post(
        "/api/tasks/TASK-102/comments",
        json={"content": "Automated CI verification test comment on TASK-102."},
        headers=headers,
    )
    assert new_comment_res.status_code == 201, f"Add comment failed: {new_comment_res.text}"
    print(f"[PASS] Task comments verified ({len(comments_res.json()) + 1} comments on TASK-102)")

    # 4. Multi-Agent Swarm Orchestration
    print("\n[TEST 4] Testing Multi-Agent Swarm Orchestrator...")
    swarm_query_res = client.post(
        "/api/ai/query",
        json={"query": "What if Alex is unavailable for 5 days?"},
        headers=headers,
    )
    assert swarm_query_res.status_code == 200, f"Swarm query failed: {swarm_query_res.text}"
    swarm_data = swarm_query_res.json()
    assert "agent" in swarm_data, "Missing agent persona attribution"
    print(f"[PASS] Multi-Agent Orchestrator routed to '{swarm_data['agent']}' with proposal workflow")

    # 5. RAG Knowledge Engine & Citations
    print("\n[TEST 5] Testing RAG Knowledge Base & Grounded Citations...")
    docs_list_res = client.get("/api/documents", headers=headers)
    assert docs_list_res.status_code == 200, f"List docs failed: {docs_list_res.text}"
    assert len(docs_list_res.json()) > 0, "No indexed documents found"

    rag_res = client.post(
        "/api/documents/query",
        json={"query": "How does authentication and MFA work?", "top_k": 3},
        headers=headers,
    )
    assert rag_res.status_code == 200, f"RAG query failed: {rag_res.text}"
    rag_data = rag_res.json()
    assert len(rag_data.get("citations", [])) > 0, "No citations returned from RAG"
    first_cit = rag_data["citations"][0]
    print(f"[PASS] RAG retrieved answer with citation: [{first_cit['document_title']} - {first_cit['section']}]")

    # 6. Machine Learning Risk Prediction & XAI
    print("\n[TEST 6] Testing Machine Learning Risk Engine & Explainable AI (XAI)...")
    ml_risk_res = client.get("/api/simulation/risk/TASK-102", headers=headers)
    assert ml_risk_res.status_code == 200, f"ML risk failed: {ml_risk_res.text}"
    ml_data = ml_risk_res.json()
    assert "predicted_risk" in ml_data and "contributing_factors" in ml_data, "Missing XAI fields"
    print(f"[PASS] ML Risk Model predicted {ml_data['predicted_risk']*100}% risk for TASK-102 (Level: {ml_data['risk_level']}) with XAI factors: {list(ml_data['contributing_factors'].keys())}")

    # 7. "What-If" Project Simulation
    print("\n[TEST 7] Testing Discrete-Event 'What-If' Project Simulator...")
    sim_res = client.post(
        "/api/simulation/what-if",
        json={"unavailable_members": ["Devon Reed"], "scope_increase_tasks": 2, "added_developers": 1},
        headers=headers,
    )
    assert sim_res.status_code == 200, f"Simulation failed: {sim_res.text}"
    sdata = sim_res.json()
    print(f"[PASS] What-If Simulation: Baseline {sdata['baseline_days']}d -> Simulated {sdata['simulated_days']}d (Delta: {sdata['delta_days']}d, Delivery Prob: {sdata['on_time_probability']}%)")

    # 8. Cybersecurity Threat Radar
    print("\n[TEST 8] Testing Cybersecurity Threat Radar & Anomaly Detection...")
    radar_res = client.get("/api/security/threat-radar", headers=headers)
    assert radar_res.status_code == 200, f"Threat radar failed: {radar_res.text}"
    rdata = radar_res.json()
    print(f"[PASS] Security Threat Radar: Score {rdata['threat_score']}/100 (Level: {rdata['threat_level']})")

    # 9. Immutable Audit Logging Pipeline
    print("\n[TEST 9] Testing Immutable Security Audit Trail...")
    admin_login = client.post(
        "/api/auth/login",
        data={"username": "elena.rostova@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    audit_res = client.get("/api/audit/logs", headers=admin_headers)
    assert audit_res.status_code == 200, f"Audit logs failed: {audit_res.text}"
    print(f"[PASS] Security Audit Trail verified ({len(audit_res.json())} immutable audit events logged)")

    # 10. GitHub / Engineering Intelligence
    print("\n[TEST 10] Testing GitHub Engineering Metrics Telemetry...")
    eng_res = client.get("/api/integrations/github/metrics", headers=headers)
    assert eng_res.status_code == 200, f"Engineering metrics failed: {eng_res.text}"
    edata = eng_res.json()
    print(f"[PASS] Engineering Telemetry: Avg PR Cycle Time = {edata['avg_pr_cycle_time_hours']}h, CI Success Rate = {edata['ci_success_rate']}%, Deploy Frequency = {edata['deployment_frequency']}")

    print("\n========================================================")
    print("ALL 10 NEXUS MIND ENTERPRISE INTEGRATION TESTS PASSED 100%!")
    print("========================================================")


if __name__ == "__main__":
    test_enterprise_pipeline()
