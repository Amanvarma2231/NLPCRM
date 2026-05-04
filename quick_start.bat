@echo off
chcp 65001 >nul
REM Direct Run - Skip Email Tests

echo.
echo ============================================================
echo   NLPCRM v3.1 - Quick Start (Skip Email Tests)
echo ============================================================
echo.

echo [INFO] Starting application without email tests...
echo [INFO] Email features will work when you use them in the app
echo.

cd /d "%~dp0"

echo [1/1] Starting NLPCRM Server...
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

python run.py

pause
