#!/bin/bash
# Start Database API and NLP Service

VENV_PYTHON="/home/newtonai/.venvs/publiclens/bin/python"
BACKEND_DIR="/home/newtonai/publiclens/backend/python"

echo "Starting Database API on port 8002..."
cd "$BACKEND_DIR" && $VENV_PYTHON db_api.py &
DB_PID=$!
echo "Database API PID: $DB_PID"

sleep 2

echo "Starting NLP Service on port 8001..."
cd "$BACKEND_DIR" && $VENV_PYTHON nlp_service.py &
NLP_PID=$!
echo "NLP Service PID: $NLP_PID"

sleep 3

echo ""
echo "Services status:"
curl -s http://127.0.0.1:8002/health 2>/dev/null && echo " (Database API OK)" || echo "Database API NOT responding"
curl -s http://127.0.0.1:8001/health 2>/dev/null && echo " (NLP API OK)" || echo "NLP API NOT responding"

echo ""
echo "To stop services:"
echo "kill $DB_PID $NLP_PID"
