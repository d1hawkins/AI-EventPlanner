# Azure Deployment with Secrets Management

This document outlines the approach for securely deploying the AI Event Planner SaaS application to Azure while properly managing sensitive information.

## Overview

The deployment solution addresses the critical issue of keeping secrets out of the Git repository while still making them available during deployment. This is achieved through:

1. Template files for configuration
2. Environment variables for runtime
3. GitHub Secrets for CI/CD
4. Docker build arguments for container builds

## Components

### Template Files

Template files provide a structure for configuration without including actual secrets:

- `AZURE_CREDENTIALS.template.json` - Template for Azure service principal credentials
- `.env.saas.template` - Template for SaaS environment variables
- `.env.backup.template` - Template for backup environment variables

Developers copy these templates and add their own secrets locally, but only the templates are committed to the repository.

### .gitignore Configuration

The `.gitignore` file is configured to:

```
# Sensitive files with credentials
AZURE_CREDENTIALS.json
azure-credentials.json
.env.saas
.env.backup*

# Keep templates
!AZURE_CREDENTIALS.template.json
!.env.saas.template
!.env.backup.template
```

This ensures that files with actual secrets are not committed, while template files are included in the repository.

### Docker Configuration

The `Dockerfile.saas` has been updated to accept build arguments for secrets:

```dockerfile
# Build arguments for secrets
ARG OPENAI_API_KEY
ARG SENDGRID_API_KEY
ARG GOOGLE_API_KEY
ARG STRIPE_API_KEY
ARG STRIPE_WEBHOOK_SECRET

# Set environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV SENDGRID_API_KEY=${SENDGRID_API_KEY}
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV STRIPE_API_KEY=${STRIPE_API_KEY}
ENV STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
```

This allows secrets to be passed at build time and set as environment variables in the container.

### GitHub Actions Workflow

The GitHub Actions workflow (`.github/workflows/azure-deploy-docker.yml`) has been updated to:

1. Pass secrets as build arguments when building the Docker image:

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v2
  with:
    context: .
    file: ./Dockerfile.saas
    push: true
    tags: aieventplannerregistry.azurecr.io/ai-event-planner-saas:latest
    build-args: |
      OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
      SENDGRID_API_KEY=${{ secrets.SENDGRID_API_KEY }}
      GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }}
      STRIPE_API_KEY=${{ secrets.STRIPE_API_KEY }}
      STRIPE_WEBHOOK_SECRET=${{ secrets.STRIPE_WEBHOOK_SECRET }}
```

2. Set environment variables in the Azure Web App configuration:

```yaml
- name: Configure Web App
  run: |
    az webapp config appsettings set --resource-group ai-event-planner-rg --name ai-event-planner-saas --settings \
      WEBSITES_PORT=8000 \
      DOCKER_REGISTRY_SERVER_URL=https://aieventplannerregistry.azurecr.io \
      DOCKER_REGISTRY_SERVER_USERNAME=${{ steps.acr-creds.outputs.username }} \
      DOCKER_REGISTRY_SERVER_PASSWORD=${{ steps.acr-creds.outputs.password }} \
      OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }} \
      SENDGRID_API_KEY=${{ secrets.SENDGRID_API_KEY }} \
      GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }} \
      STRIPE_API_KEY=${{ secrets.STRIPE_API_KEY }} \
      STRIPE_WEBHOOK_SECRET=${{ secrets.STRIPE_WEBHOOK_SECRET }}
```

## Setup Instructions

### Local Development

1. Copy template files to create your configuration:
   ```bash
   cp AZURE_CREDENTIALS.template.json AZURE_CREDENTIALS.json
   cp .env.saas.template .env.saas
   cp .env.backup.template .env.backup
   ```

2. Edit these files to add your actual credentials

3. Use these files for local development and testing

### GitHub Repository Setup

Add the following secrets to your GitHub repository:

- `AZURE_CREDENTIALS`: The entire JSON content from your AZURE_CREDENTIALS.json file
- `OPENAI_API_KEY`: Your OpenAI API key
- `SENDGRID_API_KEY`: Your SendGrid API key
- `GOOGLE_API_KEY`: Your Google API key
- `STRIPE_API_KEY`: Your Stripe API key
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret

### Deployment

1. Push changes to the main branch to trigger the CI/CD pipeline
2. The GitHub Actions workflow will:
   - Build and test the application
   - Build and push the Docker image to Azure Container Registry with secrets as build arguments
   - Deploy the image to Azure App Service
   - Configure the Web App with environment variables

## Security Considerations

- Never commit files containing actual secrets to the repository
- Regularly rotate secrets and update them in GitHub Secrets
- Consider using Azure Key Vault for more sensitive production environments
- Review GitHub Actions logs to ensure secrets are not being logged

## Conclusion

This approach ensures sensitive information is kept out of your Git repository while still being available during deployment. It provides a secure and maintainable way to manage secrets for the AI Event Planner SaaS application.
