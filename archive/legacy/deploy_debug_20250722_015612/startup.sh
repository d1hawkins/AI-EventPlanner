#!/bin/bash
echo "Starting Azure deployment with debug endpoint..."

# Set Python path
export PYTHONPATH="/home/site/wwwroot:/home/site/wwwroot/app"

# Install dependencies if needed
if [ ! -d "/home/site/wwwroot/.venv" ]; then
    echo "Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
fi

# Start the application
echo "Starting application..."
python app_adapter_with_agents_fixed.py
