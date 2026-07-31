#!/bin/bash
set -e

# Initialize DB (handled in main.py but good to have)
echo "Starting FAWS Backend..."

# Run uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
