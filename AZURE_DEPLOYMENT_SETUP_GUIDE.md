# Azure Deployment Setup Guide

## 🚨 **CRITICAL: Missing Azure Infrastructure**

Your GitHub Actions deployment is failing because the Azure Web App `ai-event-planner-saas` doesn't exist yet. This guide will help you create all necessary Azure resources.

## 📋 Prerequisites

1. **Azure CLI**: Install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Azure Account**: Active Azure subscription
3. **GitHub Access**: Repository admin permissions for setting secrets

## 🚀 Step 1: Create Azure Resources

Run the automated setup script:

```bash
# Login to Azure first
az login

# Make script executable (if not already)
chmod +x scripts/01_create_azure_resources.sh

# Run the setup script
./scripts/01_create_azure_resources.sh
```

### What This Script Creates:
- **Resource Group**: `ai-event-planner-rg`
- **App Service Plan**: `ai-event-planner-plan` (Linux B1)
- **Web App**: `ai-event-planner-saas` (Python 3.9)
- **PostgreSQL Database**: `ai-event-planner-db-XXXXXX` (Flexible Server)
- **Database**: `aieventplanner`
- **Firewall Rules**: Configured for Azure services
- **Basic Environment Variables**: Set on Web App

### Important Output:
The script will display database credentials - **SAVE THESE!**

```
🔑 Database Credentials (SAVE THESE!):
  Username: dbadmin
  Password: [generated-password]
  Connection String: postgresql://...
```

## 🔧 Step 2: Configure GitHub Secrets

Add these secrets to your GitHub repository (`Settings` > `Secrets and variables` > `Actions`):

### Required Secrets:

1. **AZURE_CREDENTIALS**
   ```bash
   # Get credentials for GitHub Actions
   az ad sp create-for-rbac --name "github-actions-ai-event-planner" \
     --role contributor \
     --scopes /subscriptions/$(az account show --query id -o tsv) \
     --sdk-auth
   ```
   Copy the entire JSON output to GitHub secret `AZURE_CREDENTIALS`

2. **DATABASE_URL**
   Use the connection string from Step 1 output

3. **SECRET_KEY**
   ```bash
   openssl rand -base64 32
   ```

4. **OPENAI_API_KEY** (Optional)
   Your OpenAI API key for AI features

5. **GOOGLE_API_KEY** (Optional)
   Your Google API key for AI features

6. **TAVILY_API_KEY** (Optional)
   Your Tavily API key for search functionality

## 🔐 Step 3: Set Additional Environment Variables

Set any additional environment variables directly on the Azure Web App:

```bash
# Example: Set OpenAI API Key
az webapp config appsettings set \
  --name ai-event-planner-saas \
  --resource-group ai-event-planner-rg \
  --settings OPENAI_API_KEY="your-key-here"

# Example: Set Google API Key
az webapp config appsettings set \
  --name ai-event-planner-saas \
  --resource-group ai-event-planner-rg \
  --settings GOOGLE_API_KEY="your-key-here"
```

## 🚀 Step 4: Deploy Application

After completing Steps 1-3, your GitHub Actions workflow should work:

1. **Push to main branch** or **manually trigger workflow**
2. **Monitor deployment** in GitHub Actions tab
3. **Access application** at: `https://ai-event-planner-saas.azurewebsites.net`

## 🛠️ Troubleshooting

### If deployment still fails:

1. **Check Resource Names**: Ensure GitHub workflow uses correct names:
   - App Name: `ai-event-planner-saas`
   - Resource Group: `ai-event-planner-rg`

2. **Verify GitHub Secrets**: All required secrets are set correctly

3. **Check Azure Logs**:
   ```bash
   az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
   ```

4. **Manual Deployment Test**:
   ```bash
   # Test if resource exists
   az webapp show --name ai-event-planner-saas --resource-group ai-event-planner-rg
   ```

### Common Issues:

- **"Resource doesn't exist"**: Run Step 1 setup script
- **"Authentication failed"**: Check AZURE_CREDENTIALS secret
- **"Database connection failed"**: Verify DATABASE_URL secret
- **"Application errors"**: Check missing environment variables

## 📊 Resource Costs

**Estimated monthly cost** (B1 tier):
- **App Service Plan (B1)**: ~$13/month
- **PostgreSQL Flexible Server (Standard_B1ms)**: ~$12/month
- **Total**: ~$25/month

**Cost optimization**:
- Use **F1 (Free)** tier for development: $0/month (limited resources)
- Scale up to **S1** or higher for production with more traffic

## 🔄 Updating Resources

To modify resources later:

```bash
# Scale up App Service Plan
az appservice plan update \
  --name ai-event-planner-plan \
  --resource-group ai-event-planner-rg \
  --sku S1

# Add custom domain (optional)
az webapp config hostname add \
  --webapp-name ai-event-planner-saas \
  --resource-group ai-event-planner-rg \
  --hostname yourdomain.com
```

## ✅ Verification Checklist

- [ ] Azure CLI installed and logged in
- [ ] Setup script completed successfully
- [ ] Database credentials saved
- [ ] GitHub secrets configured
- [ ] Additional environment variables set
- [ ] GitHub Actions workflow triggered
- [ ] Application accessible at Azure URL

## 🆘 Need Help?

1. **Check Azure Portal**: Verify resources exist at portal.azure.com
2. **Review GitHub Actions logs**: Look for specific error messages
3. **Check application logs**: Use Azure Log Stream
4. **Database connectivity**: Test connection string manually

---

**Next Step**: Run `./scripts/01_create_azure_resources.sh` to create your Azure infrastructure!
