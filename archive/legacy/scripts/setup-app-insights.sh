#!/bin/bash
# Setup script for Azure Application Insights integration with AI Event Planner

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Azure Application Insights Setup for AI Event Planner ===${NC}"
echo "This script will help you set up Azure Application Insights for the AI Event Planner application."
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: 'jq' is not installed. This script requires jq for JSON parsing.${NC}"
    echo "Please install jq using one of the following commands:"
    echo "  - For macOS: brew install jq"
    echo "  - For Ubuntu/Debian: sudo apt-get install jq"
    echo "  - For CentOS/RHEL: sudo yum install jq"
    echo "  - For Windows with Chocolatey: choco install jq"
    echo ""
    read -p "Do you want to continue without jq (manual subscription selection will be required)? (y/n): " CONTINUE_WITHOUT_JQ
    if [[ $CONTINUE_WITHOUT_JQ != "y" && $CONTINUE_WITHOUT_JQ != "Y" ]]; then
        echo "Exiting. Please install jq and run the script again."
        exit 1
    fi
    echo "Continuing without jq..."
    echo ""
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Azure CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in to Azure
echo "Checking Azure login status..."
az account show &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}You are not logged in to Azure. Please log in.${NC}"
    az login
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to log in to Azure. Exiting.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Successfully logged in to Azure.${NC}"

# Get subscription
echo "Getting Azure subscriptions..."

# Check if jq is available for JSON parsing
if command -v jq &> /dev/null; then
    # Use jq for JSON parsing
    SUBSCRIPTIONS=$(az account list --query "[].{name:name, id:id}" -o json)
    SUB_COUNT=$(echo $SUBSCRIPTIONS | jq length)

    if [ $SUB_COUNT -eq 0 ]; then
        echo -e "${RED}No Azure subscriptions found. Please create one and try again.${NC}"
        exit 1
    elif [ $SUB_COUNT -eq 1 ]; then
        SUBSCRIPTION_ID=$(echo $SUBSCRIPTIONS | jq -r '.[0].id')
        SUBSCRIPTION_NAME=$(echo $SUBSCRIPTIONS | jq -r '.[0].name')
        echo -e "Using subscription: ${GREEN}$SUBSCRIPTION_NAME${NC}"
    else
        echo "Multiple subscriptions found. Please select one:"
        echo $SUBSCRIPTIONS | jq -r '.[].name' | nl -w2 -s') '
        read -p "Enter the number of the subscription to use: " SUB_NUM
        SUBSCRIPTION_ID=$(echo $SUBSCRIPTIONS | jq -r ".[$((SUB_NUM-1))].id")
        SUBSCRIPTION_NAME=$(echo $SUBSCRIPTIONS | jq -r ".[$((SUB_NUM-1))].name")
        echo -e "Using subscription: ${GREEN}$SUBSCRIPTION_NAME${NC}"
    fi
else
    # Manual subscription selection without jq
    echo "Listing available subscriptions:"
    az account list --output table
    echo ""
    read -p "Enter the subscription ID to use: " SUBSCRIPTION_ID
    SUBSCRIPTION_NAME=$(az account show --subscription "$SUBSCRIPTION_ID" --query "name" -o tsv)
    if [ -z "$SUBSCRIPTION_NAME" ]; then
        echo -e "${RED}Invalid subscription ID. Exiting.${NC}"
        exit 1
    fi
    echo -e "Using subscription: ${GREEN}$SUBSCRIPTION_NAME${NC}"
fi

# Set the subscription
az account set --subscription "$SUBSCRIPTION_ID"

# Ask for resource group
echo ""
echo "Please provide a resource group name or create a new one."
read -p "Use existing resource group? (y/n): " USE_EXISTING_RG

if [[ $USE_EXISTING_RG == "y" || $USE_EXISTING_RG == "Y" ]]; then
    # List existing resource groups
    echo "Existing resource groups:"
    if command -v jq &> /dev/null; then
        # Use jq for parsing
        az group list --query "[].name" -o tsv | nl -w2 -s') '
        read -p "Enter the number of the resource group to use: " RG_NUM
        RESOURCE_GROUP=$(az group list --query "[].name" -o tsv | sed -n "${RG_NUM}p")
    else
        # Manual selection without jq
        az group list --output table
        read -p "Enter the name of the resource group to use: " RESOURCE_GROUP
    fi
else
    read -p "Enter a name for the new resource group: " RESOURCE_GROUP
    read -p "Enter location (e.g., eastus, westus2): " LOCATION
    
    echo "Creating resource group: $RESOURCE_GROUP in $LOCATION..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create resource group. Exiting.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Resource group created successfully.${NC}"
fi

# Create Application Insights resource
echo ""
echo "Creating Azure Application Insights resource..."
read -p "Enter a name for the Application Insights resource: " APP_INSIGHTS_NAME

# Create App Insights resource
echo "Creating Application Insights resource: $APP_INSIGHTS_NAME..."
APP_INSIGHTS_OUTPUT=$(az monitor app-insights component create \
    --app "$APP_INSIGHTS_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --kind web \
    --application-type web \
    --query "{instrumentationKey:instrumentationKey, connectionString:connectionString}" \
    -o json)

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create Application Insights resource. Exiting.${NC}"
    exit 1
fi

# Extract instrumentation key and connection string
if command -v jq &> /dev/null; then
    # Use jq for parsing
    INSTRUMENTATION_KEY=$(echo $APP_INSIGHTS_OUTPUT | jq -r '.instrumentationKey')
    CONNECTION_STRING=$(echo $APP_INSIGHTS_OUTPUT | jq -r '.connectionString')
else
    # Manual extraction without jq
    echo "Since jq is not installed, please copy your instrumentation key from the following output:"
    echo "$APP_INSIGHTS_OUTPUT"
    echo ""
    read -p "Enter the instrumentation key: " INSTRUMENTATION_KEY
fi

echo -e "${GREEN}Application Insights resource created successfully.${NC}"
echo ""
echo -e "${YELLOW}Please add the following to your .env file:${NC}"
echo ""
echo "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY"
echo "CLOUD_ROLE=ai-event-planner"
echo "APP_VERSION=1.0.0"
echo "ENVIRONMENT=development  # Options: development, staging, production"
echo ""

# Ask if user wants to update .env file automatically
read -p "Do you want to update your .env file automatically? (y/n): " UPDATE_ENV

if [[ $UPDATE_ENV == "y" || $UPDATE_ENV == "Y" ]]; then
    if [ -f .env ]; then
        # Check if the variables already exist in .env
        grep -q "APPINSIGHTS_INSTRUMENTATIONKEY" .env
        if [ $? -eq 0 ]; then
            # Update existing variables
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS requires an empty string for -i
                sed -i '' "s/APPINSIGHTS_INSTRUMENTATIONKEY=.*/APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY/" .env
            else
                # Linux version
                sed -i "s/APPINSIGHTS_INSTRUMENTATIONKEY=.*/APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY/" .env
            fi
        else
            # Add new variables
            echo "" >> .env
            echo "# Azure Application Insights Configuration" >> .env
            echo "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY" >> .env
            echo "CLOUD_ROLE=ai-event-planner" >> .env
            echo "APP_VERSION=1.0.0" >> .env
            echo "ENVIRONMENT=development  # Options: development, staging, production" >> .env
        fi
        echo -e "${GREEN}.env file updated successfully.${NC}"
    else
        echo -e "${YELLOW}.env file not found. Creating a new one...${NC}"
        echo "# Azure Application Insights Configuration" > .env
        echo "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY" >> .env
        echo "CLOUD_ROLE=ai-event-planner" >> .env
        echo "APP_VERSION=1.0.0" >> .env
        echo "ENVIRONMENT=development  # Options: development, staging, production" >> .env
        echo -e "${GREEN}.env file created successfully.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Azure Application Insights setup complete!${NC}"
echo "You can now use the Application Insights integration in your AI Event Planner application."
echo "View your telemetry data in the Azure portal: https://portal.azure.com"
echo ""
echo "For more information on Azure Application Insights, visit:"
echo "https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview"
echo ""
echo "For more details on how to use Application Insights with this application, see:"
echo "AZURE_APP_INSIGHTS_GUIDE.md"
