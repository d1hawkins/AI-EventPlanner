#!/bin/bash

# Azure App Service startup script
echo "Starting AI Event Planner application..."

# Check and set default environment variables if not provided
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./azure_app.db"}
export SECRET_KEY=${SECRET_KEY:-"azure_production_secret_key_change_me"}
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

# Run database migrations if needed
echo "Running database migrations..."
python -m scripts.migrate || echo "Migration failed, continuing with application start..."

# Start the application
echo "Starting uvicorn server..."
exec python -m uvicorn app.main_saas:app --host $HOST --port $PORT
