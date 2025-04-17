#!/bin/bash
cd /home/site/wwwroot

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $PYTHONPATH"

# Install required dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install fastapi uvicorn gunicorn sqlalchemy pydantic langchain langgraph google-generativeai openai passlib python-jose python-multipart bcrypt python-dotenv psycopg2-binary email-validator icalendar

# Print environment for debugging
echo "Environment variables:"
env | grep -v "PATH" | grep -v "PYTHONPATH"

# Add current directory to Python path
export PYTHONPATH=$PYTHONPATH:/home/site/wwwroot

# List all directories in the current path to help with debugging
echo "Listing directories in current path:"
for item in $(ls -la); do
    if [ -d "$item" ]; then
        echo "  - $item"
        if [ "$item" = "app" ]; then
            echo "    Listing contents of app directory:"
            for subitem in $(ls -la app); do
                echo "      - $subitem"
            done
        fi
    fi
done

# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    # Check if the migration script exists in the current directory
    if [ -f "run_azure_migrations_fixed.py" ]; then
        echo "Migration script found in current directory, running..."
        python run_azure_migrations_fixed.py
    # Check if the scripts directory exists
    elif [ -d "scripts" ]; then
        echo "Scripts directory found, running migrations..."
        python -m scripts.run_azure_migrations_fixed
    else
        echo "Migration script not found, skipping migrations."
    fi
fi

# Check if main_saas.py exists in the app directory
MAIN_SAAS_PATH="app/main_saas.py"
APP_ADAPTER_PATH="app_adapter.py"
MAIN_PATH="app/main.py"

echo "Checking for $MAIN_SAAS_PATH: $([ -f "$MAIN_SAAS_PATH" ] && echo "Found" || echo "Not found")"
echo "Checking for $APP_ADAPTER_PATH: $([ -f "$APP_ADAPTER_PATH" ] && echo "Found" || echo "Not found")"
echo "Checking for $MAIN_PATH: $([ -f "$MAIN_PATH" ] && echo "Found" || echo "Not found")"

# Try to determine which module to use
if [ -f "$MAIN_SAAS_PATH" ]; then
    echo "Found main_saas.py, using app.main_saas:app"
    APP_MODULE="app.main_saas:app"
elif [ -f "$MAIN_PATH" ]; then
    echo "Found main.py, using app.main:app"
    APP_MODULE="app.main:app"
else
    echo "Using app_adapter:app as fallback"
    APP_MODULE="app_adapter:app"
fi

# Run gunicorn with the determined app module
echo "Starting application with $APP_MODULE..."
gunicorn $APP_MODULE --bind=0.0.0.0:8000 --workers=4 --timeout=120
