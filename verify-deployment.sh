#!/bin/bash
# Verify Azure Deployment for AI Event Planner SaaS

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"
APP_URL="https://$APP_NAME.azurewebsites.net"
SAAS_URL="$APP_URL/static/saas/index.html"

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

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is not installed. Please install it first.${NC}"
    exit 1
fi

# Verify App Service exists
echo "Verifying App Service exists..."
if az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}App Service exists.${NC}"
else
    echo -e "${RED}Error: App Service does not exist.${NC}"
    exit 1
fi

# Check App Service status
echo "Checking App Service status..."
status=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query state -o tsv)
if [ "$status" == "Running" ]; then
    echo -e "${GREEN}App Service is running.${NC}"
else
    echo -e "${RED}Error: App Service is not running. Current state: $status${NC}"
    exit 1
fi

# Check if the application is accessible
echo "Checking if the application is accessible..."
if curl -s -o /dev/null -w "%{http_code}" $APP_URL | grep -q "2[0-9][0-9]\|3[0-9][0-9]"; then
    echo -e "${GREEN}Application is accessible.${NC}"
else
    echo -e "${RED}Error: Application is not accessible.${NC}"
    exit 1
fi

# Check if the SaaS application is accessible
echo "Checking if the SaaS application is accessible..."
if curl -s -o /dev/null -w "%{http_code}" $SAAS_URL | grep -q "2[0-9][0-9]\|3[0-9][0-9]"; then
    echo -e "${GREEN}SaaS application is accessible.${NC}"
else
    echo -e "${RED}Error: SaaS application is not accessible.${NC}"
    exit 1
fi

# Check application logs for errors
echo "Checking application logs for errors..."
logs=$(az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --filter Error)
if [ -z "$logs" ]; then
    echo -e "${GREEN}No errors found in application logs.${NC}"
else
    echo -e "${YELLOW}Warning: Errors found in application logs:${NC}"
    echo "$logs"
fi

# Check database connection
echo "Checking database connection..."

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

# Extract Python path from the response
PYTHON_PATH=$(echo "$FIND_PYTHON_BODY" | grep -o '/[a-zA-Z0-9/_.-]*python3' | head -n 1 || echo "")

if [ -z "$PYTHON_PATH" ]; then
  echo "Python path not found, using default /usr/local/bin/python3"
  PYTHON_PATH="/usr/local/bin/python3"
else
  echo "Found Python path: $PYTHON_PATH"
fi

# Check database connection using Kudu REST API
DB_CONN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -c 'from app.db.session import engine; print(\\\"Connected\\\" if engine.connect() else \\\"Failed\\\")';\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
DB_CONN_HTTP_STATUS=$(echo "$DB_CONN_RESPONSE" | tail -n1)
DB_CONN_BODY=$(echo "$DB_CONN_RESPONSE" | sed '$d')

if [[ $DB_CONN_BODY == *"Connected"* ]]; then
  echo -e "${GREEN}Database connection successful.${NC}"
else
  echo -e "${RED}Error: Database connection failed.${NC}"
  echo -e "${RED}Response: $DB_CONN_BODY${NC}"
  exit 1
fi

# Check if MCP servers are configured
echo "Checking MCP server configuration..."
sendgrid_key=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='SENDGRID_API_KEY'].value" -o tsv)
openweather_key=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='OPENWEATHER_API_KEY'].value" -o tsv)

if [ -n "$sendgrid_key" ]; then
    echo -e "${GREEN}SendGrid API key is configured.${NC}"
else
    echo -e "${YELLOW}Warning: SendGrid API key is not configured.${NC}"
fi

if [ -n "$openweather_key" ]; then
    echo -e "${GREEN}OpenWeather API key is configured.${NC}"
else
    echo -e "${YELLOW}Warning: OpenWeather API key is not configured.${NC}"
fi

# Check if Application Insights is configured
echo "Checking Application Insights configuration..."
insights_key=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='APPINSIGHTS_INSTRUMENTATIONKEY'].value" -o tsv)
if [ -n "$insights_key" ]; then
    echo -e "${GREEN}Application Insights is configured.${NC}"
else
    echo -e "${YELLOW}Warning: Application Insights is not configured.${NC}"
fi

echo -e "${GREEN}Deployment verification completed.${NC}"
echo -e "${GREEN}Your application is available at: $APP_URL${NC}"
echo -e "${GREEN}SaaS application available at: $SAAS_URL${NC}"
