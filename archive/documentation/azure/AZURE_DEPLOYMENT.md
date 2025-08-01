# Azure Deployment Guide

This document provides detailed instructions for deploying the AI Event Planner application to Azure using GitHub Actions.

## Prerequisites

- Azure subscription
- GitHub account
- Azure CLI installed locally

## Setting Up Azure Service Principal

To allow GitHub Actions to deploy to Azure, you need to create a service principal:

1. Log in to Azure CLI:

```bash
az login
```

2. Create a service principal with contributor role:

```bash
# Replace with your subscription ID
13e630db-8816-46b8-896e-511fab75a53a=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac --name "ai-event-planner-github" \
                         --role contributor \
                         --scopes /subscriptions/13e630db-8816-46b8-896e-511fab75a53a \
                         --sdk-auth
```

## Setting Up API Keys in Azure Key Vault

For enhanced security, it's recommended to store API keys in Azure Key Vault:

1. Create a Key Vault if you don't already have one:

```bash
az keyvault create --name ai-event-planner-kv --resource-group ai-event-planner-rg --location eastus
```

2. Add your API keys to the Key Vault:

```bash
az keyvault secret set --vault-name ai-event-planner-kv --name OPENAI-API-KEY --value "your_openai_api_key"
az keyvault secret set --vault-name ai-event-planner-kv --name SENDGRID-API-KEY --value "your_sendgrid_api_key"
az keyvault secret set --vault-name ai-event-planner-kv --name OPENWEATHER-API-KEY --value "your_openweather_api_key"
```

3. Configure your App Service to access Key Vault using managed identity:

```bash
# Enable managed identity for your App Service
az webapp identity assign --name ai-event-planner --resource-group ai-event-planner-rg

# Get the principal ID of the managed identity
principalId=$(az webapp identity show --name ai-event-planner --resource-group ai-event-planner-rg --query principalId -o tsv)

# Grant the managed identity access to Key Vault
az keyvault set-policy --name ai-event-planner-kv --object-id $principalId --secret-permissions get list
```

4. Configure your App Service to use Key Vault references:

```bash
az webapp config appsettings set --name ai-event-planner --resource-group ai-event-planner-rg --settings @"keyvault-references.json"
```

Where `keyvault-references.json` contains:

```json
[
  {
    "name": "OPENAI_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://ai-event-planner-kv.vault.azure.net/secrets/OPENAI-API-KEY/)",
    "slotSetting": false
  },
  {
    "name": "SENDGRID_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://ai-event-planner-kv.vault.azure.net/secrets/SENDGRID-API-KEY/)",
    "slotSetting": false
  },
  {
    "name": "OPENWEATHER_API_KEY",
    "value": "@Microsoft.KeyVault(SecretUri=https://ai-event-planner-kv.vault.azure.net/secrets/OPENWEATHER-API-KEY/)",
    "slotSetting": false
  }
]
```

3. The command will output a JSON object like this:

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

4. Copy this entire JSON object and add it as a GitHub repository secret named `AZURE_CREDENTIALS`.

## Setting Up Azure Container Registry

After running the `./azure-deploy.sh` script, you need to configure GitHub repository secrets for the Azure Container Registry:

1. Get the ACR login server:

```bash
az acr show --name aieventplanneracr --resource-group ai-event-planner-rg --query loginServer -o tsv
```

2. Get the ACR credentials:

```bash
az acr credential show --name aieventplanneracr --resource-group ai-event-planner-rg
```

3. Add the following GitHub repository secrets:
   - `ACR_LOGIN_SERVER`: The login server URL from step 1
   - `ACR_USERNAME`: The username from step 2
   - `ACR_PASSWORD`: The password from step 2
   - `AZURE_RESOURCE_GROUP`: "ai-event-planner-rg"

## Deployment Process

1. Run the Azure deployment script to create all necessary resources:

```bash
./azure-deploy.sh
```

2. Configure the GitHub repository secrets as described above.

3. Push changes to the main branch to trigger the CI/CD pipeline.

4. Monitor the GitHub Actions workflow in the "Actions" tab of your repository.

## Troubleshooting

### Database Migration Issues

If database migrations fail, you can run them manually:

1. Connect to the Azure Web App using SSH:

```bash
az webapp ssh --resource-group ai-event-planner-rg --name ai-event-planner
```

2. Run the migration script:

```bash
python scripts/migrate.py
```

### Container Deployment Issues

If the container fails to deploy, check the logs:

```bash
az webapp log tail --resource-group ai-event-planner-rg --name ai-event-planner
```

## Monitoring

Monitor your application using Azure Application Insights:

1. Navigate to the Azure Portal
2. Go to your App Service resource
3. Click on "Application Insights" in the left menu
4. View metrics, logs, and performance data

### Monitoring MCP Servers

The MCP servers run within the same container as the main application and can be monitored using the same tools. To view MCP server logs:

```bash
az webapp log tail --resource-group ai-event-planner-rg --name ai-event-planner | grep -E "SendGrid MCP|OpenWeather MCP"
```

## Scaling

To scale your application:

1. Navigate to the Azure Portal
2. Go to your App Service resource
3. Click on "Scale up (App Service plan)" to change the instance size
4. Click on "Scale out (App Service plan)" to change the number of instances

Since the MCP servers run within the same container as the main application, they will automatically scale with the App Service.
