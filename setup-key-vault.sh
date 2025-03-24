#!/bin/bash
# Setup Azure Key Vault for AI Event Planner SaaS

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
KEY_VAULT_NAME="$APP_NAME-kv"

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

# Create Key Vault
echo "Creating Azure Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Load environment variables from .env.azure
echo "Loading environment variables from .env.azure..."
if [ -f .env.azure ]; then
    source <(grep -v '^#' .env.azure | sed -E 's/(.*)=(.*)$/export \1="\2"/')
else
    echo -e "${RED}Error: .env.azure file not found.${NC}"
    exit 1
fi

# Store API keys and sensitive information in Key Vault
echo "Storing API keys and sensitive information in Key Vault..."

# OpenAI API Key
if [ -n "$OPENAI_API_KEY" ]; then
    az keyvault secret set --vault-name $KEY_VAULT_NAME --name "OPENAI-API-KEY" --value "$OPENAI_API_KEY"
    echo -e "${GREEN}Stored OPENAI API Key in Key Vault.${NC}"
else
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not found in .env.azure${NC}"
fi

# Google API Key
if [ -n "$GOOGLE_API_KEY" ]; then
    az keyvault secret set --vault-name $KEY_VAULT_NAME --name "GOOGLE-API-KEY" --value "$GOOGLE_API_KEY"
    echo -e "${GREEN}Stored GOOGLE API Key in Key Vault.${NC}"
else
    echo -e "${YELLOW}Warning: GOOGLE_API_KEY not found in .env.azure${NC}"
fi

# SendGrid API Key
if [ -n "$SENDGRID_API_KEY" ]; then
    az keyvault secret set --vault-name $KEY_VAULT_NAME --name "SENDGRID-API-KEY" --value "$SENDGRID_API_KEY"
    echo -e "${GREEN}Stored SENDGRID API Key in Key Vault.${NC}"
else
    echo -e "${YELLOW}Warning: SENDGRID_API_KEY not found in .env.azure${NC}"
fi

# OpenWeather API Key
if [ -n "$OPENWEATHER_API_KEY" ]; then
    az keyvault secret set --vault-name $KEY_VAULT_NAME --name "OPENWEATHER-API-KEY" --value "$OPENWEATHER_API_KEY"
    echo -e "${GREEN}Stored OPENWEATHER API Key in Key Vault.${NC}"
else
    echo -e "${YELLOW}Warning: OPENWEATHER_API_KEY not found in .env.azure${NC}"
fi

# JWT Secret Key
if [ -n "$SECRET_KEY" ]; then
    az keyvault secret set --vault-name $KEY_VAULT_NAME --name "JWT-SECRET-KEY" --value "$SECRET_KEY"
    echo -e "${GREEN}Stored JWT Secret Key in Key Vault.${NC}"
else
    echo -e "${YELLOW}Warning: SECRET_KEY not found in .env.azure${NC}"
fi

# Enable managed identity for App Service
echo "Enabling managed identity for App Service..."
az webapp identity assign --name $APP_NAME --resource-group $RESOURCE_GROUP

# Get the principal ID
echo "Getting the principal ID of the managed identity..."
principalId=$(az webapp identity show --name $APP_NAME --resource-group $RESOURCE_GROUP --query principalId -o tsv)

# Grant permissions to Key Vault
echo "Granting permissions to Key Vault..."
az keyvault set-policy --name $KEY_VAULT_NAME --object-id $principalId --secret-permissions get list

# Create a keyvault-references.json file for App Service settings
echo "Creating keyvault-references.json file..."
cat > keyvault-references.json << EOF
[
  {
    "name": "OPENAI_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/OPENAI-API-KEY/)",
    "slotSetting": false
  },
  {
    "name": "GOOGLE_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/GOOGLE-API-KEY/)",
    "slotSetting": false
  },
  {
    "name": "SENDGRID_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/SENDGRID-API-KEY/)",
    "slotSetting": false
  },
  {
    "name": "OPENWEATHER_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/OPENWEATHER-API-KEY/)",
    "slotSetting": false
  },
  {
    "name": "SECRET_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/JWT-SECRET-KEY/)",
    "slotSetting": false
  }
]
EOF

# Configure App Service to use Key Vault references
echo "Configuring App Service to use Key Vault references..."
az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings @"keyvault-references.json"

echo -e "${GREEN}Key Vault setup completed successfully!${NC}"
echo -e "${YELLOW}Your Key Vault is available at: https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults/resourceName/$KEY_VAULT_NAME${NC}"
