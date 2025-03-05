#!/bin/bash
set -e

# Test script to verify the Kudu REST API approach works correctly
# Note: This script requires Azure CLI to be installed and logged in

# Replace these with your actual values if testing locally
RESOURCE_GROUP="ai-event-planner-rg"
WEB_APP_NAME="ai-event-planner"

echo "Getting publishing credentials..."
CREDS=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --query "{username:publishingUserName, password:publishingPassword}" -o json)
USERNAME=$(echo $CREDS | jq -r '.username')
PASSWORD=$(echo $CREDS | jq -r '.password')

# First, find the Python executable path
echo "Finding Python executable path..."
FIND_PYTHON_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$WEB_APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"find / -name python3 2>/dev/null | head -n 1\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
HTTP_STATUS=$(echo "$FIND_PYTHON_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$FIND_PYTHON_RESPONSE" | sed '$d')

echo "Find Python response: $RESPONSE_BODY"
echo "HTTP status: $HTTP_STATUS"

# Extract Python path from the response
PYTHON_PATH=$(echo "$RESPONSE_BODY" | grep -o '/[a-zA-Z0-9/_.-]*python3' | head -n 1 || echo "")

if [ -z "$PYTHON_PATH" ]; then
  echo "Could not find Python executable. Trying with 'python3' command..."
  PYTHON_PATH="python3"
else
  echo "Found Python executable at: $PYTHON_PATH"
fi

# Use Kudu REST API to run the migration script with better error handling
echo "Running migrations with Python path: $PYTHON_PATH"
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
