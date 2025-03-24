# Azure Deployment Instructions

This document provides updated instructions for deploying the AI Event Planner SaaS application to Azure.

## Overview

The AI Event Planner SaaS application can be deployed to Azure using the following components:

1. Azure App Service - Hosts the web application
2. Azure PostgreSQL - Database for storing application data
3. Azure Storage - For storing files and resources
4. Azure Key Vault - For securely storing credentials and secrets

## Pre-requisites

- Azure CLI installed and configured
- Azure subscription
- Git repository with the application code

## Deployment Process

### Step 1: Set Up Basic Azure Resources

The `azure-deploy-saas.sh` script creates the basic Azure resources needed for the application:

```bash
# Make the script executable
chmod +x azure-deploy-saas.sh

# Run the script
./azure-deploy-saas.sh
```

This script creates:
- Resource Group
- PostgreSQL Server
- Storage Account
- App Service Plan
- App Service

### Step 2: Deploy the Application

We've created a simplified deployment script that handles packaging the application and deploying it to Azure App Service:

```bash
# Make the script executable
chmod +x deploy-app-to-azure.sh

# Run the script
./deploy-app-to-azure.sh
```

This script:
1. Creates a deployment package with all necessary files
2. Deploys the package to Azure App Service
3. Sets the required environment variables from `.env.azure`
4. Sets the startup command

### Step 3: Set Up GitHub Actions (Optional)

For continuous deployment, you can use GitHub Actions to automatically deploy when code is pushed to the repository:

1. Create a Service Principal for GitHub to use:
```bash
chmod +x setup-service-principal.sh
./setup-service-principal.sh
```

2. Add the resulting JSON as a GitHub repository secret named `AZURE_CREDENTIALS`

3. Use the `.github/workflows/azure-deploy-saas.yml` workflow to automate deployment

## Monitoring and Troubleshooting

### Application Insights

For monitoring, you can set up Application Insights:

```bash
chmod +x setup-app-insights.sh
./setup-app-insights.sh
```

### Logs and Diagnostics

To view logs from the App Service:

```bash
az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
```

## Accessing the Application

Once deployed, the application is available at:

- Main API: `https://ai-event-planner-saas.azurewebsites.net/`
- SaaS Frontend: `https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html`

## What to Do If Deployment Fails

If you encounter issues during deployment:

1. Check the Azure App Service logs for error messages
2. Verify all environment variables are set correctly
3. Ensure the database is accessible from the App Service
4. Try redeploying using the `deploy-app-to-azure.sh` script

For specific deployment issues:

- If you see errors about missing files, ensure the deployment package is being created correctly
- If you see connection errors, check network security rules and firewall settings
- If you see authentication errors, verify credentials in the environment variables
