#!/bin/bash
# Script to verify that the auth directory is properly deployed to Azure
# This script connects to the Azure App Service and checks if the auth directory and its files exist

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

# Connect to the Azure App Service using SSH
echo "Connecting to the Azure App Service using SSH..."
echo "Checking if the auth directory exists..."
AUTH_DIR_EXISTS=$(az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME --command "ls -la /home/site/wwwroot/app | grep auth")

if [ -n "$AUTH_DIR_EXISTS" ]; then
    echo -e "${GREEN}Auth directory exists in the deployment.${NC}"
    echo "Auth directory contents:"
    az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME --command "ls -la /home/site/wwwroot/app/auth"
else
    echo -e "${RED}Error: Auth directory does not exist in the deployment.${NC}"
    exit 1
fi

# Check if the auth router file exists
echo "Checking if the auth router file exists..."
AUTH_ROUTER_EXISTS=$(az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME --command "ls -la /home/site/wwwroot/app/auth | grep router.py")

if [ -n "$AUTH_ROUTER_EXISTS" ]; then
    echo -e "${GREEN}Auth router file exists in the deployment.${NC}"
else
    echo -e "${RED}Error: Auth router file does not exist in the deployment.${NC}"
    exit 1
fi

# Check if the auth dependencies file exists
echo "Checking if the auth dependencies file exists..."
AUTH_DEPENDENCIES_EXISTS=$(az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME --command "ls -la /home/site/wwwroot/app/auth | grep dependencies.py")

if [ -n "$AUTH_DEPENDENCIES_EXISTS" ]; then
    echo -e "${GREEN}Auth dependencies file exists in the deployment.${NC}"
else
    echo -e "${RED}Error: Auth dependencies file does not exist in the deployment.${NC}"
    exit 1
fi

# Check if the auth __init__.py file exists
echo "Checking if the auth __init__.py file exists..."
AUTH_INIT_EXISTS=$(az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME --command "ls -la /home/site/wwwroot/app/auth | grep __init__.py")

if [ -n "$AUTH_INIT_EXISTS" ]; then
    echo -e "${GREEN}Auth __init__.py file exists in the deployment.${NC}"
else
    echo -e "${RED}Error: Auth __init__.py file does not exist in the deployment.${NC}"
    exit 1
fi

echo -e "${GREEN}Verification completed successfully.${NC}"
echo -e "The auth directory and its files are properly deployed to Azure."
