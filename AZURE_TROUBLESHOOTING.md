# Azure Deployment Troubleshooting Guide

This guide provides steps to diagnose and fix common issues with the AI Event Planner deployment on Azure.

## Common Issues and Solutions

### 1. Application Error in Azure Web App

If you're seeing an "Application Error" message when accessing your Azure Web App, follow these steps to diagnose and fix the issue:

#### Step 1: Check Application Logs

```bash
# View the application logs
az webapp log tail --resource-group ai-event-planner-rg --name ai-event-planner
```

Look for error messages that might indicate what's causing the issue.

#### Step 2: Check Environment Variables

Make sure all required environment variables are set correctly in the Azure Web App:

```bash
# List app settings
az webapp config appsettings list --resource-group ai-event-planner-rg --name ai-event-planner
```

Ensure the following environment variables are set:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT authentication
- `LLM_PROVIDER`: Set to "openai" or "google"
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `GOOGLE_API_KEY`: Your Google AI API key (if using Google)

#### Step 3: Run Database Migrations

Database migration issues can cause the application to fail. Run migrations manually:

```bash
# Run the test-migration-command.sh script
./test-migration-command.sh
```

#### Step 4: Restart the Web App

Sometimes a simple restart can fix the issue:

```bash
# Restart the web app
az webapp restart --resource-group ai-event-planner-rg --name ai-event-planner
```

### 2. Using the Diagnostic Tool

We've created a diagnostic tool to help identify and fix common issues:

```bash
# Run the diagnostic tool
python scripts/diagnose_azure.py

# To automatically fix issues
python scripts/diagnose_azure.py --fix

# To run migrations
python scripts/diagnose_azure.py --run-migrations

# To restart the web app
python scripts/diagnose_azure.py --restart
```

## Recent Fixes

We've made several improvements to make the deployment more robust:

1. **Fixed Database Initialization**: Removed automatic table creation from app startup, relying on migrations instead.

2. **Improved Migration Process**: Enhanced the migration script with better error handling and logging.

3. **Enhanced Dockerfile**: Added health checks and improved environment variable handling.

4. **Better Error Handling**: Added more robust error handling in the GitHub Actions workflow.

## Deployment Process

To deploy the application to Azure:

1. Make sure you have the Azure CLI installed and are logged in:
   ```bash
   az login
   ```

2. Run the Azure deployment script to create all necessary resources:
   ```bash
   ./azure-deploy.sh
   ```

3. Configure the GitHub repository secrets as described in AZURE_DEPLOYMENT.md.

4. Push changes to the main branch to trigger the CI/CD pipeline.

## Monitoring

Monitor your application using Azure Application Insights:

1. Navigate to the Azure Portal
2. Go to your App Service resource
3. Click on "Application Insights" in the left menu
4. View metrics, logs, and performance data
