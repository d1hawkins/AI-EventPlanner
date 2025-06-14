#!/bin/bash
# Script to update the AI Event Planner application in Azure to use real agents
# This script updates the startup files to use app.main_saas:app instead of app_adapter:app

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to Azure
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo -e "${YELLOW}Not logged in to Azure. Please login.${NC}"
    az login
}

# Check if the app exists
echo "Checking if the app exists in Azure..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}Error: App $APP_NAME not found in resource group $RESOURCE_GROUP.${NC}"
    exit 1
fi

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy the updated files to the deployment directory
echo "Copying updated files to deployment directory..."
mkdir -p $DEPLOY_DIR
cp startup.py $DEPLOY_DIR/
cp startup.sh $DEPLOY_DIR/
cp wsgi.py $DEPLOY_DIR/
cp web.config $DEPLOY_DIR/
cp app_adapter_with_agents.py $DEPLOY_DIR/app_adapter.py
cp requirements.txt $DEPLOY_DIR/
cp run_azure_migrations_fixed.py $DEPLOY_DIR/
chmod +x $DEPLOY_DIR/startup.sh

# Copy the scripts directory
echo "Copying scripts directory..."
mkdir -p $DEPLOY_DIR/scripts
if [ -d "scripts" ]; then
    cp -r scripts/* $DEPLOY_DIR/scripts/
    # Ensure __init__.py exists in scripts directory
    touch $DEPLOY_DIR/scripts/__init__.py
fi

# Create app directory structure with __init__.py files
echo "Creating app directory structure..."
mkdir -p $DEPLOY_DIR/app
touch $DEPLOY_DIR/app/__init__.py

# Copy the entire app directory with proper structure
echo "Copying app directory with proper structure..."
for dir in agents auth db middleware graphs tools schemas state utils web; do
    if [ -d "app/$dir" ]; then
        echo "Copying app/$dir..."
        mkdir -p $DEPLOY_DIR/app/$dir
        cp -r app/$dir/* $DEPLOY_DIR/app/$dir/
        # Ensure __init__.py exists in each directory
        touch $DEPLOY_DIR/app/$dir/__init__.py
    fi
done

# Copy any Python files in the app root
echo "Copying Python files in app root..."
cp app/*.py $DEPLOY_DIR/app/ 2>/dev/null || :

# Make sure __init__.py exists in all subdirectories
echo "Ensuring __init__.py exists in all subdirectories..."
find $DEPLOY_DIR/app -type d -exec touch {}/__init__.py \;

# Print the list of files being deployed
echo "Files being deployed:"
ls -la $DEPLOY_DIR
echo "App directory contents:"
ls -la $DEPLOY_DIR/app
echo "App/agents directory contents:"
ls -la $DEPLOY_DIR/app/agents

# Create a zip file for deployment
echo "Creating deployment package..."
cd $DEPLOY_DIR
zip -r ../update-agents.zip .
cd ..

# Deploy to Azure App Service
echo "Deploying updated files to Azure App Service..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src update-agents.zip

# Set environment variables
echo "Setting critical environment variables..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
    "ENABLE_AGENT_LOGGING=true" \
    "AGENT_MEMORY_STORAGE=file" \
    "AGENT_MEMORY_PATH=/home/site/wwwroot/agent_memory" \
    "PYTHONPATH=/home/site/wwwroot" \
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7"

# Restart the app
echo "Restarting the app..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm -f update-agents.zip

echo -e "${GREEN}Update completed successfully.${NC}"
echo -e "Your application has been updated to use real agents and is available at: https://$APP_NAME.azurewebsites.net"
echo -e "Please allow a few minutes for the changes to take effect."
echo -e "You can check the logs at: https://$APP_NAME.scm.azurewebsites.net/api/logs/docker"
