#!/bin/bash
# Setup Azure Application Insights for AI Event Planner SaaS

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
INSIGHTS_NAME="$APP_NAME-insights"

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

echo "Creating Application Insights resource..."
az monitor app-insights component create \
    --app $INSIGHTS_NAME \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --application-type web

echo "Getting the instrumentation key..."
instrumentationKey=$(az monitor app-insights component show \
    --app $INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey -o tsv)

echo "Configuring the App Service to use Application Insights..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$instrumentationKey

# Add Application Insights SDK to requirements.txt if not already present
if ! grep -q "applicationinsights" requirements.txt; then
    echo "Adding Application Insights SDK to requirements.txt..."
    echo "applicationinsights>=0.11.9" >> requirements.txt
fi

echo -e "${GREEN}Application Insights setup completed successfully!${NC}"
echo -e "${GREEN}Instrumentation Key: $instrumentationKey${NC}"
echo -e "${YELLOW}You can view your application insights data at:${NC}"
echo -e "${YELLOW}https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents/resourceName/$INSIGHTS_NAME${NC}"
