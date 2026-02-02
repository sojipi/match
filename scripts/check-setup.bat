@echo off
echo AI Matchmaker Setup Check
echo ========================

echo Checking Python...
py --version
if errorlevel 1 (
    echo ✗ Python not found
) else (
    echo ✓ Python available
)

echo.
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ✗ Node.js not found
) else (
    echo ✓ Node.js available
)

echo.
echo Checking virtual environment...
if exist "..\venv\" (
    echo ✓ Virtual environment exists
    call ..\venv\Scripts\activate.bat
    echo Checking installed packages...
    pip list | findstr uvicorn
    pip list | findstr fastapi
    pip list | findstr asyncpg
    pip list | findstr redis
) else (
    echo ✗ Virtual environment not found
    echo Run 'scripts\setup-dev.bat' first
)

echo.
echo Checking project files...
if exist "..\requirements.txt" (
    echo ✓ requirements.txt found
) else (
    echo ✗ requirements.txt not found
)

if exist "..\frontend\package.json" (
    echo ✓ frontend/package.json found
) else (
    echo ✗ frontend/package.json not found
)

if exist "..\.env" (
    echo ✓ .env file found
) else (
    echo ✗ .env file not found
)

echo.
echo Setup check complete!
pause