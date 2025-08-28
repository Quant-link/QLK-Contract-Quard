#!/bin/bash

# ContractQuard Backend Entrypoint Script
# This script handles PORT environment variable properly for Railway deployment

set -e

# Default port
DEFAULT_PORT=8000

echo "=== ContractQuard Railway Deployment ==="
echo "Environment: ${ENVIRONMENT:-development}"
echo "Debug: ${DEBUG:-true}"
echo "Raw PORT value: '${PORT}'"

# Check if PORT environment variable is set and is a valid number
if [ -z "$PORT" ]; then
    echo "❌ PORT environment variable not set, using default port $DEFAULT_PORT"
    FINAL_PORT=$DEFAULT_PORT
elif ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ PORT environment variable '$PORT' is not a valid number, using default port $DEFAULT_PORT"
    FINAL_PORT=$DEFAULT_PORT
else
    echo "✅ Using PORT from environment: $PORT"
    FINAL_PORT=$PORT
fi

echo "🚀 Final port selected: $FINAL_PORT"

# Change to the correct directory (handle both local and Docker environments)
if [ -d "/app/web/backend" ]; then
    cd /app/web/backend
elif [ -f "main.py" ]; then
    # Already in the right directory
    echo "Already in backend directory"
else
    echo "Error: Cannot find main.py file"
    exit 1
fi

# Start the application with the determined port
echo "🔥 Starting ContractQuard API on port $FINAL_PORT..."
echo "📁 Current directory: $(pwd)"
echo "📋 Files in current directory:"
ls -la

# Ensure we're in the right directory and main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in current directory!"
    echo "📂 Searching for main.py..."
    find /app -name "main.py" -type f 2>/dev/null || echo "No main.py found anywhere"
    exit 1
fi

echo "✅ main.py found, starting uvicorn..."
exec python -m uvicorn main:app --host 0.0.0.0 --port $FINAL_PORT
