@echo off
REM ══════════════════════════════════════════════════════════════════════
REM  SkyBlend AI — One-Command Startup Script (Windows)
REM  Usage:  .\nwp.bat   or   nwp
REM  Starts the FastAPI backend + React/Vite frontend in parallel.
REM  Auto-installs Python and Node dependencies if missing.
REM ══════════════════════════════════════════════════════════════════════
setlocal enabledelayedexpansion

REM ── Resolve project root ──────────────────────────────────────────
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM ── Banner ────────────────────────────────────────────────────────
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         SkyBlend AI — NWP Forecast Blending System          ║
echo ║                   SIH Problem Statement PS81                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ══════════════════════════════════════════════════════════════════
REM  1. CHECK PYTHON
REM ══════════════════════════════════════════════════════════════════
echo -- Checking Python --
set "PYTHON_CMD="

where python >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    set "PYTHON_CMD=python"
    goto :python_found
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=2 delims= " %%v in ('python3 --version 2^>^&1') do set "PY_VER=%%v"
    set "PYTHON_CMD=python3"
    goto :python_found
)

echo [ERROR] Python 3.10+ is required but not found.
echo         Install from https://www.python.org/downloads/
echo         Make sure to check "Add Python to PATH" during installation.
exit /b 1

:python_found
echo [OK] Found Python %PY_VER% (%PYTHON_CMD%)

REM ══════════════════════════════════════════════════════════════════
REM  2. CHECK NODE.JS
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Checking Node.js --

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is required but not found.
    echo         Install from https://nodejs.org/ (v18+ recommended^)
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do set "NODE_VER=%%v"
echo [OK] Found Node.js %NODE_VER%

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is required but not found. It should come with Node.js.
    exit /b 1
)
for /f "tokens=*" %%v in ('npm --version') do set "NPM_VER=%%v"
echo [OK] Found npm %NPM_VER%

REM ══════════════════════════════════════════════════════════════════
REM  3. PYTHON VIRTUAL ENVIRONMENT
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Setting up Python environment --

set "VENV_DIR=%PROJECT_ROOT%venv"
if exist "%PROJECT_ROOT%.venv\Scripts\activate.bat" (
    set "VENV_DIR=%PROJECT_ROOT%.venv"
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment at %VENV_DIR% ...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment found at %VENV_DIR%
)

REM Activate
call "%VENV_DIR%\Scripts\activate.bat"
echo [OK] Virtual environment activated.

REM ══════════════════════════════════════════════════════════════════
REM  4. INSTALL PYTHON DEPENDENCIES
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Checking Python dependencies --

python -c "import fastapi, uvicorn, pandas, sklearn, joblib" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Some Python dependencies are missing. Installing...
    if exist "%PROJECT_ROOT%requirements.runtime.txt" (
        pip install --upgrade pip --quiet >nul 2>&1
        pip install -r "%PROJECT_ROOT%requirements.runtime.txt" --quiet
    ) else if exist "%PROJECT_ROOT%requirements.txt" (
        pip install --upgrade pip --quiet >nul 2>&1
        pip install -r "%PROJECT_ROOT%requirements.txt" --quiet
    ) else (
        echo [ERROR] No requirements file found.
        exit /b 1
    )
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Python dependencies.
        exit /b 1
    )
    echo [OK] Python dependencies installed.
) else (
    echo [OK] All Python dependencies are installed.
)

REM ══════════════════════════════════════════════════════════════════
REM  5. INSTALL FRONTEND DEPENDENCIES
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Checking frontend dependencies --

set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at %FRONTEND_DIR%
    exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [WARN] Node modules not found. Installing frontend dependencies...
    pushd "%FRONTEND_DIR%"
    npm install --silent
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies.
        popd
        exit /b 1
    )
    popd
    echo [OK] Frontend dependencies installed.
) else (
    echo [OK] Frontend dependencies are installed.
)

REM ══════════════════════════════════════════════════════════════════
REM  6. PRE-FLIGHT: CHECK DATA FILES
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Pre-flight checks --

set "DATA_DIR=%PROJECT_ROOT%data\processed"
set "MISSING_DATA=0"

if exist "%DATA_DIR%\multilocation_rainfall_ml_features_2023_06_to_2024_05.csv" (
    echo [OK] Rainfall features dataset found.
) else (
    echo [WARN] Rainfall features dataset not found — precipitation may be limited.
    set "MISSING_DATA=1"
)

if exist "%DATA_DIR%\multilocation_temperature_forecast_inputs.csv" (
    echo [OK] Temperature inputs dataset found.
) else (
    echo [WARN] Temperature inputs not found — temperature endpoints may return errors.
    set "MISSING_DATA=1"
)

if exist "%DATA_DIR%\multilocation_wind_forecast_inputs.csv" (
    echo [OK] Wind inputs dataset found.
) else (
    echo [WARN] Wind inputs not found — wind endpoints may return errors.
    set "MISSING_DATA=1"
)

set "MODEL_DIR=%PROJECT_ROOT%models\expanded_full_year"
if exist "%MODEL_DIR%\adaptive_blender_ECMWF_IFS.joblib" (
    echo [OK] Phase 6 rainfall model artifacts found.
) else (
    echo [WARN] Phase 6 model artifacts (.joblib) not found — ML inference unavailable.
    set "MISSING_DATA=1"
)

if "%MISSING_DATA%"=="1" (
    echo.
    echo [WARN] Some data/model files are missing (they are gitignored^).
    echo [INFO] The API will start but some endpoints may return 500 errors.
    echo [INFO] Run the training pipeline to regenerate:
    echo        python scripts\train_and_evaluate_expanded_model.py
    echo.
)

REM ══════════════════════════════════════════════════════════════════
REM  7. START BACKEND
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Starting FastAPI Backend --

set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "PYTHONPATH=%PROJECT_ROOT%"

echo [INFO] Starting uvicorn on http://%BACKEND_HOST%:%BACKEND_PORT% ...
start "SkyBlend-Backend" cmd /c "cd /d "%PROJECT_ROOT%" && call "%VENV_DIR%\Scripts\activate.bat" && set PYTHONPATH=%PROJECT_ROOT% && python -m uvicorn src.api.main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload --log-level info"

REM Wait for backend to initialize
timeout /t 4 /nobreak >nul
echo [OK] Backend starting on http://%BACKEND_HOST%:%BACKEND_PORT%
echo [INFO] API docs at http://%BACKEND_HOST%:%BACKEND_PORT%/docs

REM ══════════════════════════════════════════════════════════════════
REM  8. START FRONTEND
REM ══════════════════════════════════════════════════════════════════
echo.
echo -- Starting React Frontend --

set "FRONTEND_PORT=5173"

echo [INFO] Starting Vite dev server on http://localhost:%FRONTEND_PORT% ...
start "SkyBlend-Frontend" cmd /c "cd /d "%FRONTEND_DIR%" && set VITE_API_BASE_URL=http://%BACKEND_HOST%:%BACKEND_PORT% && npx vite --port %FRONTEND_PORT% --host"

REM Wait for frontend to initialize
timeout /t 4 /nobreak >nul
echo [OK] Frontend starting on http://localhost:%FRONTEND_PORT%

REM ══════════════════════════════════════════════════════════════════
REM  9. READY
REM ══════════════════════════════════════════════════════════════════
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              SkyBlend AI is up and running!                  ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║   Frontend:  http://localhost:%FRONTEND_PORT%                            ║
echo ║   Backend:   http://%BACKEND_HOST%:%BACKEND_PORT%                       ║
echo ║   API Docs:  http://%BACKEND_HOST%:%BACKEND_PORT%/docs                  ║
echo ║                                                              ║
echo ║   Backend and Frontend are running in separate windows.      ║
echo ║   Close those windows or press Ctrl+C in them to stop.       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Press any key to stop all services and exit...
pause >nul

REM Kill backend and frontend windows
taskkill /FI "WINDOWTITLE eq SkyBlend-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq SkyBlend-Frontend*" /F >nul 2>&1
echo [OK] All services stopped.
endlocal
