#!/bin/bash

# Azure App Service startup script
echo "Starting AI Event Planner application..."

# CRITICAL: Do NOT default to SQLite in production
# If DATABASE_URL is not set, the application should fail loudly
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    echo "This is required for production deployment."
    echo "Please configure DATABASE_URL in Azure App Service settings."
    exit 1
fi

# Validate that we're not using SQLite in production
if [[ "$DATABASE_URL" == sqlite* ]]; then
    echo "ERROR: SQLite database detected in production!"
    echo "DATABASE_URL: $DATABASE_URL"
    echo "Production deployments must use PostgreSQL."
    exit 1
fi

# Set ENVIRONMENT to production if not already set
export ENVIRONMENT=${ENVIRONMENT:-"production"}

# Check and set other environment variables with validation
export SECRET_KEY=${SECRET_KEY:-""}
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY environment variable is not set!"
    exit 1
fi

export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
export GOOGLE_API_KEY=${GOOGLE_API_KEY:-""}
export TAVILY_API_KEY=${TAVILY_API_KEY:-""}
export LLM_PROVIDER=${LLM_PROVIDER:-"openai"}
export LLM_MODEL=${LLM_MODEL:-"gpt-4"}
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8000"}

# Print environment info for debugging (without sensitive values)
echo "Environment configuration:"
echo "DATABASE_URL: ${DATABASE_URL}"
echo "LLM_PROVIDER: ${LLM_PROVIDER}"
echo "LLM_MODEL: ${LLM_MODEL}"
echo "HOST: ${HOST}"
echo "PORT: ${PORT}"
echo "OPENAI_API_KEY: $(if [ -n "$OPENAI_API_KEY" ]; then echo "***SET***"; else echo "NOT SET"; fi)"
echo "GOOGLE_API_KEY: $(if [ -n "$GOOGLE_API_KEY" ]; then echo "***SET***"; else echo "NOT SET"; fi)"
echo "TAVILY_API_KEY: $(if [ -n "$TAVILY_API_KEY" ]; then echo "***SET***"; else echo "NOT SET"; fi)"

# Create directories if they don't exist
mkdir -p /home/site/wwwroot/logs

# Check if DROP_AND_RELOAD flag is set
if [ "$DROP_AND_RELOAD" = "true" ]; then
    echo "⚠️  DROP_AND_RELOAD flag detected!"
    echo "This will DROP ALL TABLES and reload the database!"
    python scripts/drop_and_reload_db.py || {
        echo "ERROR: Drop and reload failed!"
        exit 1
    }
    # Unset the flag after running to prevent accidental re-runs
    echo "✅ Drop and reload completed. Remember to UNSET DROP_AND_RELOAD in Azure settings!"
else
    # Run database migrations if needed
    echo "Running database migrations..."
    python scripts/run_azure_migration_comprehensive.py --max-retries 3 --retry-delay 5 || {
        echo "WARNING: Comprehensive migration failed, trying fallback migration..."
        python -m scripts.migrate || echo "Migration failed, continuing with application start..."
    }
fi

# Start the application
echo "Starting uvicorn server..."
exec python -m uvicorn app.main_saas:app --host $HOST --port $PORT
