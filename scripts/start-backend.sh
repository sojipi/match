#!/bin/bash

echo "Starting AI Matchmaker Backend..."

# Go to project root
cd "$(dirname "$0")/.."

# Check if port 8000 is in use and kill it
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 8000..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t)
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Start backend server
echo "Starting FastAPI server..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
