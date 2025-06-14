#!/bin/bash
# Deploy the AI Event Planner SaaS application to Azure with REAL agents and database setup
# This script combines azure-deploy-saas-with-real-agents.sh and azure-deploy-saas-full-no-docker.sh

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
PYTHON_VERSION="3.9"
SKU="B1"

# Generate a unique suffix for the database server name
UNIQUE_SUFFIX=$(date +%Y%m%d%H%M%S)
DB_SERVER="aieventdb${UNIQUE_SUFFIX}"
DB_NAME="eventplanner"
DB_ADMIN="dbadmin"
DB_PASSWORD="P@ssw0rd${UNIQUE_SUFFIX}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to Azure
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo -e "${YELLOW}Not logged in to Azure. Please login.${NC}"
    az login
}

# Check if resource group exists
echo "Checking if resource group exists..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "Creating resource group $RESOURCE_GROUP in $LOCATION..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

# Ask if the user wants to set up a database
read -p "Do you want to set up a PostgreSQL database in Azure? (y/n): " SETUP_DB
if [[ "$SETUP_DB" == "y" || "$SETUP_DB" == "Y" ]]; then
    # List available PostgreSQL servers to help the user
    echo "Listing available PostgreSQL flexible servers in your subscription:"
    az postgres flexible-server list --query "[].{Name:name, ResourceGroup:resourceGroup, Location:location}" -o table
    
    # Ask if the PostgreSQL server already exists
    read -p "Does the PostgreSQL server already exist? (y/n): " SERVER_EXISTS_INPUT
    
    if [[ "$SERVER_EXISTS_INPUT" == "y" || "$SERVER_EXISTS_INPUT" == "Y" ]]; then
        # Server exists, ask for the server name
        read -p "Enter the existing PostgreSQL server name: " DB_SERVER
        
        # Trim leading and trailing whitespace and remove any "server" prefix
        if [[ "$DB_SERVER" =~ ^[Ss][Ee][Rr][Vv][Ee][Rr](\s+.+)$ ]]; then
            # Extract the part after "server"
            DB_SERVER="${BASH_REMATCH[1]}"
        fi
        DB_SERVER=$(echo "$DB_SERVER" | sed -e 's/^\s\+//g' -e 's/\s\+$//g')
        
        echo "Using server name: $DB_SERVER"
        
        # Ask for the resource group where the server exists
        read -p "Enter the resource group where the server exists (or press Enter to use ${RESOURCE_GROUP}): " SERVER_RESOURCE_GROUP
        if [[ -z "$SERVER_RESOURCE_GROUP" ]]; then
            SERVER_RESOURCE_GROUP=$RESOURCE_GROUP
        fi
        
        # Verify the server exists in the specified resource group
        if ! az postgres flexible-server show --name $DB_SERVER --resource-group $SERVER_RESOURCE_GROUP &> /dev/null; then
            echo -e "${RED}Error: PostgreSQL server '$DB_SERVER' not found in resource group '$SERVER_RESOURCE_GROUP'.${NC}"
            echo "Please check the server name and resource group and try again."
            echo "You can list all PostgreSQL servers with: az postgres flexible-server list --query \"[].{Name:name, ResourceGroup:resourceGroup}\" -o table"
            SETUP_DB="n"
        else
            echo "Found PostgreSQL server '$DB_SERVER' in resource group '$SERVER_RESOURCE_GROUP'."
            
            # Ask for database credentials for the existing server
            read -p "Enter database admin username: " DB_ADMIN
            read -p "Enter database admin password: " DB_PASSWORD
            
            # Ask if the database already exists
            read -p "Does the database '$DB_NAME' already exist on server '$DB_SERVER'? (y/n): " DB_EXISTS_INPUT
            
            if [[ "$DB_EXISTS_INPUT" == "n" || "$DB_EXISTS_INPUT" == "N" ]]; then
                # Database doesn't exist, create it
                echo "Creating database $DB_NAME on server $DB_SERVER..."
                if ! az postgres flexible-server db create \
                    --database-name $DB_NAME \
                    --server-name $DB_SERVER \
                    --resource-group $SERVER_RESOURCE_GROUP; then
                    echo -e "${RED}Failed to create database. Continuing without database setup.${NC}"
                    SETUP_DB="n"
                else
                    echo "Database $DB_NAME created successfully."
                fi
            else
                echo "Using existing database $DB_NAME on server $DB_SERVER."
            fi
        fi
    else
        # Server doesn't exist, create a new one
        # Ask for database server name or use the generated one
        read -p "Enter new PostgreSQL server name (or press Enter to use ${DB_SERVER}): " USER_DB_SERVER
        if [[ -n "$USER_DB_SERVER" ]]; then
            # Trim leading and trailing whitespace
            USER_DB_SERVER=$(echo "$USER_DB_SERVER" | sed -e 's/^\s\+//g' -e 's/\s\+$//g')
            
            echo "Using server name: $USER_DB_SERVER"
            DB_SERVER=$USER_DB_SERVER
        fi
        
        # Ask for database credentials
        read -p "Enter database admin username (or press Enter to use ${DB_ADMIN}): " USER_DB_ADMIN
        if [[ -n "$USER_DB_ADMIN" ]]; then
            DB_ADMIN=$USER_DB_ADMIN
        fi
        
        read -p "Enter database admin password (or press Enter to use auto-generated): " USER_DB_PASSWORD
        if [[ -n "$USER_DB_PASSWORD" ]]; then
            DB_PASSWORD=$USER_DB_PASSWORD
        fi
        
        # Create the PostgreSQL server
        echo "Creating PostgreSQL flexible server $DB_SERVER..."
        if ! az postgres flexible-server create \
            --name $DB_SERVER \
            --resource-group $RESOURCE_GROUP \
            --location $LOCATION \
            --admin-user $DB_ADMIN \
            --admin-password $DB_PASSWORD \
            --sku-name Standard_B1ms \
            --version 14 \
            --yes; then
            echo -e "${RED}Failed to create PostgreSQL server. Continuing without database setup.${NC}"
            SETUP_DB="n"
        else
            # Configure firewall rules to allow Azure services
            echo "Configuring PostgreSQL firewall rules..."
            az postgres flexible-server firewall-rule create \
                --name AllowAllAzureIPs \
                --server-name $DB_SERVER \
                --resource-group $RESOURCE_GROUP \
                --start-ip-address 0.0.0.0 \
                --end-ip-address 0.0.0.0
                
            # Create the database
            echo "Creating database $DB_NAME..."
            if ! az postgres flexible-server db create \
                --database-name $DB_NAME \
                --server-name $DB_SERVER \
                --resource-group $RESOURCE_GROUP; then
                echo -e "${RED}Failed to create database. Continuing without database setup.${NC}"
                SETUP_DB="n"
            else
                echo "Database $DB_NAME created successfully."
            fi
        fi
    fi
else
    echo "Skipping database setup."
fi

# Check if App Service Plan exists
echo "Checking if App Service Plan exists..."
APP_SERVICE_PLAN="${APP_NAME}-plan"
if ! az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating App Service Plan $APP_SERVICE_PLAN..."
    az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku $SKU --is-linux
fi

# Check if Web App exists
echo "Checking if Web App exists..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Web App $APP_NAME..."
    az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON|$PYTHON_VERSION"
fi

# Create a temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"

# Copy the updated files to the deployment directory
echo "Copying updated files to deployment directory..."
mkdir -p $DEPLOY_DIR
cp startup.py $DEPLOY_DIR/
cp wsgi.py $DEPLOY_DIR/
cp web.config $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp run_azure_migrations_fixed.py $DEPLOY_DIR/
cp alembic.ini $DEPLOY_DIR/

# Create a custom startup.sh that ensures dependencies are installed
echo "Creating custom startup.sh..."
cat > $DEPLOY_DIR/startup.sh << 'EOF'
#!/bin/bash
cd /home/site/wwwroot

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $PYTHONPATH"

# Install required dependencies with explicit versions
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi==0.95.1 uvicorn==0.22.0 gunicorn==20.1.0 sqlalchemy==2.0.9 pydantic==1.10.7 \
    langchain==0.0.267 langgraph==0.0.11 google-generativeai==0.3.1 openai==0.28.1 \
    passlib==1.7.4 python-jose==3.3.0 python-multipart==0.0.6 bcrypt==4.0.1 \
    python-dotenv==1.0.0 psycopg2-binary==2.9.6 email-validator==2.0.0 icalendar==5.0.7 alembic==1.10.4

# Print environment for debugging
echo "Environment variables:"
env | grep -v "PATH" | grep -v "PYTHONPATH"

# Add current directory to Python path
export PYTHONPATH=$PYTHONPATH:/home/site/wwwroot

# List all directories in the current path to help with debugging
echo "Listing directories in current path:"
ls -la
echo "App directory contents:"
ls -la app

# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    if [ -f "run_azure_migrations_fixed.py" ]; then
        python run_azure_migrations_fixed.py
    else
        echo "Migration script not found, skipping migrations."
    fi
fi

# Check if main_saas.py exists in the app directory
MAIN_SAAS_PATH="app/main_saas.py"
APP_ADAPTER_PATH="app_adapter.py"
MAIN_PATH="app/main.py"

echo "Checking for $MAIN_SAAS_PATH: $([ -f "$MAIN_SAAS_PATH" ] && echo "Found" || echo "Not found")"
echo "Checking for $APP_ADAPTER_PATH: $([ -f "$APP_ADAPTER_PATH" ] && echo "Found" || echo "Not found")"
echo "Checking for $MAIN_PATH: $([ -f "$MAIN_PATH" ] && echo "Found" || echo "Not found")"

# Try to determine which module to use
if [ -f "$MAIN_SAAS_PATH" ]; then
    echo "Found main_saas.py, using app.main_saas:app"
    APP_MODULE="app.main_saas:app"
elif [ -f "$MAIN_PATH" ]; then
    echo "Found main.py, using app.main:app"
    APP_MODULE="app.main:app"
else
    echo "Using app_adapter:app as fallback"
    APP_MODULE="app_adapter:app"
fi

# Run gunicorn with the determined app module
echo "Starting application with $APP_MODULE..."
gunicorn $APP_MODULE --bind=0.0.0.0:8000 --workers=4 --timeout=120
EOF

chmod +x $DEPLOY_DIR/startup.sh

# Use app_adapter_with_agents.py as app_adapter.py for real agent support
echo "Setting up app_adapter with real agent support..."
cp app_adapter_with_agents.py $DEPLOY_DIR/app_adapter.py

# Copy the scripts directory
echo "Copying scripts directory..."
mkdir -p $DEPLOY_DIR/scripts
if [ -d "scripts" ]; then
    cp -r scripts/* $DEPLOY_DIR/scripts/
    # Ensure __init__.py exists in scripts directory
    touch $DEPLOY_DIR/scripts/__init__.py
fi

# Copy the migrations directory
echo "Copying migrations directory..."
if [ -d "migrations" ]; then
    cp -r migrations $DEPLOY_DIR/
fi

# Create app directory structure with __init__.py files
echo "Creating app directory structure..."
mkdir -p $DEPLOY_DIR/app
touch $DEPLOY_DIR/app/__init__.py

# Copy the entire app directory with proper structure
echo "Copying app directory with proper structure..."
for dir in agents auth db middleware graphs tools schemas state utils web; do
    if [ -d "app/$dir" ]; then
        echo "Copying app/$dir..."
        mkdir -p $DEPLOY_DIR/app/$dir
        cp -r app/$dir/* $DEPLOY_DIR/app/$dir/
        # Ensure __init__.py exists in each directory
        touch $DEPLOY_DIR/app/$dir/__init__.py
    fi
done

# Copy any Python files in the app root
echo "Copying Python files in app root..."
cp app/*.py $DEPLOY_DIR/app/ 2>/dev/null || :

# Make sure __init__.py exists in all subdirectories
echo "Ensuring __init__.py exists in all subdirectories..."
find $DEPLOY_DIR/app -type d -exec touch {}/__init__.py \;

# Print the list of files being deployed
echo "Files being deployed:"
ls -la $DEPLOY_DIR
echo "App directory contents:"
ls -la $DEPLOY_DIR/app

# Create a zip file for deployment
echo "Creating deployment package..."
cd $DEPLOY_DIR
zip -r ../deploy-full-saas.zip .
cd ..

# Switch to a non-containerized approach
echo "Switching to a non-containerized approach..."
echo "When prompted, type 'y' to confirm deletion of the web app"
az webapp delete --name $APP_NAME --resource-group $RESOURCE_GROUP --keep-empty-plan

# Create a new web app with the non-containerized Python runtime
echo "Creating a new web app with the non-containerized Python runtime..."
az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON:$PYTHON_VERSION"

# Deploy to Azure App Service
echo "Deploying to Azure App Service..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deploy-full-saas.zip

# Configure the App Service
echo "Configuring App Service..."
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "startup.sh"

# Set environment variables
echo "Setting environment variables..."
ENV_SETTINGS=(
    "SECRET_KEY=iuoiuoi_09870_87h98h9_98h98h_vh98h98h"
    "ACCESS_TOKEN_EXPIRE_MINUTES=60"
    "REFRESH_TOKEN_EXPIRE_DAYS=7"
    "ALGORITHM=HS256"
    "LLM_PROVIDER=google"
    "GOOGLE_API_KEY=AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU"
    "GOOGLE_MODEL=gemini-2.0-flash"
    "OPENAI_API_KEY=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"
    "OPENAI_MODEL=gpt-4"
    "SENDGRID_API_KEY=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"
    "EMAIL_FROM=noreply@aieventplanner.com"
    "EMAIL_FROM_NAME=AI Event Planner"
    "DEFAULT_TENANT=default"
    "TENANT_HEADER=X-Tenant-ID"
    "ENABLE_AGENT_LOGGING=true"
    "AGENT_MEMORY_STORAGE=file"
    "AGENT_MEMORY_PATH=/home/site/wwwroot/agent_memory"
    "PYTHONPATH=/home/site/wwwroot"
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7"
    "RUN_MIGRATIONS=true"
    "ENVIRONMENT=production"
    "APP_VERSION=1.0.0"
    "APP_NAME=AI Event Planner"
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
)

# Add database connection string if database was set up
if [[ "$SETUP_DB" == "y" || "$SETUP_DB" == "Y" ]]; then
    ENV_SETTINGS+=("DATABASE_URL=postgresql://${DB_ADMIN}@${DB_SERVER}:${DB_PASSWORD}@${DB_SERVER}.postgres.database.azure.com:5432/${DB_NAME}")
fi

# Apply all environment settings
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings "${ENV_SETTINGS[@]}"

# Enable logging
echo "Enabling logging..."
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --application-logging filesystem --detailed-error-messages true --failed-request-tracing true --web-server-logging filesystem

# Restart the app
echo "Restarting the app..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# Clean up
echo "Cleaning up..."
rm -rf $DEPLOY_DIR
rm -f deploy-full-saas.zip

echo -e "${GREEN}Deployment completed successfully.${NC}"
echo -e "Your application with REAL agents and database is available at: https://$APP_NAME.azurewebsites.net"
echo -e "Please allow a few minutes for the changes to take effect."
echo -e "You can check the logs at: https://$APP_NAME.scm.azurewebsites.net/api/logs/docker"
