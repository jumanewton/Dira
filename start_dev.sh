#!/bin/bash

# Start NLP Service
echo "Starting NLP Service on port 8001..."
python backend/python/nlp_service.py &
NLP_PID=$!

# Start Notification Service
echo "Starting Notification Service on port 8003..."
python backend/python/notification_service.py &
NOTIF_PID=$!

# Start Jac Backend
echo "Starting Jac Backend on port 8002..."
cd backend/jac
./serve.sh 8002 &
JAC_PID=$!
cd ../..

# Wait for services to start up a bit
sleep 5

# Start Frontend
echo "Starting Frontend on port 3000..."
cd frontend
npm start

# Cleanup on exit
trap "kill $NLP_PID $NOTIF_PID $JAC_PID" EXIT
