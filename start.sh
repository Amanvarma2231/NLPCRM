#!/bin/bash
echo "Starting NLP CRM..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Setup .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found! Copying from .env.example..."
    cp .env.example .env
fi

# Launch server
echo "Launching server..."
python run.py
