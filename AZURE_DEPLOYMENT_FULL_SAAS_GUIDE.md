# Azure Deployment Guide for Full AI Event Planner SaaS

This guide provides detailed instructions for deploying the full AI Event Planner SaaS application with agent integration to Azure App Service without Docker.

## Prerequisites

- Azure CLI installed and configured
- Azure subscription
- Git repository cloned locally

## Deployment Steps

### 1. Prepare the Application

The following files have been updated to support the full SaaS application deployment:

- **app_adapter.py**: Updated to import from `app.main_saas` instead of `app_simplified.py`
- **startup.py**: Updated to run database migrations and start the full application
- **startup.sh**: Updated to match the changes in startup.py
- **azure-deploy-saas-full-no-docker.sh**: New deployment script for the full SaaS application

### 2. Deploy to Azure

Use the provided deployment script to deploy the application to Azure:

```bash
chmod +x azure-deploy-saas-full-no-docker.sh
./azure-deploy-saas-full-no-docker.sh
```

This script will:

1. Create a resource group if it doesn't exist
2. Create a PostgreSQL server and database if they don't exist
3. Configure firewall rules to allow connections from Azure services
4. Create an App Service Plan if it doesn't exist
5. Create a Web App if it doesn't exist
6. Package and deploy the application
7. Configure the startup command
8. Set environment variables
9. Enable logging

### 3. Verify Deployment

After deployment, verify that the application is running correctly:

```bash
# Check the status of the web app
az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --query state

# Open the website in a browser
open https://ai-event-planner-saas-py.azurewebsites.net
```

### 4. Monitor Logs

To monitor the application logs:

```bash
# Stream logs in real-time
az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg

# Download logs
az webapp log download --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --log-file app_logs.zip
```

## Understanding the Deployment

### Database Setup

The deployment script creates a PostgreSQL server and database in Azure. The database connection string is set as an environment variable in the App Service.

When the application starts, it will run database migrations if the `RUN_MIGRATIONS` environment variable is set to `true`. This will create the necessary tables in the database.

### Environment Variables

The deployment script sets the following environment variables:

- **Database Connection**: `DATABASE_URL`
- **Authentication**: `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `ALGORITHM`
- **LLM Provider**: `LLM_PROVIDER`, `GOOGLE_API_KEY`, `GOOGLE_MODEL`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- **Email**: `SENDGRID_API_KEY`, `EMAIL_FROM`, `EMAIL_FROM_NAME`
- **Multi-tenancy**: `DEFAULT_TENANT`, `TENANT_HEADER`
- **Agent Settings**: `ENABLE_AGENT_LOGGING`, `AGENT_MEMORY_STORAGE`, `AGENT_MEMORY_PATH`
- **Application Settings**: `RUN_MIGRATIONS`, `ENVIRONMENT`, `APP_VERSION`, `APP_NAME`

### Application Structure

The full SaaS application includes:

- **API Endpoints**: Authentication, events, subscriptions, agents
- **Database Models**: Users, events, organizations, subscriptions
- **Agent Integration**: Specialized agents for different aspects of event planning
- **Frontend**: SaaS web interface for users to interact with the application

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Fails to Start

If the application fails to start within the timeout period, check the following:

- **Logs**: Check the application logs for error messages
- **Database Connection**: Ensure the database connection string is correct
- **Environment Variables**: Ensure all required environment variables are set

#### 2. Database Migration Fails

If database migration fails, check the following:

- **Database Connection**: Ensure the database connection string is correct
- **Migration Scripts**: Ensure the migration scripts are correct
- **Database Permissions**: Ensure the database user has the necessary permissions

#### 3. Agent Integration Issues

If agent integration is not working, check the following:

- **LLM Provider**: Ensure the LLM provider is correctly configured
- **API Keys**: Ensure the API keys are correct
- **Agent Settings**: Ensure the agent settings are correctly configured

## Conclusion

By following this guide, you should be able to successfully deploy the full AI Event Planner SaaS application with agent integration to Azure App Service without Docker. If you encounter any issues, refer to the troubleshooting section or check the application logs for more information.
