# Deploying to Azure with GitHub Actions

Since Docker is not running on your local machine, I've created a GitHub Actions workflow file that will handle the Docker-based deployment to Azure. This approach leverages GitHub's CI/CD environment to build and deploy the Docker container.

## Workflow File

The workflow file is located at `.github/workflows/azure-deploy-docker.yml`. This workflow:

1. Builds a Docker image using the existing `Dockerfile.saas`
2. Pushes the image to Azure Container Registry
3. Deploys the image to Azure App Service
4. Configures the necessary environment variables

## Prerequisites

Before running this workflow, you need to set up GitHub secrets:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add a new repository secret named `AZURE_CREDENTIALS` with the Azure service principal credentials

To get the Azure credentials, run the following command:

```bash
az ad sp create-for-rbac --name "ai-event-planner-github" --role contributor \
    --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/ai-event-planner-rg \
    --sdk-auth
```

Copy the entire JSON output and paste it as the value for the `AZURE_CREDENTIALS` secret.

## Running the Workflow

To run the workflow:

1. Go to your GitHub repository
2. Navigate to Actions
3. Select the "Deploy to Azure with Docker" workflow
4. Click "Run workflow"

## Advantages of This Approach

Using GitHub Actions for deployment offers several advantages:

1. **No Local Docker Required**: The build happens in GitHub's CI/CD environment, not on your local machine
2. **Consistent Environment**: The build environment is consistent and isolated
3. **Automated Deployment**: The entire deployment process is automated
4. **Version Control**: The deployment configuration is version-controlled
5. **Audit Trail**: All deployments are logged and can be audited

## Monitoring the Deployment

You can monitor the deployment in the GitHub Actions tab of your repository. Once the deployment is complete, the application will be available at:

- Main URL: https://ai-event-planner-saas.azurewebsites.net/
- SaaS Application: https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html

## Troubleshooting

If the deployment fails, you can check the logs in the GitHub Actions tab. You can also check the Azure App Service logs using:

```bash
az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
