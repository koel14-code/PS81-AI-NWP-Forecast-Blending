# ======================================================================
#  SkyBlend AI — One-Command Startup Script (Windows PowerShell)
#  Usage:  .\nwp.ps1   or   .\nwp
#  Starts the FastAPI backend + React/Vite frontend in parallel.
#  Auto-detects Python, virtual environment, and Node dependencies.
# ======================================================================

param (
    [switch]$Force,
    [switch]$Train,
    [switch]$RebuildAll
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "         SkyBlend AI — NWP Forecast Blending System                   " -ForegroundColor Cyan
Write-Host "                   SIH Problem Statement PS81                         " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Check Python ───────────────────────────────────────────────────
Write-Host "-- Checking Python --" -ForegroundColor Gray
$PythonCmd = $null
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
}

if (-not $PythonCmd) {
    Write-Host "[ERROR] Python 3.10+ is required but not found in PATH." -ForegroundColor Red
    Write-Host "        Download from https://www.python.org/downloads/"
    Write-Host "        Be sure to check 'Add Python to PATH'."
    exit 1
}

$PyVer = & $PythonCmd --version 2>&1
Write-Host "[OK] Found $PyVer ($PythonCmd)" -ForegroundColor Green

# ── 2. Check Node.js & npm ─────────────────────────────────────────────
Write-Host "`n-- Checking Node.js & npm --" -ForegroundColor Gray

# If node not in current session PATH, check standard install locations
if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    $CommonNodePaths = @(
        "C:\Program Files\nodejs",
        "C:\Program Files (x86)\nodejs",
        "$env:LOCALAPPDATA\Programs\node"
    )
    foreach ($p in $CommonNodePaths) {
        if (Test-Path "$p\node.exe") {
            $env:PATH = "$p;$env:PATH"
            break
        }
    }
}

if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    Write-Host "`n======================================================================" -ForegroundColor Red
    Write-Host "[ERROR] Node.js is required to run the React frontend, but was not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Node.js on Windows:" -ForegroundColor Yellow
    Write-Host "  Option A: Run in PowerShell:" -ForegroundColor Yellow
    Write-Host "            winget install OpenJS.NodeJS.LTS" -ForegroundColor White
    Write-Host "  Option B: Download the LTS installer from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing, restart your terminal and re-run .\nwp.ps1" -ForegroundColor Yellow
    Write-Host "======================================================================`n" -ForegroundColor Red
    exit 1
}

$NodeVer = & node --version
Write-Host "[OK] Found Node.js $NodeVer" -ForegroundColor Green

if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] npm was not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
$NpmVer = & npm --version
Write-Host "[OK] Found npm $NpmVer" -ForegroundColor Green

# ── 3. Virtual Environment ────────────────────────────────────────────
Write-Host "`n-- Setting up Python environment --" -ForegroundColor Gray
$VenvDir = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
    if (Test-Path "$ProjectRoot\venv\Scripts\python.exe") {
        $VenvDir = Join-Path $ProjectRoot "venv"
    }
}

if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
    Write-Host "[INFO] Creating virtual environment at $VenvDir ..." -ForegroundColor Cyan
    & $PythonCmd -m venv $VenvDir
    Write-Host "[OK] Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment found at $VenvDir" -ForegroundColor Green
}

$PyExe = Join-Path $VenvDir "Scripts\python.exe"

# ── 4. Python Dependencies ────────────────────────────────────────────
Write-Host "`n-- Checking Python dependencies --" -ForegroundColor Gray
$TestDeps = & $PyExe -c "import fastapi, uvicorn, pandas, sklearn, joblib" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Installing runtime Python dependencies..." -ForegroundColor Yellow
    if (Test-Path "$ProjectRoot\requirements.runtime.txt") {
        & $PyExe -m pip install -r "$ProjectRoot\requirements.runtime.txt" --quiet
    } elseif (Test-Path "$ProjectRoot\requirements.txt") {
        & $PyExe -m pip install -r "$ProjectRoot\requirements.txt" --quiet
    }
    Write-Host "[OK] Python dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[OK] All Python dependencies are installed." -ForegroundColor Green
}

# ── 5. Frontend Dependencies ──────────────────────────────────────────
Write-Host "`n-- Checking frontend dependencies --" -ForegroundColor Gray
$FrontendDir = Join-Path $ProjectRoot "frontend"
if (-not (Test-Path "$FrontendDir\node_modules")) {
    Write-Host "[WARN] Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
    Push-Location $FrontendDir
    & npm install --silent
    Pop-Location
    Write-Host "[OK] Frontend dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[OK] Frontend dependencies are installed." -ForegroundColor Green
}

# ── 6. Pre-flight: Data sources & Model weights ───────────────────────
Write-Host "`n-- Pre-flight: Data sources and model weights --" -ForegroundColor Gray
$PrepArgs = @()
if ($Force -or $RebuildAll) { $PrepArgs += "--force" }
if ($Train) { $PrepArgs += "--train" }

& $PyExe "$ProjectRoot\scripts\prepare_environment.py" @PrepArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Pipeline environment preparation failed." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Datasets and model weights are verified." -ForegroundColor Green

# ── 7. Start Services ─────────────────────────────────────────────────
Write-Host "`n-- Starting SkyBlend AI Services --" -ForegroundColor Gray

$BackendHost = "127.0.0.1"
$BackendPort = 8000
$FrontendPort = 5173

$BackendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k title SkyBlend-Backend && `"$PyExe`" -m uvicorn src.api.main:app --host $BackendHost --port $BackendPort --reload --log-level info" -PassThru
Start-Sleep -Seconds 2

Push-Location $FrontendDir
$FrontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k title SkyBlend-Frontend && npm run dev" -PassThru
Pop-Location
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "               SkyBlend AI is up and running!                         " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "   Frontend:  http://localhost:$FrontendPort" -ForegroundColor Cyan
Write-Host "   Backend:   http://${BackendHost}:${BackendPort}" -ForegroundColor Cyan
Write-Host "   API Docs:  http://${BackendHost}:${BackendPort}/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Backend and Frontend are running in separate terminal windows."
Write-Host "   Press any key or Ctrl+C to stop all services..."
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

try {
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} catch {
    # If in non-interactive terminal, wait on process
    Wait-Process -Id $BackendProcess.Id -ErrorAction SilentlyContinue
}

Write-Host "`nStopping SkyBlend AI..." -ForegroundColor Yellow
Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $FrontendProcess.Id -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object { $_.MainWindowTitle -like "SkyBlend-*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "[OK] All services stopped." -ForegroundColor Green
