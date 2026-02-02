@echo off
echo Installing Redis package...

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

REM Install redis package
echo Installing redis...
pip install redis

echo.
echo Redis package installed successfully!
echo You can now run test-connections.bat to verify the setup.
pause