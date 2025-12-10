#!/bin/bash
# Startup script for SearchAgent (Linux/Mac)

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting SearchAgent..."
echo ""

python main.py
