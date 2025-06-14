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
        MIGRATION_RESULT=$?
        
        if [ $MIGRATION_RESULT -ne 0 ]; then
            echo "Migrations failed, trying direct table creation as fallback..."
            if [ -f "scripts/create_azure_tables_direct_fixed.py" ]; then
                python scripts/create_azure_tables_direct_fixed.py
            elif [ -f "scripts/create_azure_tables_direct.py" ]; then
                python scripts/create_azure_tables_direct.py
            else
                echo "Direct table creation script not found, creating tables using SQLAlchemy..."
                python -c "
import os, sys
sys.path.insert(0, '/home/site/wwwroot')
from app.db.base import Base
from app.db.session import engine
from app.db.models import User, Event, Organization, Conversation, Message
from app.db.models_saas import Subscription, SubscriptionPlan, UserOrganization
from app.db.models_updated import Event, Organization, User
print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created successfully.')
"
            fi
        fi
    else
        echo "Migration script not found, trying direct table creation..."
        if [ -f "scripts/create_azure_tables_direct_fixed.py" ]; then
            python scripts/create_azure_tables_direct_fixed.py
        elif [ -f "scripts/create_azure_tables_direct.py" ]; then
            python scripts/create_azure_tables_direct.py
        else
            echo "Direct table creation script not found, creating tables using SQLAlchemy..."
            python -c "
import os, sys
sys.path.insert(0, '/home/site/wwwroot')
from app.db.base import Base
from app.db.session import engine
from app.db.models import User, Event, Organization, Conversation, Message
from app.db.models_saas import Subscription, SubscriptionPlan, UserOrganization
from app.db.models_updated import Event, Organization, User
print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created successfully.')
"
        fi
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

# Create a debug version of app_adapter_with_agents.py with improved error handling
echo "Creating enhanced app_adapter_with_agents.py with better error handling..."
cat > $DEPLOY_DIR/app_adapter_with_agents.py << 'EOF'
# This file exists to provide the 'app' object that Azure is looking for
# It creates a simple WSGI app that serves static files from the saas directory
# and routes API requests to the appropriate handlers
# This version also integrates with the real agent implementation

import os
import mimetypes
import json
import sys
import importlib
import traceback
from datetime import datetime

# Add the current directory and parent directories to the path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(current_dir, 'app'))

# Add wwwroot directory to path for Azure deployment
wwwroot_dir = '/home/site/wwwroot'
if os.path.exists(wwwroot_dir):
    sys.path.insert(0, wwwroot_dir)
    sys.path.insert(0, os.path.join(wwwroot_dir, 'app'))

# Print the Python path for debugging
print("Python path:")
for p in sys.path:
    print(f"  {p}")

# Define variables for agent functions
get_agent_response = None
get_conversation_history = None
list_conversations = None
delete_conversation = None
get_agent_factory = None
get_db = None
get_tenant_id = None
REAL_AGENTS_AVAILABLE = False

# Try to import the agent router functions
try:
    print("Attempting to import agent modules...")
    
    # List all directories in app to help with debugging
    app_dir = os.path.join(current_dir, 'app')
    if os.path.exists(app_dir):
        print("App directory contents:")
        for item in os.listdir(app_dir):
            print(f"  {item}")
    
    # Try all possible import paths
    import_paths = [
        # Direct import
        {
            'router': 'app.agents.agent_router',
            'factory': 'app.agents.agent_factory',
            'session': 'app.db.session',
            'tenant': 'app.middleware.tenant'
        },
        # Without app prefix
        {
            'router': 'agents.agent_router',
            'factory': 'agents.agent_factory',
            'session': 'db.session',
            'tenant': 'middleware.tenant'
        },
        # From wwwroot
        {
            'router': 'app_adapter.app.agents.agent_router',
            'factory': 'app_adapter.app.agents.agent_factory',
            'session': 'app_adapter.app.db.session',
            'tenant': 'app_adapter.app.middleware.tenant'
        }
    ]
    
    imported = False
    for path in import_paths:
        try:
            print(f"Trying import path: {path['router']}")
            router_module = importlib.import_module(path['router'])
            factory_module = importlib.import_module(path['factory'])
            session_module = importlib.import_module(path['session'])
            tenant_module = importlib.import_module(path['tenant'])
            
            # Get the functions from the modules
            get_agent_response = getattr(router_module, 'get_agent_response')
            get_conversation_history = getattr(router_module, 'get_conversation_history')
            list_conversations = getattr(router_module, 'list_conversations')
            delete_conversation = getattr(router_module, 'delete_conversation')
            get_agent_factory = getattr(factory_module, 'get_agent_factory')
            get_db = getattr(session_module, 'get_db')
            get_tenant_id = getattr(tenant_module, 'get_tenant_id')
            
            # Import Session class
            from sqlalchemy.orm import Session
            
            REAL_AGENTS_AVAILABLE = True
            print(f"✅ Successfully imported real agent implementation using path: {path['router']}")
            imported = True
            break
        except ImportError as e:
            print(f"Import failed for path {path['router']}: {str(e)}")
            continue
        except Exception as e:
            print(f"Unexpected error for path {path['router']}: {str(e)}")
            traceback.print_exc()
            continue
    
    if not imported:
        raise ImportError("Could not import agent modules from any known path")
            
except ImportError as e:
    REAL_AGENTS_AVAILABLE = False
    print(f"Failed to import real agent implementation: {str(e)}")
    traceback.print_exc()
except Exception as e:
    REAL_AGENTS_AVAILABLE = False
    print(f"Unexpected error during agent import: {str(e)}")
    traceback.print_exc()

def app(environ, start_response):
    """
    Simple WSGI application that serves static files from the saas directory
    and routes API requests to the appropriate handlers.
    """
    # Get the requested path
    path_info = environ.get('PATH_INFO', '/')
    
    # Route API requests
    if path_info.startswith('/api/') or path_info.startswith('/auth/') or path_info.startswith('/subscription/'):
        # For agent-related endpoints, try to use the real implementation if available
        if REAL_AGENTS_AVAILABLE and path_info.startswith('/api/agents/'):
            try:
                # Handle agent-related endpoints
                if path_info == '/api/agents/available':
                    # Get available agents
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # Get agent factory with tenant context
                    agent_factory = get_agent_factory(db=db, organization_id=organization_id)
                    
                    # Get available agents
                    from app.agents.api_router import AGENT_METADATA, SUBSCRIPTION_TIERS
                    
                    # Default to enterprise tier to make all agents available
                    subscription_tier = "enterprise"
                    tier_level = SUBSCRIPTION_TIERS.get(subscription_tier, 2)
                    
                    # Build list of agents with availability information
                    agents = []
                    for agent_type, metadata in AGENT_METADATA.items():
                        agent_tier = metadata["subscription_tier"]
                        agent_tier_level = SUBSCRIPTION_TIERS.get(agent_tier, 0)
                        
                        # Check if agent is available for current subscription
                        available = tier_level >= agent_tier_level
                        
                        agents.append({
                            "agent_type": agent_type,
                            "name": metadata["name"],
                            "description": metadata["description"],
                            "icon": metadata["icon"],
                            "available": available,
                            "subscription_tier": agent_tier
                        })
                    
                    # Prepare response
                    response_data = {
                        "agents": agents,
                        "organization_id": organization_id,
                        "subscription_tier": subscription_tier,
                        "using_real_agents": True
                    }
                    
                    # Convert to JSON
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info.startswith('/api/agents/conversations/') and environ.get('REQUEST_METHOD') == 'GET':
                    # Get conversation history
                    conversation_id = path_info.split('/')[-1]
                    
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # Get conversation history
                    result = get_conversation_history(
                        conversation_id=conversation_id,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info == '/api/agents/conversations' and environ.get('REQUEST_METHOD') == 'GET':
                    # List conversations
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # List conversations
                    result = list_conversations(
                        limit=100,
                        offset=0,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info.startswith('/api/agents/conversations/') and environ.get('REQUEST_METHOD') == 'DELETE':
                    # Delete conversation
                    conversation_id = path_info.split('/')[-1]
                    
                    # Create a database session
                    db = next(get_db())
                    
                    # Get tenant ID from request
                    organization_id = get_tenant_id(environ) if environ else None
                    
                    # Delete conversation
                    result = delete_conversation(
                        conversation_id=conversation_id,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info == '/api/agents/message' and environ.get('REQUEST_METHOD') == 'POST':
                    # Get the request body
                    try:
                        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                    except (ValueError):
                        request_body_size = 0
                        
                    request_body = environ['wsgi.input'].read(request_body_size)
                    
                    # Parse the request body
                    try:
                        request_data = json.loads(request_body)
                        agent_type = request_data.get('agent_type', 'coordinator')
                        message = request_data.get('message', '')
                        conversation_id = request_data.get('conversation_id')
                    except:
                        agent_type = 'coordinator'
                        message = ''
                        conversation_id = None
                    
                    # Create a database session
                    db = next(get_db())
                    
                    # Get agent response
                    result = get_agent_response(
                        agent_type=agent_type,
                        message=message,
                        conversation_id=conversation_id,
                        request=None,
                        db=db,
                        current_user_id=1  # Default user ID
                    )
                    
                    # Add flag to indicate real agent was used
                    result["using_real_agent"] = True
                    
                    # Convert to JSON
                    response_json = json.dumps(result).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                elif path_info == '/api/agents/analytics' and environ.get('REQUEST_METHOD') == 'GET':
                    # Mock response for analytics
                    response_data = {
                        "total_conversations": 0,
                        "conversations_by_agent": [],
                        "messages_by_agent": [],
                        "conversations_by_date": [],
                        "feedback": {
                            "total_count": 0,
                            "average_rating": 0,
                            "distribution": [],
                            "by_agent": []
                        },
                        "organization_id": None
                    }
                    
                    # Convert to JSON
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    # Send the response
                    status = '200 OK'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
                else:
                    # Default API response for agent endpoints
                    response_data = {"message": "Agent API endpoint not implemented"}
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    status = '404 Not Found'
                    headers = [('Content-type', 'application/json'), ('Content-Length', str(len(response_json)))]
                    start_response(status, headers)
                    return [response_json]
                    
            except Exception as e:
                # Log the error
                print(f"Error in agent endpoint: {str(e)}")
                traceback.print_exc()
                
                # Fall back to mock responses
                print("Falling back to mock responses")
                
                # Continue with mock responses below
        
        # For now, return a mock response for API requests
        if path_info == '/api/agents/available':
            # Mock response for available agents
            response_data = {
                "agents": [
                    {
                        "agent_type": "coordinator",
                        "name": "Event Coordinator",
                        "description": "Orchestrates the event planning process and delegates tasks to specialized agents",
                        "icon": "bi-diagram-3",
                        "available": True,
                        "subscription_tier": "free"
                    },
                    {
                        "agent_type": "resource_planning",
                        "name": "Resource Planner",
                        "description": "Plans and manages resources needed for your event",
                        "icon": "bi-calendar-check",
                        "available": True,
                        "subscription_tier": "free"
                    },
                    {
                        "agent_type": "financial",
                        "name": "Financial Advisor",
                        "description": "Handles budgeting, cost estimation, and financial planning",
                        "icon": "bi-cash-coin",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "stakeholder_management",
                        "name": "Stakeholder Manager",
                        "description": "Manages communication and relationships with event stakeholders",
                        "icon": "bi-people",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "marketing_communications",
                        "name": "Marketing Specialist",
                        "description": "Creates marketing strategies and communication plans",
                        "icon": "bi-megaphone",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type": "project_management",
                        "name": "Project Manager",
                        "description": "Manages timelines, tasks, and overall project execution",
                        "icon": "bi-kanban",
                        "available": True,
                        "subscription_tier": "professional"
                    },
                    {
                        "agent_type":
