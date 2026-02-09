#!/bin/bash

echo "Starting AI Matchmaker Frontend..."

# Go to project root
cd "$(dirname "$0")/.."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start frontend development server
echo "Starting React development server..."
npm run dev
