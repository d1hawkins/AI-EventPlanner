# Azure Docker Deployment Fixes

This document outlines the fixes implemented to resolve issues with Docker deployment to Azure.

## Issues Fixed

1. **Security Warnings for Sensitive Data in Dockerfile**
   - Removed ARG and ENV instructions for sensitive data (API keys, secrets) from Dockerfile.saas
   - Configured environment variables to be set at runtime via App Service settings instead of build time

2. **Build Context Size Issue**
   - Enhanced .dockerignore file to exclude more unnecessary files
   - Added patterns to exclude deployment-related files, scripts, and documentation
   - Reduced the build context size to improve build performance and reliability

3. **Permission Denied Error**
   - Added LogFiles/ and deployments/ directories to .dockerignore to prevent permission issues during build

## Implementation Details

### 1. Dockerfile.saas Changes
- Removed all ARG instructions for API keys and secrets
- Removed ENV instructions that referenced those ARGs
- Added a comment indicating that API keys will be set at runtime via App Service settings

### 2. .dockerignore Enhancements
- Added LogFiles/ and deployments/ directories to fix the permission denied errors
- Added patterns to exclude more deployment-related files
- Excluded all environment files except .env.example
- Excluded Azure-related documentation and configuration files

### 3. Deployment Script Updates (azure-deploy-docker.sh)
- Added prompts to collect API keys and secrets at deployment time
- Set these values as app settings in Azure App Service
- Made the script executable with `chmod +x`

### 4. GitHub Actions Workflow Updates
- Removed build-args for sensitive data from the Docker build step
- Kept the app settings configuration that sets environment variables at runtime

## Deployment Instructions

1. Run the updated deployment script:
   ```bash
   ./azure-deploy-docker.sh
   ```

2. When prompted, enter your API keys and secrets:
   - OpenAI API Key
   - SendGrid API Key
   - Google API Key
   - Stripe API Key
   - Stripe Webhook Secret

3. The script will:
   - Create/update the Azure Container Registry
   - Build and push the Docker image
   - Create/update the App Service Plan and Web App
   - Configure the Web App with the necessary settings
   - Set your API keys and secrets as app settings

4. Once deployment is complete, your application will be available at:
   - https://ai-event-planner-saas.azurewebsites.net
   - SaaS application: https://ai-event-planner-saas.azurewebsites.net/static/saas/index.html

## Security Best Practices

- API keys and secrets are now set as app settings in Azure App Service, not in the Docker image
- This approach follows security best practices by not embedding sensitive data in container images
- For GitHub Actions deployments, secrets are stored in GitHub Secrets and accessed securely during deployment
