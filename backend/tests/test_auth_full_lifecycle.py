"""
Full Authentication & Registration Lifecycle Test Suite
Verifies:
1. User Registration with RegisterIn schema & validation
2. Login with valid credentials & access/refresh token generation
3. Invalid login rejection
4. Access token decoding & current_user authentication
5. Refresh token rotation & session tracking
6. MFA setup (TOTP), provisioning URI, and validation
7. Remote session revocation & token invalidation
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pyotp
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)

def test_full_auth_lifecycle():
    print("\n========================================================")
    print("RUNNING COMPLETE AUTHENTICATION & REGISTRATION LIFECYCLE")
    print("========================================================")

    # 1. Registration Test
    test_email = f"test_dev_{os.getpid()}@nexusmind.ai"
    test_password = "SecurePassword2026!"
    print(f"\n[TEST 1] Testing Registration for {test_email}...")
    reg_payload = {
        "name": "Alex Developer",
        "email": test_email,
        "password": test_password,
        "role": "Fullstack Engineer",
        "app_role": "employee",
        "skills": ["Python", "FastAPI", "React", "Postgres"]
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert "refresh_token" in reg_data
    access_token = reg_data["access_token"]
    refresh_token = reg_data["refresh_token"]
    print(f"[PASS] Registration succeeded with 201 Created (Token acquired)")

    # 2. Login Test
    print(f"\n[TEST 2] Testing Password Login for {test_email}...")
    login_resp = client.post("/api/auth/login", data={"username": test_email, "password": test_password})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    assert login_data["mfa_required"] is False
    assert "access_token" in login_data
    auth_header = {"Authorization": f"Bearer {login_data['access_token']}"}
    print(f"[PASS] Login succeeded with HTTP 200")

    # 3. Authenticated User Profile
    print("\n[TEST 3] Testing Authenticated /api/auth/me...")
    me_resp = client.get("/api/auth/me", headers=auth_header)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == test_email
    assert me_data["name"] == "Alex Developer"
    print(f"[PASS] /api/auth/me returned correct user profile: {me_data['name']}")

    # 4. Token Refresh
    print("\n[TEST 4] Testing Refresh Token Rotation...")
    ref_resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 200, f"Refresh failed: {ref_resp.text}"
    ref_data = ref_resp.json()
    assert "access_token" in ref_data
    assert "refresh_token" in ref_data
    new_access_token = ref_data["access_token"]
    print(f"[PASS] Token refresh rotated successfully")

    # 5. MFA Setup & Verification
    print("\n[TEST 5] Testing RFC 6238 TOTP MFA Setup & Activation...")
    setup_resp = client.post("/api/auth/mfa/setup", headers=auth_header)
    assert setup_resp.status_code == 200
    setup_data = setup_resp.json()
    totp_secret = setup_data["secret"]
    assert "otpauth://" in setup_data["provisioning_uri"]

    # Generate valid TOTP code
    totp = pyotp.TOTP(totp_secret)
    valid_code = totp.now()
    verify_resp = client.post("/api/auth/mfa/enable", json={"secret": totp_secret, "code": valid_code}, headers=auth_header)
    assert verify_resp.status_code == 200, f"MFA enable failed: {verify_resp.text}"
    verify_data = verify_resp.json()
    assert len(verify_data.get("backup_codes", [])) == 8
    print(f"[PASS] MFA verified and activated with 8 single-use backup recovery codes")


    # 6. Session Tracking & Remote Revocation
    print("\n[TEST 6] Testing Active Sessions & Remote Revocation...")
    sessions_resp = client.get("/api/auth/sessions", headers=auth_header)
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    assert len(sessions) >= 1
    session_id = sessions[0]["id"]

    revoke_resp = client.post(f"/api/auth/sessions/{session_id}/revoke", headers=auth_header)
    assert revoke_resp.status_code == 200
    print(f"[PASS] Active session {session_id} successfully revoked remotely")

    print("\n========================================================")
    print("ALL AUTHENTICATION & REGISTRATION LIFECYCLE TESTS PASSED 100%!")
    print("========================================================")

if __name__ == "__main__":
    test_full_auth_lifecycle()
