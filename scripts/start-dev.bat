@echo off
echo Starting AI Matchmaker Development Environment...

REM Ensure we're in the root directory
if exist "scripts\" (
    REM We're already in root
) else if exist "..\scripts\" (
    cd ..
) else (
    echo Error: Cannot find project root directory
    pause
    exit /b 1
)

REM Start backend in a new window
start "Backend Server" cmd /k "scripts\start-backend.bat"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in a new window
start "Frontend Server" cmd /k "scripts\start-frontend.bat"

echo Development servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs

pause