@echo off
REM Quick Python Installation Check and Setup

echo.
echo ========================================
echo Python Installation Helper
echo ========================================
echo.

REM Try to find Python in various locations
setlocal enabledelayedexpansion

echo Checking for Python installations...

REM Check common installation paths
set "found=0"

for %%P in (
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
) do (
    if exist %%P (
        echo Found Python at: %%P
        set "PYTHON_PATH=%%P"
        set "found=1"
    )
)

if !found! equ 1 (
    echo.
    echo ✅ Python found! Installing dependencies...
    "!PYTHON_PATH!" -m pip install Flask==2.3.3 Flask-CORS==4.0.0 pdfplumber==0.10.3 python-dotenv==1.0.0
    if !errorlevel! equ 0 (
        echo.
        echo ✅ Dependencies installed!
        echo.
        echo Starting Flask application...
        cd backend
        "!PYTHON_PATH!" app.py
    ) else (
        echo ❌ Failed to install dependencies
        pause
    )
) else (
    echo.
    echo ❌ Python is not installed or not found in common locations
    echo.
    echo Please install Python 3.8+ from: https://www.python.org
    echo.
    echo During installation, make sure to:
    echo 1. Check "Add Python to PATH"
    echo 2. Install pip
    echo.
    echo After installation, run this script again.
    pause
)
