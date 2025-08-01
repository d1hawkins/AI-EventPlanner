# Azure Deployment Instructions

This document provides step-by-step instructions for deploying the AI Event Planner SaaS application to Azure using GitHub Actions.

## Prerequisites

- GitHub repository with the AI Event Planner SaaS code
- Azure subscription
- Azure CLI installed (for generating credentials)

## Deployment Steps

### 1. Add Azure Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add a new repository secret named `AZURE_CREDENTIALS`
4. Copy the contents of `AZURE_CREDENTIALS.json` as the value

The `AZURE_CREDENTIALS.json` file contains the service principal credentials needed for GitHub Actions to authenticate with Azure. These credentials were generated using:

```bash
az ad sp create-for-rbac --name "ai-event-planner-github" --role contributor \
    --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/ai-event-planner-rg \
    --sdk-auth
```

### 2. Run the GitHub Actions Workflow

1. Go to your GitHub repository
2. Navigate to Actions
3. Select the "Deploy to Azure with Docker" workflow
4. Click "Run workflow"

### 3. Monitor the Deployment

You can monitor the deployment in the GitHub Actions tab of your repository. The workflow will:

1. Build a Docker image using the existing `Dockerfile.saas`
2. Push the image to Azure Container Registry
3. Deploy the image to Azure App Service
4. Configure the necessary environment variables

### 4. Access the Deployed Application

Once deployed, the application will be available at:

- Main URL: https://ai-event-planner-saas.azurewebsites.net/
- SaaS Application: https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html

## Troubleshooting

If the deployment fails, you can check the logs in the GitHub Actions tab. You can also check the Azure App Service logs using:

```bash
az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
```

## Alternative Deployment Methods

If you prefer a simpler deployment method, you can use the static HTML deployment script:

```bash
chmod +x azure-deploy-html-fixed.sh
./azure-deploy-html-fixed.sh
```

This will deploy a simple static website to Azure App Service, which can serve as a placeholder until the full application is deployed.

## Additional Documentation

For more details on the deployment process and the issues encountered, refer to:

- `AZURE_DEPLOYMENT_SUMMARY_FINAL.md` - Final deployment summary
- `AZURE_DEPLOYMENT_GITHUB_ACTIONS.md` - Detailed instructions for GitHub Actions deployment
- `AZURE_DEPLOYMENT_FINAL.md` - Summary of deployment approaches
