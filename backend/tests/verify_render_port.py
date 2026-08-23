"""
Verify Nexus Mind Production Dynamic PORT binding on PORT=10000.
Tests:
- Server binding to 0.0.0.0:10000 (Render dynamic port)
- GET http://localhost:10000/ (Vite Production SPA)
- GET http://localhost:10000/docs (OpenAPI Swagger UI)
- GET http://localhost:10000/metrics (Prometheus Observability)
- GET http://localhost:10000/api/health (API Health Endpoint)
- WebSocket real handshake to ws://localhost:10000/ws?token=<jwt>
"""
import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import websockets

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

python_exe = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")

if not os.path.exists(python_exe):
    python_exe = sys.executable

async def test_websocket_connection(token: str):
    uri = f"ws://127.0.0.1:10000/ws?token={token}"
    async with websockets.connect(uri) as ws:
        assert ws.open is True
        print("[PASS] WebSocket real-time connection established and active!")


def main():
    print("\n========================================================")
    print("TESTING PRODUCTION STARTUP WITH PORT=10000")
    print("========================================================")

    # Ensure test user MFA is clean for direct password login
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

    env = os.environ.copy()
    env["PORT"] = "10000"
    env["HOST"] = "0.0.0.0"


    cmd = [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
    print(f"Launching process: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=backend_dir, env=env)

    try:
        # Poll http://127.0.0.1:10000/api/health until ready (up to 20s)
        ready = False
        health_data = None
        for attempt in range(40):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen("http://127.0.0.1:10000/api/health", timeout=2) as resp:
                    if resp.status == 200:
                        health_data = json.loads(resp.read().decode("utf-8"))
                        ready = True
                        break
            except Exception:
                pass

        if not ready:
            raise RuntimeError("Server failed to respond on http://127.0.0.1:10000 within 20 seconds")

        print(f"[PASS] Server is listening on http://0.0.0.0:10000")
        print(f"[PASS] GET /api/health -> HTTP 200: {health_data}")

        # 1. Test GET / (SPA index.html)
        with urllib.request.urlopen("http://127.0.0.1:10000/", timeout=3) as resp:
            html_content = resp.read().decode("utf-8")
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            assert "<!doctype html>" in html_content.lower() or "nexus" in html_content.lower()
            print(f"[PASS] GET / (Vite Production SPA) -> HTTP 200 (Length: {len(html_content)} bytes)")

        # 2. Test GET /docs (Swagger UI)
        with urllib.request.urlopen("http://127.0.0.1:10000/docs", timeout=3) as resp:
            docs_content = resp.read().decode("utf-8")
            assert resp.status == 200
            assert "swagger" in docs_content.lower()
            print(f"[PASS] GET /docs (OpenAPI Swagger UI) -> HTTP 200 (Length: {len(docs_content)} bytes)")

        # 3. Test GET /metrics (Prometheus)
        with urllib.request.urlopen("http://127.0.0.1:10000/metrics", timeout=3) as resp:
            metrics_content = resp.read().decode("utf-8")
            assert resp.status == 200
            assert "nexusmind_" in metrics_content
            print(f"[PASS] GET /metrics (Prometheus Observability) -> HTTP 200 (Length: {len(metrics_content)} bytes)")

        # 4. Authenticate & acquire JWT token
        login_data = urllib.parse.urlencode({
            "username": "sarah.jenkins@nexusmind.ai",
            "password": "nexus-demo-2026"
        }).encode("utf-8")
        login_req = urllib.request.Request("http://127.0.0.1:10000/api/auth/login", data=login_data, method="POST")
        with urllib.request.urlopen(login_req, timeout=3) as resp:
            auth_res = json.loads(resp.read().decode("utf-8"))
            token = auth_res.get("access_token")
            assert token is not None, "Missing access token in login response"
            print(f"[PASS] POST /api/auth/login -> HTTP 200 (Acquired JWT Token)")

        # 5. Real WebSocket Handshake & Connection Test
        asyncio.run(test_websocket_connection(token))

        print("\n========================================================")
        print("ALL VERIFICATION CHECKS ON PORT=10000 PASSED 100%!")
        print("========================================================")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
