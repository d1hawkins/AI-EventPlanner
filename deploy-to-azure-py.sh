#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure App Service (Python)

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

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy application files to the deployment directory
echo "Copying application files..."
cp -r app $DEPLOY_DIR/
cp app_simplified.py $DEPLOY_DIR/
cp requirements_simplified.txt $DEPLOY_DIR/requirements.txt
cp startup.sh $DEPLOY_DIR/

# Make the startup script executable
chmod +x $DEPLOY_DIR/startup.sh

# Deploy to Azure App Service
echo "Deploying to Azure App Service..."
cd $DEPLOY_DIR
zip -r ../deploy.zip .
cd ..

echo "Uploading deployment package..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deploy.zip

# Configure the App Service
echo "Configuring App Service..."
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "startup.sh"
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings "WEBSITES_PORT=8000" "SCM_DO_BUILD_DURING_DEPLOYMENT=true"

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm -f deploy.zip

echo -e "${GREEN}Deployment completed successfully.${NC}"
echo -e "Your application is available at: https://$APP_NAME.azurewebsites.net"
