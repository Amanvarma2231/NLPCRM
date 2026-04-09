@echo off
echo Starting NLP CRM...
echo.
echo Installing requirements...
.venv\Scripts\pip install -r requirements.txt
echo.
echo Setting up environment variables...
if not exist .env (
    echo WARNING: .env file not found! Generating basic .env...
    echo SECRET_KEY=%RANDOM%%RANDOM% > .env
    echo ADMIN_PASSWORD=admin@2026 >> .env
    echo ADMIN_EMAIL=admin@nlpcrm.com >> .env
)
findstr /C:"SECRET_KEY" .env >nul || (echo SECRET_KEY=super-secret-%RANDOM% >> .env)
echo.
echo Launching server...
.venv\Scripts\python run.py
pause
