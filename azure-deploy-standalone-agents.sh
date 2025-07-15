#!/bin/bash

# Azure Standalone Agents Deployment - Final Solution
# This version uses a completely standalone adapter with embedded agent functionality

set -e

echo "🚀 Starting Azure Standalone Agents Deployment..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
DEPLOYMENT_VERSION="standalone_v1"

# Verify the standalone adapter exists
if [ ! -f "app_adapter_standalone.py" ]; then
    echo "❌ Error: app_adapter_standalone.py not found!"
    exit 1
fi

echo "✅ Found app_adapter_standalone.py"

# Create minimal requirements for standalone deployment
cat > requirements_standalone.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
gunicorn==21.2.0
google-generativeai==0.3.2
EOF

echo "✅ Created minimal requirements for standalone deployment"

# Create deployment package
echo "📦 Creating standalone deployment package..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Copy only the standalone adapter and requirements
cp app_adapter_standalone.py "$TEMP_DIR/"
cp requirements_standalone.txt "$TEMP_DIR/requirements.txt"

# Copy static files if they exist (optional)
if [ -d "app/web/static/saas" ]; then
    echo "📁 Copying static files..."
    mkdir -p "$TEMP_DIR/app/web/static"
    cp -r app/web/static/saas "$TEMP_DIR/app/web/static/"
    echo "✅ Static files copied"
else
    echo "⚠️ Static files not found - will serve built-in HTML"
fi

# Create the deployment zip
cd "$TEMP_DIR"
zip -r deployment_standalone.zip . -x "*.pyc" "*__pycache__*"
cd - > /dev/null

echo "✅ Created standalone deployment package"

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
    DEPLOYMENT_VERSION="$DEPLOYMENT_VERSION" \
    PYTHONPATH="/home/site/wwwroot" \
    > /dev/null

echo "✅ Environment variables configured"

# Set startup command to use the standalone adapter
echo "🔧 Setting startup command..."

az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_standalone:app" \
    > /dev/null

echo "✅ Startup command configured"

# Deploy the package
echo "🚀 Deploying to Azure..."

az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src "$TEMP_DIR/deployment_standalone.zip" \
    > /dev/null

echo "✅ Deployment package uploaded"

# Clean up
rm -rf "$TEMP_DIR"
rm -f requirements_standalone.txt

echo "🎉 Azure Standalone Agents Deployment completed!"
echo ""
echo "📊 Deployment Summary:"
echo "   • Standalone approach: no complex imports ✅"
echo "   • Embedded agent functionality ✅"
echo "   • Google Gemini integration ✅"
echo "   • Real agents enabled: USE_REAL_AGENTS=true ✅"
echo "   • Minimal dependencies ✅"
echo "   • Direct gunicorn startup ✅"
echo ""
echo "🔗 Application URL: https://$APP_NAME.azurewebsites.net"
echo ""
echo "⏳ Please wait 2-3 minutes for the deployment to complete..."
echo "   Then test: curl https://$APP_NAME.azurewebsites.net/health"
echo ""
echo "🔍 To check real agents status:"
echo "   curl https://$APP_NAME.azurewebsites.net/api/agents/available"
echo ""
echo "🧪 To test agent functionality:"
echo '   curl -X POST https://$APP_NAME.azurewebsites.net/api/agents/message \'
echo '   -H "Content-Type: application/json" \'
echo '   -d '"'"'{"agent_type": "coordinator", "message": "Help me plan a corporate event"}'"'"
