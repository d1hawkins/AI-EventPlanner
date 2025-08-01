#!/bin/bash
set -e

# Variables
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="ai-event-planner-asp"
WEB_APP_NAME="ai-event-planner"
ACR_NAME="aieventplanneracr"
POSTGRES_SERVER_NAME="ai-event-planner-db"
POSTGRES_DB_NAME="eventplanner"
POSTGRES_ADMIN="dbadmin"
POSTGRES_PASSWORD="$(openssl rand -base64 16)"
KEY_VAULT_NAME="ai-event-planner-kv"

# Create Resource Group
echo "Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Create App Service Plan
echo "Creating App Service Plan..."
az appservice plan create --resource-group $RESOURCE_GROUP --name $APP_SERVICE_PLAN --is-linux --sku P1V2

# Create Web App
echo "Creating Web App..."
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEB_APP_NAME --deployment-container-image-name $ACR_NAME.azurecr.io/ai-event-planner:latest

# Create PostgreSQL Server
echo "Creating PostgreSQL Server..."
az postgres server create --resource-group $RESOURCE_GROUP --name $POSTGRES_SERVER_NAME --location $LOCATION --admin-user $POSTGRES_ADMIN --admin-password $POSTGRES_PASSWORD --sku-name GP_Gen5_2

# Create PostgreSQL Database
echo "Creating PostgreSQL Database..."
az postgres db create --resource-group $RESOURCE_GROUP --server-name $POSTGRES_SERVER_NAME --name $POSTGRES_DB_NAME

# Allow Azure services to access PostgreSQL
echo "Configuring PostgreSQL firewall..."
az postgres server firewall-rule create --resource-group $RESOURCE_GROUP --server-name $POSTGRES_SERVER_NAME --name AllowAllAzureIPs --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# Create Key Vault
echo "Creating Key Vault..."
az keyvault create --resource-group $RESOURCE_GROUP --name $KEY_VAULT_NAME --location $LOCATION

# Store secrets in Key Vault
echo "Storing secrets in Key Vault..."
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "DATABASE-URL" --value "postgresql://$POSTGRES_ADMIN:$POSTGRES_PASSWORD@$POSTGRES_SERVER_NAME.postgres.database.azure.com:5432/$POSTGRES_DB_NAME"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "SECRET-KEY" --value "$(openssl rand -base64 32)"

# Configure Web App settings
echo "Configuring Web App settings..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --settings \
  DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/DATABASE-URL)" \
  SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/SECRET-KEY)" \
  LLM_PROVIDER="openai"

# Enable managed identity for Web App
echo "Enabling managed identity for Web App..."
az webapp identity assign --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME

# Get the principal ID of the Web App's managed identity
PRINCIPAL_ID=$(az webapp identity show --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --query principalId --output tsv)

# Grant the Web App's managed identity access to Key Vault secrets
echo "Granting Web App access to Key Vault..."
az keyvault set-policy --name $KEY_VAULT_NAME --object-id $PRINCIPAL_ID --secret-permissions get list

echo "Deployment completed successfully!"
echo "PostgreSQL Admin Password: $POSTGRES_PASSWORD"
echo "Please save this password securely and add your OpenAI API key to the Key Vault."
