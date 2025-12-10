#!/bin/bash
# Build script for SearchAgent (Linux/Mac)

set -e  # Exit on error

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Building executable with PyInstaller..."
pyinstaller SearchAgent.spec

echo ""
echo "Build complete! Executable is in the dist/ directory."
