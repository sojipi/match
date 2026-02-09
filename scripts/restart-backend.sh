#!/bin/bash

echo "Restarting AI Matchmaker Backend..."

# Go to project root
cd "$(dirname "$0")/.."

# Stop backend
./scripts/stop-backend.sh

# Wait a moment
sleep 1

# Start backend
./scripts/start-backend.sh
