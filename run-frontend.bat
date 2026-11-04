@echo off
title LOKR AI - Frontend
cd /d "%~dp0frontend"
echo ==============================================
echo   Starting LOKR AI Frontend (Vite)...
echo ==============================================
if not exist "node_modules\" (
    echo [INFO] Dependencies not detected. Running npm install...
    call npm install
)
call npm run dev
pause
