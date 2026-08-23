#!/usr/bin/env bash
# ==============================================================================
# Nexus Mind Enterprise — Linux/macOS Production Deployment Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "======================================================================"
echo "  NEXUS MIND ENTERPRISE — PRODUCTION DEPLOYMENT ENGINE"
echo "======================================================================"
echo ""

# 1. Environment Validation
echo "[STEP 1/5] Validating Python & Node environment..."
PYTHON_BIN="$SCRIPT_DIR/backend/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

$PYTHON_BIN --version
npm --version

# 2. Build Frontend Production Bundle
echo -e "\n[STEP 2/5] Compiling Web Production Bundle (Vite)..."
cd "$SCRIPT_DIR/web"
npm install --no-audit --no-fund
npm run build

# 3. Database Schema Migrations & Seeding
echo -e "\n[STEP 3/5] Running Database Schema Migrations & Seeding..."
cd "$SCRIPT_DIR/backend"
$PYTHON_BIN seed_data.py

# 4. Verification Tests
echo -e "\n[STEP 4/5] Running Automated Zero-Regression Suite..."
$PYTHON_BIN tests/regression/test_full_regression.py
$PYTHON_BIN tests/test_security_isolation.py

# 5. Launch Server
echo -e "\n[STEP 5/5] Launching Nexus Mind Unified Production Platform..."
echo "======================================================================"
echo "  PLATFORM ONLINE AT: http://localhost:8000"
echo "  • Web Dashboard & Task Graph : http://localhost:8000"
echo "  • Swagger / OpenAPI Docs     : http://localhost:8000/docs"
echo "  • Prometheus Metrics Scraping: http://localhost:8000/metrics"
echo "======================================================================"
echo ""

exec $PYTHON_BIN -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
