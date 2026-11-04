@echo off
title LOKR AI - Backend
cd /d "%~dp0backend"
echo ==============================================
echo   Starting LOKR AI Backend Server...
echo ==============================================
if exist ".\venv\Scripts\python.exe" (
    ".\venv\Scripts\python.exe" run.py
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        python run.py
    ) else (
        echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
        pause
    )
)
pause
