#!/bin/bash
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
curl -X POST -u "$USERNAME:$PASSWORD" https://$WEB_APP_NAME.scm.azurewebsites.net/api/command -d "{\"command\":\"python scripts/migrate.py\", \"dir\":\"/home/site/wwwroot\"}"

echo "Command completed."
