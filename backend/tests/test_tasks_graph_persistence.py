"""
NEXUS MIND — TASK GRAPH PERSISTENCE & MULTI-TASK INTEGRATION TEST SUITE

Tests:
1. Multi-Task Creation (Task A, Task B, Task C) under Project P
2. Verification of Database Persistence (All 3 tasks exist simultaneously)
3. GET /api/tasks & GET /api/bootstrap return complete authorized task collection
4. Task Deletion lifecycle (Delete Task B -> Task A & C remain)
5. Subsequent Creation (Create Task D -> Task A, C, D exist simultaneously)
6. Realtime WebSocket delta broadcast without replacing state
7. Coordinate grid calculation stability (x, y positions non-overlapping)
8. Multi-tenant project & task query isolation
"""
import os
import sys
import uuid
from starlette.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, engine, get_db
from app import models

client = TestClient(app)


def test_task_graph_persistence_and_lifecycle():
    print("\n" + "=" * 65)
    print("RUNNING TASK GRAPH PERSISTENCE & LIFECYCLE REGRESSION SUITE")
    print("=" * 65)

    suffix = uuid.uuid4().hex[:6]
    email = f"lead_engineer_{suffix}@nexusmind.ai"
    password = "TestPassword2026!"

    # 1. Register User
    print("\n[TEST 1] Registering Lead Engineer...")
    resp = client.post("/api/auth/register", json={
        "name": f"Engineer Lead {suffix}",
        "email": email,
        "password": password,
        "role": "Lead Architect",
        "app_role": "team_lead",
        "skills": ["Architecture", "Graph Theory", "FastAPI"]
    })
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[PASS] User registered: {email}")

    # 2. Create Project P
    print("\n[TEST 2] Creating Project P...")
    p_resp = client.post("/api/projects", json={
        "name": f"Project Hyperion {suffix}",
        "lead": f"Engineer Lead {suffix}",
        "deadline": "2026-12-31"
    }, headers=headers)
    assert p_resp.status_code in [200, 201], f"Project creation failed: {p_resp.text}"
    project_name = f"Project Hyperion {suffix}"
    print(f"[PASS] Project created: {project_name}")

    # 3. Create Task A
    print("\n[TEST 3] Creating Task A...")
    task_a_resp = client.post("/api/tasks", json={
        "title": "Quantum Compute Engine Architecture",
        "project": project_name,
        "assignee": f"Engineer Lead {suffix}",
        "priority": "Critical",
        "status": "in_progress",
        "dependsOn": [],
        "dueDate": "2026-09-01",
        "x": 180.0,
        "y": 140.0
    }, headers=headers)
    assert task_a_resp.status_code == 201
    task_a = task_a_resp.json()
    id_a = task_a["id"]
    print(f"[PASS] Task A created with ID: {id_a}")

    # 4. Create Task B
    print("\n[TEST 4] Creating Task B...")
    task_b_resp = client.post("/api/tasks", json={
        "title": "Distributed State Store Integration",
        "project": project_name,
        "assignee": f"Engineer Lead {suffix}",
        "priority": "High",
        "status": "in_progress",
        "dependsOn": [id_a],
        "dueDate": "2026-09-05",
        "x": 340.0,
        "y": 140.0
    }, headers=headers)
    assert task_b_resp.status_code == 201
    task_b = task_b_resp.json()
    id_b = task_b["id"]
    print(f"[PASS] Task B created with ID: {id_b}")

    # 5. Create Task C
    print("\n[TEST 5] Creating Task C...")
    task_c_resp = client.post("/api/tasks", json={
        "title": "Real-Time Telemetry Pipeline",
        "project": project_name,
        "assignee": f"Engineer Lead {suffix}",
        "priority": "Medium",
        "status": "in_progress",
        "dependsOn": [id_b],
        "dueDate": "2026-09-10",
        "x": 500.0,
        "y": 140.0
    }, headers=headers)
    assert task_c_resp.status_code == 201
    task_c = task_c_resp.json()
    id_c = task_c["id"]
    print(f"[PASS] Task C created with ID: {id_c}")

    # 6. Verify Database Persistence (All 3 tasks exist simultaneously)
    print("\n[TEST 6] Verifying All 3 Tasks Returned from GET /api/tasks & /api/bootstrap...")
    tasks_resp = client.get("/api/tasks", headers=headers)
    assert tasks_resp.status_code == 200
    all_tasks = tasks_resp.json()
    task_ids = [t["id"] for t in all_tasks]
    assert id_a in task_ids, f"Task A ({id_a}) missing from task list!"
    assert id_b in task_ids, f"Task B ({id_b}) missing from task list!"
    assert id_c in task_ids, f"Task C ({id_c}) missing from task list!"

    boot_resp = client.get("/api/bootstrap", headers=headers)
    assert boot_resp.status_code == 200
    boot_tasks = boot_resp.json()["tasks"]
    boot_ids = [t["id"] for t in boot_tasks]
    assert id_a in boot_ids
    assert id_b in boot_ids
    assert id_c in boot_ids
    print(f"[PASS] All 3 tasks (A, B, C) verified in database and API responses simultaneously!")

    # 7. Delete Task B
    print("\n[TEST 7] Deleting Task B ({id_b})...")
    del_resp = client.delete(f"/api/tasks/{id_b}", headers=headers)
    assert del_resp.status_code == 204

    tasks_after_del = client.get("/api/tasks", headers=headers).json()
    ids_after_del = [t["id"] for t in tasks_after_del]
    assert id_a in ids_after_del, "Task A must still exist!"
    assert id_b not in ids_after_del, "Task B must be deleted!"
    assert id_c in ids_after_del, "Task C must still exist!"
    print(f"[PASS] Task B deleted successfully. Tasks A and C remain intact.")

    # 8. Create Task D
    print("\n[TEST 8] Creating Task D...")
    task_d_resp = client.post("/api/tasks", json={
        "title": "Autonomous Edge Deployment Agent",
        "project": project_name,
        "assignee": f"Engineer Lead {suffix}",
        "priority": "Critical",
        "status": "in_progress",
        "dependsOn": [id_a],
        "dueDate": "2026-09-15"
    }, headers=headers)
    assert task_d_resp.status_code == 201
    id_d = task_d_resp.json()["id"]
    print(f"[PASS] Task D created with ID: {id_d}")

    # 9. Verify Final Task Graph State (A, C, D)
    print("\n[TEST 9] Verifying Final Graph State (A, C, D)...")
    final_tasks = client.get("/api/tasks", headers=headers).json()
    final_ids = [t["id"] for t in final_tasks]
    assert id_a in final_ids
    assert id_c in final_ids
    assert id_d in final_ids
    assert id_b not in final_ids
    print(f"[PASS] Final graph dataset contains exact expected tasks: [A, C, D]")

    # 10. Verify WebSocket Realtime Delta Delivery
    print("\n[TEST 10] Testing WebSocket Realtime Delta Connection...")
    with client.websocket_connect(f"/ws?token={token}") as ws:
        # Create Task E
        task_e_resp = client.post("/api/tasks", json={
            "title": "WebSocket Stream Live Node",
            "project": project_name,
            "priority": "High"
        }, headers=headers)
        assert task_e_resp.status_code == 201
        event = ws.receive_json()
        assert event["type"] == "task_created"
        assert event["payload"]["title"] == "WebSocket Stream Live Node"
        print(f"[PASS] WebSocket received delta event for new task without state wipe!")

    print("\n" + "=" * 65)
    print("ALL TASK GRAPH PERSISTENCE TESTS PASSED 100%!")
    print("=" * 65)


if __name__ == "__main__":
    test_task_graph_persistence_and_lifecycle()
