#!/usr/bin/env bash
set -euo pipefail

# Helper script to build and serve the Jac app in this folder.
# Usage:
#   cd backend/jac
#   ./serve.sh 8002
# Default port is 8002.

PORT=${1:-8002}

echo "[jac] Running 'jac check' to show diagnostics (if any)..."
jac check main.jac || echo "jac used to show errors above; continuing to build might fail..."

echo "[jac] Building main.jac into .jir/.bytecode..."
jac build main.jac

echo "[jac] Starting server on port ${PORT}..."
jac serve main.jac --port ${PORT}
