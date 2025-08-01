#!/bin/bash
echo "Starting Azure App Service with fixed agent system..."

# Set Python path
export PYTHONPATH="/home/site/wwwroot:/home/site/wwwroot/app:/home/site/wwwroot/app/agents:/home/site/wwwroot/app/graphs:/home/site/wwwroot/app/tools:/home/site/wwwroot/app/utils:/home/site/wwwroot/app/db:/home/site/wwwroot/app/middleware"

echo "Python path set to: $PYTHONPATH"

# Run diagnostics
echo "Running import diagnostics..."
cd /home/site/wwwroot
python azure_import_diagnostics.py || echo "Diagnostics completed with warnings"

# Start the application
echo "Starting application..."
python -m gunicorn --bind=0.0.0.0 --timeout 600 app:app
