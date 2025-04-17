#!/bin/bash
# Script to check the Azure App Service logs
# This script will check the logs of the Azure App Service to see what's happening

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

# Check the logs
echo "Checking the logs..."
echo "You can also check the logs at: https://$APP_NAME.scm.azurewebsites.net/api/logs/docker"

# Get the logs
echo "Getting the logs..."
az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file logs.zip

# Extract the logs
echo "Extracting the logs..."
unzip -o logs.zip -d logs

# Check for errors in the logs
echo "Checking for errors in the logs..."
grep -r "Error" logs || echo "No errors found in the logs."
grep -r "Exception" logs || echo "No exceptions found in the logs."
grep -r "ModuleNotFoundError" logs || echo "No ModuleNotFoundError found in the logs."

# Check for passlib in the logs
echo "Checking for passlib in the logs..."
grep -r "passlib" logs || echo "No passlib found in the logs."

# Check for auth in the logs
echo "Checking for auth in the logs..."
grep -r "auth" logs || echo "No auth found in the logs."

# Check for router in the logs
echo "Checking for router in the logs..."
grep -r "router" logs || echo "No router found in the logs."

# Check for dependencies in the logs
echo "Checking for dependencies in the logs..."
grep -r "dependencies" logs || echo "No dependencies found in the logs."

# Check for startup in the logs
echo "Checking for startup in the logs..."
grep -r "startup" logs || echo "No startup found in the logs."

# Check for wsgi in the logs
echo "Checking for wsgi in the logs..."
grep -r "wsgi" logs || echo "No wsgi found in the logs."

# Check for app_adapter in the logs
echo "Checking for app_adapter in the logs..."
grep -r "app_adapter" logs || echo "No app_adapter found in the logs."

# Check for main_saas in the logs
echo "Checking for main_saas in the logs..."
grep -r "main_saas" logs || echo "No main_saas found in the logs."

# Clean up
echo "Cleaning up..."
rm -f logs.zip

echo -e "${GREEN}Log check completed.${NC}"
echo "You can find the logs in the logs directory."
