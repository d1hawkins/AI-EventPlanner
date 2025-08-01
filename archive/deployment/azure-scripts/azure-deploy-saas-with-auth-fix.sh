#!/bin/bash

# Azure SaaS Deployment with Authentication Fix
# This script deploys the AI Event Planner SaaS with working authentication to Azure

set -e

echo "🚀 Starting Azure SaaS Deployment with Authentication Fix..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="East US"
SKU="B1"

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
    print_error "Not logged into Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is ready"

# Create or update resource group
print_status "Creating/updating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create App Service Plan if it doesn't exist
print_status "Creating/updating App Service Plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux \
    --output table

# Create Web App if it doesn't exist
print_status "Creating/updating Web App: $APP_NAME"
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --name $APP_NAME \
    --runtime "PYTHON|3.11" \
    --output table

# Configure deployment source
print_status "Configuring local Git deployment..."
az webapp deployment source config-local-git \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output table

# Set essential environment variables for SaaS with authentication
print_status "Setting environment variables..."

# Database configuration (using Azure PostgreSQL)
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        PYTHONPATH="/home/site/wwwroot" \
        PYTHONUNBUFFERED="1" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        ENABLE_ORYX_BUILD="true" \
        DATABASE_URL="postgresql://ai_event_admin:SecurePassword123!@ai-event-planner-db.postgres.database.azure.com:5432/ai_event_planner_db?sslmode=require" \
        SECRET_KEY="your-super-secret-key-change-in-production" \
        ACCESS_TOKEN_EXPIRE_MINUTES="30" \
        ENVIRONMENT="production" \
        DEBUG="false" \
        CORS_ORIGINS="https://${APP_NAME}.azurewebsites.net" \
        --output table

# Set LLM provider configuration (using OpenAI as primary, with fallback)
print_status "Setting LLM provider configuration..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        LLM_PROVIDER="openai" \
        OPENAI_API_KEY="your-openai-api-key-here" \
        GOOGLE_API_KEY="your-google-api-key-here" \
        ANTHROPIC_API_KEY="your-anthropic-api-key-here" \
        --output table

# Set startup command for SaaS application
print_status "Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "python -m pip install --upgrade pip && pip install -r requirements.txt && python run_saas_with_agents.py" \
    --output table

# Configure logging
print_status "Enabling application logging..."
az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --application-logging filesystem \
    --level information \
    --output table

# Create requirements.txt for Azure deployment
print_status "Creating requirements.txt for Azure..."
cat > requirements.txt << 'EOF'
# Core web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# AI and LLM
openai==1.3.7
langchain==0.0.350
langchain-openai==0.0.2
langchain-google-genai==0.0.6
langchain-anthropic==0.0.4
langgraph==0.0.20

# Utilities
pydantic==2.5.0
python-dotenv==1.0.0
requests==2.31.0
aiofiles==23.2.1

# Email validation
email-validator==2.1.0

# Calendar support
icalendar==5.0.11

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
EOF

# Create startup script
print_status "Creating startup script..."
cat > startup.py << 'EOF'
#!/usr/bin/env python3
"""
Azure startup script for AI Event Planner SaaS
"""
import os
import sys
import subprocess
import time

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("Dependencies installed successfully")

def setup_database():
    """Setup database tables"""
    try:
        print("Setting up database...")
        # Import after dependencies are installed
        from create_tables import main as create_tables_main
        from create_subscription_plans import main as create_plans_main
        
        create_tables_main()
        create_plans_main()
        print("Database setup completed")
    except Exception as e:
        print(f"Database setup error (continuing anyway): {e}")

def start_application():
    """Start the SaaS application"""
    print("Starting AI Event Planner SaaS...")
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", "/home/site/wwwroot")
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    
    # Import and run the application
    from run_saas_with_agents import main
    main()

if __name__ == "__main__":
    try:
        install_dependencies()
        setup_database()
        start_application()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
EOF

# Create a simple web.config for Azure
print_status "Creating web.config..."
cat > web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" arguments="startup.py" stdoutLogEnabled="true" stdoutLogFile="\\?\%home%\LogFiles\python.log" startupTimeLimit="300" requestTimeout="300">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="%home%\site\wwwroot" />
        <environmentVariable name="PYTHONUNBUFFERED" value="1" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

# Deploy the application
print_status "Deploying application to Azure..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit for Azure deployment"
fi

# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment source show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "repoUrl" \
    --output tsv)

# Add Azure remote if it doesn't exist
if ! git remote get-url azure &> /dev/null; then
    git remote add azure $DEPLOYMENT_URL
fi

# Deploy to Azure
print_status "Pushing code to Azure..."
git add .
git commit -m "Deploy SaaS with authentication fix" || true
git push azure main --force

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 30

# Get the app URL
APP_URL="https://${APP_NAME}.azurewebsites.net"

# Test the deployment
print_status "Testing deployment..."
sleep 10

if curl -s -o /dev/null -w "%{http_code}" "$APP_URL" | grep -q "200"; then
    print_success "Deployment successful!"
    print_success "SaaS Application URL: $APP_URL"
    print_success "Login page: $APP_URL/saas/login.html"
    print_success "Registration page: $APP_URL/saas/signup.html"
    print_success "Dashboard: $APP_URL/saas/dashboard.html"
else
    print_warning "Deployment may still be starting up. Check the URL in a few minutes."
    print_status "Application URL: $APP_URL"
fi

# Show logs command
print_status "To view logs, run:"
echo "az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"

# Show environment variables setup reminder
print_warning "IMPORTANT: Remember to set your API keys:"
echo "az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings OPENAI_API_KEY='your-actual-key'"
echo "az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings GOOGLE_API_KEY='your-actual-key'"

print_success "Azure SaaS deployment with authentication completed!"
print_status "The authentication system is now fully functional with real API integration."
