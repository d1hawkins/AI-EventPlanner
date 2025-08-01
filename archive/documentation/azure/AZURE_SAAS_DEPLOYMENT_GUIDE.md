# Azure SaaS Deployment Guide - Complete Authentication Fix

## 🎯 Overview

This guide provides step-by-step instructions to deploy the AI Event Planner SaaS application to Azure with **fully functional authentication**. The authentication system has been fixed to use real API calls instead of mock authentication.

## ✅ What's Fixed

### Authentication System
- **Frontend**: Real API calls to `/auth/register` and `/auth/token` endpoints
- **Backend**: Proper JWT token generation and validation
- **Database**: User registration with bcrypt password hashing
- **Session Management**: Secure token-based authentication

### Key Improvements
1. **Real Registration**: Users can actually register accounts
2. **Real Login**: Authentication uses actual backend validation
3. **Secure Passwords**: Bcrypt hashing for password storage
4. **JWT Tokens**: Proper token generation and validation
5. **Database Integration**: Real user data storage

## 🚀 Quick Deployment

### Prerequisites
1. Azure CLI installed and configured
2. Azure subscription with appropriate permissions
3. Git repository initialized

### One-Command Deployment
```bash
./azure-deploy-saas-with-auth-fix.sh
```

This script will:
- Create Azure resources (App Service, Database)
- Configure environment variables
- Deploy the application with authentication
- Set up logging and monitoring

## 📋 Manual Deployment Steps

### 1. Azure Login
```bash
az login
az account set --subscription "your-subscription-id"
```

### 2. Create Resource Group
```bash
az group create --name ai-event-planner-rg --location "East US"
```

### 3. Create App Service Plan
```bash
az appservice plan create \
    --name ai-event-planner-saas-py-plan \
    --resource-group ai-event-planner-rg \
    --sku B1 \
    --is-linux
```

### 4. Create Web App
```bash
az webapp create \
    --resource-group ai-event-planner-rg \
    --plan ai-event-planner-saas-py-plan \
    --name ai-event-planner-saas-py \
    --runtime "PYTHON|3.11"
```

### 5. Configure Environment Variables
```bash
az webapp config appsettings set \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py \
    --settings \
        PYTHONPATH="/home/site/wwwroot" \
        PYTHONUNBUFFERED="1" \
        DATABASE_URL="your-database-url" \
        SECRET_KEY="your-secret-key" \
        LLM_PROVIDER="openai" \
        OPENAI_API_KEY="your-openai-key"
```

### 6. Deploy Code
```bash
az webapp deployment source config-local-git \
    --name ai-event-planner-saas-py \
    --resource-group ai-event-planner-rg

git remote add azure [deployment-url]
git push azure main
```

## 🔧 Configuration Details

### Environment Variables

#### Required Variables
```bash
PYTHONPATH="/home/site/wwwroot"
PYTHONUNBUFFERED="1"
DATABASE_URL="postgresql://user:pass@host:5432/db"
SECRET_KEY="your-super-secret-key"
```

#### Authentication Variables
```bash
ACCESS_TOKEN_EXPIRE_MINUTES="30"
ENVIRONMENT="production"
DEBUG="false"
```

#### LLM Provider Variables
```bash
LLM_PROVIDER="openai"
OPENAI_API_KEY="your-openai-api-key"
GOOGLE_API_KEY="your-google-api-key"  # Optional fallback
```

### Database Configuration

#### Azure PostgreSQL
```bash
# Create PostgreSQL server
az postgres server create \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-db \
    --admin-user ai_event_admin \
    --admin-password "SecurePassword123!" \
    --sku-name B_Gen5_1

# Create database
az postgres db create \
    --resource-group ai-event-planner-rg \
    --server-name ai-event-planner-db \
    --name ai_event_planner_db
```

## 🧪 Testing the Deployment

### 1. Access the Application
```
https://ai-event-planner-saas-py.azurewebsites.net
```

### 2. Test Authentication Flow

#### Registration Test
1. Go to: `https://your-app.azurewebsites.net/saas/signup.html`
2. Fill out the registration form
3. Verify success message and redirect to login

#### Login Test
1. Go to: `https://your-app.azurewebsites.net/saas/login.html`
2. Use the credentials you just registered
3. Verify successful login and redirect to dashboard

#### Dashboard Access
1. After login, access: `https://your-app.azurewebsites.net/saas/dashboard.html`
2. Verify authenticated user interface
3. Test agent functionality

### 3. Verify Backend Endpoints

#### Health Check
```bash
curl https://your-app.azurewebsites.net/health
```
Expected response:
```json
{
  "status": "healthy",
  "real_agents_available": true,
  "environment": "production"
}
```

#### Authentication Endpoints
```bash
# Test registration
curl -X POST https://your-app.azurewebsites.net/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass"}'

# Test login
curl -X POST https://your-app.azurewebsites.net/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Authentication Not Working
**Symptoms**: Login fails, registration doesn't work
**Solution**: Check environment variables
```bash
az webapp config appsettings list \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py
```

#### 2. Database Connection Issues
**Symptoms**: 500 errors, database connection failures
**Solution**: Verify DATABASE_URL and firewall rules
```bash
# Check PostgreSQL firewall
az postgres server firewall-rule create \
    --resource-group ai-event-planner-rg \
    --server ai-event-planner-db \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

#### 3. Agent Functionality Issues
**Symptoms**: Agents return "not implemented" or errors
**Solution**: Check LLM provider configuration
```bash
# Set OpenAI API key
az webapp config appsettings set \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py \
    --settings OPENAI_API_KEY="your-actual-openai-key"
```

### Viewing Logs
```bash
# Stream live logs
az webapp log tail \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py

# Download log files
az webapp log download \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py
```

## 🔐 Security Considerations

### Production Security Checklist

#### 1. Environment Variables
- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Set proper CORS_ORIGINS
- [ ] Configure DEBUG=false

#### 2. Database Security
- [ ] Enable SSL connections
- [ ] Configure firewall rules
- [ ] Use strong authentication
- [ ] Regular backups

#### 3. Application Security
- [ ] HTTPS only (Azure handles this)
- [ ] Secure headers configured
- [ ] Input validation enabled
- [ ] Rate limiting configured

### Recommended Production Settings
```bash
az webapp config appsettings set \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py \
    --settings \
        SECRET_KEY="$(openssl rand -base64 32)" \
        DEBUG="false" \
        ENVIRONMENT="production" \
        CORS_ORIGINS="https://ai-event-planner-saas-py.azurewebsites.net"
```

## 📊 Monitoring and Analytics

### Azure Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
    --app ai-event-planner-insights \
    --location "East US" \
    --resource-group ai-event-planner-rg

# Get instrumentation key
az monitor app-insights component show \
    --app ai-event-planner-insights \
    --resource-group ai-event-planner-rg \
    --query instrumentationKey
```

### Configure Application Insights
```bash
az webapp config appsettings set \
    --resource-group ai-event-planner-rg \
    --name ai-event-planner-saas-py \
    --settings \
        APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

## 🎯 Success Metrics

### Technical Metrics
- ✅ HTTP 200 responses from all endpoints
- ✅ Successful user registration and login
- ✅ Database connections working
- ✅ Agent endpoints returning real responses
- ✅ No import errors in logs

### User Experience Metrics
- ✅ Registration flow completes successfully
- ✅ Login redirects to dashboard
- ✅ Agent chat interface responds to messages
- ✅ Conversation history persists
- ✅ All SaaS pages load quickly (<3 seconds)

## 🔄 Continuous Deployment

### GitHub Actions (Optional)
Create `.github/workflows/azure-deploy.yml`:
```yaml
name: Deploy to Azure
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: ai-event-planner-saas-py
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## 📞 Support

### Getting Help
1. **Azure Documentation**: [Azure App Service Python](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
2. **Application Logs**: Use `az webapp log tail` for real-time debugging
3. **Azure Portal**: Monitor metrics and performance
4. **GitHub Issues**: Report bugs and feature requests

### Common Commands
```bash
# Restart the application
az webapp restart --resource-group ai-event-planner-rg --name ai-event-planner-saas-py

# Scale the application
az appservice plan update --resource-group ai-event-planner-rg --name ai-event-planner-saas-py-plan --sku S1

# Update environment variables
az webapp config appsettings set --resource-group ai-event-planner-rg --name ai-event-planner-saas-py --settings KEY=VALUE
```

---

## 🎉 Conclusion

The AI Event Planner SaaS application is now ready for Azure deployment with fully functional authentication. The system provides:

- **Real user registration and login**
- **Secure password handling with bcrypt**
- **JWT-based session management**
- **Database-backed user storage**
- **Production-ready configuration**

Follow this guide to deploy a fully functional SaaS application with working authentication to Azure.
