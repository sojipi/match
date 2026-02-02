@echo off
echo Starting AI Matchmaker Backend...

REM Check if we're in the scripts directory, if so go back to root
if exist "..\venv\" (
    cd ..
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    py -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat


REM Start backend server
echo Starting FastAPI server...
cd backend
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause