#!/bin/bash

# Azure App Services startup script for Python FastAPI application

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Install dependencies if needed (Azure usually handles this automatically)
# python -m pip install --upgrade pip
# pip install -r requirements.txt

# Start the FastAPI application with uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
