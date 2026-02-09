#!/bin/bash

echo "Stopping AI Matchmaker Backend..."

# Go to project root
cd "$(dirname "$0")/.."

# Define PID file
PID_FILE="logs/backend.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Backend is not running (no PID file found)"

    # Try to kill by port anyway
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Found process on port 8000, killing it..."
        kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t)
        echo "Process killed"
    fi
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Stopping backend with PID $PID..."
    kill "$PID"

    # Wait for graceful shutdown
    sleep 2

    # Force kill if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Force killing backend..."
        kill -9 "$PID"
    fi

    echo "Backend stopped"
else
    echo "Backend process (PID $PID) is not running"
fi

# Remove PID file
rm "$PID_FILE"

echo "Done"
