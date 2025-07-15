#!/bin/bash
echo "Starting Azure standalone deployment..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting standalone application..."
python -m gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_standalone:app
