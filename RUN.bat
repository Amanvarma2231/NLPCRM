@echo off
chcp 65001 >nul 2>&1
cls

echo.
echo ============================================================
echo            NLPCRM v3.1 - Professional Start
echo ============================================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Checking system...
python --version

echo.
echo [2/3] Starting NLPCRM server...
echo.

REM Start the application
python run.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start!
    echo.
    echo Common fixes:
    echo   1. Run: pip install -r requirements.txt
    echo   2. Check .env file exists
    echo   3. Port 5000 might be busy
    echo.
    pause
    exit /b 1
)

pause
