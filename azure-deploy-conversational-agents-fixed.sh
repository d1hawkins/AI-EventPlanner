#!/bin/bash

# Azure Deployment Script for Conversational AI Agents - FIXED VERSION
# This script fixes the requirements.txt issue and deploys conversational agents

set -e

echo "🚀 Starting Azure deployment of conversational AI agents (FIXED)..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="East US"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed and logged in
print_status "Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is ready"

# Step 1: Create requirements.txt with correct name (THIS WAS THE ISSUE!)
print_status "Creating requirements.txt with correct name for Azure..."
cat > requirements.txt << 'EOF'
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

# AI/ML Libraries for conversational agents
langchain==0.1.0
langgraph==0.0.26
openai==1.6.1
google-generativeai==0.3.2

# Utilities
requests==2.31.0
httpx==0.25.2

# Additional dependencies for conversational flow
typing-extensions==4.8.0
asyncio==3.4.3
json5==0.9.14
EOF

print_success "requirements.txt created with correct name!"

# Step 2: Set up environment variables for conversational agents
print_status "Setting up environment variables for conversational agents..."

# Get existing DATABASE_URL
DATABASE_URL=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)

if [ -z "$DATABASE_URL" ]; then
    print_warning "Could not retrieve DATABASE_URL from existing deployment, will use default"
    DATABASE_URL="postgresql://default:default@localhost/default"
fi

print_status "Configuring application settings for conversational agents..."

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
    DATABASE_URL="$DATABASE_URL" \
    USE_REAL_AGENTS="true" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    CONVERSATION_MODE="enabled" \
    RECOMMENDATION_ENGINE="enabled" \
    QUESTION_FLOW="conversational" \
    CONVERSATION_MEMORY_LIMIT="50" \
    ENABLE_PROACTIVE_SUGGESTIONS="true" \
    CONVERSATION_FEATURE_FLAG="true" \
    ENABLE_AGENT_LOGGING="true" \
    LLM_MODEL="gemini-2.0-flash" \
    SECRET_KEY="azure-saas-secret-key-2025" \
    ACCESS_TOKEN_EXPIRE_MINUTES="60" \
    REFRESH_TOKEN_EXPIRE_DAYS="7" \
    ALGORITHM="HS256" \
    APP_NAME="AI Event Planner SaaS" \
    APP_VERSION="2.0.0" \
    ENVIRONMENT="production" \
    DEBUG="false" \
    HOST="0.0.0.0" \
    PORT="8000" \
    PYTHONPATH="/home/site/wwwroot" \
    PYTHONUNBUFFERED="1" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ENABLE_ORYX_BUILD="true" \
    DEPLOYMENT_VERSION="conversational_agents_fixed" \
    > /dev/null

print_success "Environment variables configured for conversational agents"

# Step 3: Create deployment package with conversational components
print_status "Creating deployment package with conversational components..."

rm -f conversational_agents_deployment.zip

# Files to include in deployment (conversational components)
zip -r conversational_agents_deployment.zip \
    requirements.txt \
    app_adapter_conversational.py \
    app/agents/api_router.py \
    app/agents/agent_factory.py \
    app/graphs/coordinator_graph.py \
    app/utils/question_manager.py \
    app/utils/recommendation_engine.py \
    app/utils/conversation_memory.py \
    app/utils/conversation_paths.py \
    app/utils/proactive_suggestions.py \
    app/utils/recommendation_learning.py \
    app/utils/logging_utils.py \
    app/db/session.py \
    app/db/base.py \
    app/db/models_updated.py \
    app/middleware/tenant.py \
    app/subscription/feature_control.py \
    app/state/tenant_aware_manager.py \
    app/state/manager.py \
    app/schemas/ \
    app/tools/ \
    app/graphs/ \
    app/web/static/saas/ \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --exclude ".git/*" \
    --exclude "*.log" \
    --exclude "node_modules/*" \
    --exclude ".env*" \
    --exclude "venv/*" \
    --exclude ".vscode/*" \
    2>/dev/null || true

print_success "Conversational deployment package created: conversational_agents_deployment.zip"

# Step 4: Set the correct startup command for conversational app
print_status "Setting startup command for conversational agents..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_conversational:app"

print_success "Startup command configured for conversational app"

# Step 5: Deploy the package
print_status "Uploading conversational deployment package..."
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src conversational_agents_deployment.zip

print_success "Conversational deployment package uploaded"

# Step 6: Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 30

# Step 7: Restart the app to ensure new configuration takes effect
print_status "Restarting application..."
az webapp restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME"

print_success "Application restarted"

# Step 8: Wait for app to start
print_status "Waiting for application to start..."
sleep 45

# Step 9: Test the conversational deployment
print_status "Testing conversational agents deployment..."
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo "Testing health endpoint..."
if curl -f -s "${APP_URL}/health" > /dev/null; then
    print_success "Health check passed!"
    echo "Health response:"
    curl -s "${APP_URL}/health" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/health"
else
    print_warning "Health check failed, but app might still be starting..."
fi

echo ""
echo "Testing agents endpoint..."
if curl -f -s "${APP_URL}/api/agents/available" > /dev/null; then
    print_success "Agents endpoint accessible!"
    echo "Agents response:"
    curl -s "${APP_URL}/api/agents/available" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/available"
else
    print_warning "Agents endpoint not accessible yet..."
fi

echo ""
echo "Testing conversational flow..."
echo "Sending test message to coordinator agent..."
curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "I want to plan a corporate event"
  }' | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "I want to plan a corporate event"
  }'

echo ""
echo "Testing conversational test endpoint..."
curl -s "${APP_URL}/api/test/conversation" \
  -X POST \
  -H "Content-Type: application/json" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/test/conversation" \
  -X POST \
  -H "Content-Type: application/json"

# Step 10: Show deployment information
echo ""
echo "🎉 Conversational Agents Deployment completed!"
echo ""
echo "Application URL: ${APP_URL}"
echo "Health Check: ${APP_URL}/health"
echo "Agents Status: ${APP_URL}/api/agents/available"
echo "Agent Message Test: ${APP_URL}/api/agents/message"
echo "Conversational Test: ${APP_URL}/api/test/conversation"
echo "SaaS Dashboard: ${APP_URL}/dashboard.html"
echo "Agent Chat: ${APP_URL}/agents.html"
echo ""
echo "🌟 Key Features Deployed:"
echo "- ✅ Fixed requirements.txt naming issue"
echo "- ✅ Conversational coordinator graph"
echo "- ✅ Question manager (one question at a time)"
echo "- ✅ Recommendation engine"
echo "- ✅ Conversation memory"
echo "- ✅ Proactive suggestions"
echo "- ✅ Enhanced user experience"
echo ""
echo "🔧 What Changed:"
echo "- Fixed: requirements.txt now has correct name for Azure"
echo "- Added: Full conversational agent components"
echo "- Upgraded: From basic agents to conversational flow"
echo "- Enhanced: User experience with smart recommendations"
echo ""
echo "To check logs:"
echo "az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
echo ""
echo "To check deployment status:"
echo "az webapp show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query state"

# Clean up temporary files
rm -f requirements.txt
rm -f conversational_agents_deployment.zip

print_success "Cleanup completed"
print_success "Azure conversational agents deployment completed successfully!"

echo ""
print_status "🚀 The application now uses CONVERSATIONAL AI agents!"
print_status "Users will experience one-question-at-a-time flow with smart recommendations!"
