@echo off
echo Starting ReviewGuard - Fake Review Detection System...

start "Backend API" cmd /k "cd /d %~dp0 && py -3.10 -m uvicorn backend.api.main:app --reload --port 8000"
timeout /t 3 >nul
start "Frontend" cmd /k "cd /d %~dp0\frontend-next && npm run dev"

echo.
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Frontend:    http://localhost:3000
echo.
pause
