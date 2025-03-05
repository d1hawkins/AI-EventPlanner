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

echo "Running migration script via Kudu REST API..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$WEB_APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"python -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}")

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
