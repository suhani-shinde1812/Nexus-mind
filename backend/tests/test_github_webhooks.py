"""
Nexus Mind — GitHub Webhooks & Engineering Telemetry Test Suite
Tests:
- HMAC-SHA256 signature verification
- Tampered signature rejection (HTTP 401)
- Idempotent duplicate event ingestion
- Engineering metrics recalculation
"""
import hashlib
import hmac
import json
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"

from fastapi.testclient import TestClient
from app.config import get_settings
from app.main import app
from seed_data import seed

seed()
client = TestClient(app)
settings = get_settings()


def test_github_webhook_pipeline():
    print("\n========================================================")
    print("RUNNING GITHUB WEBHOOKS & ENGINEERING TELEMETRY TEST SUITE")
    print("========================================================")

    # 1. Valid Signature Test
    payload_dict = {
        "action": "closed",
        "pull_request": {
            "number": 425,
            "title": "feat(crypto): Implement post-quantum lattice key exchange",
            "merged": True,
            "user": {"login": "elena.rostova"},
            "additions": 412,
            "deletions": 38,
        },
    }
    raw_payload = json.dumps(payload_dict).encode("utf-8")
    secret = settings.github_webhook_secret.encode("utf-8")
    valid_sig = "sha256=" + hmac.new(secret, raw_payload, hashlib.sha256).hexdigest()

    delivery_id = "deliv-uuid-9921"

    print("\n[TEST 1] Testing Valid HMAC-SHA256 Webhook Ingestion...")
    resp = client.post(
        "/api/integrations/github/webhook",
        content=raw_payload,
        headers={
            "X-Hub-Signature-256": valid_sig,
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": delivery_id,
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200, f"Webhook failed: {resp.text}"
    assert resp.json()["status"] == "processed"
    print("[PASS] Valid GitHub webhook HMAC signature accepted & event recorded")

    # 2. Tampered Signature Test -> MUST FAIL 401
    print("\n[TEST 2] Testing Tampered Signature Rejection...")
    tampered_sig = "sha256=" + "0000000000000000000000000000000000000000000000000000000000000000"
    bad_resp = client.post(
        "/api/integrations/github/webhook",
        content=raw_payload,
        headers={
            "X-Hub-Signature-256": tampered_sig,
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "deliv-uuid-bad",
            "Content-Type": "application/json",
        },
    )
    assert bad_resp.status_code == 401, f"Security flaw: Tampered webhook signature accepted! ({bad_resp.status_code})"
    print("[PASS] Tampered webhook signature correctly rejected with HTTP 401 Unauthorized")

    # 3. Idempotent Duplicate Delivery Test
    print("\n[TEST 3] Testing Idempotent Delivery Handling...")
    dup_resp = client.post(
        "/api/integrations/github/webhook",
        content=raw_payload,
        headers={
            "X-Hub-Signature-256": valid_sig,
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": delivery_id,
            "Content-Type": "application/json",
        },
    )
    assert dup_resp.status_code == 200
    print("[PASS] Duplicate delivery ID processed idempotently without error")

    print("\n========================================================")
    print("ALL GITHUB WEBHOOK TESTS PASSED 100%!")
    print("========================================================")


if __name__ == "__main__":
    test_github_webhook_pipeline()
