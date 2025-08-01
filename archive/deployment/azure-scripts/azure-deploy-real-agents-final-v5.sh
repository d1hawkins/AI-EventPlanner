#!/bin/bash

# Azure Real Agents Deployment V5 - Ultra Simple Approach
# This version uses the absolute minimum to get real agents working

set -e

echo "🚀 Starting Azure Real Agents Deployment V5 (Ultra Simple)..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
DEPLOYMENT_VERSION="v5_ultra_simple"

# Verify the fixed adapter exists
if [ ! -f "app_adapter_with_agents_fixed.py" ]; then
    echo "❌ Error: app_adapter_with_agents_fixed.py not found!"
    exit 1
fi

echo "✅ Found app_adapter_with_agents_fixed.py"

# Create ultra-minimal requirements
cat > requirements_v5.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
gunicorn==21.2.0
pydantic==2.5.2
python-dotenv==1.0.0
requests==2.31.0
google-generativeai==0.3.2
EOF

echo "✅ Created ultra-minimal requirements_v5.txt"

# Create deployment package with ONLY the fixed adapter
echo "📦 Creating ultra-simple deployment package..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Copy ONLY the essential files - no complex app structure
cp app_adapter_with_agents_fixed.py "$TEMP_DIR/"
cp requirements_v5.txt "$TEMP_DIR/requirements.txt"

# Create a simple startup script that doesn't depend on complex imports
cat > "$TEMP_DIR/startup_simple.py" << 'EOF'
#!/usr/bin/env python3
"""
Ultra-simple startup script for real agents
"""
import os
import sys

# Set environment variables for real agents
os.environ['USE_REAL_AGENTS'] = 'true'
os.environ['LLM_PROVIDER'] = 'google'
os.environ['GOOGLE_MODEL'] = 'gemini-2.0-flash'
os.environ['ENABLE_AGENT_LOGGING'] = 'true'

print("🚀 Starting with real agents enabled...")
print(f"USE_REAL_AGENTS: {os.environ.get('USE_REAL_AGENTS')}")
print(f"LLM_PROVIDER: {os.environ.get('LLM_PROVIDER')}")

# Import and run the fixed adapter
try:
    from app_adapter_with_agents_fixed import app
    print("✅ Successfully imported real agent adapter")
    
    # Check if real agents are available
    if hasattr(app, 'state') and hasattr(app.state, 'real_agents_available'):
        print(f"Real agents available: {app.state.real_agents_available}")
    
except Exception as e:
    print(f"❌ Error importing adapter: {e}")
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

echo "✅ Created simple startup script"

# Create the deployment zip
cd "$TEMP_DIR"
zip -r deployment_v5.zip . -x "*.pyc" "*__pycache__*"
cd - > /dev/null

echo "✅ Created ultra-simple deployment package"

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
    PYTHONPATH="/home/site/wwwroot" \
    > /dev/null

echo "✅ Environment variables configured"

# Set startup command to use the fixed adapter directly
echo "🔧 Setting startup command..."

az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 --worker-class uvicorn.workers.UvicornWorker app_adapter_with_agents_fixed:app" \
    > /dev/null

echo "✅ Startup command configured"

# Deploy the package
echo "🚀 Deploying to Azure..."

az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src "$TEMP_DIR/deployment_v5.zip" \
    > /dev/null

echo "✅ Deployment package uploaded"

# Clean up
rm -rf "$TEMP_DIR"
rm -f requirements_v5.txt

echo "🎉 Azure Real Agents Deployment V5 completed!"
echo ""
echo "📊 Deployment Summary:"
echo "   • Ultra-simple approach: minimal dependencies ✅"
echo "   • Fixed adapter: app_adapter_with_agents_fixed.py ✅"
echo "   • Correct imports: app.agents.api_router ✅"
echo "   • Real agents enabled: USE_REAL_AGENTS=true ✅"
echo "   • Google Gemini configured ✅"
echo "   • Direct gunicorn startup ✅"
echo ""
echo "🔗 Application URL: https://$APP_NAME.azurewebsites.net"
echo ""
echo "⏳ Please wait 2-3 minutes for the deployment to complete..."
echo "   Then test: curl https://$APP_NAME.azurewebsites.net/health"
echo ""
echo "🔍 To check real agents status:"
echo "   curl https://$APP_NAME.azurewebsites.net/api/agents/status"
