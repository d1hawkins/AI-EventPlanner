# Azure Docker Deployment with .env.saas Integration

This guide explains how to deploy the AI Event Planner SaaS application to Azure as a Docker container while reading secrets and keys from the `.env.saas` file.

## Overview

The deployment process has been updated to automatically read environment variables, API keys, and secrets from the `.env.saas` file instead of requiring manual input or GitHub Secrets. This approach:

1. Improves security by keeping secrets out of the codebase
2. Simplifies deployment by automating the process
3. Ensures consistency between local development and production environments
4. Makes it easier to manage and update secrets

## Components

### 1. Dockerfile.saas

The Dockerfile has been updated to accept build arguments for all environment variables defined in `.env.saas`. These build arguments are then set as environment variables in the container, making them available to the application at runtime.

```dockerfile
# Build arguments for secrets
ARG OPENAI_API_KEY
ARG SENDGRID_API_KEY
# ... other arguments

# Set environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV SENDGRID_API_KEY=${SENDGRID_API_KEY}
# ... other environment variables
```

### 2. azure-deploy-docker.sh

This script has been updated to:
- Check if the `.env.saas` file exists
- Read each environment variable from the file
- Pass them as build arguments to Docker
- Set them as app settings in the Azure Web App

```bash
# Load environment variables from .env.saas
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue
    
    # Extract key and value
    key=$(echo "$line" | cut -d= -f1)
    value=$(echo "$line" | cut -d= -f2-)
    
    # Add to build args array
    BUILD_ARGS+=("--build-arg $key=\"$value\"")
    
    # Add to app settings array
    APP_SETTINGS+=("$key=\"$value\"")
done < "$ENV_FILE"
```

### 3. GitHub Actions Workflow

The GitHub Actions workflow (`.github/workflows/azure-deploy-docker.yml`) has been updated to:
- Read environment variables from `.env.saas` instead of GitHub Secrets
- Pass them as build arguments to Docker
- Set them as app settings in the Azure Web App

## Deployment Instructions

### Local Deployment

1. Ensure you have the `.env.saas` file in the project root with all required environment variables:
   ```
   # Application Settings
   APP_NAME=AI Event Planner SaaS
   APP_VERSION=1.0.0
   # ... other environment variables
   ```

2. Make sure you have the Azure CLI installed and are logged in:
   ```bash
   az login
   ```

3. Run the deployment script:
   ```bash
   ./azure-deploy-docker.sh
   ```

4. The script will:
   - Read environment variables from `.env.saas`
   - Build and push the Docker image to Azure Container Registry
   - Create or update the App Service Plan and Web App
   - Configure the Web App with the environment variables
   - Restart the Web App

### GitHub Actions Deployment

1. Ensure you have the `.env.saas` file in the project root with all required environment variables.

2. Make sure you have set up the `AZURE_CREDENTIALS` secret in your GitHub repository:
   - Create a service principal in Azure
   - Add the JSON output as a secret named `AZURE_CREDENTIALS` in your GitHub repository

3. Trigger the workflow manually from the GitHub Actions tab.

4. The workflow will:
   - Read environment variables from `.env.saas`
   - Build and push the Docker image to Azure Container Registry
   - Create or update the App Service Plan and Web App
   - Configure the Web App with the environment variables
   - Restart the Web App

## Security Considerations

1. **Keep `.env.saas` secure**: Do not commit this file to your repository. It's already added to `.gitignore`.

2. **Rotate secrets regularly**: Update your API keys and secrets periodically for better security.

3. **Consider Azure Key Vault**: For production environments, consider using Azure Key Vault to store and manage your secrets.

4. **Review logs**: Make sure sensitive information is not being logged during the deployment process.

## Troubleshooting

1. **Missing `.env.saas` file**: If you get an error about a missing `.env.saas` file, make sure it exists in the project root. You can copy `.env.saas.template` and fill in your actual values.

2. **Docker build errors**: If you encounter errors during the Docker build, check that all required environment variables are defined in `.env.saas`.

3. **Azure deployment errors**: If the deployment to Azure fails, check the Azure CLI output for specific error messages. You may need to adjust resource names or create the resource group manually.

4. **Application errors**: If the application doesn't work correctly after deployment, check the Azure App Service logs to identify any issues related to environment variables or configuration.

## Conclusion

This updated deployment process simplifies the deployment of the AI Event Planner SaaS application to Azure while maintaining security best practices. By reading secrets and keys from the `.env.saas` file, you can ensure consistency between your development and production environments and avoid the need for manual input during deployment.
