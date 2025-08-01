# Azure Deployment Guide for AI Event Planner

This guide provides detailed instructions for deploying the AI Event Planner application to Azure App Service and troubleshooting common issues.

## Prerequisites

- Azure CLI installed and configured
- Azure subscription
- Git repository cloned locally

## Deployment Steps

### 1. Fix Application Code

Before deployment, ensure the application code is free of syntax errors:

- Check `app_simplified.py` for syntax errors
- Ensure the startup script has the correct shebang line
- Use the simplified requirements file for faster deployment

### 2. Deploy to Azure

Use the provided deployment script to deploy the application to Azure:

```bash
./azure-deploy-saas-python-no-docker-v2.sh
```

This script will:
- Create a resource group if it doesn't exist
- Create an App Service Plan if it doesn't exist
- Create a Web App if it doesn't exist
- Package and deploy the application
- Configure the startup command
- Enable logging

### 3. Verify Deployment

After deployment, verify that the application is running correctly:

```bash
# Check the status of the web app
az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --query state

# Open the website in a browser
open https://ai-event-planner-saas-py.azurewebsites.net
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Fails to Start

If the application fails to start within the timeout period (10 minutes), check the following:

- **Syntax Errors**: Ensure there are no syntax errors in your Python code.
  - Fix: Review and correct any syntax errors in `app_simplified.py`.

- **Missing Dependencies**: Ensure all required dependencies are included in the requirements file.
  - Fix: Update `requirements_simplified.txt` to include all necessary packages.

- **Startup Script Issues**: Ensure the startup script is correctly configured.
  - Fix: Check that `startup.sh` has the correct shebang line and permissions.

#### 2. Viewing Logs

To view logs for troubleshooting:

```bash
# View application logs
az webapp log download --name ai-event-planner-saas-py --resource-group ai-event-planner-rg

# Stream logs in real-time
az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

#### 3. Environment Variables

If your application requires environment variables:

```bash
# Set environment variables
az webapp config appsettings set --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --settings KEY=VALUE
```

#### 4. Restarting the Application

If you need to restart the application:

```bash
# Restart the web app
az webapp restart --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

## Debugging Azure Deployment

### 1. Check Application Logs

Azure App Service stores logs that can help diagnose issues:

```bash
# Download logs
az webapp log download --name ai-event-planner-saas-py --resource-group ai-event-planner-rg --log-file app_logs.zip
```

### 2. Check Deployment Status

```bash
# Check deployment status
az webapp deployment list --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

### 3. SSH into the App Service

For more advanced debugging:

```bash
# Enable SSH
az webapp ssh --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

### 4. Check Resource Utilization

If the application is slow or unresponsive:

```bash
# Check CPU and memory usage
az monitor metrics list --resource-id /subscriptions/{subscription-id}/resourceGroups/ai-event-planner-rg/providers/Microsoft.Web/sites/ai-event-planner-saas-py --metric "CpuPercentage" "MemoryPercentage"
```

## Best Practices for Azure Deployment

1. **Use Simplified Dependencies**: Only include necessary dependencies to reduce deployment time and potential issues.

2. **Enable Detailed Logging**: Always enable detailed logging to help diagnose issues.

3. **Use Application Insights**: Consider adding Application Insights for better monitoring and diagnostics.

4. **Test Locally First**: Always test your application locally before deploying to Azure.

5. **Use Deployment Slots**: For production applications, use deployment slots for zero-downtime deployments.

## Understanding Azure App Service Containerization

Even when using a "non-Docker" deployment, Azure App Service for Linux still uses containerization technology behind the scenes:

1. **Managed Containers**: Azure App Service for Linux uses Docker containers internally to run applications, even when you're not explicitly using Docker in your deployment process.

2. **Log Paths**: This is why error messages may reference Docker logs (e.g., `/api/logs/docker`), as that's where Azure stores the runtime logs for all Linux App Service applications.

3. **Deployment Process**: When you deploy without a custom Docker image, Azure builds and manages the container for you using its default Python container image.

## Conclusion

By following this guide, you should be able to successfully deploy the AI Event Planner application to Azure App Service and troubleshoot any issues that arise. If you encounter persistent issues, consider simplifying your application further or reaching out to Azure support.
