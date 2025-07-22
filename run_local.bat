@echo off
REM Windows batch file to run the Discord Crypto Bot locally

echo Discord Crypto Bot - Windows Startup
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found
    echo Please copy .env.example to .env and fill in your API keys
    pause
    exit /b 1
)

REM Run setup if this is first time
if not exist data (
    echo Running initial setup...
    python setup_local.py
    pause
)

REM Start the bot
echo Starting Discord Crypto Bot...
python main.py

pause