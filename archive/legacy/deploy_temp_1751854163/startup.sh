#!/bin/bash
echo "Starting Azure deployment..."
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application..."
python app_adapter_conversational.py
