#!/bin/bash
# Run database migrations for AI Event Planner SaaS on Azure

set -e

# Configuration
APP_NAME="ai-event-planner-saas"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration options
DB_SERVER_NAME=${DB_SERVER_NAME:-"ai-event-planner-db"}
DB_NAME=${DB_NAME:-"eventplanner"}
DB_USER=${DB_USER:-"dbadmin"}
DB_PASSWORD=${DB_PASSWORD:-"VM*admin"}
SKIP_DB_CHECK=${SKIP_DB_CHECK:-"false"}
SKIP_KUDU_COMMANDS=${SKIP_KUDU_COMMANDS:-"false"}

# Check if jq is installed and set a flag
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Using alternative approach for JSON parsing.${NC}"
    USE_JQ=false
else
    USE_JQ=true
fi

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

# Check if the App Service exists
echo "Checking if the App Service exists..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}Error: App Service does not exist.${NC}"
    exit 1
fi

# Run migrations using Kudu REST API
echo "Running database migrations..."
echo -e "${YELLOW}This may take a few minutes...${NC}"

# Get publishing credentials
echo "Getting publishing credentials..."
if [ "$USE_JQ" = false ]; then
    # Get publishing credentials using direct Azure CLI queries
    USERNAME=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingUserName -o tsv)
    PASSWORD=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query publishingPassword -o tsv)
else
    # Get publishing credentials using jq
    CREDS=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_NAME --query "{username:publishingUserName, password:publishingPassword}" -o json)
    USERNAME=$(echo $CREDS | jq -r '.username')
    PASSWORD=$(echo $CREDS | jq -r '.password')
fi

# Find Python executable path - using common paths in Azure App Service
if [ "$SKIP_KUDU_COMMANDS" = "false" ]; then
  echo "Finding Python executable path..."
  FIND_PYTHON_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
    -H "Content-Type: application/json" \
    https://$APP_NAME.scm.azurewebsites.net/api/command \
    -d "{\"command\":\"which python || which python3 || echo 'not found'\", \"dir\":\"/\"}")

  # Extract status code and response body
  FIND_PYTHON_HTTP_STATUS=$(echo "$FIND_PYTHON_RESPONSE" | tail -n1)
  FIND_PYTHON_BODY=$(echo "$FIND_PYTHON_RESPONSE" | sed '$d')

  echo "Find Python response: $FIND_PYTHON_BODY"
  echo "HTTP status: $FIND_PYTHON_HTTP_STATUS"

  # Try common Python paths in Azure App Service
  if [[ $FIND_PYTHON_BODY == *"not found"* || -z "$FIND_PYTHON_BODY" ]]; then
    # Common Python paths in Azure App Service
    COMMON_PATHS=(
      "/home/site/wwwroot/env/bin/python"
      "/usr/bin/python3"
      "/usr/bin/python"
      "python"  # Use PATH to find Python
    )
    
    for path in "${COMMON_PATHS[@]}"; do
      echo "Trying Python path: $path"
      TEST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
        -H "Content-Type: application/json" \
        https://$APP_NAME.scm.azurewebsites.net/api/command \
        -d "{\"command\":\"$path --version || echo 'not found'\", \"dir\":\"/home/site/wwwroot\"}")
      
      TEST_STATUS=$(echo "$TEST_RESPONSE" | tail -n1)
      TEST_BODY=$(echo "$TEST_RESPONSE" | sed '$d')
      
      if [[ $TEST_BODY != *"not found"* && $TEST_BODY != *"No such file"* ]]; then
        PYTHON_PATH=$path
        echo "Found working Python path: $PYTHON_PATH"
        break
      fi
    done
  else
    PYTHON_PATH=$(echo "$FIND_PYTHON_BODY" | head -n 1)
    echo "Found Python path: $PYTHON_PATH"
  fi

  # If still no Python path found, use a simple command
  if [ -z "$PYTHON_PATH" ]; then
    echo "No Python path found, using 'python' command"
    PYTHON_PATH="python"
  fi
else
  echo -e "${YELLOW}Skipping Kudu commands as requested.${NC}"
  PYTHON_PATH="python"  # Default value, won't be used
fi

# Check if the database exists and create it if it doesn't
echo "Checking if database exists and creating it if needed..."

if [ "$SKIP_DB_CHECK" = "true" ]; then
  echo -e "${YELLOW}Skipping database check as requested.${NC}"
else
  # Check if the PostgreSQL server exists
  echo "Checking if PostgreSQL server exists..."
  PG_SERVER_EXISTS=$(az postgres server list --query "[?name=='$DB_SERVER_NAME']" -o tsv 2>/dev/null)
  
  if [ -z "$PG_SERVER_EXISTS" ]; then
    echo -e "${YELLOW}PostgreSQL server '$DB_SERVER_NAME' not found. Creating it...${NC}"
    
    # Default values for server creation
    PG_ADMIN_USER=${PG_ADMIN_USER:-"dbadmin"}
    PG_ADMIN_PASSWORD=${PG_ADMIN_PASSWORD:-"VM*admin"}
    PG_SKU=${PG_SKU:-"B_Gen5_1"}
    PG_LOCATION=${PG_LOCATION:-"eastus"}
    PG_VERSION=${PG_VERSION:-"11"}
    
    # Create the PostgreSQL server
    echo "Creating PostgreSQL server '$DB_SERVER_NAME'..."
    az postgres server create \
      --resource-group $RESOURCE_GROUP \
      --name $DB_SERVER_NAME \
      --location $PG_LOCATION \
      --admin-user $PG_ADMIN_USER \
      --admin-password $PG_ADMIN_PASSWORD \
      --sku-name $PG_SKU \
      --version $PG_VERSION
    
    if [ $? -ne 0 ]; then
      echo -e "${RED}Error: Failed to create PostgreSQL server.${NC}"
      echo -e "${YELLOW}Please create the PostgreSQL server manually.${NC}"
      echo -e "${YELLOW}Skipping database creation and continuing with migrations...${NC}"
    else
      echo -e "${GREEN}PostgreSQL server '$DB_SERVER_NAME' created successfully.${NC}"
      
      # Configure firewall rules to allow Azure services
      echo "Configuring firewall rules..."
      az postgres server firewall-rule create \
        --resource-group $RESOURCE_GROUP \
        --server-name $DB_SERVER_NAME \
        --name AllowAllAzureIPs \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0
      
      if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Warning: Failed to configure Azure services firewall rule.${NC}"
        echo -e "${YELLOW}You may need to configure firewall rules manually.${NC}"
      else
        echo -e "${GREEN}Azure services firewall rule configured successfully.${NC}"
      fi
      
      # Get the client IP address
      echo "Getting client IP address..."
      CLIENT_IP=$(curl -s https://api.ipify.org)
      
      if [ -z "$CLIENT_IP" ]; then
        echo -e "${YELLOW}Warning: Failed to get client IP address.${NC}"
        echo -e "${YELLOW}You may need to configure firewall rules manually.${NC}"
      else
        echo "Client IP address: $CLIENT_IP"
        
        # Configure firewall rules to allow the client IP
        echo "Configuring firewall rule for client IP..."
        az postgres server firewall-rule create \
          --resource-group $RESOURCE_GROUP \
          --server-name $DB_SERVER_NAME \
          --name AllowClientIP \
          --start-ip-address $CLIENT_IP \
          --end-ip-address $CLIENT_IP
        
        if [ $? -ne 0 ]; then
          echo -e "${YELLOW}Warning: Failed to configure client IP firewall rule.${NC}"
          echo -e "${YELLOW}You may need to configure firewall rules manually.${NC}"
        else
          echo -e "${GREEN}Client IP firewall rule configured successfully.${NC}"
        fi
      fi
      
      # Add a firewall rule for the specific IP mentioned in the error
      echo "Configuring firewall rule for specific IP..."
      az postgres server firewall-rule create \
        --resource-group $RESOURCE_GROUP \
        --server-name $DB_SERVER_NAME \
        --name AllowSpecificIP \
        --start-ip-address 107.194.36.34 \
        --end-ip-address 107.194.36.34
      
      if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Warning: Failed to configure specific IP firewall rule.${NC}"
        echo -e "${YELLOW}You may need to configure firewall rules manually.${NC}"
      else
        echo -e "${GREEN}Specific IP firewall rule configured successfully.${NC}"
      fi
      
      # Update DB_USER to match the admin user
      DB_USER=$PG_ADMIN_USER
    fi
  else
    echo -e "${GREEN}PostgreSQL server '$DB_SERVER_NAME' already exists.${NC}"
    # Check if the database exists
    echo "Checking if '$DB_NAME' database exists..."
    DB_EXISTS=$(az postgres db list --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --query "[?name=='$DB_NAME']" -o tsv 2>/dev/null)
    
    if [ -z "$DB_EXISTS" ]; then
      echo -e "${YELLOW}Database '$DB_NAME' does not exist. Creating it...${NC}"
      
      # Create the database
      az postgres db create --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --name $DB_NAME
      
      if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create database '$DB_NAME'.${NC}"
        echo -e "${YELLOW}Trying alternative approach...${NC}"
        
        # Try using psql directly
        echo "Trying to create database using psql..."
        
        # Get the PostgreSQL server FQDN
        PG_FQDN=$(az postgres server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query fullyQualifiedDomainName -o tsv)
        
        # Create a temporary script to create the database
        cat > /tmp/create_db.sql << EOF
CREATE DATABASE $DB_NAME;
EOF
        
        # Run the script using psql
        PGPASSWORD="$DB_PASSWORD" psql -h $PG_FQDN -U "${DB_USER}@${DB_SERVER_NAME}" -d postgres -f /tmp/create_db.sql
        
        if [ $? -ne 0 ]; then
          echo -e "${RED}Error: Failed to create database using psql.${NC}"
          echo -e "${YELLOW}Please create the database manually.${NC}"
          
          # Clean up
          rm -f /tmp/create_db.sql
          
          # Continue anyway, as the database might already exist
          echo -e "${YELLOW}Continuing with migrations...${NC}"
        else
          echo -e "${GREEN}Database '$DB_NAME' created successfully using psql.${NC}"
          
          # Clean up
          rm -f /tmp/create_db.sql
        fi
      else
        echo -e "${GREEN}Database '$DB_NAME' created successfully.${NC}"
      fi
    else
      echo -e "${GREEN}Database '$DB_NAME' already exists.${NC}"
    fi
  fi

  # Set the DATABASE_URL environment variable in the App Service
  echo "Setting DATABASE_URL environment variable in App Service..."
  DB_URL="postgresql://${DB_USER}%40${DB_SERVER_NAME}:${DB_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/${DB_NAME}?sslmode=require"
  az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings DATABASE_URL="$DB_URL"

  if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to set DATABASE_URL environment variable.${NC}"
    echo -e "${YELLOW}Please set it manually.${NC}"
  else
    echo -e "${GREEN}DATABASE_URL environment variable set successfully.${NC}"
  fi
fi

if [ "$SKIP_KUDU_COMMANDS" = "true" ]; then
  echo -e "${YELLOW}Skipping Kudu commands for table creation and migrations.${NC}"
  echo -e "${YELLOW}Please run the following commands manually on the App Service:${NC}"
  echo -e "${YELLOW}1. python -m scripts.create_azure_tables${NC}"
  echo -e "${YELLOW}2. python -m scripts.run_azure_migrations${NC}"
  echo -e "${YELLOW}You can do this using the Azure Portal's Console feature.${NC}"
  echo -e "${YELLOW}Alternatively, you can SSH into the App Service and run the commands.${NC}"
  
  echo -e "${GREEN}Database setup completed.${NC}"
  echo -e "${GREEN}Remember to run the migrations manually!${NC}"
  exit 0
fi

# Now create the tables using the create_azure_tables.py script
echo "Creating database tables..."
TABLES_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -m scripts.create_azure_tables\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body for table creation
TABLES_HTTP_STATUS=$(echo "$TABLES_RESPONSE" | tail -n1)
TABLES_BODY=$(echo "$TABLES_RESPONSE" | sed '$d')

echo "Table creation response: $TABLES_BODY"
echo "HTTP status: $TABLES_HTTP_STATUS"

# Check if the table creation was successful
if [ "$TABLES_HTTP_STATUS" -ne 200 ]; then
  echo -e "${RED}Table creation failed with status $TABLES_HTTP_STATUS${NC}"
  echo -e "${RED}Response: $TABLES_BODY${NC}"
  echo -e "${YELLOW}You may need to run the table creation manually.${NC}"
  echo -e "${YELLOW}Try running 'python -m scripts.create_azure_tables' on the App Service.${NC}"
  # Continue anyway, as migrations might still work
fi

# Use the Python path to run the Azure migration script
echo "Running migrations..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -m scripts.run_azure_migrations\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

echo "Migration response: $RESPONSE_BODY"
echo "HTTP status: $HTTP_STATUS"

# Check if the request was successful
if [ "$HTTP_STATUS" -ne 200 ]; then
  echo -e "${RED}Migration failed with status $HTTP_STATUS${NC}"
  echo -e "${RED}Response: $RESPONSE_BODY${NC}"
  
  # Provide troubleshooting steps
  echo -e "${YELLOW}Troubleshooting steps:${NC}"
  echo -e "${YELLOW}1. Check if the database connection string is correct in the App Service settings.${NC}"
  echo -e "${YELLOW}2. Check if the database server is accessible from the App Service.${NC}"
  echo -e "${YELLOW}3. Check if the database user has the necessary permissions.${NC}"
  echo -e "${YELLOW}4. Check if the database exists.${NC}"
  echo -e "${YELLOW}5. Try running 'python -m scripts.run_azure_migrations' manually on the App Service.${NC}"
  
  # Get database connection string (masked)
  db_conn=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)
  if [ -n "$db_conn" ]; then
      echo -e "${YELLOW}Database connection string is configured.${NC}"
  else
      echo -e "${RED}Error: Database connection string is not configured.${NC}"
  fi
  
  exit 1
fi

# Check if the response contains error messages
if [[ "$RESPONSE_BODY" == *"Error"* || "$RESPONSE_BODY" == *"error"* || "$RESPONSE_BODY" == *"Exception"* ]]; then
  echo -e "${RED}Migration script reported errors${NC}"
  echo -e "${RED}Response details: $RESPONSE_BODY${NC}"
  
  # Check if it's a Python not found error
  if [[ "$RESPONSE_BODY" == *"No such file or directory"* ]]; then
    echo -e "${YELLOW}Python path not found. This might be due to a different Python installation on Azure App Service.${NC}"
    echo -e "${YELLOW}Try running the migrations directly on the App Service using the Azure Portal's Console feature.${NC}"
  fi
  
  exit 1
fi

echo -e "${GREEN}Database migrations completed successfully!${NC}"

# Verify database schema
echo "Verifying database schema..."
SCHEMA_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -m alembic current\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
SCHEMA_HTTP_STATUS=$(echo "$SCHEMA_RESPONSE" | tail -n1)
SCHEMA_BODY=$(echo "$SCHEMA_RESPONSE" | sed '$d')

echo -e "${GREEN}Current database schema:${NC}"
echo "$SCHEMA_BODY"

# Check database connection
echo "Checking database connection..."
DB_CONN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  https://$APP_NAME.scm.azurewebsites.net/api/command \
  -d "{\"command\":\"$PYTHON_PATH -c 'from app.db.session import engine; print(\\\"Connected\\\" if engine.connect() else \\\"Failed\\\")';\", \"dir\":\"/home/site/wwwroot\"}")

# Extract status code and response body
DB_CONN_HTTP_STATUS=$(echo "$DB_CONN_RESPONSE" | tail -n1)
DB_CONN_BODY=$(echo "$DB_CONN_RESPONSE" | sed '$d')

if [[ $DB_CONN_BODY == *"Connected"* ]]; then
  echo -e "${GREEN}Database connection successful.${NC}"
else
  echo -e "${RED}Error: Database connection failed.${NC}"
  echo -e "${RED}Response: $DB_CONN_BODY${NC}"
  exit 1
fi

echo -e "${GREEN}Database migrations and verification completed successfully!${NC}"
