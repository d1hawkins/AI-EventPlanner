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

## DATABASE_URL Fix - IMPORTANT UPDATE

### Problem with Original Script
The original `azure-deploy-real-agents.sh` script was failing with:
```
[ERROR] Could not retrieve DATABASE_URL from existing deployment
```

This happened because the script tried to retrieve the DATABASE_URL from Azure app settings before it was set there.

### Solution - Use Fixed Script
**Use `azure-deploy-real-agents-fixed.sh` instead of the original script.**

The fixed script:
- Reads environment variables from local `.env.azure` file
- Validates required environment variables before proceeding
- Sets all environment variables in Azure including the DATABASE_URL
- Provides better error handling and logging
- Includes optional environment variables (SendGrid, OpenWeather) if they exist

### Prerequisites for Fixed Script
1. **Ensure you have a properly configured `.env.azure` file** with:
   ```bash
   DATABASE_URL=postgresql://dbadmin:password@server.postgres.database.azure.com:5432/eventplanner
   GOOGLE_API_KEY=your-google-api-key
   SECRET_KEY=your-secret-key
   SENDGRID_API_KEY=your-sendgrid-api-key  # Optional
   OPENWEATHER_API_KEY=your-openweather-api-key  # Optional
   ```

2. **Make sure you're logged into Azure CLI**:
   ```bash
   az login
   ```

3. **Verify your Azure resources exist**:
   ```bash
   az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   ```

## How It Works

The script performs the following key operations:

1. **Directory Structure**: Creates a complete directory structure with all necessary files and `__init__.py` files
2. **Agent Support**: Replaces `app_adapter.py` with `app_adapter_with_agents.py` to enable real agent functionality
3. **SaaS Support**: Uses the original `startup.sh` which has logic to check for and use `main_saas.py`
4. **Dependencies**: Includes all necessary dependencies for both SaaS and agent functionality
5. **Environment Variables**: Sets critical environment variables for agent logging and memory storage

## Usage

### Using the Fixed Script (Recommended)

To deploy the application with the DATABASE_URL fix:

```bash
./azure-deploy-real-agents-fixed.sh
```

### Using the Original Script (Legacy)

To deploy the application with the original approach:

```bash
./azure-deploy-saas-with-real-agents.sh
```

### What the Fixed Script Does

The fixed script will:
1. **Validate Prerequisites**: Check Azure CLI, login status, and required files
2. **Read Environment Variables**: Extract DATABASE_URL and other settings from `.env.azure`
3. **Update Dependencies**: Copy `requirements_with_agents.txt` to `requirements.txt`
4. **Set Azure Configuration**: Configure all environment variables in Azure App Service
5. **Deploy Application**: Create deployment package and upload to Azure
6. **Restart and Verify**: Restart the app and verify real agents are working

### What the Original Script Does

The original script will:
1. Create or use an existing resource group and App Service Plan
2. Create or use an existing Web App
3. Deploy all necessary files with the proper structure
4. Configure the App Service with the right startup file and environment variables
5. Restart the app to apply the changes

### Environment Variables Set by Fixed Script

The fixed script automatically sets these environment variables in Azure:

**Required Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `LLM_PROVIDER` - "google"
- `GOOGLE_API_KEY` - Your Google AI API key
- `GOOGLE_MODEL` - "gemini-2.0-flash"
- `SECRET_KEY` - Application secret key

**Agent Configuration:**
- `ENABLE_AGENT_LOGGING` - "true"
- `AGENT_MEMORY_STORAGE` - "file"
- `AGENT_MEMORY_PATH` - "./agent_memory"

**Application Settings:**
- `APP_NAME` - "AI Event Planner"
- `APP_VERSION` - "1.0.0"
- `ENVIRONMENT` - "production"
- `DEBUG` - "false"
- `HOST` - "0.0.0.0"
- `PORT` - "8000"

**Authentication:**
- `ACCESS_TOKEN_EXPIRE_MINUTES` - "60"
- `REFRESH_TOKEN_EXPIRE_DAYS` - "7"
- `ALGORITHM` - "HS256"

**Multi-tenancy:**
- `DEFAULT_TENANT` - "default"
- `TENANT_HEADER` - "X-Tenant-ID"

**Optional Variables (if present in .env.azure):**
- `SENDGRID_API_KEY` - SendGrid API key for email
- `EMAIL_FROM` - "noreply@aieventplanner.com"
- `EMAIL_FROM_NAME` - "AI Event Planner"
- `OPENWEATHER_API_KEY` - OpenWeather API key

## Verification

After deployment, you can verify that real agents are working by:

1. Accessing your application at `https://ai-event-planner-saas-py.azurewebsites.net`
2. Checking the health endpoint at `/health` which should show `"real_agents_available": true`
3. Navigating to the Agents section and interacting with an agent
4. Confirming that you receive real, dynamic responses instead of mock responses

If you encounter any issues, you can check the logs at:
`https://ai-event-planner-saas-py.scm.azurewebsites.net/api/logs/docker`

## Troubleshooting

### DATABASE_URL Issues

If you encounter DATABASE_URL related errors:

1. **Verify .env.azure file exists and contains DATABASE_URL**:
   ```bash
   grep "DATABASE_URL" .env.azure
   ```

2. **Check if DATABASE_URL is properly formatted**:
   ```bash
   # Should be in format:
   # DATABASE_URL=postgresql://username:password@server.postgres.database.azure.com:5432/database
   ```

3. **Verify Azure app settings were set**:
   ```bash
   az webapp config appsettings list --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --query "[?name=='DATABASE_URL']"
   ```

4. **Test database connectivity**:
   ```bash
   python scripts/test_postgres_connection.py
   ```

### General Issues

If the site fails to load or agents are still showing as mock:

1. **Check the application logs**:
   ```bash
   az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   ```

2. **Verify environment variables are set**:
   ```bash
   az webapp config appsettings list --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
   ```

3. **Check application status**:
   ```bash
   az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --query "state"
   ```

4. **Test health endpoint**:
   ```bash
   curl https://ai-event-planner-saas-py.azurewebsites.net/health
   ```

5. **Verify all necessary directories and files were deployed correctly**
6. **Ensure the startup script is correctly detecting and using `main_saas.py`**

### Common Error Messages and Solutions

**Error**: `[ERROR] Could not retrieve DATABASE_URL from existing deployment`
- **Solution**: Use `azure-deploy-real-agents-fixed.sh` instead of the original script

**Error**: `[ERROR] DATABASE_URL not found in .env.azure file`
- **Solution**: Create or update `.env.azure` with proper DATABASE_URL

**Error**: `[ERROR] GOOGLE_API_KEY not found in .env.azure file`
- **Solution**: Add GOOGLE_API_KEY to your `.env.azure` file

**Error**: `[ERROR] SECRET_KEY not found in .env.azure file`
- **Solution**: Add SECRET_KEY to your `.env.azure` file

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: The script should handle this automatically, but you can manually restart the app:
  ```bash
  az webapp restart --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
  ```

### Verification Commands

After deployment, use these commands to verify everything is working:

```bash
# Check if the app is running
az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --query "state"

# Check environment variables
az webapp config appsettings list --name ai-event-planner-saas-py --resource-group ai-event-planner-rg

# Test health endpoint
curl https://ai-event-planner-saas-py.azurewebsites.net/health

# Test agents endpoint
curl https://ai-event-planner-saas-py.azurewebsites.net/api/agents/available

# Check logs
az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

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
