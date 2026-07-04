@echo off
title Leave Management Agent - HRMS Dashboard
color 0A
echo.
echo ========================================
echo    LEAVE MANAGEMENT AGENT
echo    Enterprise HRMS Dashboard
echo ========================================
echo.
echo Starting application...
echo.

cd /d "%~dp0"
python start_app.py

pause
