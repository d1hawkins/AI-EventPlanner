# AI Event Planner: Local Testing and Azure Deployment Guide

I've successfully tested the AI Event Planner application locally and explored the Azure deployment options. Here's a comprehensive guide for both local testing and Azure deployment:

## Local Testing Options

You have three options for running the application locally:

### 1. Static Frontend Only (Simplest)
```bash
python serve_saas_static.py
```
- **What it does**: Serves only the static frontend files on port 8090
- **Pros**: No database or environment setup needed, quick to start
- **Cons**: No backend functionality (API calls will fail)
- **Best for**: UI/UX testing, frontend development

### 2. Full Application with Python
```bash
python run_saas.py
```
- **What it does**: Runs the complete application directly on your machine
- **Requirements**: 
  - PostgreSQL database
  - Environment variables in `.env` file (copy from `.env.saas.example`)
- **Pros**: Full functionality, easier debugging
- **Cons**: Requires database setup and environment configuration
- **Best for**: Complete testing of all features

### 3. Full Application with Docker
```bash
chmod +x run_saas_docker.sh
./run_saas_docker.sh
```
- **What it does**: Builds and runs the application in a Docker container
- **Requirements**:
  - Docker installed
  - Environment variables in `.env` file
- **Pros**: Closest to production environment, isolates dependencies
- **Cons**: Requires Docker, slower to build initially
- **Best for**: Final testing before deployment to Azure

## Azure Deployment Options

For deploying to Azure, you have the following options:

### 1. GitHub Actions with Docker (Recommended)
- **Key Files**: 
  - GitHub workflow: `.github/workflows/azure-deploy-docker.yml`
  - Docker configuration: `Dockerfile.saas`
  - Secrets management: `AZURE_CREDENTIALS.template.json`, `.env.saas.template`

- **Setup**:
  1. Add Azure credentials to GitHub repository secrets
  2. Add API keys (OpenAI, SendGrid, Google, Stripe) to GitHub secrets
  3. Trigger the workflow from GitHub Actions tab

- **Advantages**:
  - Fully automated CI/CD pipeline
  - No need for Docker on your local machine
  - Consistent environment between development and production
  - Secure secrets management
  - Runs database migrations automatically

### 2. Local Docker Deployment
- **Key File**: `azure-deploy-docker.sh`

- **Process**:
  1. Build Docker image locally
  2. Push to Azure Container Registry
  3. Deploy to Azure App Service

- **Advantages**:
  - More direct control over the deployment process
  - Can be run from your local machine
  - Useful for testing deployment before setting up GitHub Actions

### 3. Static HTML Deployment
- **Key File**: `azure-deploy-html-fixed.sh`

- **Process**:
  1. Creates a simple static website
  2. Deploys to Azure App Service

- **Advantages**:
  - Simplest deployment option
  - No Docker required
  - Quick to deploy
  - Useful as a temporary solution

## Recommendation

For local testing, start with the static frontend option to quickly test the UI, then move to the Docker option for a more complete test that closely matches the production environment.

For Azure deployment, the GitHub Actions approach is recommended as it provides a fully automated CI/CD pipeline with proper secrets management and consistent deployments.

## Next Steps

1. Test the application locally using one of the methods above
2. Set up your Azure resources (App Service, Container Registry)
3. Configure your GitHub repository with the necessary secrets
4. Deploy to Azure using the GitHub Actions workflow
