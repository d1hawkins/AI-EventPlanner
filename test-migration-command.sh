#!/bin/bash
# Test script to verify the az webapp run-command works correctly
# Note: This script requires Azure CLI to be installed and logged in

# Replace these with your actual values if testing locally
RESOURCE_GROUP="ai-event-planner-rg"
WEB_APP_NAME="ai-event-planner"

echo "Testing migration command..."
az webapp run-command --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --command "python scripts/migrate.py"

echo "Command completed."
