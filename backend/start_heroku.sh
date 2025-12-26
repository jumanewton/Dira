#!/bin/bash
set -e

echo "🚀 Starting Dira Backend Services on Heroku"

# Parse DATABASE_URL to individual components for pg_isready
if [ -n "$DATABASE_URL" ]; then
  export PGHOST=$(echo $DATABASE_URL | sed -E 's/postgres:\/\/[^:]+:[^@]+@([^:]+):.*/\1/')
  export PGPORT=$(echo $DATABASE_URL | sed -E 's/postgres:\/\/[^:]+:[^@]+@[^:]+:([0-9]+).*/\1/')
  export PGDATABASE=$(echo $DATABASE_URL | sed -E 's/.*\/([^?]+).*/\1/')
  export PGUSER=$(echo $DATABASE_URL | sed -E 's/postgres:\/\/([^:]+):.*/\1/')
fi

# Wait for database to be ready
echo "⏳ Waiting for database..."
for i in {1..30}; do
  if pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" 2>/dev/null; then
    echo "✅ Database is ready!"
    break
  fi
  echo "Attempt $i/30: Database not ready, waiting..."
  sleep 2
done

# Run database setup (idempotent)
echo "📋 Setting up database schema..."
cd backend
python3 setup_db.py || echo "⚠️  Schema setup failed or already exists"

# Seed organisations if needed
echo "🌱 Seeding organisations..."
python3 seed_orgs.py || echo "⚠️  Org seeding failed or already done"

# Start Database API in the background on port 8002
echo "🔧 Starting Database API on port 8002..."
cd python
python3 db_api.py &
DB_API_PID=$!
echo "Database API PID: $DB_API_PID"

# Start NLP Service in the background on port 8001
echo "🧠 Starting NLP Service on port 8001..."
export NLP_PORT=8001
python3 nlp_service.py &
NLP_PID=$!
echo "NLP Service PID: $NLP_PID"

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Start the JAC Server on the port provided by Heroku ($PORT)
echo "📡 Starting JAC Backend on port $PORT..."
cd ../jac

# Build JAC code to bytecode
echo "🔨 Building JAC bytecode..."
jac build main.jac || { echo "❌ JAC build failed"; exit 1; }
echo "✅ JAC build complete!"

export PYTHONUNBUFFERED=1
jac serve main.jac --port $PORT | grep --line-buffered -vE "^\{|^\["
