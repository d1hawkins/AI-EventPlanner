#!/bin/bash
# Quick fix script for Azure 504 timeout issue
# This script applies immediate fixes and enhanced logging

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚨 Quick Fix for Azure 504 Timeout Issue${NC}"

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

echo -e "${BLUE}Step 1: Setting critical environment variables...${NC}"

# Set essential environment variables that are commonly missing
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    "PYTHONPATH=/home/site/wwwroot" \
    "PYTHONUNBUFFERED=1" \
    "LOG_LEVEL=DEBUG" \
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7" \
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
    "ENABLE_ORYX_BUILD=true" \
    "DISABLE_COLLECTSTATIC=1"

echo -e "${BLUE}Step 2: Setting a simpler startup command...${NC}"

# Use a simpler startup command that's more likely to work
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "gunicorn app_adapter:app --bind=0.0.0.0:8000 --timeout=300 --workers=1 --log-level=debug"

echo -e "${BLUE}Step 3: Enabling comprehensive logging...${NC}"

# Enable all logging options
az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem \
    --level verbose

echo -e "${BLUE}Step 4: Restarting the application...${NC}"

# Restart the app
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

echo -e "${YELLOW}Waiting 30 seconds for restart...${NC}"
sleep 30

echo -e "${BLUE}Step 5: Testing application status...${NC}"

# Test the application
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$APP_NAME.azurewebsites.net" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Application is now responding! (HTTP $HTTP_STATUS)${NC}"
else
    echo -e "${RED}❌ Application still not responding (HTTP $HTTP_STATUS)${NC}"
    echo -e "${YELLOW}Let's check the logs for more information...${NC}"
fi

echo -e "${BLUE}Step 6: Streaming startup logs...${NC}"
echo "Press Ctrl+C to stop log streaming"
echo ""

# Stream logs to see what's happening
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME
