# Azure Deployment for AI Event Planner SaaS

This repository contains multiple solutions for deploying the AI Event Planner SaaS application to Azure. The recommended approach is to use GitHub Actions for a Docker-based deployment.

## Recommended Deployment Method: GitHub Actions

### Key Files

1. **GitHub Actions Workflow**: `.github/workflows/azure-deploy-docker.yml`
   - Builds and deploys the Docker image using GitHub's CI/CD environment
   - Configures the Azure App Service with the necessary settings

2. **Azure Service Principal**: `AZURE_CREDENTIALS.json`
   - Contains the credentials needed for GitHub Actions to authenticate with Azure
   - Should be added as a secret in your GitHub repository

3. **Documentation**:
   - `AZURE_DEPLOYMENT_INSTRUCTIONS.md` - Step-by-step deployment instructions
   - `AZURE_DEPLOYMENT_GITHUB_ACTIONS.md` - Detailed GitHub Actions deployment guide
   - `AZURE_DEPLOYMENT_SUMMARY_FINAL.md` - Final deployment summary

### Quick Start

1. Add the Azure credentials to your GitHub repository:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add a new repository secret named `AZURE_CREDENTIALS`
   - Copy the contents of `AZURE_CREDENTIALS.json` as the value

2. Run the GitHub Actions workflow:
   - Go to your GitHub repository → Actions
   - Select the "Deploy to Azure with Docker" workflow
   - Click "Run workflow"

3. Monitor the deployment in the GitHub Actions tab

4. Once deployed, the application will be available at:
   - https://ai-event-planner-saas.azurewebsites.net/
   - https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html

## Alternative Deployment Methods

If you prefer a simpler deployment method, you can use the static HTML deployment script:

```bash
chmod +x azure-deploy-html-fixed.sh
./azure-deploy-html-fixed.sh
```

This will deploy a simple static website to Azure App Service, which can serve as a placeholder until the full application is deployed.

## Troubleshooting

If the deployment fails, you can check the logs in the GitHub Actions tab. You can also check the Azure App Service logs using:

```bash
az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
```

## Why GitHub Actions?

The GitHub Actions approach is recommended because:

1. It avoids the need for Docker to be running on your local machine
2. It provides a consistent environment between development and production
3. It uses the existing `Dockerfile.saas` which properly installs all dependencies
4. It automates the entire deployment process
5. It provides a clear audit trail of deployments

For detailed instructions, refer to the `AZURE_DEPLOYMENT_INSTRUCTIONS.md` file.
