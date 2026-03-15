@echo off
title ClickPulse — Monitor de Mouse
color 0D

echo.
echo   ========================================
echo     ClickPulse — Monitor de Mouse
echo     Rastreamento Global de Cliques
echo   ========================================
echo.

pip install pynput >nul 2>&1

echo   [OK] Iniciando ClickPulse...
echo.

python "%~dp0clickpulse.py"

pause
