#!/bin/bash
# Setup Azure Service Principal for GitHub Actions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

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

# Get subscription ID
echo "Getting subscription ID..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo -e "${GREEN}Subscription ID: $SUBSCRIPTION_ID${NC}"

# Create service principal
echo "Creating service principal..."
echo -e "${YELLOW}This will create a service principal with Contributor role on your subscription.${NC}"
echo -e "${YELLOW}Press Enter to continue or Ctrl+C to cancel.${NC}"
read

SP_JSON=$(az ad sp create-for-rbac \
    --name "ai-event-planner-saas-github" \
    --role contributor \
    --scopes /subscriptions/$SUBSCRIPTION_ID \
    --sdk-auth)

# Save service principal JSON to file
echo "Saving service principal JSON to azure-credentials.json..."
echo "$SP_JSON" > azure-credentials.json

echo -e "${GREEN}Service principal created successfully!${NC}"
echo -e "${GREEN}The service principal JSON has been saved to azure-credentials.json${NC}"
echo -e "${YELLOW}IMPORTANT: Add this JSON as a GitHub repository secret named 'AZURE_CREDENTIALS'${NC}"
echo -e "${YELLOW}To do this:${NC}"
echo -e "${YELLOW}1. Go to your GitHub repository${NC}"
echo -e "${YELLOW}2. Click on 'Settings' > 'Secrets and variables' > 'Actions'${NC}"
echo -e "${YELLOW}3. Click on 'New repository secret'${NC}"
echo -e "${YELLOW}4. Name: AZURE_CREDENTIALS${NC}"
echo -e "${YELLOW}5. Value: Copy and paste the entire content of azure-credentials.json${NC}"
echo -e "${YELLOW}6. Click 'Add secret'${NC}"

# Display the JSON for easy copying
echo -e "${YELLOW}Here is the JSON to copy (if needed):${NC}"
echo -e "${GREEN}$SP_JSON${NC}"
