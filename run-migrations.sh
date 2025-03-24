
#!/bin/bash
# Run database migrations for AI Event Planner SaaS on Azure

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
    echo -e "${RED}Error: App Service does not exist.${NC}"
    exit 1
fi

# Run migrations using Kudu REST API
echo "Running database migrations..."
echo -e "${YELLOW}This may take a few minutes...${NC}"

# Install Azure CLI extensions if needed
echo "Installing Azure CLI extensions if needed..."
az extension add --name db-up

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
  
  # Provide troubleshooting steps
  echo -e "${YELLOW}Troubleshooting steps:${NC}"
  echo -e "${YELLOW}1. Check if the database connection string is correct in the App Service settings.${NC}"
  echo -e "${YELLOW}2. Check if the database server is accessible from the App Service.${NC}"
  echo -e "${YELLOW}3. Check if the database user has the necessary permissions.${NC}"
  echo -e "${YELLOW}4. Check if the database exists.${NC}"
  
  # Get database connection string (masked)
  db_conn=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)
  if [ -n "$db_conn" ]; then
      echo -e "${YELLOW}Database connection string is configured.${NC}"
  else
      echo -e "${RED}Error: Database connection string is not configured.${NC}"
  fi
  
  exit 1
fi

# Check if the response contains error messages
if echo "$RESPONSE_BODY" | grep -i "error"; then
  echo -e "${RED}Migration script reported errors${NC}"
  echo -e "${RED}Response details: $RESPONSE_BODY${NC}"
  exit 1
fi

echo -e "${GREEN}Database migrations completed successfully!${NC}"

# Verify database schema
echo "Verifying database schema..."
SCHEMA_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -m alembic current\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
SCHEMA_HTTP_STATUS=$(echo "$SCHEMA_RESPONSE" | tail -n1)
SCHEMA_BODY=$(echo "$SCHEMA_RESPONSE" | sed '$d')

echo -e "${GREEN}Current database schema:${NC}"
echo "$SCHEMA_BODY"

# Check database connection
echo "Checking database connection..."
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

echo -e "${GREEN}Database migrations and verification completed successfully!${NC}"
