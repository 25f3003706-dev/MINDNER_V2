param(
    [ValidateSet('start', 'test')]
    [string]$Mode = 'start'
)

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "   MINDNER - AI Caregiver & Dementia Assistance          " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$pipExe = Join-Path $PSScriptRoot ".venv\Scripts\pip.exe"
$uvicornExe = Join-Path $PSScriptRoot ".venv\Scripts\uvicorn.exe"
$pytestExe = Join-Path $PSScriptRoot ".venv\Scripts\pytest.exe"
$dbFile = Join-Path $PSScriptRoot "database\caregiver.db"
$seedScript = Join-Path $PSScriptRoot "database\seed.py"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[1/3] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[2/3] Installing Python dependencies..." -ForegroundColor Yellow
    & $pipExe install -r requirements.txt
} else {
    Write-Host "[1/3] Virtual environment verified (.venv)" -ForegroundColor Green
}

if ($Mode -eq 'test') {
    if (-not (Test-Path $pytestExe)) {
        Write-Host "[2/3] Installing pytest in the virtual environment..." -ForegroundColor Yellow
        & $pythonExe -m pip install pytest
    }

    Write-Host "[3/3] Running test suite..." -ForegroundColor Cyan
    & $pytestExe -v @args
    exit $LASTEXITCODE
}

if (-not (Test-Path $dbFile)) {
    Write-Host "[2/3] Initializing and seeding SQLite database..." -ForegroundColor Yellow
    & $pythonExe $seedScript
} else {
    Write-Host "[2/3] SQLite database ready ($dbFile)" -ForegroundColor Green
}

Write-Host "[3/3] Access Endpoints:" -ForegroundColor Green
Write-Host "   Frontend UI:   http://127.0.0.1:8000/frontend/home.html" -ForegroundColor Yellow
Write-Host "   Swagger Docs:  http://127.0.0.1:8000/api/v1/docs" -ForegroundColor Yellow
Write-Host "   Health Check:  http://127.0.0.1:8000/api/v1/health" -ForegroundColor Yellow

Write-Host "Opening Frontend in your web browser..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8000/frontend/home.html"

Write-Host ""
Write-Host "Server running on http://127.0.0.1:8000. Press Ctrl+C to stop." -ForegroundColor White
Write-Host ""

& $uvicornExe app.main:app --reload --host 127.0.0.1 --port 8000
