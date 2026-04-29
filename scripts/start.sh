#!/bin/bash
# Quick start script for Zapret UI

echo "Starting Zapret UI..."
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Using virtual environment..."
    .venv/bin/python main.py
else
    echo "Using system Python..."
    python3 main.py
fi
