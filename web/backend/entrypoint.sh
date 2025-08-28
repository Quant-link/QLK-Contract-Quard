#!/bin/bash

# ContractQuard Backend Entrypoint Script
# This script handles PORT environment variable properly for Railway deployment

set -e

# Default port
DEFAULT_PORT=8000

# Check if PORT environment variable is set and is a valid number
if [ -z "$PORT" ]; then
    echo "PORT environment variable not set, using default port $DEFAULT_PORT"
    FINAL_PORT=$DEFAULT_PORT
elif ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "PORT environment variable '$PORT' is not a valid number, using default port $DEFAULT_PORT"
    FINAL_PORT=$DEFAULT_PORT
else
    echo "Using PORT from environment: $PORT"
    FINAL_PORT=$PORT
fi

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
echo "Starting ContractQuard API on port $FINAL_PORT..."
exec python -m uvicorn main:app --host 0.0.0.0 --port $FINAL_PORT
