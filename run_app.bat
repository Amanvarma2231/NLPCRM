@echo off
setlocal enabledelayedexpansion

:: Professional Header
echo ====================================================
echo           NLP CRM - SMART BUSINESS ENGINE
echo ====================================================
echo.

:: Set Directory
cd /d "%~dp0"

:: Virtual Environment Check
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found in system path. Please install Python.
    pause
    exit /b
)

if not exist .venv (
    echo [SYSTEM] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Please install Python.
        pause
        exit /b 1
    )
)

:: Dependency Check (Silent unless missing)
if exist requirements.txt (
    echo [SYSTEM] Checking dependencies...
    .venv\Scripts\python -m pip install -r requirements.txt --quiet
)

:: Environment Setup
if not exist .env (
    echo [SYSTEM] Generating initial .env configuration...
    echo SECRET_KEY=!RANDOM!!RANDOM! > .env
    echo ADMIN_PASSWORD=admin@2026 >> .env
    echo ADMIN_EMAIL=admin@nlpcrm.com >> .env
    echo HF_API_KEY= >> .env
    echo SQLITE_CLOUD_URL= >> .env
)

:: Launch Application
echo.
echo [SUCCESS] NLPCRM Intelligence Engine is online!
echo [INFO] Access the application at: http://localhost:5001
echo [TIP] Using port 5001 avoids browser-cached security errors.

:: Open browser automatically
start http://localhost:5001

.venv\Scripts\python run.py

if errorlevel 1 (
    echo.
    echo [CRITICAL] Server stopped unexpectedly.
    pause
)

endlocal

