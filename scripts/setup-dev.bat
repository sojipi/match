@echo off
echo Setting up AI Matchmaker Development Environment...

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "..\venv\" (
    echo Creating Python virtual environment...
    cd ..
    py -m venv venv
    cd scripts
)

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r ..\requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
cd ..\frontend
npm install
cd ..\scripts

REM Copy environment file if it doesn't exist
if not exist "..\.env" (
    echo Creating .env file from template...
    copy ..\.env.example ..\.env
    echo Please edit .env file with your database and API configurations
)

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your remote database URLs and API keys
echo 2. Run 'scripts\start-dev.bat' to start development servers
echo.
pause