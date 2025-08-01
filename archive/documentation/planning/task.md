# Azure Deployment Plan for SaaS and Agent Applications

This document outlines the comprehensive plan for deploying both the SaaS application and real agents to Azure. Each task can be marked as completed by replacing `[ ]` with `[x]`.

## Background

The AI Event Planner consists of two main components:
1. **SaaS Application**: The multi-tenant web application with user management, team features, and subscription plans
2. **Agent System**: The AI agents that provide event planning assistance (coordinator, resource planning, financial, etc.)

Previous deployment attempts have faced issues with:
- SaaS-only deployments using mock agents instead of real ones
- Agent integration failures due to import errors or missing dependencies
- Directory structure problems and missing `__init__.py` files
- Inconsistent dependency installation
- Missing or incorrect environment variables

## Recommended Approach

The most effective approach is using the `azure-deploy-saas-with-real-agents.sh` script, which combines:
- Non-containerized Python runtime to avoid volume mount issues
- Complete directory structure with proper `__init__.py` files
- Integration of `app_adapter_with_agents.py` for real agent functionality
- Explicit dependency installation with specific versions
- Proper environment variable configuration
- Startup script that detects and uses the appropriate entry point

## Deployment Tasks

### Task 1: Prepare the Environment
- [x] 1.1 Verify Azure CLI is installed and configured
- [x] 1.2 Login to Azure account (`az login`)
- [x] 1.3 Verify resource group exists or create a new one (`az group create`)
- [x] 1.4 Check for existing App Service Plan or create a new one (`az appservice plan create`)

### Task 2: Prepare the Application Files
- [x] 2.1 Verify all required Python files are present
- [x] 2.2 Ensure `app_adapter_with_agents.py` is available and properly configured
- [x] 2.3 Check that `startup.sh` has the correct shebang line and permissions (`chmod +x startup.sh`)
- [x] 2.4 Verify `wsgi.py` has proper module import logic
- [x] 2.5 Ensure `requirements.txt` includes all necessary dependencies
- [x] 2.6 Verify all directories have proper `__init__.py` files (`find app -type d -exec touch {}/__init__.py \;`)

### Task 3: Configure the Database
- [x] 3.1 Verify PostgreSQL server exists or create a new one (`az postgres server create`)
- [x] 3.2 Ensure database connection string is correctly formatted
- [x] 3.3 Prepare migration scripts for database schema setup (`run_azure_migrations_fixed.py`)
- [x] 3.4 Test database connection locally if possible (`scripts/test_postgres_connection.py`)

### Task 4: Deploy the Application
- [x] 4.1 Run the `azure-deploy-saas-with-real-agents.sh` script
- [x] 4.2 Monitor the deployment process for any errors
- [x] 4.3 Verify all files are correctly uploaded to Azure (`az webapp ssh`)
- [x] 4.4 Check that environment variables are properly set (`az webapp config appsettings list`)

### Task 5: Verify the Deployment
- [x] 5.1 Run the `verify_azure_agents.sh` script
- [x] 5.2 Check the health endpoint for `"real_agents_available": true` (`check_azure_agents.sh`)
- [x] 5.3 Test agent functionality with a sample message (`curl` command in `verify_azure_agents.sh`)
- [x] 5.4 Verify SaaS functionality (login, dashboard, etc.)

### Task 6: Troubleshoot Common Issues
- [x] 6.1 Check application logs for import errors (`az webapp log download`)
- [x] 6.2 Verify Python path is correctly set (`check_env.py`)
- [x] 6.3 Ensure all dependencies are properly installed (`check_passlib_installation.py`, `check_psycopg2_installation.py`, etc.)
- [x] 6.4 Check for any missing files or directories (`verify_auth_directory.py`)

### Task 7: Optimize and Secure
- [x] 7.1 Enable Application Insights for monitoring (`setup-app-insights.sh`)
- [x] 7.2 Configure proper logging retention (`enable_azure_logging.sh`)
- [x] 7.3 Set up secure environment variable storage (`setup-key-vault.sh`)
- [x] 7.4 Implement proper authentication and authorization (`setup-service-principal.sh`)

## Detailed Implementation Instructions

### Task 1: Prepare the Environment

#### 1.1 Verify Azure CLI is installed and configured
```bash
az --version
```
If not installed, follow the instructions at https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

#### 1.2 Login to Azure account
```bash
az login
```

#### 1.3 Verify resource group exists or create a new one
```bash
# Check if resource group exists
az group show --name ai-event-planner-rg

# Create if it doesn't exist
az group create --name ai-event-planner-rg --location eastus
```

#### 1.4 Check for existing App Service Plan or create a new one
```bash
# Check if App Service Plan exists
az appservice plan show --name ai-event-planner-saas-py-plan --resource-group ai-event-planner-rg

# Create if it doesn't exist
az appservice plan create --name ai-event-planner-saas-py-plan --resource-group ai-event-planner-rg --sku B1 --is-linux
```

### Task 2: Prepare the Application Files

#### 2.1 Verify all required Python files are present
Check for the following key files:
- `app/main_saas.py`: Main SaaS application entry point
- `app_adapter_with_agents.py`: Adapter for real agent functionality
- `startup.py`: Python startup script
- `startup.sh`: Shell startup script
- `wsgi.py`: WSGI entry point
- `web.config`: Azure web configuration

#### 2.2 Ensure `app_adapter_with_agents.py` is available and properly configured
Verify that `app_adapter_with_agents.py` has the correct import paths and error handling for agent modules.

#### 2.3 Check that `startup.sh` has the correct shebang line and permissions
```bash
# Check shebang line
head -1 startup.sh  # Should be #!/bin/bash

# Set correct permissions
chmod +x startup.sh
```

#### 2.4 Verify `wsgi.py` has proper module import logic
Ensure `wsgi.py` tries to import from multiple paths and has proper error handling.

#### 2.5 Ensure `requirements.txt` includes all necessary dependencies
Verify that `requirements.txt` includes all required packages, especially:
- fastapi
- uvicorn
- gunicorn
- sqlalchemy
- pydantic
- langchain
- langgraph
- google-generativeai
- openai
- passlib
- python-jose
- python-multipart
- bcrypt
- python-dotenv
- psycopg2-binary
- email-validator
- icalendar
- alembic

#### 2.6 Verify all directories have proper `__init__.py` files
```bash
# Create __init__.py files in all app subdirectories
find app -type d -exec touch {}/__init__.py \;
```

### Task 3: Configure the Database

#### 3.1 Verify PostgreSQL server exists or create a new one
```bash
# Check if PostgreSQL server exists
az postgres server show --name ai-event-planner-db --resource-group ai-event-planner-rg

# Create if it doesn't exist
az postgres server create \
    --name ai-event-planner-db \
    --resource-group ai-event-planner-rg \
    --location eastus \
    --admin-user aiepadmin \
    --admin-password "YourSecurePassword" \
    --sku-name GP_Gen5_2 \
    --version 11
```

#### 3.2 Ensure database connection string is correctly formatted
The connection string should be in the format:
```
postgresql://username@servername:password@servername.postgres.database.azure.com/dbname
```

#### 3.3 Prepare migration scripts for database schema setup
Verify that `run_azure_migrations_fixed.py` is properly configured with the correct database connection parameters.

#### 3.4 Test database connection locally if possible
```bash
python scripts/test_postgres_connection.py
```

### Task 4: Deploy the Application

#### 4.1 Run the `azure-deploy-saas-with-real-agents.sh` script
```bash
./azure-deploy-saas-with-real-agents.sh
```

#### 4.2 Monitor the deployment process for any errors
Watch the output of the deployment script for any errors or warnings.

#### 4.3 Verify all files are correctly uploaded to Azure
```bash
# SSH into the App Service
az webapp ssh --name ai-event-planner-saas-py --resource-group ai-event-planner-rg

# Check the files
ls -la /home/site/wwwroot
ls -la /home/site/wwwroot/app
```

#### 4.4 Check that environment variables are properly set
```bash
az webapp config appsettings list --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

Ensure the following environment variables are set:
- `ENABLE_AGENT_LOGGING=true`
- `AGENT_MEMORY_STORAGE=file`
- `AGENT_MEMORY_PATH=/home/site/wwwroot/agent_memory`
- `PYTHONPATH=/home/site/wwwroot`
- `WEBSITE_HTTPLOGGING_RETENTION_DAYS=7`
- `SCM_DO_BUILD_DURING_DEPLOYMENT=true`

### Task 5: Verify the Deployment

#### 5.1 Run the `verify_azure_agents.sh` script
```bash
./verify_azure_agents.sh
```

#### 5.2 Check the health endpoint for `"real_agents_available": true`
```bash
curl https://ai-event-planner-saas-py.azurewebsites.net/health
```

#### 5.3 Test agent functionality with a sample message
```bash
curl -X POST https://ai-event-planner-saas-py.azurewebsites.net/api/agents/message \
    -H "Content-Type: application/json" \
    -d '{"agent_type":"coordinator","message":"Hello, I need help planning an event."}'
```

#### 5.4 Verify SaaS functionality (login, dashboard, etc.)
Open a browser and navigate to:
```
https://ai-event-planner-saas-py.azurewebsites.net/static/saas/index.html
```

### Task 6: Troubleshoot Common Issues

#### 6.1 Check application logs for import errors
```bash
az webapp log download --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --log-file app_logs.zip
```

#### 6.2 Verify Python path is correctly set
```bash
az webapp ssh --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
# Then inside the SSH session:
echo $PYTHONPATH
```

#### 6.3 Ensure all dependencies are properly installed
```bash
az webapp ssh --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
# Then inside the SSH session:
pip list
```

#### 6.4 Check for any missing files or directories
```bash
az webapp ssh --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
# Then inside the SSH session:
find /home/site/wwwroot -type d -name "agents" -o -name "graphs"
```

### Task 7: Optimize and Secure

#### 7.1 Enable Application Insights for monitoring
```bash
# Run the setup-app-insights.sh script
./setup-app-insights.sh
```

#### 7.2 Configure proper logging retention
```bash
az webapp log config --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --application-logging filesystem --detailed-error-messages true --failed-request-tracing true --web-server-logging filesystem
```

#### 7.3 Set up secure environment variable storage
```bash
# Run the setup-key-vault.sh script
./setup-key-vault.sh
```

#### 7.4 Implement proper authentication and authorization
```bash
# Run the setup-service-principal.sh script
./setup-service-principal.sh
```

## Validation Checklist

After completing the deployment, use this checklist to validate that everything is working correctly:

- [x] Web application loads successfully
- [x] Health endpoint returns `"real_agents_available": true`
- [x] Agent responses are dynamic and not mock responses
- [x] Database migrations have been applied successfully
- [x] User authentication works correctly
- [x] Team and subscription features work correctly
- [x] All agent types are available based on subscription tier
- [x] Application logs show no critical errors
- [x] Application Insights is collecting telemetry
- [x] Environment variables are securely stored

## Troubleshooting Guide

### Common Issues and Solutions

#### Application fails to start
- Check for syntax errors in Python files
- Verify all dependencies are installed
- Check startup script permissions and shebang line
- Verify Python path is correctly set

#### Mock agents instead of real agents
- Verify `app_adapter_with_agents.py` is being used
- Check import paths in `wsgi.py` and `startup.py`
- Ensure all agent modules are included in the deployment
- Check for import errors in the logs

#### Database connection issues
- Verify connection string format
- Check firewall rules for the PostgreSQL server
- Ensure the database exists and has the correct schema
- Check for database-related errors in the logs

#### Missing files or directories
- Verify all files were included in the deployment
- Check for proper directory structure
- Ensure all `__init__.py` files are present
- Verify file permissions

#### Environment variable issues
- Check if all required environment variables are set
- Verify environment variable values are correct
- Ensure environment variables are accessible to the application

## References

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure PostgreSQL Documentation](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
