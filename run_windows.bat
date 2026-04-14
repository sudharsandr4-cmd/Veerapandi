@echo off
REM Voter Data Management System - Windows Startup Script
REM This script starts the Flask application on Windows

echo.
echo ========================================
echo Voter Data Management System Launcher
echo Veerapandi Constituency (No. 91), Salem
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing required packages...
    echo (This may take a minute on first run)
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

echo.
echo Starting Voter Data Management System...
echo.
echo ^> Application will be available at: http://localhost:5000
echo ^> Press Ctrl+C to stop the server
echo.

REM Start the Flask app
python app.py

pause
