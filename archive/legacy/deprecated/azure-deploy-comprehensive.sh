#!/bin/bash
# Deploy the full AI Event Planner SaaS application with agents to Azure App Service (Python) without Docker

set -e

# --- Configuration ---
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
PYTHON_VERSION="3.9"
APP_SERVICE_PLAN_SKU="B1" # Basic tier, adjust as needed
DB_SERVER_NAME="ai-event-planner-db" # -$(openssl rand -hex 4)" # Unique DB server name
DB_NAME="eventplanner_db"
DB_ADMIN_USER="dbadmin"
# DB_ADMIN_PASSWORD will be prompted for securely
POSTGRES_VERSION="11"
POSTGRES_SKU="GP_Gen5_2" # General Purpose, Gen 5, 2 vCores

# --- Colors for Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Helper Functions ---
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: Command '$1' not found. Please install it.${NC}"
        exit 1
    fi
}

prompt_for_secret() {
    local prompt_message=$1
    local env_var_name=$2
    local secret_value=""
    while [ -z "$secret_value" ]; do
        read -sp "$prompt_message" secret_value
        echo
        if [ -z "$secret_value" ]; then
            echo -e "${YELLOW}Input cannot be empty. Please try again.${NC}"
        fi
    done
    # Add the secret to app settings command
    APP_SETTINGS_CMD+=" ${env_var_name}=${secret_value}"
}

# --- Pre-checks ---
echo -e "${BLUE}--- Running Pre-checks ---${NC}"
check_command "az"
check_command "zip"
check_command "openssl" # For generating unique names/passwords if needed

# --- Azure Login ---
echo -e "${BLUE}--- Checking Azure Login Status ---${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Azure. Please login.${NC}"
    az login
else
    echo -e "${GREEN}Already logged in to Azure.${NC}"
    az account show --query "{name:name, environmentName:environmentName, tenantId:tenantId}" -o table
fi

# --- Resource Group ---
echo -e "${BLUE}--- Ensuring Resource Group '$RESOURCE_GROUP' Exists ---${NC}"
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}Resource group '$RESOURCE_GROUP' already exists in location $(az group show --name $RESOURCE_GROUP --query location -o tsv).${NC}"
else
    echo "Creating resource group '$RESOURCE_GROUP' in '$LOCATION'..."
    az group create --name $RESOURCE_GROUP --location $LOCATION --output table
    echo -e "${GREEN}Resource group '$RESOURCE_GROUP' created.${NC}"
fi

# --- PostgreSQL Database ---
echo -e "${BLUE}--- Ensuring PostgreSQL Database Exists ---${NC}"

# Prompt for DB Admin Password securely
prompt_for_secret "Enter desired PostgreSQL Admin Password: " DB_ADMIN_PASSWORD_SECRET
DB_ADMIN_PASSWORD=$secret_value # Assign to variable for connection string

# Check if PostgreSQL server exists
echo "Checking for PostgreSQL server '$DB_SERVER_NAME'..."
if az postgres server show --name $DB_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}PostgreSQL server '$DB_SERVER_NAME' already exists.${NC}"
else
    echo "Creating PostgreSQL server '$DB_SERVER_NAME' (this may take a few minutes)..."
    az postgres server create \
        --name $DB_SERVER_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --admin-user $DB_ADMIN_USER \
        --admin-password "$DB_ADMIN_PASSWORD" \
        --sku-name $POSTGRES_SKU \
        --version $POSTGRES_VERSION \
        --output table
    echo -e "${GREEN}PostgreSQL server '$DB_SERVER_NAME' created.${NC}"

    echo "Configuring PostgreSQL firewall rules to allow Azure services..."
    az postgres server firewall-rule create \
        --name AllowAllAzureIPs \
        --server $DB_SERVER_NAME \
        --resource-group $RESOURCE_GROUP \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0 \
        --output table
    echo -e "${GREEN}Firewall rule 'AllowAllAzureIPs' created.${NC}"
fi

# Check if database exists
echo "Checking for database '$DB_NAME' on server '$DB_SERVER_NAME'..."
if az postgres db show --name $DB_NAME --server $DB_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}Database '$DB_NAME' already exists.${NC}"
else
    echo "Creating database '$DB_NAME'..."
    az postgres db create \
        --name $DB_NAME \
        --server $DB_SERVER_NAME \
        --resource-group $RESOURCE_GROUP \
        --output table
    echo -e "${GREEN}Database '$DB_NAME' created.${NC}"
fi

# Construct Database URL
DATABASE_URL="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/${DB_NAME}"

# --- App Service Plan ---
echo -e "${BLUE}--- Ensuring App Service Plan Exists ---${NC}"
APP_SERVICE_PLAN_NAME="${APP_NAME}-plan"
if az appservice plan show --name $APP_SERVICE_PLAN_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}App Service Plan '$APP_SERVICE_PLAN_NAME' already exists.${NC}"
else
    echo "Creating App Service Plan '$APP_SERVICE_PLAN_NAME' with SKU '$APP_SERVICE_PLAN_SKU'..."
    az appservice plan create \
        --name $APP_SERVICE_PLAN_NAME \
        --resource-group $RESOURCE_GROUP \
        --sku $APP_SERVICE_PLAN_SKU \
        --is-linux \
        --output table
    echo -e "${GREEN}App Service Plan '$APP_SERVICE_PLAN_NAME' created.${NC}"
fi

# --- Web App ---
echo -e "${BLUE}--- Ensuring Web App '$APP_NAME' Exists ---${NC}"
if az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${YELLOW}Web App '$APP_NAME' already exists. It will be updated.${NC}"
else
    echo "Creating Web App '$APP_NAME' with Python runtime '$PYTHON_VERSION'..."
    az webapp create \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN_NAME \
        --runtime "PYTHON|$PYTHON_VERSION" \
        --output table
    echo -e "${GREEN}Web App '$APP_NAME' created.${NC}"
fi

# --- Prepare Deployment Package ---
echo -e "${BLUE}--- Preparing Deployment Package ---${NC}"
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary deployment directory: $DEPLOY_DIR"

echo "Copying application files..."
# Copy essential root files
cp requirements.txt $DEPLOY_DIR/
cp alembic.ini $DEPLOY_DIR/
cp web.config $DEPLOY_DIR/
cp wsgi.py $DEPLOY_DIR/
cp startup.py $DEPLOY_DIR/
cp startup.sh $DEPLOY_DIR/
cp app_adapter.py $DEPLOY_DIR/ # Use the main adapter
# Ensure startup script is executable
chmod +x $DEPLOY_DIR/startup.sh

# Copy directories (app, migrations, scripts)
echo "Copying directories (app, migrations, scripts)..."
cp -r app $DEPLOY_DIR/
cp -r migrations $DEPLOY_DIR/
cp -r scripts $DEPLOY_DIR/

# Ensure __init__.py files exist in all relevant directories
echo "Ensuring __init__.py files exist..."
touch $DEPLOY_DIR/app/__init__.py
touch $DEPLOY_DIR/migrations/__init__.py
touch $DEPLOY_DIR/scripts/__init__.py
find $DEPLOY_DIR/app -type d -exec touch {}/__init__.py \;

echo "Deployment package contents:"
ls -lR $DEPLOY_DIR | head -n 20 # Show top level and start of app dir

# Create zip file
DEPLOY_ZIP_FILE="deploy-comprehensive-$(date +%Y%m%d%H%M%S).zip"
echo "Creating deployment zip file '$DEPLOY_ZIP_FILE'..."
cd $DEPLOY_DIR
zip -r ../$DEPLOY_ZIP_FILE . > /dev/null # Suppress zip output for cleaner logs
cd ..
echo -e "${GREEN}Deployment package created.${NC}"

# --- Deploy to Azure ---
echo -e "${BLUE}--- Deploying Application to Azure App Service ---${NC}"
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src $DEPLOY_ZIP_FILE \
    --output table
echo -e "${GREEN}Deployment package uploaded.${NC}"

# --- Configure App Service ---
echo -e "${BLUE}--- Configuring Azure App Service ---${NC}"

echo "Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.sh" \
    --output table

echo "Setting environment variables (you will be prompted for secrets)..."
# Initialize the command string for app settings
APP_SETTINGS_CMD="az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings"

# Add non-sensitive settings
APP_SETTINGS_CMD+=" DATABASE_URL=${DATABASE_URL}"
APP_SETTINGS_CMD+=" ACCESS_TOKEN_EXPIRE_MINUTES=60"
APP_SETTINGS_CMD+=" REFRESH_TOKEN_EXPIRE_DAYS=7"
APP_SETTINGS_CMD+=" ALGORITHM=HS256"
APP_SETTINGS_CMD+=" LLM_PROVIDER=google" # Default to Google, change if needed
APP_SETTINGS_CMD+=" GOOGLE_MODEL=gemini-1.5-flash" # Updated model
APP_SETTINGS_CMD+=" OPENAI_MODEL=gpt-4o" # Updated model
APP_SETTINGS_CMD+=" EMAIL_FROM=noreply@aieventplanner.com"
APP_SETTINGS_CMD+=" EMAIL_FROM_NAME=\"AI Event Planner\""
APP_SETTINGS_CMD+=" DEFAULT_TENANT=default"
APP_SETTINGS_CMD+=" TENANT_HEADER=X-Tenant-ID"
APP_SETTINGS_CMD+=" ENABLE_AGENT_LOGGING=true"
APP_SETTINGS_CMD+=" AGENT_MEMORY_STORAGE=file" # Use file storage for simplicity in App Service
APP_SETTINGS_CMD+=" AGENT_MEMORY_PATH=/home/site/wwwroot/agent_memory" # Path within App Service container
APP_SETTINGS_CMD+=" RUN_MIGRATIONS=true" # Run migrations on startup
APP_SETTINGS_CMD+=" ENVIRONMENT=production"
APP_SETTINGS_CMD+=" APP_VERSION=1.1.0" # Increment version
APP_SETTINGS_CMD+=" APP_NAME=\"AI Event Planner SaaS\""
APP_SETTINGS_CMD+=" PYTHONPATH=/home/site/wwwroot"
APP_SETTINGS_CMD+=" WEBSITE_HTTPLOGGING_RETENTION_DAYS=7"
APP_SETTINGS_CMD+=" SCM_DO_BUILD_DURING_DEPLOYMENT=true" # Ensure build process runs

# Prompt for secrets
prompt_for_secret "Enter SECRET_KEY for JWT: " SECRET_KEY
prompt_for_secret "Enter GOOGLE_API_KEY: " GOOGLE_API_KEY
prompt_for_secret "Enter OPENAI_API_KEY: " OPENAI_API_KEY
prompt_for_secret "Enter SENDGRID_API_KEY: " SENDGRID_API_KEY

# Execute the command to set app settings
echo "Applying environment variables..."
eval $APP_SETTINGS_CMD --output table
echo -e "${GREEN}Environment variables set.${NC}"

echo "Verifying environment variables..."
VARS_TO_CHECK=("LLM_PROVIDER" "GOOGLE_API_KEY" "OPENAI_API_KEY" "SECRET_KEY" "DATABASE_URL")
for VAR in "${VARS_TO_CHECK[@]}"; do
    VALUE=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='$VAR'].value" -o tsv)
    if [ -z "$VALUE" ]; then
        echo -e "${YELLOW}Warning: $VAR is not set or empty.${NC}"
    else
        echo -e "${GREEN}$VAR is set.${NC}"
    fi
done

echo "Enabling detailed logging..."
az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem \
    --output table
echo -e "${GREEN}Logging enabled.${NC}"

# --- Restart and Verify ---
echo -e "${BLUE}--- Restarting and Verifying Deployment ---${NC}"
echo "Restarting the Web App (allow a few minutes for startup)..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
sleep 60 # Wait a bit for the restart to initiate

echo "Checking application status..."
STATUS_CHECKS=0
MAX_STATUS_CHECKS=10 # Check for 5 minutes (10 * 30 seconds)
while [ $STATUS_CHECKS -lt $MAX_STATUS_CHECKS ]; do
    STATUS=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query state -o tsv)
    echo "Current status: $STATUS"
    if [ "$STATUS" == "Running" ]; then
        echo -e "${GREEN}App is running.${NC}"
        break
    fi
    STATUS_CHECKS=$((STATUS_CHECKS + 1))
    if [ $STATUS_CHECKS -eq $MAX_STATUS_CHECKS ]; then
        echo -e "${RED}Error: App failed to reach 'Running' state after $MAX_STATUS_CHECKS checks.${NC}"
        echo -e "${YELLOW}Please check the logs using 'az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP'${NC}"
        exit 1
    fi
    sleep 30
done

echo "Checking application health endpoint..."
HEALTH_URL="https://$APP_NAME.azurewebsites.net/health"
HEALTH_CHECKS=0
MAX_HEALTH_CHECKS=6 # Check for 3 minutes (6 * 30 seconds)
while [ $HEALTH_CHECKS -lt $MAX_HEALTH_CHECKS ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
    echo "Health check response code: $HTTP_CODE"
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}App health endpoint is accessible and returning 200 OK.${NC}"
        HEALTH_RESPONSE=$(curl -s $HEALTH_URL)
        echo "Health Response: $HEALTH_RESPONSE"
        break
    fi
    HEALTH_CHECKS=$((HEALTH_CHECKS + 1))
    if [ $HEALTH_CHECKS -eq $MAX_HEALTH_CHECKS ]; then
        echo -e "${RED}Error: App health endpoint did not return 200 OK after $MAX_HEALTH_CHECKS checks (Last code: $HTTP_CODE).${NC}"
        echo -e "${YELLOW}Please check the logs using 'az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP'${NC}"
        exit 1
    fi
    sleep 30
done

# --- Cleanup ---
echo -e "${BLUE}--- Cleaning Up ---${NC}"
rm -rf $DEPLOY_DIR
rm -f $DEPLOY_ZIP_FILE
echo "Removed temporary directory and zip file."

# --- Completion ---
echo -e "${GREEN}=== Comprehensive Deployment Completed Successfully ===${NC}"
echo -e "Your application is available at: ${GREEN}https://$APP_NAME.azurewebsites.net${NC}"
echo -e "Database server: ${GREEN}$DB_SERVER_NAME.postgres.database.azure.com${NC}"
echo -e "Database name: ${GREEN}$DB_NAME${NC}"
echo -e "Admin user: ${GREEN}$DB_ADMIN_USER${NC}"
echo -e "${YELLOW}Remember to check the application logs if you encounter issues:${NC}"
echo -e "  az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo -e "  Or visit: https://$APP_NAME.scm.azurewebsites.net/api/logs/docker"
