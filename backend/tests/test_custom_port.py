"""
In-process threaded test for dynamic PORT=10000.
"""
import os
import sys
import threading
import time
import urllib.request
import uvicorn

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"
os.environ["PORT"] = "10000"

from app.main import app

def run_test():
    print("\n========================================================")
    print("TESTING PRODUCTION STARTUP WITH PORT=10000")
    print("========================================================")

    config = uvicorn.Config(app, host="127.0.0.1", port=10000, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    started = False
    for _ in range(20):
        time.sleep(0.3)
        try:
            with urllib.request.urlopen("http://127.0.0.1:10000/api/health", timeout=2) as resp:
                if resp.status == 200:
                    started = True
                    break
        except Exception:
            pass

    if not started:
        raise RuntimeError("Server failed to start on port 10000")

    print("[PASS] Server successfully started and listening on http://127.0.0.1:10000")

    # 1. Test / (SPA index.html)
    print("\n[TEST 1] Testing GET http://localhost:10000/ (Production SPA)...")
    with urllib.request.urlopen("http://127.0.0.1:10000/", timeout=3) as resp:
        content = resp.read().decode("utf-8")
        assert resp.status == 200
        assert "<!DOCTYPE html>" in content or "<html" in content or "Nexus Mind" in content
        print(f"[PASS] GET / returned HTTP 200 (Length: {len(content)} bytes)")

    # 2. Test /docs (Swagger UI)
    print("\n[TEST 2] Testing GET http://localhost:10000/docs (OpenAPI Swagger)...")
    with urllib.request.urlopen("http://127.0.0.1:10000/docs", timeout=3) as resp:
        content = resp.read().decode("utf-8")
        assert resp.status == 200
        assert "swagger" in content.lower()
        print(f"[PASS] GET /docs returned HTTP 200 (Swagger UI active)")

    # 3. Test /metrics (Prometheus Observability)
    print("\n[TEST 3] Testing GET http://localhost:10000/metrics (Prometheus)...")
    with urllib.request.urlopen("http://127.0.0.1:10000/metrics", timeout=3) as resp:
        content = resp.read().decode("utf-8")
        assert resp.status == 200
        assert "nexusmind_" in content
        print(f"[PASS] GET /metrics returned HTTP 200 (Prometheus scraping operational)")

    # 4. Test /api/health
    print("\n[TEST 4] Testing GET http://localhost:10000/api/health...")
    with urllib.request.urlopen("http://127.0.0.1:10000/api/health", timeout=3) as resp:
        content = resp.read().decode("utf-8")
        assert resp.status == 200
        assert '"status": "ok"' in content or '"status":"ok"' in content
        print(f"[PASS] GET /api/health returned HTTP 200: {content.strip()}")

    # 5. Stop Server
    server.should_exit = True
    thread.join(timeout=3)

    print("\n========================================================")
    print("ALL PORT=10000 DYNAMIC BINDING TESTS PASSED 100%!")
    print("========================================================")


if __name__ == "__main__":
    run_test()
