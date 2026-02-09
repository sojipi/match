@echo off
REM Seed scenario templates into the database

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Seeding scenario templates...
python backend\scripts\seed_scenarios.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Scenarios seeded successfully!
) else (
    echo.
    echo ✗ Failed to seed scenarios. Check the error messages above.
)

echo.
pause
