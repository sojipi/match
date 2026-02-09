@echo off
REM Create scenario tables in the database

echo Creating scenario tables...
echo.

REM Read database connection from .env file
for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /i "DATABASE_URL"') do set %%a=%%b

if "%DATABASE_URL%"=="" (
    echo Error: DATABASE_URL not found in .env file
    pause
    exit /b 1
)

REM Extract connection details from DATABASE_URL
REM Format: postgresql+asyncpg://user:password@host:port/database
echo Connecting to database...

REM Use psql to run the SQL script
REM You may need to adjust this based on your PostgreSQL installation
psql "%DATABASE_URL:postgresql+asyncpg://=postgresql://%" -f backend\create_scenario_tables.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Scenario tables created successfully!
    echo.
    echo Now you can run: scripts\seed-scenarios.bat
) else (
    echo.
    echo ✗ Failed to create tables. Make sure PostgreSQL client (psql) is installed.
    echo.
    echo Alternative: Run the SQL script manually:
    echo   backend\create_scenario_tables.sql
)

echo.
pause
