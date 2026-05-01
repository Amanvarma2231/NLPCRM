@echo off
REM ============================================
REM NLPCRM v3.1 - Quick Start
REM ============================================

echo.
echo ========================================
echo   NLPCRM v3.1 - Starting Server...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate and run
call .venv\Scripts\activate.bat
python run.py

pause
