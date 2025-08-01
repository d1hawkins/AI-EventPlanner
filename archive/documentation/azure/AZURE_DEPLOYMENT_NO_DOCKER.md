# Azure Deployment Without Docker

This document provides instructions for deploying the AI Event Planner SaaS application to Azure App Service without using Docker.

## Prerequisites

- Azure CLI installed and configured
- Azure account with active subscription
- Python 3.9 or higher

## Deployment Files

The following files are used for deployment:

1. `run_saas_no_docker.py` - The main application file
2. `requirements.txt` - Python dependencies
3. `azure-deploy-saas-python-no-docker.sh` - Deployment script

## Deployment Steps

### 1. Prepare the Application

The application is a FastAPI-based web application that serves static files and provides API endpoints. The main application file is `run_saas_no_docker.py`.

### 2. Run the Deployment Script

Execute the deployment script to deploy the application to Azure App Service:

```bash
./azure-deploy-saas-python-no-docker.sh
```

The script performs the following actions:

1. Checks if Azure CLI is installed
2. Verifies Azure login status
3. Creates a resource group if it doesn't exist
4. Creates an App Service Plan if it doesn't exist
5. Creates a Web App if it doesn't exist
6. Prepares the deployment package
7. Deploys the application to Azure App Service
8. Configures the startup command

### 3. Verify the Deployment

After the deployment is complete, you can access the application at:

```
https://ai-event-planner-saas-py.azurewebsites.net
```

## Troubleshooting

If you encounter any issues during deployment, check the following:

1. Azure CLI is installed and configured correctly
2. You have sufficient permissions to create resources in your Azure subscription
3. The resource group, App Service Plan, and Web App names are unique
4. The application dependencies are correctly specified in `requirements.txt`

## Additional Information

- The application is deployed as a Python application to Azure App Service
- The application uses gunicorn with uvicorn workers to serve the FastAPI application
- Static files are served from the `/static` endpoint
