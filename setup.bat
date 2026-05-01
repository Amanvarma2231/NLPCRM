@echo off
REM ============================================
REM NLPCRM v3.1 - Professional Setup Script
REM ============================================

echo.
echo ========================================
echo   NLPCRM v3.1 - Setup Wizard
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Python detected...
python --version

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv .venv
    echo Virtual environment created successfully!
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Setup environment file
echo.
echo [5/5] Checking environment configuration...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file with your credentials:
    echo   - HF_API_KEY: Your Hugging Face API key
    echo   - SECRET_KEY: Generate a secure random key
    echo   - SMTP/POP3: Your email credentials
    echo.
) else (
    echo .env file already exists.
)

echo.
echo ========================================
echo   Setup Complete! 
echo ========================================
echo.
echo To start the application:
echo   1. Run: .venv\Scripts\activate
echo   2. Run: python run.py
echo   3. Open: http://localhost:5000
echo.
echo Login Credentials:
echo   Email: admin@nlpcrm.com
echo   Password: admin@2026
echo.
echo ========================================
pause
