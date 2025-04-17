#!/bin/bash
# Script to verify the Azure deployment
# This script runs all the verification scripts to check if the deployment is correct

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Print a header
echo -e "${YELLOW}=== Azure Deployment Verification ===${NC}"
echo "This script will verify that the Azure deployment is correct."
echo "It will check:"
echo "1. If the auth directory and its files are properly deployed to Azure"
echo "2. If the passlib package is installed in the Azure App Service"
echo

# Verify the auth directory
echo -e "${YELLOW}=== Verifying Auth Directory ===${NC}"
./verify_auth_directory.sh
echo

# Verify the passlib installation
echo -e "${YELLOW}=== Verifying Passlib Installation ===${NC}"
./check_passlib_installation.py
echo

# Verify the psycopg2 installation
echo -e "${YELLOW}=== Verifying Psycopg2 Installation ===${NC}"
./check_psycopg2_installation.py
echo

# Verify the email-validator installation
echo -e "${YELLOW}=== Verifying Email-Validator Installation ===${NC}"
./check_email_validator_installation.py
echo

# Verify the icalendar installation
echo -e "${YELLOW}=== Verifying iCalendar Installation ===${NC}"
./check_icalendar_installation.py
echo

# Check if the application is running
echo -e "${YELLOW}=== Checking Application Status ===${NC}"
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

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

# Check if the app exists
echo "Checking if the app exists in Azure..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}Error: App $APP_NAME not found in resource group $RESOURCE_GROUP.${NC}"
    exit 1
fi

# Check if the app is running
echo "Checking if the app is running..."
STATUS=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query state -o tsv)
if [ "$STATUS" == "Running" ]; then
    echo -e "${GREEN}App is running.${NC}"
else
    echo -e "${RED}Error: App is not running. Current state: $STATUS${NC}"
    exit 1
fi

# Check if the app is accessible
echo "Checking if the app is accessible..."
URL="https://$APP_NAME.azurewebsites.net/health"
if curl -s -o /dev/null -w "%{http_code}" $URL | grep -q "200"; then
    echo -e "${GREEN}App is accessible.${NC}"
else
    echo -e "${RED}Error: App is not accessible. Please check the logs.${NC}"
    exit 1
fi

echo -e "${GREEN}All verification checks passed. The Azure deployment is correct.${NC}"
