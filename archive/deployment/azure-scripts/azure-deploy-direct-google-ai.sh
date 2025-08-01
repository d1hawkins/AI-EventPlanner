#!/bin/bash

# Azure Deployment Script - Direct Google AI Integration (Nuclear Option)
# This script deploys a completely self-contained adapter that bypasses all complex imports

set -e

echo "🚀 Starting Azure deployment with Direct Google AI Integration (Nuclear Option)..."

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

# Step 1: Create minimal requirements.txt for direct Google AI
print_status "Creating minimal requirements.txt for direct Google AI integration..."

cat > requirements_direct.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
google-generativeai==0.3.2
python-multipart==0.0.6
EOF

print_success "Minimal requirements.txt created"

# Step 2: Set up environment variables for direct Google AI
print_status "Setting up environment variables for direct Google AI..."

print_status "Configuring application settings for direct Google AI integration..."

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
    USE_REAL_AGENTS="true" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    ENABLE_AGENT_LOGGING="true" \
    LLM_MODEL="gemini-2.0-flash" \
    SECRET_KEY="azure-saas-secret-key-2025" \
    APP_NAME="AI Event Planner SaaS - Direct Google AI" \
    APP_VERSION="1.0.0" \
    ENVIRONMENT="production" \
    DEBUG="false" \
    HOST="0.0.0.0" \
    PORT="8000" \
    PYTHONPATH="/home/site/wwwroot" \
    PYTHONUNBUFFERED="1" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ENABLE_ORYX_BUILD="true" \
    DEPLOYMENT_VERSION="direct_google_ai_v1.0" \
    > /dev/null

print_success "Environment variables configured for direct Google AI"

# Step 3: Create deployment package with direct Google AI adapter
print_status "Creating deployment package with direct Google AI adapter..."

rm -f direct_google_ai_deployment.zip

# Create the deployment package with only essential files
print_status "Creating minimal deployment package..."
zip -r direct_google_ai_deployment.zip \
    requirements_direct.txt \
    app_adapter_direct_google_ai.py \
    2>/dev/null || true

# Verify the direct adapter is included
if unzip -l direct_google_ai_deployment.zip | grep -q "app_adapter_direct_google_ai.py"; then
    print_success "✅ Direct Google AI adapter is included in deployment package"
else
    print_error "❌ Direct Google AI adapter not found in package!"
    exit 1
fi

# Check if zip file was created successfully
if [ ! -f "direct_google_ai_deployment.zip" ]; then
    print_error "Deployment package was not created successfully!"
    exit 1
fi

# Get zip file size for verification
ZIP_SIZE=$(ls -lh direct_google_ai_deployment.zip | awk '{print $5}')
print_success "Direct Google AI deployment package created: direct_google_ai_deployment.zip (${ZIP_SIZE})"

# Step 4: Set the correct startup command for direct Google AI
print_status "Setting startup command for direct Google AI adapter..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_direct_google_ai:app"

print_success "Startup command configured for direct Google AI"

# Step 5: Deploy the package
print_status "Uploading direct Google AI deployment package..."
az webapp deploy \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src-path direct_google_ai_deployment.zip \
    --type zip

print_success "Direct Google AI deployment package uploaded"

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

# Step 9: Test the direct Google AI deployment
print_status "Testing direct Google AI deployment..."
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
echo "Testing direct Google AI agent message endpoint..."
echo "Sending test message to coordinator agent..."
curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "I need to plan a talent show for 200 people. Can you help me get started?",
    "conversation_id": "test-direct-google-ai"
  }' | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "I need to plan a talent show for 200 people. Can you help me get started?"
  }'

# Step 10: Show deployment information
echo ""
echo "🎉 Direct Google AI Deployment completed!"
echo ""
echo "Application URL: ${APP_URL}"
echo "Health Check: ${APP_URL}/health"
echo "Agents Status: ${APP_URL}/api/agents/available"
echo "Agent Message Test: ${APP_URL}/api/agents/message"
echo ""
echo "🔥 NUCLEAR OPTION DEPLOYED:"
echo "- Direct Google AI integration (no complex imports)"
echo "- Minimal dependencies (FastAPI + Google AI only)"
echo "- Self-contained adapter with no external module dependencies"
echo "- Bypasses all import issues completely"
echo ""
echo "Key Features:"
echo "- ✅ Direct Google Gemini 2.0 Flash integration"
echo "- ✅ Agent-specific prompts for different event planning roles"
echo "- ✅ Comprehensive error handling and fallbacks"
echo "- ✅ No dependency on complex agent system imports"
echo "- ✅ Immediate startup with no lazy loading needed"
echo ""
echo "Available Agents:"
echo "- coordinator: Main event planning coordination"
echo "- financial: Budget and cost management"
echo "- marketing: Event promotion and marketing"
echo "- stakeholder: Vendor and partner management"
echo ""
echo "To check logs:"
echo "az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
echo ""
echo "To check deployment status:"
echo "az webapp show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query state"

# Clean up temporary files
rm -f requirements_direct.txt
rm -f direct_google_ai_deployment.zip

print_success "Cleanup completed"
print_success "Direct Google AI deployment completed successfully!"

echo ""
print_status "🚀 NUCLEAR OPTION COMPLETE:"
print_status "✅ This deployment completely bypasses all import issues"
print_status "✅ Uses only FastAPI + Google AI (minimal dependencies)"
print_status "✅ Should provide REAL AI responses immediately"
print_status "✅ No complex agent system - just direct Google AI integration"
print_status ""
print_status "🎯 Test the agents now - they should provide real AI responses!"
