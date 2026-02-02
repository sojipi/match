@echo off
echo Updating AI Matchmaker dependencies...

REM Check if we're in the scripts directory, if so go back to root
if exist "..\venv\" (
    cd ..
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found. Please run setup-dev.bat first.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
py -m pip install --upgrade pip

REM Install/update all dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Dependencies updated successfully!
echo You can now run test-connections.bat to verify the setup.
pause