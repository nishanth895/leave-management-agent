@echo off
echo Opening Leave Management Agent in browser...
timeout /t 1 /nobreak > nul
start http://localhost:8501
echo.
echo Browser should open now!
echo If not, copy this URL: http://localhost:8501
echo.
pause
