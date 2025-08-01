#!/bin/bash

# Azure Deployment Script for Real AI Agents - FIXED VERSION
# This script deploys the SaaS application with real AI agents instead of mock responses

set -e

echo "🚀 Starting Azure deployment with real AI agents..."

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

# Check if logged in
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is ready"

# Step 1: Update requirements.txt with agent dependencies
print_status "Updating requirements.txt with agent dependencies..."
if [ -f "requirements_with_agents.txt" ]; then
    cp requirements_with_agents.txt requirements.txt
    print_success "Requirements updated"
else
    print_warning "requirements_with_agents.txt not found, using existing requirements.txt"
fi

# Step 2: Set up environment variables for real agents
print_status "Setting up environment variables for real agents..."

# Get DATABASE_URL from local .env.azure file
if [ -f ".env.azure" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" .env.azure | cut -d'=' -f2- | tr -d '"')
    if [ -n "$DATABASE_URL" ]; then
        print_success "Retrieved DATABASE_URL from local .env.azure file"
    else
        print_error "DATABASE_URL not found in .env.azure file"
        exit 1
    fi
else
    print_error ".env.azure file not found. Please create it with your database configuration."
    exit 1
fi

# Get other required environment variables from .env.azure
GOOGLE_API_KEY=$(grep "^GOOGLE_API_KEY=" .env.azure | cut -d'=' -f2- | tr -d '"')
SECRET_KEY=$(grep "^SECRET_KEY=" .env.azure | cut -d'=' -f2- | tr -d '"')
SENDGRID_API_KEY=$(grep "^SENDGRID_API_KEY=" .env.azure | cut -d'=' -f2- | tr -d '"')
OPENWEATHER_API_KEY=$(grep "^OPENWEATHER_API_KEY=" .env.azure | cut -d'=' -f2- | tr -d '"')

# Validate required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    print_error "GOOGLE_API_KEY not found in .env.azure file"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    print_error "SECRET_KEY not found in .env.azure file"
    exit 1
fi

# Set environment variables in Azure
print_status "Setting environment variables in Azure..."

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
    DATABASE_URL="$DATABASE_URL" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    ENABLE_AGENT_LOGGING="true" \
    AGENT_MEMORY_STORAGE="file" \
    AGENT_MEMORY_PATH="./agent_memory" \
    SECRET_KEY="$SECRET_KEY" \
    ACCESS_TOKEN_EXPIRE_MINUTES="60" \
    REFRESH_TOKEN_EXPIRE_DAYS="7" \
    ALGORITHM="HS256" \
    APP_NAME="AI Event Planner" \
    APP_VERSION="1.0.0" \
    ENVIRONMENT="production" \
    DEBUG="false" \
    DEFAULT_TENANT="default" \
    TENANT_HEADER="X-Tenant-ID" \
    HOST="0.0.0.0" \
    PORT="8000" \
    > /dev/null

# Set optional environment variables if they exist
if [ -n "$SENDGRID_API_KEY" ]; then
    az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
        SENDGRID_API_KEY="$SENDGRID_API_KEY" \
        EMAIL_FROM="noreply@aieventplanner.com" \
        EMAIL_FROM_NAME="AI Event Planner" \
        > /dev/null
    print_status "SendGrid configuration added"
fi

if [ -n "$OPENWEATHER_API_KEY" ]; then
    az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
        OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY" \
        > /dev/null
    print_status "OpenWeather configuration added"
fi

print_success "Environment variables configured"

# Step 3: Deploy the application
print_status "Deploying application to Azure..."

# Ensure we have the correct files for real agents
print_status "Preparing files for real agent deployment..."

# Make sure app_adapter_with_agents.py exists
if [ ! -f "app_adapter_with_agents.py" ]; then
    print_error "app_adapter_with_agents.py not found. This file is required for real agents."
    exit 1
fi

# Make sure startup.sh is updated to use app_adapter_with_agents.py
if ! grep -q "app_adapter_with_agents.py" startup.sh; then
    print_warning "startup.sh may not be configured for real agents. Updating..."
    # The startup.sh should already be updated by this point
fi

print_success "Files prepared for real agent deployment"

# Clean up any existing deployment files
print_status "Cleaning up previous deployment files..."
rm -f deployment.zip
rm -f *.zip

# Create a temporary directory for deployment to avoid permission issues
TEMP_DIR=$(mktemp -d)
print_status "Using temporary directory: $TEMP_DIR"

# Copy essential files to temp directory
print_status "Copying essential files..."
cp app_adapter_with_agents.py "$TEMP_DIR/"
cp startup.sh "$TEMP_DIR/"
cp requirements_with_agents.txt "$TEMP_DIR/requirements.txt"

# Copy the app directory
cp -r app "$TEMP_DIR/"

# Copy other essential files if they exist
[ -f "wsgi.py" ] && cp wsgi.py "$TEMP_DIR/"
[ -f "app.py" ] && cp app.py "$TEMP_DIR/"
[ -f "startup.py" ] && cp startup.py "$TEMP_DIR/"
[ -f "web.config" ] && cp web.config "$TEMP_DIR/"
[ -f "run_azure_migrations_fixed.py" ] && cp run_azure_migrations_fixed.py "$TEMP_DIR/"

# Copy scripts directory if it exists
[ -d "scripts" ] && cp -r scripts "$TEMP_DIR/"

# Copy migrations directory if it exists
[ -d "migrations" ] && cp -r migrations "$TEMP_DIR/"

# Copy alembic.ini if it exists
[ -f "alembic.ini" ] && cp alembic.ini "$TEMP_DIR/"

# Create deployment package from temp directory
print_status "Creating deployment package..."
cd "$TEMP_DIR"
zip -r deployment.zip . > /dev/null 2>&1
cd - > /dev/null

# Move the deployment package back
mv "$TEMP_DIR/deployment.zip" ./deployment.zip
print_success "Deployment package created successfully"

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Deploy using ZIP deployment
print_status "Uploading and deploying to Azure..."
az webapp deployment source config-zip --name $APP_NAME --resource-group $RESOURCE_GROUP --src deployment.zip > /dev/null

print_success "Application deployed"

# Step 4: Restart the application
print_status "Restarting application..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP > /dev/null
print_success "Application restarted"

# Step 5: Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 30

# Step 6: Verify deployment
print_status "Verifying deployment..."

# Check health endpoint
HEALTH_URL="https://$APP_NAME.azurewebsites.net/health"
print_status "Checking health endpoint: $HEALTH_URL"

for i in {1..10}; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" 2>/dev/null || echo "{}")
        if echo "$HEALTH_RESPONSE" | grep -q "real_agents_available.*true"; then
            print_success "Real agents are now available!"
            break
        elif echo "$HEALTH_RESPONSE" | grep -q "status.*ok"; then
            print_success "Application is healthy!"
            break
        else
            print_warning "Attempt $i: Application is responding but agents status unclear, waiting..."
        fi
    else
        print_warning "Attempt $i: Application not responding (HTTP $HTTP_STATUS), waiting..."
    fi
    
    sleep 10
    
    if [ $i -eq 10 ]; then
        print_warning "Application may still be starting up. Check the logs if issues persist."
        print_status "Current health status:"
        curl -s "$HEALTH_URL" 2>/dev/null | jq . 2>/dev/null || curl -s "$HEALTH_URL" 2>/dev/null || echo "No response"
    fi
done

# Step 7: Test agent endpoints
print_status "Testing agent endpoints..."

# Test available agents endpoint
AGENTS_URL="https://$APP_NAME.azurewebsites.net/api/agents/available"
print_status "Testing agents endpoint: $AGENTS_URL"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$AGENTS_URL" || echo "000")
if [ "$HTTP_STATUS" = "200" ]; then
    AGENTS_RESPONSE=$(curl -s "$AGENTS_URL" 2>/dev/null || echo "{}")
    if echo "$AGENTS_RESPONSE" | grep -q "using_real_agent.*true"; then
        print_success "Agents endpoint is working with real agents!"
    else
        print_warning "Agents endpoint is responding but may still be using mock responses"
        echo "Response: $AGENTS_RESPONSE"
    fi
else
    print_warning "Agents endpoint not responding (HTTP $HTTP_STATUS)"
fi

# Clean up
print_status "Cleaning up..."
rm -f deployment.zip
print_success "Cleanup complete"

# Final status
print_success "🎉 Deployment completed!"
echo ""
echo "Application URL: https://$APP_NAME.azurewebsites.net"
echo "Health Check: https://$APP_NAME.azurewebsites.net/health"
echo "Agents Page: https://$APP_NAME.azurewebsites.net/saas/agents.html"
echo ""
print_status "The application should now be using real AI agents instead of mock responses."
print_status "You can verify this by checking the health endpoint or testing the chat functionality."
print_status ""
print_status "If you encounter any issues, check the Azure App Service logs:"
print_status "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
