# Azure SaaS Deployment with Real Agents

This guide explains how to deploy the AI Event Planner SaaS application to Azure with real agent functionality.

## Overview

The deployment script `azure-deploy-saas-with-real-agents.sh` combines the best elements of two existing scripts:
1. `azure-deploy-saas-python-no-docker-v3.sh` - Successfully deploys the SaaS application but uses mock agents
2. `update-azure-agents.sh` - Tries to enable real agents but causes the site not to load

The combined script ensures that:
1. The full SaaS functionality is preserved (using `main_saas.py` when available)
2. Real agents are enabled (using `app_adapter_with_agents.py`)
3. All necessary files and directory structures are properly deployed

## How It Works

The script performs the following key operations:

1. **Directory Structure**: Creates a complete directory structure with all necessary files and `__init__.py` files
2. **Agent Support**: Replaces `app_adapter.py` with `app_adapter_with_agents.py` to enable real agent functionality
3. **SaaS Support**: Uses the original `startup.sh` which has logic to check for and use `main_saas.py`
4. **Dependencies**: Includes all necessary dependencies for both SaaS and agent functionality
5. **Environment Variables**: Sets critical environment variables for agent logging and memory storage

## Usage

To deploy the application:

```bash
./azure-deploy-saas-with-real-agents.sh
```

The script will:
1. Create or use an existing resource group and App Service Plan
2. Create or use an existing Web App
3. Deploy all necessary files with the proper structure
4. Configure the App Service with the right startup file and environment variables
5. Restart the app to apply the changes

## Verification

After deployment, you can verify that real agents are working by:

1. Accessing your application at `https://ai-event-planner-saas-py.azurewebsites.net`
2. Checking the health endpoint at `/health` which should show `"real_agents_available": true`
3. Navigating to the Agents section and interacting with an agent
4. Confirming that you receive real, dynamic responses instead of mock responses

If you encounter any issues, you can check the logs at:
`https://ai-event-planner-saas-py.scm.azurewebsites.net/api/logs/docker`

## Troubleshooting

If the site fails to load or agents are still showing as mock:

1. Check the logs for any import errors
2. Verify that all necessary directories and files were deployed correctly
3. Ensure the startup script is correctly detecting and using `main_saas.py`
4. Check that environment variables are set correctly

### Non-Containerized Approach

The script now uses a non-containerized approach to avoid volume mount issues:

1. It first deletes the existing containerized web app (keeping the app service plan)
2. Then creates a new web app with the non-containerized Python runtime (`PYTHON:3.9` instead of `PYTHON|3.9`)
3. Sets `SCM_DO_BUILD_DURING_DEPLOYMENT=true` to ensure dependencies are installed during deployment

This approach avoids the "Volume: DaasLogs cannot be mounted" error that occurs with containerized deployments.

### Dependency Installation Issues

The script now includes a custom `startup.sh` that explicitly installs all required dependencies with specific versions:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi==0.95.1 uvicorn==0.22.0 gunicorn==20.1.0 sqlalchemy==2.0.9 pydantic==1.10.7 \
    langchain==0.0.267 langgraph==0.0.11 google-generativeai==0.3.1 openai==0.28.1 \
    passlib==1.7.4 python-jose==3.3.0 python-multipart==0.0.6 bcrypt==4.0.1 \
    python-dotenv==1.0.0 psycopg2-binary==2.9.6 email-validator==2.0.0 icalendar==5.0.7 alembic==1.10.4
```

This ensures that all dependencies are properly installed before the application starts, preventing errors like `ModuleNotFoundError: No module named 'fastapi'`.
