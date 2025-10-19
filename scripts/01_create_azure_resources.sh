#!/bin/bash

# Azure Infrastructure Setup Script for AI Event Planner SaaS
# This script creates all necessary Azure resources for deployment

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="East US"
APP_SERVICE_PLAN="ai-event-planner-plan"
WEB_APP_NAME="ai-event-planner-saas"
SKU="B1"  # Basic tier - can be upgraded later

echo "🚀 Setting up Azure Infrastructure for AI Event Planner SaaS"
echo "============================================================"

# Check if Azure CLI is logged in
echo "📋 Checking Azure CLI authentication..."
if ! az account show &>/dev/null; then
    echo "❌ Not logged into Azure CLI. Please run: az login"
    exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅ Logged into Azure (Subscription: $SUBSCRIPTION_ID)"

# Create Resource Group
echo ""
echo "📦 Creating Resource Group: $RESOURCE_GROUP"
if az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Resource Group '$RESOURCE_GROUP' already exists"
else
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    echo "✅ Created Resource Group '$RESOURCE_GROUP' in $LOCATION"
fi

# Create App Service Plan
echo ""
echo "🏗️  Creating App Service Plan: $APP_SERVICE_PLAN"
if az appservice plan show --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "✅ App Service Plan '$APP_SERVICE_PLAN' already exists"
else
    az appservice plan create \
        --name "$APP_SERVICE_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku "$SKU" \
        --is-linux
    echo "✅ Created App Service Plan '$APP_SERVICE_PLAN' (Linux, $SKU)"
fi

# Create Web App
echo ""
echo "🌐 Creating Web App: $WEB_APP_NAME"
if az webapp show --name "$WEB_APP_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Web App '$WEB_APP_NAME' already exists"
else
    az webapp create \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "PYTHON:3.9" \
        --startup-file "gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
    echo "✅ Created Web App '$WEB_APP_NAME' with Python 3.9 runtime"
fi

# Configure Web App Settings
echo ""
echo "⚙️  Configuring Web App Settings..."

# Set Python version and startup command
az webapp config set \
    --name "$WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "gunicorn app.main_saas:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"

# Enable application logging
az webapp log config \
    --name "$WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --application-logging filesystem \
    --level information

# Set up CORS (if needed)
az webapp cors add \
    --name "$WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --allowed-origins "*"

echo "✅ Configured Web App settings"

# Get Web App URL
WEB_APP_URL=$(az webapp show --name "$WEB_APP_NAME" --resource-group "$RESOURCE_GROUP" --query defaultHostName -o tsv)

# Create PostgreSQL Database (Flexible Server)
DB_SERVER_NAME="ai-event-planner-db-$(date +%s | tail -c 6)"
DB_NAME="aieventplanner"
DB_USERNAME="dbadmin"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

echo ""
echo "🗄️  Creating PostgreSQL Database..."
echo "Database Server: $DB_SERVER_NAME"
echo "Database Name: $DB_NAME"
echo "Username: $DB_USERNAME"
echo "Password: $DB_PASSWORD"

# Create PostgreSQL Flexible Server
az postgres flexible-server create \
    --name "$DB_SERVER_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --admin-user "$DB_USERNAME" \
    --admin-password "$DB_PASSWORD" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 13 \
    --public-access All

# Create database
az postgres flexible-server db create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$DB_SERVER_NAME" \
    --database-name "$DB_NAME"

echo "✅ Created PostgreSQL Database"

# Configure firewall rules for Azure services
az postgres flexible-server firewall-rule create \
    --name "$DB_SERVER_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --rule-name "AllowAzureServices" \
    --start-ip-address "0.0.0.0" \
    --end-ip-address "0.0.0.0"

echo "✅ Configured database firewall rules"

# Set Web App environment variables
echo ""
echo "🔧 Setting Web App Environment Variables..."

DATABASE_URL="postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_SERVER_NAME.postgres.database.azure.com:5432/$DB_NAME?sslmode=require"

az webapp config appsettings set \
    --name "$WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
    DATABASE_URL="$DATABASE_URL" \
    SECRET_KEY="$(openssl rand -base64 32)" \
    ENVIRONMENT="production" \
    PYTHONPATH="/home/site/wwwroot"

echo "✅ Set basic environment variables"

echo ""
echo "🎉 Azure Infrastructure Setup Complete!"
echo "========================================"
echo ""
echo "📋 Summary:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  App Service Plan: $APP_SERVICE_PLAN"
echo "  Web App: $WEB_APP_NAME"
echo "  Web App URL: https://$WEB_APP_URL"
echo "  Database Server: $DB_SERVER_NAME"
echo "  Database Name: $DB_NAME"
echo ""
echo "🔑 Database Credentials (SAVE THESE!):"
echo "  Username: $DB_USERNAME"
echo "  Password: $DB_PASSWORD"
echo "  Connection String: $DATABASE_URL"
echo ""
echo "⚠️  IMPORTANT: Save the database credentials above!"
echo ""
echo "🚀 Next Steps:"
echo "  1. Update GitHub Secrets with database credentials"
echo "  2. Set additional environment variables (OPENAI_API_KEY, etc.)"
echo "  3. Run deployment workflow"
echo ""
echo "💡 To set additional secrets, use:"
echo "   az webapp config appsettings set --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --settings KEY=VALUE"
