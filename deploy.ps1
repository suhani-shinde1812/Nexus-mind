# ==============================================================================
# Nexus Mind Enterprise - Windows Production Deployment Automation Script
# ==============================================================================
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  NEXUS MIND ENTERPRISE - PRODUCTION DEPLOYMENT ENGINE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Environment and Dependency Validation
Write-Host "[STEP 1/5] Validating Python and Node.js environment..." -ForegroundColor Yellow
$PythonCmd = "$ScriptDir\backend\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonCmd)) {
    $PythonCmd = "python"
}

& $PythonCmd --version
npm --version

# 2. Build Frontend Production Bundle
Write-Host "`n[STEP 2/5] Compiling Web Production Bundle (Vite)..." -ForegroundColor Yellow
Set-Location "$ScriptDir\web"
npm run build

# 3. Database Schema Synchronization and Migration
Write-Host "`n[STEP 3/5] Running Database Schema Migrations and Seeding..." -ForegroundColor Yellow
Set-Location "$ScriptDir\backend"
& $PythonCmd seed_data.py

# 4. Execute Benchmark Verification
Write-Host "`n[STEP 4/5] Running Automated Zero-Regression Benchmark Suite..." -ForegroundColor Yellow
& $PythonCmd tests/regression/test_full_regression.py
& $PythonCmd tests/test_security_isolation.py

# 5. Launch Unified Single-Port Production Server
Write-Host "`n[STEP 5/5] Launching Nexus Mind Unified Production Platform..." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  PLATFORM ONLINE AT: http://localhost:8000" -ForegroundColor Green
Write-Host "  * Web Dashboard and Task Graph : http://localhost:8000" -ForegroundColor White
Write-Host "  * Swagger / OpenAPI Docs       : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * Prometheus Metrics Scraping  : http://localhost:8000/metrics" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

& $PythonCmd -m uvicorn app.main:app --host 0.0.0.0 --port 8000
