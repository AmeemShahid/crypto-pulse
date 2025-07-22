#!/bin/bash

# Linux/Mac shell script to run the Discord Crypto Bot locally

echo "Discord Crypto Bot - Linux/Mac Startup"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check Python version
VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
MAJOR_VERSION=$(echo $VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $VERSION | cut -d. -f2)

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $($PYTHON_CMD --version)"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found"
    echo "Please copy .env.example to .env and fill in your API keys"
    echo "cp .env.example .env"
    exit 1
fi

# Run setup if this is first time
if [ ! -d "data" ]; then
    echo "Running initial setup..."
    $PYTHON_CMD setup_local.py
    echo ""
    echo "Press Enter to continue..."
    read
fi

# Start the bot
echo "Starting Discord Crypto Bot..."
$PYTHON_CMD main.py