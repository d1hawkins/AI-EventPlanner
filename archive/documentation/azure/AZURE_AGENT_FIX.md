# Azure AI Agent Fix

This document explains how to fix the issue with AI agents not running in the Azure deployment of the AI Event Planner application.

## Problem

The application is running in Azure, but the AI agents are not functioning. This is because the application is using `app_adapter.py` which provides mock responses for agent endpoints instead of using the real agent implementation in `app/main_saas.py`.

## Solution

The solution is to modify the app_adapter.py file to integrate with the real agent implementation while still handling static file serving. This approach ensures that the application starts up reliably while still providing real agent functionality.

The changes involve:

1. Updating `app_adapter.py` to try to import the real agent implementation and use it for agent-related endpoints
2. Updating `startup.sh` to ensure all required dependencies are installed before starting the application

These changes have been made in the repository, and a deployment script has been created to update the application in Azure.

## Deployment

To deploy the fix to Azure, follow these steps:

1. Make sure you have the Azure CLI installed and are logged in to your Azure account.

2. Run the update script:
   ```bash
   ./update-azure-agents.sh
   ```

3. The script will:
   - Check if the Azure CLI is installed and if you're logged in
   - Check if the app exists in Azure
   - Create a temporary deployment directory
   - Copy the updated startup files to the deployment directory
   - Create a zip file for deployment
   - Deploy the updated files to Azure App Service
   - Restart the app
   - Clean up temporary files

4. After the script completes, wait a few minutes for the changes to take effect.

5. Access your application at `https://ai-event-planner-saas-py.azurewebsites.net` to verify that the AI agents are now working.

## Verification

To verify that the AI agents are working correctly:

1. Log in to the application.
2. Navigate to the Agents section.
3. Try to interact with one of the agents (e.g., the Coordinator agent).
4. If the agent responds with real, dynamic responses instead of mock responses, the fix has been successful.
5. You can also check the health endpoint at `/health` which will indicate whether the real agent implementation is available.

## Troubleshooting

If the agents are still not working after deploying the fix, check the following:

1. **Application Logs**: Check the application logs in the Azure portal for any errors.

2. **Environment Variables**: Verify that all required environment variables are set correctly, especially:
   - `LLM_PROVIDER`: Should be set to "google" or "openai"
   - `GOOGLE_API_KEY` or `OPENAI_API_KEY`: Should be set to valid API keys
   - `DATABASE_URL`: Should point to a valid PostgreSQL database

3. **Database Migrations**: Make sure the database migrations have been run successfully. You can set the `RUN_MIGRATIONS` environment variable to "true" to run migrations on startup.

4. **Agent Memory Storage**: The agent state is stored using the method specified in the `AGENT_MEMORY_STORAGE` environment variable. Make sure this is set correctly (e.g., "file", "database").

5. **Restart the App**: Sometimes a simple restart can fix issues. You can restart the app from the Azure portal or using the Azure CLI:
   ```bash
   az webapp restart --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   ```

## Additional Notes

- The fix does not require any changes to the database schema or data.
- The fix does not affect the static files or frontend functionality.
- The application will continue to use the same LLM provider and API keys as before.
- The agent state persistence mechanism remains the same.
