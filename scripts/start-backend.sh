#!/bin/bash

echo "Starting AI Matchmaker Backend..."

# Go to project root
cd "$(dirname "$0")/.."

# Define log files
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
ACCESS_LOG="$LOG_DIR/backend-access.log"
ERROR_LOG="$LOG_DIR/backend-error.log"
PID_FILE="$LOG_DIR/backend.pid"

# Check if backend is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Backend is already running with PID $OLD_PID"
        echo "To restart, run: kill $OLD_PID && $0"
        exit 1
    else
        echo "Removing stale PID file..."
        rm "$PID_FILE"
    fi
fi

# Check if port 8000 is in use and kill it
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Killing process on port 8000..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t)
    sleep 2
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Start backend server in background
echo "Starting FastAPI server in background..."
cd backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > "../$ACCESS_LOG" 2> "../$ERROR_LOG" &

# Save PID
echo $! > "../$PID_FILE"

echo "Backend started with PID $(cat ../$PID_FILE)"
echo "Access log: $ACCESS_LOG"
echo "Error log: $ERROR_LOG"
echo ""
echo "To stop the backend, run: kill $(cat ../$PID_FILE)"
echo "To view logs, run: tail -f $ACCESS_LOG"
