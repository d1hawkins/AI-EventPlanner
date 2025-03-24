#!/bin/bash
# Master deployment script for AI Event Planner SaaS to Azure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
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

# Make all scripts executable
echo "Making all deployment scripts executable..."
chmod +x setup-service-principal.sh
chmod +x setup-key-vault.sh
chmod +x setup-app-insights.sh
chmod +x run-migrations.sh
chmod +x verify-deployment.sh
chmod +x azure-deploy-saas.sh

# Display deployment plan
echo -e "${BLUE}=== AI Event Planner SaaS Azure Deployment Plan ===${NC}"
echo -e "${BLUE}This script will execute the following steps:${NC}"
echo -e "${BLUE}1. Create Azure Service Principal for GitHub Actions${NC}"
echo -e "${BLUE}2. Create Azure resources using azure-deploy-saas.sh${NC}"
echo -e "${BLUE}3. Configure Azure Key Vault for secure credential storage${NC}"
echo -e "${BLUE}4. Set up Application Insights for monitoring${NC}"
echo -e "${BLUE}5. Run database migrations${NC}"
echo -e "${BLUE}6. Verify deployment${NC}"
echo -e "${YELLOW}Press Enter to continue or Ctrl+C to cancel.${NC}"
read

# Step 1: Create Azure Service Principal
echo -e "${GREEN}=== Step 1: Creating Azure Service Principal ===${NC}"
./setup-service-principal.sh
echo -e "${GREEN}Service Principal created successfully.${NC}"
echo -e "${YELLOW}Please add the azure-credentials.json content as a GitHub repository secret named 'AZURE_CREDENTIALS'.${NC}"
echo -e "${YELLOW}Press Enter to continue after adding the secret, or Ctrl+C to cancel.${NC}"
read

# Step 2: Create Azure resources
echo -e "${GREEN}=== Step 2: Creating Azure resources ===${NC}"
./azure-deploy-saas.sh
echo -e "${GREEN}Azure resources created successfully.${NC}"

# Step 3: Configure Azure Key Vault
echo -e "${GREEN}=== Step 3: Configuring Azure Key Vault ===${NC}"
./setup-key-vault.sh
echo -e "${GREEN}Azure Key Vault configured successfully.${NC}"

# Step 4: Set up Application Insights
echo -e "${GREEN}=== Step 4: Setting up Application Insights ===${NC}"
./setup-app-insights.sh
echo -e "${GREEN}Application Insights set up successfully.${NC}"

# Step 5: Run database migrations
echo -e "${GREEN}=== Step 5: Running database migrations ===${NC}"
./run-migrations.sh
echo -e "${GREEN}Database migrations completed successfully.${NC}"

# Step 6: Verify deployment
echo -e "${GREEN}=== Step 6: Verifying deployment ===${NC}"
./verify-deployment.sh
echo -e "${GREEN}Deployment verification completed.${NC}"

# Deployment summary
APP_NAME="ai-event-planner-saas"
APP_URL="https://$APP_NAME.azurewebsites.net"
SAAS_URL="$APP_URL/static/saas/index.html"

echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo -e "${GREEN}AI Event Planner SaaS has been successfully deployed to Azure!${NC}"
echo -e "${GREEN}Application URL: $APP_URL${NC}"
echo -e "${GREEN}SaaS Application URL: $SAAS_URL${NC}"
echo -e "${YELLOW}GitHub Actions CI/CD is configured to automatically deploy changes when you push to the main branch.${NC}"
echo -e "${YELLOW}You can also manually trigger a deployment from the GitHub Actions tab.${NC}"

echo -e "${BLUE}=== Next Steps ===${NC}"
echo -e "${BLUE}1. Test the application by visiting $SAAS_URL${NC}"
echo -e "${BLUE}2. Monitor the application using Azure Application Insights${NC}"
echo -e "${BLUE}3. Check the logs using 'az webapp log tail --name $APP_NAME --resource-group ai-event-planner-rg'${NC}"
echo -e "${BLUE}4. Make changes to the code and push to GitHub to trigger automatic deployment${NC}"
