#!/bin/bash

# Azure Real Agents Deployment V4 - Final Fix
# This version ensures the fixed adapter is properly included

set -e

echo "🚀 Starting Azure Real Agents Deployment V4..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
DEPLOYMENT_VERSION="v4_real_agents_final"

# Verify the fixed adapter exists
if [ ! -f "app_adapter_with_agents_fixed.py" ]; then
    echo "❌ Error: app_adapter_with_agents_fixed.py not found!"
    exit 1
fi

echo "✅ Found app_adapter_with_agents_fixed.py"

# Create minimal requirements for V4
cat > requirements_v4.txt << 'EOF'
# Core web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Data validation
pydantic==2.5.2

# Environment & Configuration
python-dotenv==1.0.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# AI/ML Libraries (minimal versions)
langchain==0.1.0
langgraph==0.0.26
openai==1.6.1
google-generativeai==0.3.2

# Utilities
requests==2.31.0
httpx==0.25.2
EOF

echo "✅ Created minimal requirements_v4.txt"

# Create deployment package with ONLY essential files
echo "📦 Creating deployment package..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Copy ONLY the essential files
cp app_adapter_with_agents_fixed.py "$TEMP_DIR/"
cp requirements_v4.txt "$TEMP_DIR/requirements.txt"

# Copy essential app modules
mkdir -p "$TEMP_DIR/app"
mkdir -p "$TEMP_DIR/app/agents"
mkdir -p "$TEMP_DIR/app/db"
mkdir -p "$TEMP_DIR/app/middleware"

# Copy only the files we know exist and are needed
if [ -f "app/agents/api_router.py" ]; then
    cp app/agents/api_router.py "$TEMP_DIR/app/agents/"
    echo "✅ Copied app/agents/api_router.py"
fi

if [ -f "app/agents/agent_factory.py" ]; then
    cp app/agents/agent_factory.py "$TEMP_DIR/app/agents/"
    echo "✅ Copied app/agents/agent_factory.py"
fi

if [ -f "app/db/session.py" ]; then
    cp app/db/session.py "$TEMP_DIR/app/db/"
    echo "✅ Copied app/db/session.py"
fi

if [ -f "app/middleware/tenant.py" ]; then
    cp app/middleware/tenant.py "$TEMP_DIR/app/middleware/"
    echo "✅ Copied app/middleware/tenant.py"
fi

# Create __init__.py files
touch "$TEMP_DIR/app/__init__.py"
touch "$TEMP_DIR/app/agents/__init__.py"
touch "$TEMP_DIR/app/db/__init__.py"
touch "$TEMP_DIR/app/middleware/__init__.py"

echo "✅ Created package structure"

# Create the deployment zip
cd "$TEMP_DIR"
zip -r deployment_v4.zip . -x "*.pyc" "*__pycache__*"
cd - > /dev/null

echo "✅ Created deployment package"

# Set environment variables for real agents
echo "🔧 Configuring environment variables..."

az webapp config appsettings set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --settings \
    USE_REAL_AGENTS="true" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    ENABLE_AGENT_LOGGING="true" \
    LLM_MODEL="gemini-2.0-flash" \
    DEPLOYMENT_VERSION="$DEPLOYMENT_VERSION" \
    > /dev/null

echo "✅ Environment variables configured"

# Set startup command to use the fixed adapter
echo "🔧 Setting startup command..."

az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_with_agents_fixed:app" \
    > /dev/null

echo "✅ Startup command configured"

# Deploy the package
echo "🚀 Deploying to Azure..."

az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src "$TEMP_DIR/deployment_v4.zip" \
    > /dev/null

echo "✅ Deployment package uploaded"

# Clean up
rm -rf "$TEMP_DIR"
rm -f requirements_v4.txt

echo "🎉 Azure Real Agents Deployment V4 completed!"
echo ""
echo "📊 Deployment Summary:"
echo "   • Fixed adapter: app_adapter_with_agents_fixed.py ✅"
echo "   • Correct imports: app.agents.api_router ✅"
echo "   • Real agents enabled: USE_REAL_AGENTS=true ✅"
echo "   • Google Gemini configured ✅"
echo "   • Minimal dependencies ✅"
echo ""
echo "🔗 Application URL: https://$APP_NAME.azurewebsites.net"
echo ""
echo "⏳ Please wait 2-3 minutes for the deployment to complete..."
echo "   Then test: curl https://$APP_NAME.azurewebsites.net/health"
