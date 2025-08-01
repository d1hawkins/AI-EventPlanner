#!/bin/bash
echo "🚀 Starting application with real agents..."
echo "Environment: $ENVIRONMENT"
echo "LLM Provider: $LLM_PROVIDER"
echo "Use Real Agents: $USE_REAL_AGENTS"

# Install dependencies
pip install -r requirements.txt

# Start the application
python startup.py
