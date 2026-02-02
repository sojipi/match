@echo off
echo Starting AI Matchmaker Frontend...

REM Check if we're in the scripts directory, if so go back to root
if exist "..\frontend\" (
    cd ..
)

cd frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
)

REM Start frontend development server
echo Starting React development server...
npm run dev

pause