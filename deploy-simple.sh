#!/bin/bash
# Deploy and update the AI Event Planner SaaS application on Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if jq is installed and set a flag
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Using alternative approach for JSON parsing.${NC}"
    USE_JQ=false
else
    USE_JQ=true
fi

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

# Check if the App Service exists
echo "Checking if the App Service exists..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}Error: App Service does not exist. Please run azure-deploy-saas.sh first.${NC}"
    exit 1
fi

# Update environment variables from .env.azure
echo "Updating environment variables..."
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -z "$key" || "$key" == \#* ]]; then
        continue
    fi
    
    # Set environment variable
    az webapp config appsettings set \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings "$key=$value"
done < .env.azure

echo -e "${GREEN}Environment variables updated successfully!${NC}"

# Restart the web app to apply changes
echo "Restarting the web app..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

echo -e "${GREEN}Web app restarted successfully!${NC}"

# Run migrations using Kudu REST API
echo "Running database migrations..."

# Get publishing credentials
echo "Getting publishing credentials..."
if [ "$USE_JQ" = false ]; then
    # Get publishing credentials using direct Azure CLI queries
    USERNAME=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingUserName -o tsv)
    PASSWORD=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingPassword -o tsv)
else
    # Get publishing credentials using jq
    CREDS=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query "{username:publishingUserName, password:publishingPassword}" -o json)
    USERNAME=$(echo $CREDS | jq -r '.username')
    PASSWORD=$(echo $CREDS | jq -r '.password')
fi

# Find Python executable path
echo "Finding Python executable path..."
FIND_PYTHON_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"find / -name python3 2>/dev/null | head -n 1\", \"dir\":\"/\"}")

# Extract status code and response body
FIND_PYTHON_HTTP_STATUS=$(echo "$FIND_PYTHON_RESPONSE" | tail -n1)
FIND_PYTHON_BODY=$(echo "$FIND_PYTHON_RESPONSE" | sed '$d')

echo "Find Python response: $FIND_PYTHON_BODY"
echo "HTTP status: $FIND_PYTHON_HTTP_STATUS"

# Extract Python path from the response
PYTHON_PATH=$(echo "$FIND_PYTHON_BODY" | grep -o '/[a-zA-Z0-9/_.-]*python3' | head -n 1 || echo "")

if [ -z "$PYTHON_PATH" ]; then
  echo "Python path not found, using default /usr/local/bin/python3"
  PYTHON_PATH="/usr/local/bin/python3"
else
  echo "Found Python path: $PYTHON_PATH"
fi

# Use the Python path to run the migration script
echo "Running migrations..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

echo "Migration response: $RESPONSE_BODY"
echo "HTTP status: $HTTP_STATUS"

# Check if the request was successful
if [ "$HTTP_STATUS" -ne 200 ]; then
  echo -e "${RED}Migration failed with status $HTTP_STATUS${NC}"
  echo -e "${RED}Response: $RESPONSE_BODY${NC}"
  exit 1
fi

# Check if the response contains error messages
if echo "$RESPONSE_BODY" | grep -i "error"; then
  echo -e "${RED}Migration script reported errors${NC}"
  echo -e "${RED}Response details: $RESPONSE_BODY${NC}"
  exit 1
fi

echo -e "${GREEN}Database migrations completed successfully!${NC}"

# Get the URL of the deployed application
APP_URL="https://$APP_NAME.azurewebsites.net"

echo -e "${GREEN}Deployment updated successfully!${NC}"
echo -e "${GREEN}Your application is available at: $APP_URL${NC}"
echo -e "${GREEN}SaaS application available at: $APP_URL/static/saas/index.html${NC}"
