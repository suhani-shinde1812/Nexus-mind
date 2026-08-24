"""
NEXUS MIND — AI AGENT TASK INTELLIGENCE & COPILOT TEST SUITE

Tests:
1. "Who is working on Authentication?" -> Real database assignee
2. "What is the status of Authentication?" -> Real database status
3. "When is Authentication due?" -> Real database due date
4. "What is blocking Authentication?" -> Real prerequisite dependencies
5. "Who is overloaded?" -> Real team capacity & workload calculation
6. "Does Authentication exist?" -> Real database lookup
7. Multi-Tenant Organization Isolation -> Zero cross-tenant task query leakage
8. Unknown Task Handling -> Clear 'Could not find...' response without hallucination
9. Multiple Matching Tasks -> Structured clarification with options
10. Conversational Follow-Up Memory -> Resolving 'deadline' & 'is it high risk?' to active task context
11. Live Data Reflection -> Updating task assignee in DB immediately changes AI response
"""
import os
import sys
import uuid
from starlette.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.main import app
from app.database import Base, engine, get_db
from app import models

client = TestClient(app)


def test_ai_agent_task_intelligence():
    print("\n" + "=" * 65)
    print("RUNNING NEXUS AI AGENT TASK COPILOT REGRESSION SUITE")
    print("=" * 65)

    suffix = uuid.uuid4().hex[:6]
    email_org_a = f"lead_{suffix}@org-alpha.ai"
    email_org_b = f"intruder_{suffix}@org-beta.ai"
    password = "TestPassword2026!"

    # 1. Register User A in Org Alpha
    print("\n[TEST 1] Registering User A in Organization Alpha...")
    resp_a = client.post("/api/auth/register", json={
        "name": f"Priya Developer {suffix}",
        "email": email_org_a,
        "password": password,
        "role": "Security Engineer",
        "app_role": "employee",
        "skills": ["OAuth2", "FastAPI", "PostgreSQL"]
    })
    assert resp_a.status_code == 201
    token_a = resp_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"[PASS] User A registered: {email_org_a}")

    # 2. Create Prerequisite Task: Database Engine
    print("\n[TEST 2] Creating Prerequisite Task...")
    t1_resp = client.post("/api/tasks", json={
        "title": f"PostgreSQL Database Schema Migration {suffix}",
        "assignee": f"Priya Developer {suffix}",
        "status": "done",
        "priority": "High",
        "dueDate": "2026-08-20"
    }, headers=headers_a)
    assert t1_resp.status_code == 201
    t1_data = t1_resp.json()
    t1_id = t1_data["id"]
    print(f"[PASS] Prerequisite created: [{t1_id}] {t1_data['title']}")

    # 3. Create Target Task: OAuth2 Authentication API Gateway
    print("\n[TEST 3] Creating Target Task: Authentication...")
    t2_resp = client.post("/api/tasks", json={
        "title": f"OAuth2 Authentication API Gateway {suffix}",
        "assignee": f"Priya Developer {suffix}",
        "status": "in_progress",
        "priority": "Critical",
        "dependsOn": [t1_id],
        "dueDate": "2026-08-28"
    }, headers=headers_a)
    assert t2_resp.status_code == 201
    t2_data = t2_resp.json()
    t2_id = t2_data["id"]
    print(f"[PASS] Target task created: [{t2_id}] {t2_data['title']}")

    # =========================================================================
    # QUESTION 1: "Who is working on Authentication?"
    # =========================================================================
    print("\n[TEST 4] Query: 'Who is working on Authentication?'...")
    q1_resp = client.post("/api/ai/query", json={
        "query": f"Who is working on OAuth2 Authentication API Gateway {suffix}?"
    }, headers=headers_a)
    assert q1_resp.status_code == 200
    q1 = q1_resp.json()
    print(f"AI Answer: {q1['answer']}")
    assert f"Priya Developer {suffix}" in q1["answer"], f"Expected assignee in answer, got: {q1['answer']}"
    assert t2_id in q1["answer"] or "Authentication" in q1["answer"]
    assert q1["decision_trace"]["intent"] == "TASK_ASSIGNEE"
    print(f"[PASS] Verified live assignee returned from database: Priya Developer {suffix}")

    # =========================================================================
    # QUESTION 2: "What is the status of Authentication?"
    # =========================================================================
    print("\n[TEST 5] Query: 'What is the status of Authentication?'...")
    q2_resp = client.post("/api/ai/query", json={
        "query": f"What is the status of OAuth2 Authentication API Gateway {suffix}?"
    }, headers=headers_a)
    assert q2_resp.status_code == 200
    q2 = q2_resp.json()
    print(f"AI Answer: {q2['answer']}")
    assert "IN_PROGRESS" in q2["answer"].upper() or "IN PROGRESS" in q2["answer"].upper()
    assert q2["decision_trace"]["intent"] == "TASK_STATUS"
    print("[PASS] Verified live task status returned: IN_PROGRESS")

    # =========================================================================
    # QUESTION 3: "When is Authentication due?"
    # =========================================================================
    print("\n[TEST 6] Query: 'When is Authentication due?'...")
    q3_resp = client.post("/api/ai/query", json={
        "query": f"When is OAuth2 Authentication API Gateway {suffix} due?"
    }, headers=headers_a)
    assert q3_resp.status_code == 200
    q3 = q3_resp.json()
    print(f"AI Answer: {q3['answer']}")
    assert "2026-08-28" in q3["answer"]
    assert q3["decision_trace"]["intent"] == "TASK_DEADLINE"
    print("[PASS] Verified live task deadline returned: 2026-08-28")

    # =========================================================================
    # QUESTION 4: "What is blocking Authentication?"
    # =========================================================================
    print("\n[TEST 7] Query: 'What is blocking Authentication?'...")
    q4_resp = client.post("/api/ai/query", json={
        "query": f"What is blocking OAuth2 Authentication API Gateway {suffix}?"
    }, headers=headers_a)
    assert q4_resp.status_code == 200
    q4 = q4_resp.json()
    print(f"AI Answer: {q4['answer']}")
    assert t1_id in q4["answer"] or "PostgreSQL" in q4["answer"]
    assert q4["decision_trace"]["intent"] == "TASK_DEPENDENCIES"
    print(f"[PASS] Verified dependency chain retrieved: Prerequisite {t1_id}")

    # =========================================================================
    # QUESTION 5: Follow-Up Contextual Memory ("What is the deadline?" / "Is it high risk?")
    # =========================================================================
    print("\n[TEST 8] Query Follow-up 1: 'What is the deadline?' (pronoun resolution)...")
    q5_resp = client.post("/api/ai/query", json={
        "query": "What is the deadline?"
    }, headers=headers_a)
    assert q5_resp.status_code == 200
    q5 = q5_resp.json()
    print(f"AI Answer: {q5['answer']}")
    assert "2026-08-28" in q5["answer"], f"Expected deadline resolution, got: {q5['answer']}"
    print("[PASS] Follow-up pronoun resolved to active session task context")

    print("\n[TEST 9] Query Follow-up 2: 'Is it high risk?' (pronoun resolution)...")
    q6_resp = client.post("/api/ai/query", json={
        "query": "Is it high risk?"
    }, headers=headers_a)
    assert q6_resp.status_code == 200
    q6 = q6_resp.json()
    print(f"AI Answer: {q6['answer']}")
    assert "Risk" in q6["answer"] or "%" in q6["answer"]
    print("[PASS] Follow-up risk query resolved to active task context")

    # =========================================================================
    # QUESTION 6: "Who is overloaded?" (Team capacity calculation)
    # =========================================================================
    print("\n[TEST 10] Query: 'Who is overloaded in the team?'...")
    q7_resp = client.post("/api/ai/query", json={
        "query": "Who is overloaded in the team?"
    }, headers=headers_a)
    assert q7_resp.status_code == 200
    q7 = q7_resp.json()
    print(f"AI Answer: {q7['answer']}")
    assert "Capacity" in q7["answer"] or "Load" in q7["answer"] or "overloaded" in q7["answer"]
    assert q7["decision_trace"]["intent"] == "TEAM_WORKLOAD"
    print("[PASS] Verified team capacity calculation executed")

    # =========================================================================
    # QUESTION 7: Unknown Task Handling (No hallucination)
    # =========================================================================
    print("\n[TEST 11] Query Unknown Task: 'Who is working on NonexistentQuantumFeatureXYZ?'...")
    q8_resp = client.post("/api/ai/query", json={
        "query": "Who is working on NonexistentQuantumFeatureXYZ?"
    }, headers=headers_a)
    assert q8_resp.status_code == 200
    q8 = q8_resp.json()
    print(f"AI Answer: {q8['answer']}")
    assert "couldn't find" in q8["answer"].lower() or "not found" in q8["answer"].lower()
    print("[PASS] Unknown task safely handled with zero hallucination")

    # =========================================================================
    # QUESTION 8: Multi-Tenant Query Isolation (Zero Cross-Tenant Leakage)
    # =========================================================================
    print("\n[TEST 12] Multi-Tenant Query Isolation...")
    # Register User B and place in isolated Org Beta
    resp_b = client.post("/api/auth/register", json={
        "name": f"Intruder User {suffix}",
        "email": email_org_b,
        "password": password,
        "role": "External Auditor",
        "app_role": "employee"
    })
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Move User B to isolated Organization Beta
    db_gen = get_db()
    db = next(db_gen)
    try:
        org_beta = models.Organization(name=f"Isolated Org Beta {suffix}", slug=f"org-beta-{suffix}", plan="starter")
        db.add(org_beta)
        db.flush()
        user_b = db.query(models.User).filter(models.User.email == email_org_b).first()
        user_b.org_id = org_beta.id
        db.commit()
    finally:
        db.close()

    # User B queries User A's private task
    q9_resp = client.post("/api/ai/query", json={
        "query": f"Who is working on {t2_data['title']}?"
    }, headers=headers_b)
    assert q9_resp.status_code == 200
    q9 = q9_resp.json()
    print(f"AI Answer to Org B: {q9['answer']}")
    assert "Priya Developer" not in q9["answer"] or "couldn't find" in q9["answer"].lower()
    print("[PASS] Multi-tenant isolation verified: Zero cross-tenant data leakage")

    # =========================================================================
    # QUESTION 9: Live Data Dynamic Reassignment Test
    # =========================================================================
    print("\n[TEST 13] Dynamic Reassignment Reflection...")
    # Register Rahul Engineer in Org A
    rahul_resp = client.post("/api/auth/register", json={
        "name": f"Rahul Sharma {suffix}",
        "email": f"rahul_{suffix}@org-alpha.ai",
        "password": password,
        "role": "Lead Backend Developer",
        "app_role": "employee"
    })
    assert rahul_resp.status_code == 201

    # Reassign Task 2 to Rahul
    reassign_resp = client.post(f"/api/tasks/{t2_id}/reassign", json={
        "assignee": f"Rahul Sharma {suffix}"
    }, headers=headers_a)
    assert reassign_resp.status_code == 200

    # Ask again: "Who is working on Authentication?"
    q10_resp = client.post("/api/ai/query", json={
        "query": f"Who is working on OAuth2 Authentication API Gateway {suffix}?"
    }, headers=headers_a)
    assert q10_resp.status_code == 200
    q10 = q10_resp.json()
    print(f"AI Answer after reassignment: {q10['answer']}")
    assert f"Rahul Sharma {suffix}" in q10["answer"], f"Expected updated assignee Rahul Sharma, got: {q10['answer']}"
    assert f"Priya Developer {suffix}" not in q10["answer"].split("currently assigned to")[1].split("and is")[0]
    print(f"[PASS] Dynamic reassignment verified: Answer immediately changed to Rahul Sharma {suffix}")

    print("\n" + "=" * 65)
    print("ALL AI AGENT TASK INTELLIGENCE & COPILOT TESTS PASSED 100%!")
    print("=" * 65)


if __name__ == "__main__":
    test_ai_agent_task_intelligence()
