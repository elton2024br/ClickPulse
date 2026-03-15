@echo off
chcp 65001 >nul 2>&1
title ClickPulse

:: Se o .exe existe, usar ele
if exist "%~dp0dist\ClickPulse.exe" (
    start "" "%~dp0dist\ClickPulse.exe"
    exit /b 0
)

:: Senao, rodar via Python com venv
if exist "%~dp0venv\Scripts\python.exe" (
    start "" /min "%~dp0venv\Scripts\pythonw.exe" "%~dp0main.py"
    exit /b 0
)

:: Fallback: Python global
pythonw "%~dp0main.py" 2>nul
if errorlevel 1 (
    python "%~dp0main.py"
)
