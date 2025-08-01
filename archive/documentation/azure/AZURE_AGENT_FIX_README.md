# Azure AI Agent Fix Guide

This guide explains how to fix the issue with AI agents returning mock responses in the Azure deployment of the AI Event Planner application.

## Problem

The application is running in Azure, but the AI agents are returning mock responses instead of real, dynamic responses. This is because the application is using `app_adapter.py` which provides mock responses for agent endpoints when it fails to import the real agent implementation.

We identified two specific issues:
1. `ModuleNotFoundError: No module named 'app.main_saas'` - The application couldn't find the main_saas.py file
2. `ImportError: Could not import agent modules from any known path` - The application couldn't find the agent modules

## Solution

We've created a comprehensive solution that addresses several potential issues:

1. **Complete Application Deployment**: Updated the deployment script to include the entire app directory with all necessary modules
2. **Robust Module Loading**: Updated all startup files to dynamically check which modules are available and use the appropriate one
3. **Enhanced Debugging**: Added extensive logging to help diagnose any issues
4. **Python Path Configuration**: Ensured the Python path is correctly set to find all modules
5. **Environment Variables**: Set critical environment variables needed for agent functionality

### Key Improvements

1. Updated `update-azure-agents.sh` to:
   - Include the entire app directory in the deployment
   - Copy all necessary Python modules
   - Provide detailed logging of the deployment process

2. Updated `startup.py` to:
   - Check if main_saas.py, main.py, or app_adapter.py exists
   - Use the appropriate module based on what's available
   - Add detailed logging of the file system and environment

3. Updated `startup.sh` to:
   - Perform similar checks for available modules
   - Provide detailed logging
   - Set the Python path correctly

4. Enhanced `wsgi.py` to:
   - Try multiple import paths with proper error handling
   - Fall back gracefully to available modules
   - Log detailed debugging information

5. Updated `web.config` to:
   - Include the PYTHONPATH environment variable
   - Increase the startup timeout to allow for more debugging

## Deployment Steps

1. Make sure you have the Azure CLI installed and are logged in to your Azure account.

2. Run the update script:
   ```bash
   ./update-azure-agents.sh
   ```

3. The script will:
   - Check if the Azure CLI is installed and if you're logged in
   - Check if the app exists in Azure
   - Create a temporary deployment directory
   - Copy the updated files to the deployment directory
   - Create a zip file for deployment
   - Deploy the updated files to Azure App Service
   - Set critical environment variables
   - Restart the app
   - Clean up temporary files

4. After the script completes, wait a few minutes for the changes to take effect.

5. Verify that the agents are working correctly:
   ```bash
   ./verify_azure_agents.sh
   ```

## Verification

The verification script will:

1. Check the health endpoint to see if real agents are available
2. Check the available agents endpoint
3. Send a test message to the coordinator agent
4. Check if the response is a mock response or a real response

If the agents are still using mock responses after these changes, you should check the logs in the Azure portal for any errors. The logs can be accessed at:
https://ai-event-planner-saas-py.scm.azurewebsites.net/api/logs/docker

## Environment Variables

The following environment variables are set by the deployment script:

- `ENABLE_AGENT_LOGGING`: Set to "true" to enable agent logging
- `AGENT_MEMORY_STORAGE`: Set to "file" to store agent memory in files
- `AGENT_MEMORY_PATH`: Set to "/home/site/wwwroot/agent_memory" to specify where agent memory files are stored
- `PYTHONPATH`: Set to "/home/site/wwwroot" to ensure Python can find the application modules
- `WEBSITE_HTTPLOGGING_RETENTION_DAYS`: Set to "7" to retain HTTP logs for 7 days

You may also need to check the following environment variables in the Azure portal:

- `LLM_PROVIDER`: Should be set to "google" or "openai"
- `GOOGLE_API_KEY` or `OPENAI_API_KEY`: Should be valid API keys
- `DATABASE_URL`: Should point to a valid PostgreSQL database

## Files Modified

- `startup.py`: Updated to dynamically check for available modules and add extensive debugging
- `startup.sh`: Updated to dynamically check for available modules and set PYTHONPATH
- `wsgi.py`: Enhanced to try multiple import paths with proper error handling
- `web.config`: Updated to set PYTHONPATH environment variable
- `update-azure-agents.sh`: Enhanced to deploy all files and set environment variables
- `verify_azure_agents.sh`: Created to verify if agents are working correctly

## Troubleshooting

If the agents are still not working after deploying the fix, check the following:

1. **Application Logs**: Check the application logs in the Azure portal for any errors.

2. **File Structure**: Verify that the expected files exist in the correct locations:
   ```bash
   az webapp ssh --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   # Then inside the SSH session:
   cd /home/site/wwwroot
   ls -la
   ls -la app/
   ```

3. **Environment Variables**: Verify that all required environment variables are set correctly:
   ```bash
   az webapp config appsettings list --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   ```

4. **Database Connection**: Make sure the application can connect to the database.

5. **LLM API Keys**: Ensure the LLM provider API keys are valid.

6. **Python Path**: Check if the Python path is set correctly.

7. **Import Errors**: Look for any import errors in the logs.

8. **Restart the App**: Sometimes a simple restart can fix issues. You can restart the app from the Azure portal or using the Azure CLI:
   ```bash
   az webapp restart --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   ```
