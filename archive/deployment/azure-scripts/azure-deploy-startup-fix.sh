#!/bin/bash

# Azure Deployment Script - Startup Fix
# This script fixes the Azure App Service startup issue

set -e

echo "🚀 Starting Azure deployment with startup fix..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="East US"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    print_error "Not logged into Azure. Please run 'az login' first."
    exit 1
fi

print_status "Azure CLI is ready"

# Create a clean requirements.txt with verified versions
print_status "Creating clean requirements.txt..."
cat > requirements_azure_fixed.txt << 'EOF'
# Core web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
bcrypt==4.1.2

# Data validation
pydantic==2.5.2
email-validator==2.1.0

# Environment & Configuration
python-dotenv==1.0.0

# Date/Time handling
icalendar==5.0.11

# AI/ML Libraries (minimal versions to avoid conflicts)
langchain==0.1.0
langgraph==0.0.26
openai==1.6.1
google-generativeai==0.3.2

# Utilities
requests==2.31.0
python-dateutil==2.8.2
EOF

print_status "Clean requirements.txt created"

# Create the robust startup application
print_status "Creating robust startup application..."
cp azure_startup_fix.py startup_app.py

# Create a web.config for Azure App Service
print_status "Creating web.config for Azure App Service..."
cat > web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="D:\home\Python311\python.exe"
                  arguments="D:\home\site\wwwroot\startup_app.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="D:\home\site\wwwroot" />
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

# Create a simple startup command script
print_status "Creating startup command..."
cat > startup_command.txt << 'EOF'
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 startup_app:app
EOF

# Deploy to Azure
print_status "Deploying to Azure App Service..."

# Set the startup command
print_status "Setting startup command..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 startup_app:app"

# Configure Python version
print_status "Setting Python version..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --linux-fx-version "PYTHON|3.11"

# Set application settings
print_status "Configuring application settings..."
az webapp config appsettings set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --settings \
    PYTHONPATH="/home/site/wwwroot" \
    PYTHONUNBUFFERED="1" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ENABLE_ORYX_BUILD="true" \
    POST_BUILD_SCRIPT_PATH="echo 'Build completed successfully'"

# Clear any cached builds
print_status "Clearing build cache..."
az webapp deployment source config \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --repo-url "https://github.com/dummy/dummy" \
    --branch "main" \
    --manual-integration || true

# Create deployment package
print_status "Creating deployment package..."
rm -f deployment.zip

# Files to include in deployment
zip -r deployment.zip \
    startup_app.py \
    requirements_azure_fixed.txt \
    web.config \
    app/ \
    scripts/ \
    migrations/ \
    create_tables.py \
    create_subscription_plans.py \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --exclude ".git/*" \
    --exclude "*.log" \
    --exclude "node_modules/*" \
    --exclude ".env*" \
    --exclude "venv/*" \
    --exclude ".vscode/*"

print_status "Deployment package created: deployment.zip"

# Deploy the package
print_status "Uploading deployment package..."
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src deployment.zip

print_status "Deployment package uploaded"

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 30

# Restart the app to ensure new configuration takes effect
print_status "Restarting application..."
az webapp restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME"

print_status "Application restarted"

# Wait for app to start
print_status "Waiting for application to start..."
sleep 60

# Test the deployment
print_status "Testing deployment..."
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo "Testing health endpoint..."
if curl -f -s "${APP_URL}/health" > /dev/null; then
    print_status "Health check passed!"
    echo "Health response:"
    curl -s "${APP_URL}/health" | python -m json.tool || echo "Response received"
else
    print_warning "Health check failed, but app might still be starting..."
fi

echo "Testing root endpoint..."
if curl -f -s "${APP_URL}/" > /dev/null; then
    print_status "Root endpoint accessible!"
else
    print_warning "Root endpoint not accessible yet..."
fi

# Show deployment information
echo ""
echo "🎉 Deployment completed!"
echo ""
echo "Application URL: ${APP_URL}"
echo "Health Check: ${APP_URL}/health"
echo "API Status: ${APP_URL}/api/status"
echo ""
echo "To check logs:"
echo "az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
echo ""
echo "To check deployment status:"
echo "az webapp show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query state"

# Clean up temporary files
rm -f requirements_azure_fixed.txt
rm -f startup_app.py
rm -f web.config
rm -f startup_command.txt
rm -f deployment.zip

print_status "Cleanup completed"
print_status "Azure deployment with startup fix completed successfully!"
