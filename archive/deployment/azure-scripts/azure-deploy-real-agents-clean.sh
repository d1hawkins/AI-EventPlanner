#!/bin/bash

# Azure Deployment Script for SaaS with Real Conversational Agents
# This script deploys a completely fresh instance with real Google AI agents

set -e

echo "🚀 Starting Fresh Azure Deployment with Real Agents..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="eastus"
RUNTIME="PYTHON|3.11"

# Database credentials (preserved from previous deployment)
DATABASE_URL="postgresql://dbadmin:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner"

echo "📋 Deployment Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  App Name: $APP_NAME"
echo "  Location: $LOCATION"
echo "  Runtime: $RUNTIME"
echo "  Database: Preserved existing Azure PostgreSQL"

# Step 1: Create App Service Plan (if it doesn't exist)
echo "🏗️  Creating App Service Plan..."
az appservice plan create \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux || echo "App Service Plan already exists"

# Step 2: Create Web App
echo "🌐 Creating Web App..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "${APP_NAME}-plan" \
  --name $APP_NAME \
  --runtime $RUNTIME

# Step 3: Configure environment variables for real agents
echo "⚙️  Setting environment variables for real agents..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    DATABASE_URL="$DATABASE_URL" \
    USE_REAL_AGENTS="true" \
    LLM_PROVIDER="google" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    ENVIRONMENT="production" \
    SECRET_KEY="your-secret-key-here" \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="30" \
    ENABLE_CONVERSATIONAL_MODE="true" \
    AGENT_TIMEOUT="300" \
    MAX_CONVERSATION_HISTORY="50"

# Step 4: Create deployment package with correct requirements
echo "📦 Creating deployment package..."
DEPLOY_DIR="deploy_real_agents_$(date +%s)"
mkdir -p $DEPLOY_DIR

# Copy all application files
cp -r app/ $DEPLOY_DIR/
cp -r migrations/ $DEPLOY_DIR/
cp app_adapter_conversational.py $DEPLOY_DIR/
cp requirements_real_agents.txt $DEPLOY_DIR/requirements.txt
cp startup.py $DEPLOY_DIR/

# Create startup script
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting application with real agents..."
echo "Environment: $ENVIRONMENT"
echo "LLM Provider: $LLM_PROVIDER"
echo "Use Real Agents: $USE_REAL_AGENTS"

# Install dependencies
pip install -r requirements.txt

# Start the application
python startup.py
EOF

chmod +x $DEPLOY_DIR/startup.sh

# Step 5: Deploy to Azure
echo "🚀 Deploying to Azure..."
cd $DEPLOY_DIR
zip -r ../deployment.zip .
cd ..

az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --src deployment.zip

# Step 6: Configure startup command
echo "⚙️  Configuring startup command..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "python startup.py"

# Step 7: Wait for deployment and test
echo "⏳ Waiting for deployment to complete..."
sleep 60

echo "🧪 Testing real agent deployment..."
APP_URL="https://${APP_NAME}.azurewebsites.net"

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$APP_URL/health" || echo "Health check failed"

# Test real agent endpoint
echo "Testing real agent endpoint..."
AGENT_RESPONSE=$(curl -s -X POST "$APP_URL/api/agents/message" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "coordinator", "message": "Hello, test real agent"}')

echo "Agent Response: $AGENT_RESPONSE"

# Check if real agents are working
if echo "$AGENT_RESPONSE" | grep -q '"using_real_agent": true'; then
    echo "✅ SUCCESS: Real agents are working!"
    echo "🎉 Deployment completed successfully!"
    echo "🌐 Application URL: $APP_URL"
else
    echo "❌ WARNING: Agents may still be in mock mode"
    echo "Response: $AGENT_RESPONSE"
fi

# Cleanup
rm -rf $DEPLOY_DIR deployment.zip

echo "🏁 Deployment script completed!"
echo "📊 Check the application at: $APP_URL"
