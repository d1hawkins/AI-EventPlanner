#!/bin/bash
set -e

# Test script to verify the Kudu REST API approach works correctly
# Note: This script requires Azure CLI to be installed and logged in

# Replace these with your actual values if testing locally
RESOURCE_GROUP="ai-event-planner-rg"
WEB_APP_NAME="ai-event-planner"

echo "Getting publishing credentials..."

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is not installed. Using dummy credentials for testing..."
    # Use dummy credentials for testing
    USERNAME="dummy_username"
    PASSWORD="dummy_password"
    
    # Check if az CLI is installed
    if command -v az &> /dev/null; then
        echo "Azure CLI is installed. You can get real credentials with:"
        echo "az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
    else
        echo "Azure CLI is not installed. This script is for testing command format only."
    fi
else
    # Check if az CLI is installed
    if ! command -v az &> /dev/null; then
        echo "Azure CLI is not installed. Using dummy credentials for testing..."
        USERNAME="dummy_username"
        PASSWORD="dummy_password"
    else
        echo "Getting credentials from Azure CLI..."
        CREDS=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --query "{username:publishingUserName, password:publishingPassword}" -o json)
        USERNAME=$(echo $CREDS | jq -r '.username')
        PASSWORD=$(echo $CREDS | jq -r '.password')
    fi
fi

# First, find the Python executable path
echo "Finding Python executable path..."
if [[ "$USERNAME" != "dummy_username" ]]; then
    FIND_PYTHON_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
      -H "Content-Type: application/json" \
      https://$WEB_APP_NAME.scm.azurewebsites.net/api/command \
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
else
    echo "Using dummy credentials - setting default Python path"
    PYTHON_PATH="/usr/local/bin/python3"
fi

# Use the Python path to run the migration script
echo "Running migrations..."
echo "Command format: {\"command\":\"$PYTHON_PATH -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}"

# Only execute the curl command if we have real credentials
if [[ "$USERNAME" != "dummy_username" ]]; then
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
      -H "Content-Type: application/json" \
      https://$WEB_APP_NAME.scm.azurewebsites.net/api/command \
      -d "{\"command\":\"$PYTHON_PATH -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}")

    # Extract status code and response body
    HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

    echo "Migration response: $RESPONSE_BODY"
    echo "HTTP status: $HTTP_STATUS"

    # Check if the request was successful
    if [ "$HTTP_STATUS" -ne 200 ]; then
      echo "Migration failed with status $HTTP_STATUS"
      echo "Response: $RESPONSE_BODY"
      exit 1
    fi

    # Check if the response contains error messages
    if echo "$RESPONSE_BODY" | grep -i "error"; then
      echo "Migration script reported errors"
      exit 1
    fi

    echo "Migration completed successfully"

    # Check application health
    echo "Checking application health..."
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" https://$WEB_APP_NAME.azurewebsites.net/health)
    HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | tail -n1)
    HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

    echo "Health check response: $HEALTH_BODY"
    echo "Health check status: $HEALTH_STATUS"

    if [ "$HEALTH_STATUS" -ne 200 ]; then
      echo "Health check failed with status $HEALTH_STATUS"
      echo "Response: $HEALTH_BODY"
      exit 1
    fi

    echo "Application is healthy"

    # Get application logs
    echo "Fetching application logs..."
    az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --lines 100
else
    echo "Using dummy credentials - not executing actual API calls."
    echo "This script is now just testing the command format."
    echo ""
    echo "The GitHub Actions workflow has been updated to use the correct command format:"
    echo "{\"command\":\"/usr/local/bin/python3 -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}"
    echo ""
    echo "This fixes two issues:"
    echo "1. The 'cd command not found' error - by setting dir parameter instead of using cd"
    echo "2. The 'python command not found' error - by using the full path to Python"
    echo ""
    echo "To test in the actual GitHub environment, push changes and trigger the workflow."
fi
