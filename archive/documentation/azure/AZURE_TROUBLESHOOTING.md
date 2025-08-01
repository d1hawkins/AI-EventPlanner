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

5. **Fixed Content-Type Issue**: Added proper Content-Type headers to API requests to fix 415 Unsupported Media Type errors.

## Common Errors

### HTTP 415 Unsupported Media Type

If you encounter a 415 Unsupported Media Type error when running migrations or using the Kudu REST API, it means the API is expecting a specific content type. Make sure to include the Content-Type header in your requests:

```bash
curl -X POST -u "username:password" \
  -H "Content-Type: application/json" \
  https://your-app.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"your command\", \"dir\":\"/home/site/wwwroot\"}"
```

### "cd command not found" Error

If you encounter an error like `/opt/Kudu/Scripts/starter.sh: line 2: exec: cd: not found` when using the Kudu REST API, it means the `cd` command is not available in the Kudu environment. Instead of using `cd` in your command, set the `dir` parameter to the directory where you want to execute the command:

```bash
# Instead of this:
curl -X POST -u "username:password" \
  -H "Content-Type: application/json" \
  https://your-app.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"cd /home/site/wwwroot && python -m scripts.migrate\", \"dir\":\"/\"}"

# Do this:
curl -X POST -u "username:password" \
  -H "Content-Type: application/json" \
  https://your-app.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"python -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}"
```

This approach sets the working directory directly using the `dir` parameter, which is more compatible with the Kudu environment.

### "python command not found" Error

If you encounter an error like `/opt/Kudu/Scripts/starter.sh: line 2: exec: python: not found` when using the Kudu REST API, it means the `python` command is not in the PATH in the Kudu environment. The best approach is to use the full path to the Python executable:

```bash
# Instead of this:
curl -X POST -u "username:password" \
  -H "Content-Type: application/json" \
  https://your-app.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"python -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}"

# Do this:
curl -X POST -u "username:password" \
  -H "Content-Type: application/json" \
  https://your-app.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"/usr/local/bin/python3 -m scripts.migrate\", \"dir\":\"/home/site/wwwroot\"}"
```

Common Python executable paths in Azure App Service containers include:
- `/usr/local/bin/python3` (most common in Docker containers)
- `/usr/bin/python3`
- `/home/site/wwwroot/env/bin/python` (if using a virtual environment)

If you're not sure which path to use, you can first find the Python executable path:

```bash
# Find the Python executable path
curl -X POST -u "username:password" \
  -H "Content-Type: application/json" \
  https://your-app.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"find / -name python3 2>/dev/null | head -n 1\", \"dir\":\"/home/site/wwwroot\"}"
```

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
