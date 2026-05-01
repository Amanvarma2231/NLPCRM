@echo off
REM Quick Fix: Enable IMAP instead of POP3

echo.
echo ============================================================
echo   NLPCRM - Switching to IMAP (More Reliable)
echo ============================================================
echo.

echo [INFO] POP3 requires manual Gmail setup.
echo [INFO] IMAP is more reliable and easier to use.
echo.
echo Updating .env file to use IMAP...

REM Backup .env
copy .env .env.backup >nul 2>&1

REM Add IMAP configuration
echo. >> .env
echo # IMAP Enabled (More Reliable than POP3) >> .env
echo USE_IMAP=true >> .env
echo IMAP_HOST=imap.gmail.com >> .env
echo IMAP_PORT=993 >> .env
echo IMAP_USER=amangurauli@gmail.com >> .env
echo IMAP_PASSWORD=ohmpmddxlqlahmno >> .env

echo.
echo [SUCCESS] IMAP enabled!
echo.
echo Now test again:
echo   python test_email.py
echo.
pause
