# Azure Deployment Plan for AI Event Planner SaaS

This document outlines the complete process to deploy the AI Event Planner SaaS application to Azure.

## Prerequisites
- Azure subscription
- GitHub account with repository access
- Azure CLI installed locally

## Deployment Steps

### 1. Setting Up Azure Service Principal
You'll need a service principal to allow GitHub Actions to deploy to Azure:

```bash
# Login to Azure
az login

# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac --name "ai-event-planner-saas-github" \
                         --role contributor \
                         --scopes /subscriptions/$SUBSCRIPTION_ID \
                         --sdk-auth
```

Save the JSON output as a GitHub repository secret named `AZURE_CREDENTIALS`.

### 2. Update Environment Variables
Update the `.env.azure` file:
- Set a valid OpenWeather API key: `OPENWEATHER_API_KEY=your_actual_key`
- Verify the database connection string
- Verify all other API keys

### 3. Configure Key Vault for Secure Credential Storage
For enhanced security in production:

```bash
# Create a Key Vault
az keyvault create --name ai-event-planner-saas-kv --resource-group ai-event-planner-rg --location eastus

# Store API keys and sensitive information
az keyvault secret set --vault-name ai-event-planner-saas-kv --name OPENAI-API-KEY --value "your_openai_api_key"
az keyvault secret set --vault-name ai-event-planner-saas-kv --name SENDGRID-API-KEY --value "your_sendgrid_api_key"
az keyvault secret set --vault-name ai-event-planner-saas-kv --name GOOGLE-API-KEY --value "your_google_api_key"
az keyvault secret set --vault-name ai-event-planner-saas-kv --name JWT-SECRET-KEY --value "your_jwt_secret_key"
az keyvault secret set --vault-name ai-event-planner-saas-kv --name OPENWEATHER-API-KEY --value "your_openweather_api_key"

# Enable managed identity for App Service
az webapp identity assign --name ai-event-planner-saas --resource-group ai-event-planner-rg

# Get the principal ID
principalId=$(az webapp identity show --name ai-event-planner-saas --resource-group ai-event-planner-rg --query principalId -o tsv)

# Grant permissions to Key Vault
az keyvault set-policy --name ai-event-planner-saas-kv --object-id $principalId --secret-permissions get list
```

### 4. Set Up GitHub Repository Secrets
Add these secrets to your GitHub repository:
- `AZURE_CREDENTIALS`: Service principal JSON from step 1
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Your JWT secret key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_API_KEY`: Your Google API key
- `STORAGE_CONNECTION_STRING`: Azure Storage connection string
- `TEST_DATABASE_URL`: Connection string for test database

### 5. Configure MCP Servers
Ensure MCP servers have valid API keys:
- Update SendGrid API key in `.env.azure`
- Update OpenWeather API key in `.env.azure`

### 6. Set Up Automated Testing
Enhance the GitHub workflow to run tests before deployment:

```yaml
- name: Run tests
  run: |
    pytest -xvs tests/
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

### 7. Configure Application Insights for Monitoring
Set up Azure Application Insights:

```bash
# Create Application Insights resource
az monitor app-insights component create --app ai-event-planner-saas-insights \
                                         --location eastus \
                                         --resource-group ai-event-planner-rg \
                                         --application-type web

# Get the instrumentation key
instrumentationKey=$(az monitor app-insights component show --app ai-event-planner-saas-insights \
                                                           --resource-group ai-event-planner-rg \
                                                           --query instrumentationKey -o tsv)

# Configure the App Service to use Application Insights
az webapp config appsettings set --name ai-event-planner-saas \
                                 --resource-group ai-event-planner-rg \
                                 --settings APPINSIGHTS_INSTRUMENTATIONKEY=$instrumentationKey
```

### 8. Run the Azure Deployment Script
Create all necessary Azure resources:

```bash
./azure-deploy-saas.sh
```

The script will:
- Create a resource group if it doesn't exist
- Set up a PostgreSQL server and database
- Create a storage account
- Set up an App Service plan and App Service
- Configure environment variables

### 9. Deploy Using GitHub Actions
Either:
- Push changes to the main branch to trigger automatic deployment
- Manually trigger deployment from the GitHub Actions tab

### 10. Verify Deployment
After deployment completes:
- Access the SaaS application at: `https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html`
- Check logs if there are any issues: `az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg`

### 11. Run Database Migrations if Needed
If database migrations need to be run manually:
```bash
az webapp ssh --name ai-event-planner-saas --resource-group ai-event-planner-rg --command "cd /home/site/wwwroot && alembic upgrade head"
```

## Key Recommendations

1. **Secure Environment Variables**: Move API keys from `.env.azure` to Azure Key Vault for enhanced security in production environments. This protects sensitive credentials from exposure in configuration files.

2. **MCP Server Configuration**: Ensure all MCP servers (SendGrid, OpenWeather) have valid API keys configured before deployment to avoid runtime errors related to external service connectivity.

3. **Comprehensive Testing**: Run the full test suite before each deployment using the pipeline in GitHub Actions to catch potential issues early in the development process.

4. **Application Monitoring**: Use Azure Application Insights to monitor application performance, track usage patterns, and quickly identify issues in the production environment.
