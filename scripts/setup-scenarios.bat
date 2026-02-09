@echo off
REM Setup scenario system: create tables and seed data

echo ========================================
echo   Scenario System Setup
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 1: Creating scenario tables...
echo ----------------------------------------
python backend\scripts\create_scenario_tables.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ Failed to create tables. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Step 2: Seeding scenario data...
echo ----------------------------------------
python backend\scripts\seed_scenarios.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ Scenario system setup complete!
    echo ========================================
    echo.
    echo You can now use the scenario simulation feature.
) else (
    echo.
    echo ✗ Failed to seed scenarios. Check the error messages above.
)

echo.
pause
