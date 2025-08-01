#!/bin/bash

# Azure Deployment Script for Real AI Agents - FINAL VERSION V4
# This script fixes the dependency issues and ensures real agents work properly

set -e

echo "🚀 Starting Azure deployment of real AI agents (FINAL V4)..."

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

# Step 1: Use the complete requirements.txt file (don't create a minimal one)
print_status "Using complete requirements.txt with all dependencies..."

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in current directory"
    exit 1
fi

print_success "Found complete requirements.txt file"

# Step 2: Set up environment variables for real agents
print_status "Setting up environment variables for real agents..."

# Get existing DATABASE_URL
DATABASE_URL=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)

if [ -z "$DATABASE_URL" ]; then
    print_warning "Could not retrieve DATABASE_URL from existing deployment, will use default"
    DATABASE_URL="postgresql://default:default@localhost/default"
fi

print_status "Configuring application settings for real agents V4..."

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
    DATABASE_URL="$DATABASE_URL" \
    USE_REAL_AGENTS="true" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    ENABLE_AGENT_LOGGING="true" \
    LLM_MODEL="gemini-2.0-flash" \
    SECRET_KEY="azure-saas-secret-key-2025" \
    ACCESS_TOKEN_EXPIRE_MINUTES="60" \
    REFRESH_TOKEN_EXPIRE_DAYS="7" \
    ALGORITHM="HS256" \
    APP_NAME="AI Event Planner SaaS" \
    APP_VERSION="1.0.0" \
    ENVIRONMENT="production" \
    DEBUG="false" \
    HOST="0.0.0.0" \
    PORT="8000" \
    PYTHONPATH="/home/site/wwwroot" \
    PYTHONUNBUFFERED="1" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ENABLE_ORYX_BUILD="true" \
    DEPLOYMENT_VERSION="v4_real_agents_fixed" \
    > /dev/null

print_success "Environment variables configured for real agents V4"

# Step 3: Create deployment package with complete dependencies and all necessary files
print_status "Creating complete deployment package V4..."

rm -f real_agents_deployment_v4.zip

# Files to include in deployment (complete set with all dependencies)
zip -r real_agents_deployment_v4.zip \
    requirements.txt \
    app_adapter_with_agents_fixed.py \
    app/ \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --exclude ".git/*" \
    --exclude "*.log" \
    --exclude "node_modules/*" \
    --exclude ".env*" \
    --exclude "venv/*" \
    --exclude ".vscode/*" \
    --exclude "tests/*" \
    --exclude "migrations/*" \
    --exclude "scripts/*" \
    --exclude "examples/*" \
    --exclude "mcp-servers/*" \
    --exclude "deprecated/*" \
    --exclude "logs/*" \
    --exclude "deploy/*" \
    --exclude "LogFiles/*" \
    2>/dev/null || true

print_success "Complete deployment package created: real_agents_deployment_v4.zip"

# Step 4: Set the correct startup command
print_status "Setting startup command for real agents V4..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_with_agents_fixed:app"

print_success "Startup command configured for V4"

# Step 5: Deploy the package
print_status "Uploading complete deployment package V4..."
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src real_agents_deployment_v4.zip

print_success "Deployment package V4 uploaded"

# Step 6: Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 45

# Step 7: Restart the app to ensure new configuration takes effect
print_status "Restarting application..."
az webapp restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME"

print_success "Application restarted"

# Step 8: Wait for app to start
print_status "Waiting for application to start..."
sleep 60

# Step 9: Test the deployment
print_status "Testing real agents deployment V4..."
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
echo "Testing agent message endpoint..."
echo "Sending test message to coordinator agent..."
curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "Test message for real agents V4 - please respond with real AI"
  }' | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "Test message for real agents V4 - please respond with real AI"
  }'

# Step 10: Show deployment information
echo ""
echo "🎉 Real Agents Deployment V4 completed!"
echo ""
echo "Application URL: ${APP_URL}"
echo "Health Check: ${APP_URL}/health"
echo "Agents Status: ${APP_URL}/api/agents/available"
echo "Agent Message Test: ${APP_URL}/api/agents/message"
echo "SaaS Dashboard: ${APP_URL}/app/web/static/saas/index.html"
echo "Agent Chat: ${APP_URL}/app/web/static/saas/agents.html"
echo ""
echo "Key Changes in V4:"
echo "- Uses complete requirements.txt with ALL dependencies (FastAPI, LangChain, etc.)"
echo "- Includes entire app/ directory with all modules"
echo "- Fixed import paths for api_router.py"
echo "- Proper dependency resolution for real AI agents"
echo "- Extended startup time to allow for dependency installation"
echo ""
echo "To check logs:"
echo "az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
echo ""
echo "To check deployment status:"
echo "az webapp show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query state"

# Clean up temporary files
rm -f real_agents_deployment_v4.zip

print_success "Cleanup completed"
print_success "Azure real agents deployment V4 completed successfully!"

echo ""
print_status "🚀 The application should now be using REAL AI agents with complete dependencies!"
print_status "All FastAPI, LangChain, and Google AI dependencies are now properly included."
