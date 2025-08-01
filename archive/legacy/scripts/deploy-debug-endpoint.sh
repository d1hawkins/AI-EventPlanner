#!/bin/bash

# Deploy Debug Endpoint to Azure
# This script deploys the updated agent code with debug endpoint to Azure

set -e

echo "=== Deploying Debug Endpoint to Azure ==="
echo "Timestamp: $(date)"

# Check if we have the necessary files
if [ ! -f "app/agents/api_router.py" ]; then
    echo "❌ Error: app/agents/api_router.py not found"
    exit 1
fi

if [ ! -f "app/web/static/saas/js/agent-ui.js" ]; then
    echo "❌ Error: app/web/static/saas/js/agent-ui.js not found"
    exit 1
fi

echo "✅ Required files found"

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "❌ Error: Azure CLI not found. Please install Azure CLI first."
    exit 1
fi

echo "✅ Azure CLI found"

# Check if we're logged in to Azure
if ! az account show &> /dev/null; then
    echo "❌ Error: Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

echo "✅ Azure login verified"

# Set Azure app name
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

echo "📦 Preparing deployment package..."

# Create a temporary deployment directory
DEPLOY_DIR="deploy_debug_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Copy essential files
echo "📋 Copying application files..."
cp -r app/ "$DEPLOY_DIR/"
cp -r migrations/ "$DEPLOY_DIR/"
cp -r scripts/ "$DEPLOY_DIR/"
cp requirements.txt "$DEPLOY_DIR/"
cp app_adapter_with_agents_fixed.py "$DEPLOY_DIR/"
cp .env.azure.sample "$DEPLOY_DIR/.env"

# Copy startup files
if [ -f "startup.py" ]; then
    cp startup.py "$DEPLOY_DIR/"
fi

if [ -f "web.config" ]; then
    cp web.config "$DEPLOY_DIR/"
fi

echo "🔧 Creating startup script..."
cat > "$DEPLOY_DIR/startup.sh" << 'EOF'
#!/bin/bash
echo "Starting Azure deployment with debug endpoint..."

# Set Python path
export PYTHONPATH="/home/site/wwwroot:/home/site/wwwroot/app"

# Install dependencies if needed
if [ ! -d "/home/site/wwwroot/.venv" ]; then
    echo "Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
fi

# Start the application
echo "Starting application..."
python app_adapter_with_agents_fixed.py
EOF

chmod +x "$DEPLOY_DIR/startup.sh"

echo "🚀 Deploying to Azure App Service..."

# Deploy using Azure CLI
cd "$DEPLOY_DIR"
zip -r "../${DEPLOY_DIR}.zip" .
cd ..

echo "📤 Uploading deployment package..."
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src "${DEPLOY_DIR}.zip"

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🔗 App URL: https://${APP_NAME}.azurewebsites.net"
    echo "🐛 Debug endpoint: https://${APP_NAME}.azurewebsites.net/api/agents/debug/memory/{conversation_id}"
    
    # Wait a moment for deployment to complete
    echo "⏳ Waiting for deployment to complete..."
    sleep 30
    
    # Test the debug endpoint
    echo "🧪 Testing debug endpoint..."
    python ../test_debug_endpoint.py
    
else
    echo "❌ Deployment failed!"
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up..."
rm -rf "$DEPLOY_DIR"
rm -f "${DEPLOY_DIR}.zip"

echo "✅ Debug endpoint deployment complete!"
