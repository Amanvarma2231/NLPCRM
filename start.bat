@echo off
echo Starting NLPCRM...
cd /d "%~dp0"
call .venv\Scripts\activate
python run.py
pause
