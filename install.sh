#!/bin/bash
# Installation script for SearchAgent (Linux/Mac)

set -e  # Exit on error

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up crawl4ai browser components..."
crawl4ai-setup

echo ""
echo "Installation complete!"
echo "To start SearchAgent, run: ./start.sh"
