#!/bin/bash

# Go to project root
cd "$(dirname "$0")/.."

# Define log files
ACCESS_LOG="logs/backend-access.log"
ERROR_LOG="logs/backend-error.log"

echo "=== Backend Logs Viewer ==="
echo ""
echo "1. View access log (live)"
echo "2. View error log (live)"
echo "3. View access log (last 50 lines)"
echo "4. View error log (last 50 lines)"
echo "5. View both logs (last 50 lines)"
echo ""
read -p "Select option (1-5): " option

case $option in
    1)
        echo "Viewing access log (Ctrl+C to exit)..."
        tail -f "$ACCESS_LOG"
        ;;
    2)
        echo "Viewing error log (Ctrl+C to exit)..."
        tail -f "$ERROR_LOG"
        ;;
    3)
        echo "=== Last 50 lines of access log ==="
        tail -50 "$ACCESS_LOG"
        ;;
    4)
        echo "=== Last 50 lines of error log ==="
        tail -50 "$ERROR_LOG"
        ;;
    5)
        echo "=== Last 50 lines of access log ==="
        tail -50 "$ACCESS_LOG"
        echo ""
        echo "=== Last 50 lines of error log ==="
        tail -50 "$ERROR_LOG"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
