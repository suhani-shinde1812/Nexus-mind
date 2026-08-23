"""
Nexus Mind — Cybersecurity, IAM & Multi-Tenancy Negative Test Suite
Tests:
- Cross-tenant organization isolation (Org A cannot see Org B resources)
- RBAC authorization barriers (Employee forbidden from admin audit logs)
- MFA Fernet encryption at rest
- MFA TOTP verification & invalid challenge rejection
- Single-use backup recovery code consumption
- Session revocation enforcement
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models, security
from seed_data import seed

seed()
client = TestClient(app)


def test_cybersecurity_and_tenant_isolation():
    db = SessionLocal()

    print("\n========================================================")
    print("RUNNING CYBERSECURITY, IAM & TENANT ISOLATION TEST SUITE")
    print("========================================================")

    # 1. Setup Tenant A and Tenant B
    org_a = db.query(models.Organization).filter(models.Organization.slug == "nexus-corp").first()
    org_b = db.query(models.Organization).filter(models.Organization.slug == "cyberdyne-defense").first()
    if not org_b:
        org_b = models.Organization(
            name="Cyberdyne Defense Systems",
            slug="cyberdyne-defense",
            plan="enterprise",
        )
        db.add(org_b)
        db.commit()
        db.refresh(org_b)

    # Create user in Org B
    user_b = db.query(models.User).filter(models.User.email == "john.connor@cyberdyne.io").first()
    if not user_b:
        user_b = models.User(
            org_id=org_b.id,
            name="John Connor",
            email="john.connor@cyberdyne.io",
            hashed_password=security.hash_password("defense-pass-2026"),
            role="Security Lead",
            app_role="team_lead",
            avatar="JC",
        )
        db.add(user_b)
        db.commit()
        db.refresh(user_b)

    # Create confidential project & task in Org B
    proj_b = db.query(models.Project).filter(models.Project.name == "Skynet Quarantine Protocol").first()
    if not proj_b:
        proj_b = models.Project(
            org_id=org_b.id,
            name="Skynet Quarantine Protocol",
            lead="John Connor",
            deadline="2026-12-31",
            progress=15,
        )
        db.add(proj_b)
        db.commit()
        db.refresh(proj_b)

    task_b = db.get(models.Task, "TASK-CYBER-01")
    if not task_b:
        task_b = models.Task(
            id="TASK-CYBER-01",
            org_id=org_b.id,
            title="Isolate Quantum Core",
            description="Strict containment in Org B.",
            project_id=proj_b.id,
            assignee_id=user_b.id,
            status="in_progress",
            priority="Critical",
        )
        db.add(task_b)
        db.commit()

    # Reset Sarah Jenkins MFA state for idempotent test run
    user_a = db.query(models.User).filter(models.User.email == "sarah.jenkins@nexusmind.ai").first()
    if user_a:
        user_a.mfa_enabled = False
        user_a.mfa_secret = None
        user_a.mfa_backup_codes = []
        db.commit()

    # Login as Sarah Jenkins (Org A - Lead)
    login_a = client.post(
        "/api/auth/login",
        data={"username": "sarah.jenkins@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Test Multi-Tenant Isolation: Org A user listing projects/tasks MUST NOT see Org B project/task
    print("\n[TEST 1] Testing Multi-Tenant Project & Task Query Isolation...")
    projects_res = client.get("/api/projects", headers=headers_a)
    assert projects_res.status_code == 200
    org_a_projects = [p["name"] for p in projects_res.json()]
    assert "Skynet Quarantine Protocol" not in org_a_projects, "Tenant leak: Org A saw Org B project!"

    tasks_res = client.get("/api/tasks", headers=headers_a)
    assert tasks_res.status_code == 200
    org_a_task_ids = [t["id"] for t in tasks_res.json()]
    assert "TASK-CYBER-01" not in org_a_task_ids, "Tenant leak: Org A saw Org B task!"
    print("[PASS] Multi-tenant data isolation verified (Zero cross-organization leakage)")

    # 3. Test RBAC Authorization Barrier: Employee cannot access Admin Audit Logs
    print("\n[TEST 2] Testing RBAC Authorization Boundaries (Negative Test)...")
    login_emp = client.post(
        "/api/auth/login",
        data={"username": "alex.vance@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    assert login_emp.status_code == 200
    token_emp = login_emp.json()["access_token"]
    headers_emp = {"Authorization": f"Bearer {token_emp}"}

    audit_res = client.get("/api/audit/logs", headers=headers_emp)
    assert audit_res.status_code == 403, f"RBAC escalation bug: Employee accessed audit logs (HTTP {audit_res.status_code})"
    print("[PASS] RBAC boundary enforced: Employee restricted from Admin Audit Logs (HTTP 403 Forbidden)")

    # 4. Test MFA TOTP Setup, Fernet Encryption At Rest & Backup Recovery Codes
    print("\n[TEST 3] Testing MFA Setup & Fernet Secret Encryption At Rest...")
    setup_res = client.post("/api/auth/mfa/setup", headers=headers_a)
    assert setup_res.status_code == 200
    secret = setup_res.json()["secret"]

    import pyotp
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()

    enable_res = client.post(
        "/api/auth/mfa/enable",
        json={"code": valid_code, "secret": secret},
        headers=headers_a,
    )
    assert enable_res.status_code == 200
    mfa_data = enable_res.json()
    assert mfa_data["status"] == "mfa_enabled"
    backup_codes = mfa_data["backup_codes"]
    assert len(backup_codes) == 8, f"Expected 8 backup codes, got {len(backup_codes)}"

    # Verify secret is Fernet-encrypted in the database, not raw base32
    db.expire_all()
    user_db = db.query(models.User).filter(models.User.email == "sarah.jenkins@nexusmind.ai").first()
    assert user_db.mfa_secret != secret, "Security flaw: MFA secret stored in plaintext!"
    assert user_db.mfa_secret.startswith("gAAAAA"), "MFA secret is not encrypted with Fernet format"
    assert security.decrypt_secret(user_db.mfa_secret) == secret, "Fernet secret decryption mismatch"
    print("[PASS] MFA secret encrypted at rest with Fernet AES-CBC ciphertext verified")

    # 5. Test MFA Challenge & Invalid Code Rejection
    print("\n[TEST 4] Testing MFA Challenge & Negative Code Validation...")
    login_mfa = client.post(
        "/api/auth/login",
        data={"username": "sarah.jenkins@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    assert login_mfa.status_code == 200
    mfa_payload = login_mfa.json()
    assert mfa_payload["mfa_required"] is True
    temp_token = mfa_payload["temp_token"]

    # Try invalid code
    bad_verify = client.post(
        "/api/auth/mfa/verify",
        json={"code": "000000", "temp_token": temp_token},
    )
    assert bad_verify.status_code == 401, f"Security flaw: Invalid MFA code accepted (HTTP {bad_verify.status_code})"
    print("[PASS] Invalid MFA TOTP code safely rejected (HTTP 401 Unauthorized)")

    # 6. Test Single-Use Backup Recovery Code Consumption
    print("\n[TEST 5] Testing Single-Use Backup Recovery Code Login & Invalidation...")
    recovery_code = backup_codes[0]
    rec_verify = client.post(
        "/api/auth/mfa/verify",
        json={"code": recovery_code, "temp_token": temp_token},
    )
    assert rec_verify.status_code == 200, f"Backup code verification failed: {rec_verify.text}"
    tokens = rec_verify.json()
    assert "access_token" in tokens

    # Try reusing the exact same backup code on a new login -> MUST FAIL
    login_mfa2 = client.post(
        "/api/auth/login",
        data={"username": "sarah.jenkins@nexusmind.ai", "password": "nexus-demo-2026"},
    )
    temp_token2 = login_mfa2.json()["temp_token"]
    reuse_verify = client.post(
        "/api/auth/mfa/verify",
        json={"code": recovery_code, "temp_token": temp_token2},
    )
    assert reuse_verify.status_code == 401, "Security flaw: Single-use backup code was reused!"
    print("[PASS] Single-use backup recovery code successfully verified and consumed")

    # 7. Test Session Revocation
    print("\n[TEST 6] Testing Session Tracking & Remote Token Revocation...")
    refresh_token = tokens["refresh_token"]
    rev_res = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert rev_res.status_code == 200

    # Invalidate session in DB
    ref_hash = security.hash_token(refresh_token)
    db.query(models.UserSession).filter(models.UserSession.refresh_token_hash == ref_hash).update({"is_revoked": True})
    db.commit()

    rev_check = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert rev_check.status_code == 401, "Security flaw: Revoked session was allowed to refresh tokens!"
    # 8. Test Unauthorized Document RAG Retrieval Isolation (Org A cannot retrieve Org B confidential documents)
    print("\n[TEST 7] Testing Unauthorized Document RAG Retrieval Isolation...")
    # Add confidential doc in Org B
    doc_b = models.Document(
        org_id=org_b.id,
        title="Classified Skynet Defense Blueprint",
        filename="classified_defense.md",
        file_type="md",
        summary="Strictly restricted to Cyberdyne Defense.",
    )
    db.add(doc_b)
    db.flush()

    chunk_b = models.DocumentChunk(
        org_id=org_b.id,
        document_id=doc_b.id,
        chunk_index=0,
        content="Secret quantum coordinates and classified defense protocols.",
        section_title="Classified",
        embedding_vector=[0.5] * 256,
    )
    db.add(chunk_b)
    db.commit()

    # Org A user executes RAG query searching for classified defense blueprint
    rag_leak_check = client.post(
        "/api/documents/query",
        json={"query": "classified defense blueprint", "top_k": 5},
        headers=headers_a,
    )
    assert rag_leak_check.status_code == 200
    rag_data = rag_leak_check.json()
    citations = [c.get("document_title") for c in rag_data.get("citations", [])]
    assert "Classified Skynet Defense Blueprint" not in citations, "Security leak: Org A retrieved Org B confidential document via RAG!"
    print("[PASS] Unauthorized Document RAG Isolation verified (Zero cross-tenant vector leakage)")

    # 9. Test Invalid GitHub Webhook Signature Rejection
    print("\n[TEST 8] Testing Invalid GitHub Webhook Signature Rejection...")
    webhook_leak = client.post(
        "/api/integrations/github/webhook",
        content=b'{"action":"push"}',
        headers={
            "X-Hub-Signature-256": "sha256=invalid0000000000000000000000000000000000000000000000000000000000",
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        },
    )
    assert webhook_leak.status_code == 401, f"Security flaw: Invalid webhook accepted (HTTP {webhook_leak.status_code})"
    print("[PASS] Invalid GitHub webhook HMAC signature rejected with HTTP 401 Unauthorized")

    db.close()
    print("\n========================================================")
    print("ALL 8 NEGATIVE CYBERSECURITY & TENANT ISOLATION TESTS PASSED 100%!")
    print("========================================================")


if __name__ == "__main__":
    test_cybersecurity_and_tenant_isolation()

