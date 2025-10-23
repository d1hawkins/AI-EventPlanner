# Azure Direct Deployment Guide

This guide explains how to deploy your AI Event Planner SaaS application directly to Azure without using GitHub Actions.

## Quick Start

Deploy your application with a single command:

```bash
./scripts/deploy_to_azure.sh
```

That's it! The script handles everything automatically.

## What the Script Does

The deployment script automates the following steps:

1. **Cleans up** previous deployment artifacts
2. **Creates** a deployment package with your application code
3. **Deploys** directly to Azure using the Azure CLI
4. **Cleans up** temporary files
5. **Shows** deployment status and URL

## Prerequisites

Before running the script, ensure you have:

- ✅ Azure CLI installed and configured (`az login`)
- ✅ Proper permissions for the resource group `ai-event-planner-rg`
- ✅ The app service `ai-event-planner-saas-py` is already created

## Script Output

The script provides colored output showing:

- 🟡 Progress through each step
- 🟢 Success confirmations
- 🔵 Deployment details and URL

Example output:
```
╔═══════════════════════════════════════════╗
║  Azure Direct Deployment Script          ║
║  AI Event Planner SaaS                    ║
╚═══════════════════════════════════════════╝

[1/5] Cleaning up previous deployment artifacts...
✓ Cleanup complete

[2/5] Creating deployment package...
✓ Deployment package created: 1.4M

[3/5] Deploying to Azure...
   → Resource Group: ai-event-planner-rg
   → App Name: ai-event-planner-saas-py

✓ Deployment initiated successfully

[4/5] Cleaning up temporary files...
✓ Temporary files removed

[5/5] Checking deployment status...

╔═══════════════════════════════════════════╗
║  Deployment Complete!                     ║
╚═══════════════════════════════════════════╝

  App Status: Running
  App URL: https://ai-event-planner-saas-py.azurewebsites.net
```

## Monitoring Deployment

The build process takes 10-15 minutes. Monitor with:

```bash
az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

## Environment Variables

The script uses the current Azure configuration. Key environment variables:

- **DATABASE_URL**: PostgreSQL connection string (already configured)
- **SECRET_KEY**: Application secret key (already configured)
- **OPENAI_API_KEY**: OpenAI API key (already configured)
- **LLM_PROVIDER**: Set to "openai"
- **LLM_MODEL**: Set to "gpt-4"

All environment variables are pre-configured and don't need to be changed.

## Troubleshooting

### Script fails with "command not found"

Make sure the Azure CLI is installed:
```bash
az --version
```

If not installed, visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

### Permission denied when running script

Make the script executable:
```bash
chmod +x scripts/deploy_to_azure.sh
```

### Azure authentication error

Login to Azure:
```bash
az login
```

### Check deployment status

```bash
az webapp show --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

### View application logs

```bash
# Tail logs in real-time
az webapp log tail --name ai-event-planner-saas-py --resource-group ai-event-planner-rg

# Download logs
az webapp log download --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

## Advantages Over GitHub Actions

- ⚡ **Faster**: Deploy in seconds, not minutes
- 🎯 **Direct**: No waiting for CI/CD pipeline
- 🔍 **Transparent**: See exactly what's being deployed
- 🛠️ **Flexible**: Easy to modify for your needs
- 📦 **Reliable**: No GitHub quota limits

## Configuration

The script uses these default values (can be modified in the script):

```bash
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
DEPLOY_DIR="deploy"
DEPLOY_ZIP="deploy.zip"
```

## Files Included in Deployment

The script deploys these directories and files:

- `app/` - Application code
- `migrations/` - Database migrations
- `scripts/` - Utility scripts
- `alembic.ini` - Alembic configuration
- `requirements.txt` - Python dependencies
- `startup.sh` - Startup script

## Post-Deployment

After deployment completes:

1. **Wait 10-15 minutes** for the build process to complete
2. **Test your application** at: https://ai-event-planner-saas-py.azurewebsites.net
3. **Verify PostgreSQL connection** by checking logs
4. **Test authentication** by logging in or registering

## Additional Commands

### Restart the application
```bash
az webapp restart --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

### Stop the application
```bash
az webapp stop --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

### Start the application
```bash
az webapp start --name ai-event-planner-saas-py --resource-group ai-event-planner-rg
```

---

## Support

For issues or questions about deployment:

1. Check the troubleshooting section above
2. Review Azure logs for detailed error messages
3. Ensure all prerequisites are met

**Application URL**: https://ai-event-planner-saas-py.azurewebsites.net

**Last Updated**: October 2025
