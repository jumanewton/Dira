#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

# Start NLP Service
echo "Starting NLP Service on port 8001..."
python3 backend/python/nlp_service.py &
NLP_PID=$!

# Start Notification Service
echo "Starting Notification Service on port 8003..."
python3 backend/python/notification_service.py &
NOTIF_PID=$!

# Start DB API Service
echo "Starting DB API Service on port 8004..."
python3 -m uvicorn backend.python.db_api:app --port 8004 --host 0.0.0.0 &
DB_API_PID=$!

# Start Jac Backend
echo "Starting Jac Backend on port 8002..."
cd backend/jac
./serve.sh 8002 > ../../jac_service.log 2>&1 &
JAC_PID=$!
cd ../..

# Wait for services to start up a bit
sleep 5

# Start Frontend
echo "Starting Frontend on port 3000... $DB_API_PID"
cd frontend
npm start

# Cleanup on exit
trap "kill $NLP_PID $NOTIF_PID $JAC_PID" EXIT
