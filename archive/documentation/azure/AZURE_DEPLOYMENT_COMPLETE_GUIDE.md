# Azure Deployment Guide for Complete AI Event Planner SaaS with Real Agents

This guide provides detailed instructions for deploying the complete AI Event Planner SaaS application with real agent functionality to Azure App Service.

## Overview

The deployment script `azure-deploy-saas-complete.sh` combines the best elements of two existing scripts:

1. `azure-deploy-saas-with-real-agents.sh` - Focuses on enabling real agent functionality
2. `azure-deploy-saas-full-no-docker.sh` - Sets up the database and comprehensive environment variables

This combined script ensures that:

1. A PostgreSQL database is properly set up in Azure
2. The full SaaS functionality is preserved (using `main_saas.py` when available)
3. Real agents are enabled (using `app_adapter_with_agents.py`)
4. All necessary files and directory structures are properly deployed
5. All required environment variables are set

## Prerequisites

- Azure CLI installed and configured
- Azure subscription
- Git repository cloned locally

## Deployment Steps

### 1. Make the Script Executable

```bash
chmod +x azure-deploy-saas-complete.sh
```

### 2. Run the Deployment Script

```bash
./azure-deploy-saas-complete.sh
```

The script will:

1. Create or use an existing resource group
2. Prompt you about setting up a PostgreSQL database:
   - If you choose to set up a database, it will:
     - Ask for a database server name (or use a generated unique name)
     - Ask for database credentials (or use defaults)
     - Create the PostgreSQL server and database
     - Configure firewall rules to allow connections from Azure services
   - If you choose not to set up a database, it will skip this step
3. Create or use an existing App Service Plan
4. Create or use an existing Web App
5. Package and deploy the application with the proper directory structure
6. Configure the App Service with the right startup file
7. Set all necessary environment variables
8. Enable logging
9. Restart the app to apply the changes

### 3. Verify Deployment

After deployment, verify that the application is running correctly:

```bash
# Check the status of the web app
az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --query state

# Open the website in a browser
open https://ai-event-planner-saas-py.azurewebsites.net
```

## Understanding the Deployment

### Database Setup

The script offers an interactive database setup process:

1. It asks if you want to set up a PostgreSQL database in Azure
2. If you choose to set up a database:
   - It generates a unique database server name to avoid conflicts
   - It allows you to customize the server name, admin username, and password
   - It creates the PostgreSQL server and database
   - It configures firewall rules to allow connections from Azure services
   - It sets the database connection string as an environment variable

When the application starts, it will run database migrations if the `RUN_MIGRATIONS` environment variable is set to `true`. This will create the necessary tables in the database.

If you choose not to set up a database or if database creation fails, the application will still be deployed without database functionality.

### Real Agent Support

The script uses `app_adapter_with_agents.py` as the adapter file, which enables real agent functionality. It also sets the necessary environment variables for agent logging and memory storage.

### Directory Structure

The script creates a complete directory structure with all necessary files and `__init__.py` files. This ensures that Python can properly import modules from all directories.

### Environment Variables

The script sets comprehensive environment variables including:

- **Database Connection**: `DATABASE_URL`
- **Authentication**: `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `ALGORITHM`
- **LLM Provider**: `LLM_PROVIDER`, `GOOGLE_API_KEY`, `GOOGLE_MODEL`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- **Email**: `SENDGRID_API_KEY`, `EMAIL_FROM`, `EMAIL_FROM_NAME`
- **Multi-tenancy**: `DEFAULT_TENANT`, `TENANT_HEADER`
- **Agent Settings**: `ENABLE_AGENT_LOGGING`, `AGENT_MEMORY_STORAGE`, `AGENT_MEMORY_PATH`
- **Application Settings**: `RUN_MIGRATIONS`, `ENVIRONMENT`, `APP_VERSION`, `APP_NAME`
- **Deployment Settings**: `PYTHONPATH`, `WEBSITE_HTTPLOGGING_RETENTION_DAYS`, `SCM_DO_BUILD_DURING_DEPLOYMENT`

### Non-Containerized Approach

The script uses a non-containerized approach to avoid volume mount issues:

1. It first deletes the existing web app (keeping the app service plan)
2. Then creates a new web app with the non-containerized Python runtime (`PYTHON:3.9` instead of `PYTHON|3.9`)
3. Sets `SCM_DO_BUILD_DURING_DEPLOYMENT=true` to ensure dependencies are installed during deployment

This approach avoids the "Volume: DaasLogs cannot be mounted" error that occurs with containerized deployments.

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Fails to Start

If the application fails to start within the timeout period, check the following:

- **Logs**: Check the application logs for error messages
- **Database Connection**: Ensure the database connection string is correct (if using a database)
- **Environment Variables**: Ensure all required environment variables are set

#### 2. Database Creation Fails

If database creation fails, the script will continue without database setup. Common reasons for failure include:

- **Server Name Already Exists**: Azure PostgreSQL server names must be globally unique
- **Password Complexity**: Azure requires complex passwords for database servers
- **Subscription Limitations**: Your Azure subscription may have limitations on creating database servers

You can try running the script again with a different server name or check your Azure subscription limitations.

#### 3. Database Migration Fails

If database migration fails, check the following:

- **Database Connection**: Ensure the database connection string is correct
- **Migration Scripts**: Ensure the migration scripts are correct
- **Database Permissions**: Ensure the database user has the necessary permissions

#### 3. Agent Integration Issues

If agent integration is not working, check the following:

- **LLM Provider**: Ensure the LLM provider is correctly configured
- **API Keys**: Ensure the API keys are correct
- **Agent Settings**: Ensure the agent settings are correctly configured

### Viewing Logs

To view logs for troubleshooting:

```bash
# View application logs
az webapp log download --name ai-event-planner-saas-py --resource-group ai-event-planner-rg

# Stream logs in real-time
az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

You can also view logs in the Azure portal or at:
`https://ai-event-planner-saas-py.scm.azurewebsites.net/api/logs/docker`

### Restarting the Application

If you need to restart the application:

```bash
# Restart the web app
az webapp restart --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

## Conclusion

By using the `azure-deploy-saas-complete.sh` script, you can deploy the complete AI Event Planner SaaS application with real agent functionality to Azure App Service. The script handles all the necessary steps to ensure a successful deployment, including database setup, environment variable configuration, and proper directory structure.

If you encounter any issues during deployment, refer to the troubleshooting section or check the application logs for more information.
