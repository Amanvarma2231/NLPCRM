@echo off
echo Starting NLP CRM...
echo.
echo Installing requirements...
.venv\Scripts\pip install -r requirements.txt
echo.
echo Setting up environment variables...
if not exist .env (
    echo WARNING: .env file not found! Using defaults.
)
echo.
echo Launching server...
.venv\Scripts\python run.py
pause
