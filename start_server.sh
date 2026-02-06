#!/bin/bash
# Startup script for PromptGuard API Server

# Set environment to avoid OpenMP conflicts
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1

# Start the server
cd "$(dirname "$0")"
echo "🚀 Starting PromptGuard API Server..."
python3 api_server.py
