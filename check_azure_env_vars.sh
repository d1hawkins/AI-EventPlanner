#!/bin/bash
# Script to check Azure App Service environment variables

set -e

echo "Checking Azure App Service Environment Variables"
echo "=============================================="

# Azure App Service details
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"

echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo ""

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed or not in PATH"
    echo "Please install Azure CLI to check Azure environment variables"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure CLI"
    echo "Please run 'az login' first"
    exit 1
fi

echo "✅ Azure CLI is available and logged in"
echo ""

# Get all app settings
echo "📋 CURRENT AZURE APP SERVICE ENVIRONMENT VARIABLES:"
echo "=================================================="

# Get app settings and format them nicely
az webapp config appsettings list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --query "[].{Name:name, Value:value}" \
    --output table

echo ""
echo "🔍 CHECKING SPECIFIC LLM-RELATED VARIABLES:"
echo "=========================================="

# Check specific LLM variables
LLM_VARS=("LLM_PROVIDER" "GOOGLE_API_KEY" "GOOGLE_MODEL" "OPENAI_API_KEY" "LLM_MODEL")

for var in "${LLM_VARS[@]}"; do
    value=$(az webapp config appsettings list \
        --resource-group "$RESOURCE_GROUP" \
        --name "$APP_NAME" \
        --query "[?name=='$var'].value" \
        --output tsv 2>/dev/null || echo "")
    
    if [ -n "$value" ]; then
        # Mask API keys for security
        if [[ "$var" == *"API_KEY"* ]]; then
            masked_value="${value:0:20}..."
            echo "✅ $var: $masked_value"
        else
            echo "✅ $var: $value"
        fi
    else
        echo "❌ $var: NOT SET"
    fi
done

echo ""
echo "🔍 CHECKING OTHER IMPORTANT VARIABLES:"
echo "===================================="

OTHER_VARS=("DATABASE_URL" "SECRET_KEY" "ENVIRONMENT" "APPINSIGHTS_INSTRUMENTATIONKEY" "TAVILY_API_KEY")

for var in "${OTHER_VARS[@]}"; do
    value=$(az webapp config appsettings list \
        --resource-group "$RESOURCE_GROUP" \
        --name "$APP_NAME" \
        --query "[?name=='$var'].value" \
        --output tsv 2>/dev/null || echo "")
    
    if [ -n "$value" ]; then
        # Mask sensitive values
        if [[ "$var" == *"KEY"* ]] || [[ "$var" == *"URL"* ]] || [[ "$var" == "SECRET_KEY" ]]; then
            if [ ${#value} -gt 20 ]; then
                masked_value="${value:0:20}..."
            else
                masked_value="SET"
            fi
            echo "✅ $var: $masked_value"
        else
            echo "✅ $var: $value"
        fi
    else
        echo "❌ $var: NOT SET"
    fi
done

echo ""
echo "📊 SUMMARY:"
echo "=========="

# Count total variables
total_vars=$(az webapp config appsettings list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --query "length(@)" \
    --output tsv)

echo "Total environment variables set: $total_vars"

# Check if Google AI is properly configured
google_provider=$(az webapp config appsettings list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --query "[?name=='LLM_PROVIDER'].value" \
    --output tsv 2>/dev/null || echo "")

google_key=$(az webapp config appsettings list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --query "[?name=='GOOGLE_API_KEY'].value" \
    --output tsv 2>/dev/null || echo "")

if [ "$google_provider" = "google" ] && [ -n "$google_key" ]; then
    echo "✅ Google AI configuration appears complete"
    echo "   - LLM_PROVIDER: google"
    echo "   - GOOGLE_API_KEY: SET"
else
    echo "❌ Google AI configuration incomplete"
    if [ "$google_provider" != "google" ]; then
        echo "   - LLM_PROVIDER: $google_provider (should be 'google')"
    fi
    if [ -z "$google_key" ]; then
        echo "   - GOOGLE_API_KEY: NOT SET"
    fi
fi

echo ""
echo "🔗 Azure Portal Links:"
echo "===================="
echo "App Service: https://portal.azure.com/#@/resource/subscriptions/[subscription-id]/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$APP_NAME"
echo "Configuration: https://portal.azure.com/#@/resource/subscriptions/[subscription-id]/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$APP_NAME/configuration"
