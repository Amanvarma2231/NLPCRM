@echo off
chcp 65001 >nul
REM ============================================
REM NLPCRM v3.1 - Professional Start Script
REM ============================================

echo.
echo ============================================================
echo   NLPCRM v3.1 - Neural Intelligence Platform
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

REM Run system verification
echo [1/2] Running system verification...
python verify_system.py
if errorlevel 1 (
    echo.
    echo [ERROR] System verification failed!
    echo Please fix the errors above before starting.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting NLPCRM server...
echo.
echo ============================================================
echo   Server Information
echo ============================================================
echo   URL: http://localhost:5000
echo   Login: admin@nlpcrm.com
echo   Password: admin@2026
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python run.py

pause
