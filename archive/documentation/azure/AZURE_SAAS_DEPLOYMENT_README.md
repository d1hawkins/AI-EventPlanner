# AI Event Planner SaaS Azure Deployment

This document provides instructions for deploying the AI Event Planner SaaS application to Azure.

## Prerequisites

- Azure subscription
- GitHub account with repository access
- Azure CLI installed locally
- Git installed locally

## Deployment Files

The following files are included in this deployment package:

- `AZURE_DEPLOYMENT_PLAN.md` - Detailed deployment plan
- `deploy-to-azure.sh` - Master deployment script
- `setup-service-principal.sh` - Script to create Azure Service Principal for GitHub Actions
- `setup-key-vault.sh` - Script to configure Azure Key Vault for secure credential storage
- `setup-app-insights.sh` - Script to set up Application Insights for monitoring
- `run-migrations.sh` - Script to run database migrations
- `verify-deployment.sh` - Script to verify deployment
- `azure-deploy-saas.sh` - Script to create Azure resources
- `.github/workflows/azure-deploy-saas.yml` - GitHub Actions workflow for CI/CD

## Deployment Options

You have two options for deploying the application:

### Option 1: Automated Deployment (Recommended)

Run the master deployment script, which will execute all the necessary steps in the correct order:

```bash
./deploy-to-azure.sh
```

This script will:
1. Create an Azure Service Principal for GitHub Actions
2. Create Azure resources (App Service, PostgreSQL DB, etc.)
3. Configure Azure Key Vault for secure credential storage
4. Set up Application Insights for monitoring
5. Run database migrations
6. Verify deployment

### Option 2: Manual Deployment

If you prefer to run each step manually, you can execute the scripts individually:

1. Create Azure Service Principal:
   ```bash
   ./setup-service-principal.sh
   ```

2. Create Azure resources:
   ```bash
   ./azure-deploy-saas.sh
   ```

3. Configure Azure Key Vault:
   ```bash
   ./setup-key-vault.sh
   ```

4. Set up Application Insights:
   ```bash
   ./setup-app-insights.sh
   ```

5. Run database migrations:
   ```bash
   ./run-migrations.sh
   ```

6. Verify deployment:
   ```bash
   ./verify-deployment.sh
   ```

## GitHub Actions CI/CD

The repository includes a GitHub Actions workflow that automatically deploys the application to Azure when changes are pushed to the main branch. To set up GitHub Actions:

1. Create an Azure Service Principal using the `setup-service-principal.sh` script
2. Add the JSON output as a GitHub repository secret named `AZURE_CREDENTIALS`
3. Add the following additional secrets to your GitHub repository:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Your JWT secret key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GOOGLE_API_KEY`: Your Google API key
   - `STORAGE_CONNECTION_STRING`: Azure Storage connection string
   - `TEST_DATABASE_URL`: Connection string for test database

## Security Recommendations

1. **Use Azure Key Vault**: Store API keys and sensitive information in Azure Key Vault instead of environment variables.
2. **Enable Managed Identity**: Use managed identity for App Service to access Key Vault securely.
3. **Secure Database**: Ensure the PostgreSQL server is properly secured with firewall rules.
4. **HTTPS Only**: Configure the App Service to use HTTPS only.
5. **Regular Updates**: Keep the application and dependencies up to date.

## Monitoring

The application is configured with Azure Application Insights for monitoring. You can access the monitoring dashboard in the Azure Portal.

To view application logs:

```bash
az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
```

## Troubleshooting

If you encounter issues during deployment:

1. Check the logs:
   ```bash
   az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
   ```

2. Verify database connection:
   ```bash
   az webapp ssh --name ai-event-planner-saas --resource-group ai-event-planner-rg --command "cd /home/site/wwwroot && python -c 'from app.db.session import engine; print(\"Connected\" if engine.connect() else \"Failed\")'"
   ```

3. Run migrations manually:
   ```bash
   ./run-migrations.sh
   ```

4. Check environment variables:
   ```bash
   az webapp config appsettings list --name ai-event-planner-saas --resource-group ai-event-planner-rg
   ```

## MCP Servers

The application uses MCP servers for SendGrid and OpenWeather API integration. Ensure these servers have valid API keys configured in the `.env.azure` file or Azure Key Vault.

## Application URLs

After deployment, the application will be available at:

- Main application: `https://ai-event-planner-saas.azurewebsites.net`
- SaaS application: `https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html`
