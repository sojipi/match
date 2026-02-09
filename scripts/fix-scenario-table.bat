@echo off
REM Fix scenario_templates table structure

echo ========================================
echo   Fix Scenario Table Structure
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Fixing scenario_templates table...
echo ----------------------------------------
python backend\scripts\fix_scenario_table.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ Table fixed successfully!
    echo ========================================
    echo.
    echo Please restart the backend server.
) else (
    echo.
    echo ✗ Failed to fix table. Check the error messages above.
)

echo.
pause
