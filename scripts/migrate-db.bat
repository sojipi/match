@echo off
echo Running database migrations...

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

REM Run the migration script
py scripts\migrate-simple.py

echo.
echo Database migration complete!
pause