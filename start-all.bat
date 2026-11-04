@echo off
title LOKR AI - Launcher
cd /d "%~dp0"
echo ==============================================
echo   Launching LOKR AI (Backend + Frontend)...
echo ==============================================
start "LOKR AI - Backend" cmd /c "run-backend.bat"
timeout /t 2 /nobreak >nul
start "LOKR AI - Frontend" cmd /c "run-frontend.bat"
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo Application launched!
