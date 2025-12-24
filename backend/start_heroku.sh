#!/bin/bash
set -e

# Start the NLP Service in the background on port 8001
echo "Starting NLP Service on port 8001..."
export NLP_PORT=8001
python3 backend/python/nlp_service.py &

# Wait for NLP service to be ready (optional but good practice)
sleep 5

# Start the Jac Server on the port provided by Heroku ($PORT)
echo "Starting Jac Server on port $PORT..."
# We use the pipe to grep to filter logs as requested previously
export PYTHONUNBUFFERED=1
jac serve backend/jac/main.jac --port $PORT | grep --line-buffered -vE "^\{|^\["
