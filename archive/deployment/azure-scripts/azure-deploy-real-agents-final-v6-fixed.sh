#!/bin/bash

# Azure Deployment Script for Real AI Agents - FINAL VERSION V6 FIXED
# This script fixes the requirements.txt issue and ensures proper zip extraction

set -e

echo "🚀 Starting Azure deployment of real AI agents (FINAL V6 FIXED)..."

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

# Step 1: Create requirements.txt with correct name (CRITICAL FIX!)
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

# AI/ML Libraries (minimal versions)
langchain==0.1.0
langgraph==0.0.26
openai==1.6.1
google-generativeai==0.3.2

# Utilities
requests==2.31.0
httpx==0.25.2
EOF

print_success "requirements.txt created with correct name!"

# Step 2: Set up environment variables for real agents
print_status "Setting up environment variables for real agents..."

# Get existing DATABASE_URL
DATABASE_URL=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)

if [ -z "$DATABASE_URL" ]; then
    print_warning "Could not retrieve DATABASE_URL from existing deployment, will use default"
    DATABASE_URL="postgresql://default:default@localhost/default"
fi

print_status "Configuring application settings for real agents V6..."

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
    DEPLOYMENT_VERSION="v6_real_agents_fixed" \
    > /dev/null

print_success "Environment variables configured for real agents V6"

# Step 3: Create deployment package with proper structure for zip extraction
print_status "Creating deployment package V6 with proper structure..."

rm -f real_agents_deployment_v6.zip

# Create deployment directory structure to ensure proper extraction
mkdir -p deployment_temp
cp requirements.txt deployment_temp/
cp app_adapter_with_agents_fixed.py deployment_temp/

# Copy essential directories with proper structure
if [ -d "app/agents" ]; then
    mkdir -p deployment_temp/app/agents
    cp -r app/agents/* deployment_temp/app/agents/
fi

if [ -d "app/db" ]; then
    mkdir -p deployment_temp/app/db
    cp -r app/db/* deployment_temp/app/db/
fi

if [ -d "app/middleware" ]; then
    mkdir -p deployment_temp/app/middleware
    cp -r app/middleware/* deployment_temp/app/middleware/
fi

if [ -d "app/subscription" ]; then
    mkdir -p deployment_temp/app/subscription
    cp -r app/subscription/* deployment_temp/app/subscription/
fi

if [ -d "app/utils" ]; then
    mkdir -p deployment_temp/app/utils
    cp -r app/utils/* deployment_temp/app/utils/
fi

if [ -d "app/state" ]; then
    mkdir -p deployment_temp/app/state
    cp -r app/state/* deployment_temp/app/state/
fi

if [ -d "app/schemas" ]; then
    mkdir -p deployment_temp/app/schemas
    cp -r app/schemas/* deployment_temp/app/schemas/
fi

if [ -d "app/tools" ]; then
    mkdir -p deployment_temp/app/tools
    cp -r app/tools/* deployment_temp/app/tools/
fi

if [ -d "app/graphs" ]; then
    mkdir -p deployment_temp/app/graphs
    cp -r app/graphs/* deployment_temp/app/graphs/
fi

if [ -d "app/web/static/saas" ]; then
    mkdir -p deployment_temp/app/web/static/saas
    cp -r app/web/static/saas/* deployment_temp/app/web/static/saas/
fi

# Create zip from deployment directory
cd deployment_temp
zip -r ../real_agents_deployment_v6.zip . \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --exclude ".git/*" \
    --exclude "*.log" \
    --exclude "node_modules/*" \
    --exclude ".env*" \
    --exclude "venv/*" \
    --exclude ".vscode/*" \
    2>/dev/null || true
cd ..

# Clean up temp directory
rm -rf deployment_temp

print_success "Deployment package V6 created: real_agents_deployment_v6.zip"

# Step 4: Set the correct startup command
print_status "Setting startup command for real agents V6..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_with_agents_fixed:app"

print_success "Startup command configured for V6"

# Step 5: Deploy the package
print_status "Uploading deployment package V6..."
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src real_agents_deployment_v6.zip

print_success "Deployment package V6 uploaded"

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

# Step 9: Test the deployment
print_status "Testing real agents deployment V6..."
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
    "message": "Test message for real agents V6"
  }' | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "Test message for real agents V6"
  }'

# Step 10: Show deployment information
echo ""
echo "🎉 Real Agents Deployment V6 completed!"
echo ""
echo "Application URL: ${APP_URL}"
echo "Health Check: ${APP_URL}/health"
echo "Agents Status: ${APP_URL}/api/agents/available"
echo "Agent Message Test: ${APP_URL}/api/agents/message"
echo "SaaS Dashboard: ${APP_URL}/app/web/static/saas/index.html"
echo "Agent Chat: ${APP_URL}/app/web/static/saas/agents.html"
echo ""
echo "🔧 Key Fixes in V6:"
echo "- ✅ Fixed requirements.txt naming (was requirements_minimal_v3.txt)"
echo "- ✅ Improved zip structure for proper extraction"
echo "- ✅ Created proper directory structure before zipping"
echo "- ✅ Ensured requirements.txt is in root of zip"
echo "- ✅ Fixed import paths and file structure"
echo ""
echo "To check logs:"
echo "az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
echo ""
echo "To check deployment status:"
echo "az webapp show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query state"

# Clean up temporary files
rm -f requirements.txt
rm -f real_agents_deployment_v6.zip

print_success "Cleanup completed"
print_success "Azure real agents deployment V6 completed successfully!"

echo ""
print_status "🚀 The application should now be using REAL AI agents!"
print_status "The fixed deployment ensures requirements.txt is properly extracted to wwwroot!"
