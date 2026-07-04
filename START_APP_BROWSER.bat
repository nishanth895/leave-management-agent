@echo off
title Leave Management Agent - HRMS Dashboard
color 0A

echo.
echo ================================================
echo    LEAVE MANAGEMENT AGENT - HRMS DASHBOARD
echo ================================================
echo.
echo Starting application with auto browser open...
echo.

cd /d "%~dp0"

REM Run PowerShell script with execution policy bypass
PowerShell.exe -ExecutionPolicy Bypass -File "%~dp0START_APP_AUTO_OPEN.ps1"

pause
