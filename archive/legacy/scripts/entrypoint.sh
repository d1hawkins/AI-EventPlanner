#!/bin/bash
# Robust entrypoint script for AI Event Planner SaaS Docker container
# This script includes error handling, retry logic, and proper logging

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to log messages
log() {
  local level=$1
  local message=$2
  local color=$NC
  
  case $level in
    "INFO") color=$GREEN ;;
    "WARN") color=$YELLOW ;;
    "ERROR") color=$RED ;;
  esac
  
  echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message${NC}"
}

# Function to retry commands with exponential backoff
retry() {
  local max_attempts=$1
  local delay=$2
  local command="${@:3}"
  local attempt=1
  
  while true; do
    log "INFO" "Executing command (attempt $attempt/$max_attempts): $command"
    
    if eval "$command"; then
      log "INFO" "Command executed successfully"
      return 0
    else
      local exit_code=$?
      log "WARN" "Command failed with exit code $exit_code"
      
      if (( attempt >= max_attempts )); then
        log "ERROR" "Maximum number of attempts reached. Giving up."
        return $exit_code
      fi
      
      log "INFO" "Retrying in $delay seconds..."
      sleep $delay
      attempt=$((attempt + 1))
      delay=$((delay * 2)) # Exponential backoff
    fi
  done
}

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  log "ERROR" "DATABASE_URL environment variable is not set"
  exit 1
fi

# Handle port configuration
# Azure sets PORT=8002 but expects the app to listen on WEBSITES_PORT=8000
if [ -n "$WEBSITES_PORT" ]; then
  log "INFO" "Using WEBSITES_PORT: $WEBSITES_PORT instead of PORT: $PORT"
  export PORT=$WEBSITES_PORT
elif [ -z "$PORT" ]; then
  log "WARN" "PORT environment variable is not set, defaulting to 8000"
  export PORT=8000
fi

# Print environment information
log "INFO" "Starting AI Event Planner SaaS application"
log "INFO" "Environment: ${ENVIRONMENT:-development}"
log "INFO" "Port: $PORT"
log "INFO" "Database URL: ${DATABASE_URL//:*@/:***@}" # Hide password in logs

# Create a simple health check file that doesn't require database access
log "INFO" "Creating health check endpoint..."
mkdir -p /tmp/health
cat > /tmp/health/app.py << EOF
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
EOF

# Start a simple health check server in the background
log "INFO" "Starting health check server on port 8000..."
python -m uvicorn /tmp/health/app:app --host 0.0.0.0 --port 8000 &
HEALTH_PID=$!

# Run database setup using the fixed script with retry logic
log "INFO" "Setting up database..."
if retry 5 10 "python -m scripts.setup_azure_db_complete_fixed --force"; then
  log "INFO" "Database setup completed successfully"
else
  log "WARN" "Database setup failed, but continuing with application startup"
  # We continue even if database setup fails, as the application might still work
  # if the database was already set up previously
fi

# Kill the health check server
log "INFO" "Stopping health check server..."
kill $HEALTH_PID || true

# Start the application
log "INFO" "Starting the application..."
exec gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --workers 2
