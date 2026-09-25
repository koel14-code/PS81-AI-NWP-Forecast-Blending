@echo off
REM ======================================================================
REM  SkyBlend AI - One-Command Startup Script (Windows)
REM  Usage:  .\nwp.bat   or   nwp
REM  Starts the FastAPI backend + React/Vite frontend in parallel.
REM  Auto-installs Python and Node dependencies if missing.
REM  Auto-initializes demonstration datasets and trained model weights.
REM ======================================================================
setlocal enabledelayedexpansion

REM -- Resolve project root --
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM -- Banner --
echo.
echo ======================================================================
echo          SkyBlend AI - NWP Forecast Blending System
echo                    SIH Problem Statement PS81
echo ======================================================================
echo.

REM ======================================================================
REM  1. CHECK PYTHON
REM ======================================================================
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

REM ======================================================================
REM  2. CHECK NODE.JS & NPM
REM ======================================================================
echo.
echo -- Checking Node.js --

REM Check if node is in PATH, or try standard install locations
where node >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\nodejs\node.exe" (
        set "PATH=C:\Program Files\nodejs;%PATH%"
    ) else if exist "C:\Program Files (x86)\nodejs\node.exe" (
        set "PATH=C:\Program Files (x86)\nodejs;%PATH%"
    ) else if exist "%LOCALAPPDATA%\Programs\node\node.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\node;%PATH%"
    )
)

where node >nul 2>&1
if %errorlevel% neq 0 goto :node_missing
goto :node_found

:node_missing
echo.
echo ======================================================================
echo [ERROR] Node.js is required to run the React frontend, but was not found.
echo.
echo To install Node.js:
echo   Option A: Download the LTS installer from https://nodejs.org/
echo   Option B: Run in PowerShell: winget install OpenJS.NodeJS.LTS
echo.
echo After installing, restart your terminal/VS Code and re-run .\nwp.bat
echo ======================================================================
echo.
exit /b 1

:node_found
for /f "tokens=*" %%v in ('node --version 2^>nul') do set "NODE_VER=%%v"
echo [OK] Found Node.js %NODE_VER%

where npm >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\nodejs\npm.cmd" (
        set "PATH=C:\Program Files\nodejs;%PATH%"
    )
)

where npm >nul 2>&1
if %errorlevel% neq 0 goto :npm_missing
goto :npm_found

:npm_missing
echo.
echo ======================================================================
echo [ERROR] npm was not found. It usually comes bundled with Node.js.
echo Please reinstall Node.js LTS from https://nodejs.org/
echo ======================================================================
echo.
exit /b 1

:npm_found
for /f "tokens=*" %%v in ('npm --version 2^>nul') do set "NPM_VER=%%v"
echo [OK] Found npm %NPM_VER%

REM ======================================================================
REM  3. PYTHON VIRTUAL ENVIRONMENT
REM ======================================================================
echo.
echo -- Setting up Python environment --

set "VENV_DIR=%PROJECT_ROOT%.venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    if exist "%PROJECT_ROOT%venv\Scripts\activate.bat" (
        set "VENV_DIR=%PROJECT_ROOT%venv"
    )
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment at %VENV_DIR% ...
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment found at %VENV_DIR%
)

set "PY_EXE=%VENV_DIR%\Scripts\python.exe"

REM ======================================================================
REM  4. INSTALL PYTHON DEPENDENCIES
REM ======================================================================
echo.
echo -- Checking Python dependencies --

"%PY_EXE%" -c "import fastapi, uvicorn, pandas, sklearn, joblib" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Some Python dependencies are missing. Installing...
    if exist "%PROJECT_ROOT%requirements.runtime.txt" (
        "%PY_EXE%" -m pip install --upgrade pip --quiet >nul 2>&1
        "%PY_EXE%" -m pip install -r "%PROJECT_ROOT%requirements.runtime.txt" --quiet
    ) else if exist "%PROJECT_ROOT%requirements.txt" (
        "%PY_EXE%" -m pip install --upgrade pip --quiet >nul 2>&1
        "%PY_EXE%" -m pip install -r "%PROJECT_ROOT%requirements.txt" --quiet
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

REM ======================================================================
REM  5. INSTALL FRONTEND DEPENDENCIES
REM ======================================================================
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
    call npm install --silent
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

REM ======================================================================
REM  6. PRE-FLIGHT: VERIFY DATA SOURCES & MODEL WEIGHTS
REM ======================================================================
echo.
echo -- Pre-flight: Data sources and model weights --

set "PREP_FLAG="
if /i "%~1"=="--force" set "PREP_FLAG=--force"
if /i "%~1"=="--rebuild-all" set "PREP_FLAG=--force"
if /i "%~1"=="--train" set "PREP_FLAG=--train"

"%PY_EXE%" "%PROJECT_ROOT%scripts\prepare_environment.py" %PREP_FLAG%
if %errorlevel% neq 0 (
    echo [ERROR] Pipeline environment preparation failed.
    exit /b 1
)
echo [OK] Datasets and model weights are verified.

REM ======================================================================
REM  7. START BACKEND
REM ======================================================================
echo.
echo -- Starting FastAPI Backend --

set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "PYTHONPATH=%PROJECT_ROOT%"

echo [INFO] Starting uvicorn on http://%BACKEND_HOST%:%BACKEND_PORT% ...
start "SkyBlend-Backend" cmd /k "title SkyBlend-Backend && "%PY_EXE%" -m uvicorn src.api.main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload --log-level info"

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul
echo [OK] Backend starting on http://%BACKEND_HOST%:%BACKEND_PORT%
echo [INFO] API docs at http://%BACKEND_HOST%:%BACKEND_PORT%/docs

REM ======================================================================
REM  8. START FRONTEND
REM ======================================================================
echo.
echo -- Starting React Frontend --

set "FRONTEND_PORT=5173"

echo [INFO] Starting Vite dev server on http://localhost:%FRONTEND_PORT% ...
start "SkyBlend-Frontend" cmd /k "title SkyBlend-Frontend && cd /d "%FRONTEND_DIR%" && npm run dev"

REM Wait for frontend to initialize
timeout /t 3 /nobreak >nul
echo [OK] Frontend starting on http://localhost:%FRONTEND_PORT%

REM ======================================================================
REM  9. READY
REM ======================================================================
echo.
echo ======================================================================
echo               SkyBlend AI is up and running!
echo ======================================================================
echo.
echo    Frontend:  http://localhost:%FRONTEND_PORT%
echo    Backend:   http://%BACKEND_HOST%:%BACKEND_PORT%
echo    API Docs:  http://%BACKEND_HOST%:%BACKEND_PORT%/docs
echo.
echo    Backend and Frontend are running in separate windows.
echo    Close those windows or press Ctrl+C in them to stop.
echo.
echo ======================================================================
echo.
echo Press any key to stop all services and exit...
pause >nul

REM Kill backend and frontend windows
taskkill /FI "WINDOWTITLE eq SkyBlend-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq SkyBlend-Frontend*" /F >nul 2>&1
echo [OK] All services stopped.
endlocal
