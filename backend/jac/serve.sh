#!/usr/bin/env bash
set -euo pipefail

# Helper script to build and serve the Jac app in this folder.
# Usage:
#   cd backend/jac
#   ./serve.sh 8002
# Default port is 8002.

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Activate virtual environment 
if [ -f ~/.venvs/publiclens/bin/activate ]; then
    source ~/.venvs/publiclens/bin/activate
fi

PORT=${1:-8002}

echo "[jac] Running 'jac check' to show diagnostics (if any)..."
jac check main.jac || echo "jac used to show errors above; continuing to build might fail..."

echo "[jac] Building main.jac into .jir/.bytecode..."
jac build main.jac

echo "[jac] Starting server on port ${PORT}..."
export PYTHONUNBUFFERED=1
jac serve main.jac --port "${PORT}" | grep --line-buffered -vE "^\{|^\[" || true
