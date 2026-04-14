#!/bin/bash
# Voter Data Management System - macOS/Linux Startup Script
# This script starts the Flask application on macOS/Linux

echo ""
echo "========================================"
echo "Voter Data Management System Launcher"
echo "Veerapandi Constituency (No. 91), Salem"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python 3.8+ using: brew install python3"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if requirements are installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "Installing required packages..."
    echo "(This may take a minute on first run)"
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install packages"
        exit 1
    fi
fi

echo ""
echo "Starting Voter Data Management System..."
echo ""
echo "> Application will be available at: http://localhost:5000"
echo "> Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python3 app.py
