#!/bin/bash
# Production startup script for PromptGuard

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server with gunicorn
echo "Starting PromptGuard API Server..."
gunicorn api_server:app \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
