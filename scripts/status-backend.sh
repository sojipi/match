#!/bin/bash

echo "=== AI Matchmaker Backend Status ==="
echo ""

# Go to project root
cd "$(dirname "$0")/.."

# Define PID file
PID_FILE="logs/backend.pid"

# Check if PID file exists
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")

    # Check if process is running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ Backend is RUNNING"
        echo "  PID: $PID"

        # Get process info
        echo "  Memory: $(ps -p $PID -o rss= | awk '{printf "%.2f MB", $1/1024}')"
        echo "  CPU: $(ps -p $PID -o %cpu= | awk '{print $1"%"}')"
        echo "  Started: $(ps -p $PID -o lstart=)"

        # Check port
        if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "  Port 8000: LISTENING"
        else
            echo "  Port 8000: NOT LISTENING (warning!)"
        fi
    else
        echo "✗ Backend is NOT RUNNING (stale PID file)"
        echo "  Stale PID: $PID"
    fi
else
    echo "✗ Backend is NOT RUNNING (no PID file)"

    # Check if something is on port 8000
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  Warning: Port 8000 is in use by another process"
        echo "  PID: $(lsof -Pi :8000 -sTCP:LISTEN -t)"
    fi
fi

echo ""
echo "=== Log Files ==="
if [ -f "logs/backend-access.log" ]; then
    ACCESS_SIZE=$(du -h logs/backend-access.log | cut -f1)
    ACCESS_LINES=$(wc -l < logs/backend-access.log)
    echo "  Access log: $ACCESS_SIZE ($ACCESS_LINES lines)"
else
    echo "  Access log: Not found"
fi

if [ -f "logs/backend-error.log" ]; then
    ERROR_SIZE=$(du -h logs/backend-error.log | cut -f1)
    ERROR_LINES=$(wc -l < logs/backend-error.log)
    echo "  Error log: $ERROR_SIZE ($ERROR_LINES lines)"

    # Show last error if any
    if [ $ERROR_LINES -gt 0 ]; then
        echo ""
        echo "=== Last Error (if any) ==="
        tail -5 logs/backend-error.log | grep -i "error" | tail -1 || echo "  No recent errors"
    fi
else
    echo "  Error log: Not found"
fi

echo ""
echo "=== Quick Actions ==="
echo "  Start:   ./scripts/start-backend.sh"
echo "  Stop:    ./scripts/stop-backend.sh"
echo "  Restart: ./scripts/restart-backend.sh"
echo "  Logs:    ./scripts/view-backend-logs.sh"
