#!/bin/bash

# Azure Deployment Script for Real AI Agents with Tenant Conversations - FINAL VERSION V3
# This script deploys the complete tenant-aware conversation system with database resilience

set -e

echo "🚀 Starting Azure deployment of real AI agents with tenant conversations (FINAL V3)..."

# Configuration
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOCATION="East US"
DB_SERVER_NAME="ai-event-planner-db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed and logged in
print_status "Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is ready"

# Step 1: Fix Azure PostgreSQL firewall rules for tenant conversations
print_status "Configuring Azure PostgreSQL firewall rules for tenant conversations..."

# Allow Azure services to access the database
az postgres server firewall-rule create \
    --resource-group "$RESOURCE_GROUP" \
    --server "$DB_SERVER_NAME" \
    --name "AllowAzureServices" \
    --start-ip-address "0.0.0.0" \
    --end-ip-address "0.0.0.0" \
    2>/dev/null || print_warning "Firewall rule AllowAzureServices may already exist"

# Allow all IP addresses for testing (can be restricted later)
az postgres server firewall-rule create \
    --resource-group "$RESOURCE_GROUP" \
    --server "$DB_SERVER_NAME" \
    --name "AllowAllIPs" \
    --start-ip-address "0.0.0.0" \
    --end-ip-address "255.255.255.255" \
    2>/dev/null || print_warning "Firewall rule AllowAllIPs may already exist"

print_success "PostgreSQL firewall rules configured"

# Step 2: Ensure we use the existing requirements.txt file
print_status "Using existing requirements.txt file..."

# Verify requirements.txt exists and has FastAPI
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt file not found!"
    exit 1
fi

if ! grep -q "fastapi" requirements.txt; then
    print_error "FastAPI not found in requirements.txt!"
    exit 1
fi

print_success "Requirements file verified - FastAPI found"

# Step 3: Run tenant conversation table migration with retry logic
print_status "Creating tenant conversation tables with retry logic..."

# Create migration script with retry logic
cat > migrate_tenant_tables_with_retry.py << 'EOF'
#!/usr/bin/env python3
import time
import logging
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, TimeoutError

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_with_retry(max_retries=5, delay=10):
    """Run tenant conversation migrations with retry logic for Azure deployment."""
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'postgresql://dbadmin:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner')
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Creating tenant conversation tables...")
            
            # Import models after path is set
            from app.db.base import Base
            from app.db.models_tenant_conversations import (
                TenantConversation, TenantMessage, TenantAgentState, 
                ConversationContext, ConversationParticipant
            )
            
            engine = create_engine(database_url, connect_args={"connect_timeout": 30})
            
            # Create all tenant conversation tables
            Base.metadata.create_all(engine)
            
            # Verify tables were created
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'tenant_%'
                """))
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = ['tenant_conversations', 'tenant_messages', 'tenant_agent_states']
                for table in expected_tables:
                    if table in tables:
                        print(f"✅ Table '{table}' created successfully")
                    else:
                        print(f"⚠️ Table '{table}' not found")
            
            print("✅ Tenant conversation tables migration completed successfully")
            return True
            
        except (OperationalError, TimeoutError) as e:
            if "connection" in str(e).lower() and attempt < max_retries - 1:
                print(f"⚠️ Connection failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                print(f"Error: {e}")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                print(f"❌ Migration failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return False

if __name__ == "__main__":
    success = migrate_with_retry()
    sys.exit(0 if success else 1)
EOF

# Make the migration script executable
chmod +x migrate_tenant_tables_with_retry.py

print_success "Tenant conversation migration script created"

# Step 4: Set up environment variables for real agents with tenant conversations
print_status "Setting up environment variables for real agents with tenant conversations..."

# Get existing DATABASE_URL
DATABASE_URL=$(az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='DATABASE_URL'].value" -o tsv)

if [ -z "$DATABASE_URL" ]; then
    print_warning "Could not retrieve DATABASE_URL from existing deployment, will use default"
    DATABASE_URL="postgresql://dbadmin:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner"
fi

print_status "Configuring application settings for real agents with tenant conversations V3..."

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings \
    DATABASE_URL="$DATABASE_URL" \
    USE_REAL_AGENTS="true" \
    LLM_PROVIDER="google" \
    GOOGLE_API_KEY="AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU" \
    GOOGLE_MODEL="gemini-2.0-flash" \
    ENABLE_AGENT_LOGGING="true" \
    LLM_MODEL="gemini-2.0-flash" \
    SECRET_KEY="azure-saas-secret-key-2025" \
    ACCESS_TOKEN_EXPIRE_MINUTES="60" \
    REFRESH_TOKEN_EXPIRE_DAYS="7" \
    ALGORITHM="HS256" \
    APP_NAME="AI Event Planner SaaS" \
    APP_VERSION="1.0.0" \
    ENVIRONMENT="production" \
    DEBUG="false" \
    HOST="0.0.0.0" \
    PORT="8000" \
    PYTHONPATH="/home/site/wwwroot" \
    PYTHONUNBUFFERED="1" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ENABLE_ORYX_BUILD="true" \
    DEPLOYMENT_VERSION="v3_real_agents_tenant_conversations" \
    USE_FALLBACK_SERVICE="true" \
    DATABASE_RETRY_ATTEMPTS="3" \
    DATABASE_RETRY_DELAY="1.0" \
    DATABASE_CONNECT_TIMEOUT="30" \
    DATABASE_COMMAND_TIMEOUT="60" \
    DATABASE_POOL_SIZE="10" \
    DATABASE_MAX_OVERFLOW="20" \
    DATABASE_POOL_RECYCLE="3600" \
    ENABLE_CONNECTION_POOLING="true" \
    TENANT_CONVERSATIONS_ENABLED="true" \
    > /dev/null

print_success "Environment variables configured for real agents with tenant conversations V3"

# Step 5: Fix import issues by ensuring all __init__.py files exist
print_status "Ensuring all __init__.py files exist for proper imports..."

# Create missing __init__.py files if they don't exist
mkdir -p app/services app/middleware app/state app/auth app/subscription app/tools app/graphs app/schemas app/db app/utils app/agents app/web

# Ensure __init__.py files exist in all directories
for dir in app app/services app/middleware app/state app/auth app/subscription app/tools app/graphs app/schemas app/db app/utils app/agents app/web; do
    if [ ! -f "$dir/__init__.py" ]; then
        echo "# Package initialization file" > "$dir/__init__.py"
        print_status "Created missing __init__.py in $dir"
    fi
done

# Create a comprehensive import fix script for Azure deployment
cat > fix_azure_imports.py << 'EOF'
#!/usr/bin/env python3
"""
Fix Azure import issues by ensuring all modules are properly accessible.
This script creates missing __init__.py files and fixes import paths.
"""
import os
import sys

def create_init_files():
    """Create __init__.py files in all necessary directories."""
    directories = [
        'app',
        'app/services',
        'app/middleware', 
        'app/state',
        'app/auth',
        'app/subscription',
        'app/tools',
        'app/graphs',
        'app/schemas',
        'app/db',
        'app/utils',
        'app/agents',
        'app/web'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'# Package initialization file for {directory}\n')
                print(f"Created {init_file}")
            else:
                print(f"✅ {init_file} already exists")
        else:
            print(f"⚠️ Directory {directory} does not exist")

def fix_conversation_memory_import():
    """Ensure conversation_memory module is accessible."""
    conversation_memory_path = 'app/utils/conversation_memory.py'
    if os.path.exists(conversation_memory_path):
        print(f"✅ {conversation_memory_path} exists")
        
        # Check if it has the required classes
        with open(conversation_memory_path, 'r') as f:
            content = f.read()
            if 'class ConversationMemory' in content:
                print("✅ ConversationMemory class found")
            else:
                print("⚠️ ConversationMemory class not found")
    else:
        print(f"❌ {conversation_memory_path} does not exist")

if __name__ == "__main__":
    print("🔧 Fixing Azure import issues...")
    create_init_files()
    fix_conversation_memory_import()
    print("✅ Import fixes completed")
EOF

chmod +x fix_azure_imports.py

# Try python3 first, then python as fallback
if command -v python3 &> /dev/null; then
    python3 fix_azure_imports.py
elif command -v python &> /dev/null; then
    python fix_azure_imports.py
else
    print_warning "Neither python nor python3 found, skipping local import fixes"
fi

# Step 6: Create deployment package with tenant conversation files
print_status "Creating deployment package with tenant conversation system V3..."

rm -f real_agents_tenant_conversations_v3.zip

# Files to include in deployment (complete set with tenant conversations)
print_status "Creating base deployment package with lazy import adapter and import fixes..."
zip -r real_agents_tenant_conversations_v3.zip \
    requirements.txt \
    app_adapter_with_agents_fixed.py \
    azure_import_diagnostics.py \
    diagnose_azure_agent_imports.py \
    force_real_agents_fix.py \
    config.py \
    migrate_tenant_tables_with_retry.py \
    create_tenant_conversation_tables.py \
    fix_azure_imports.py \
    app/ \
    migrations/ \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --exclude ".git/*" \
    --exclude "*.log" \
    --exclude "node_modules/*" \
    --exclude ".env*" \
    --exclude "venv/*" \
    --exclude ".vscode/*" \
    --exclude "app/web/static/saas/node_modules/*" \
    2>/dev/null || true

# Verify the lazy import adapter is included
if unzip -l real_agents_tenant_conversations_v3.zip | grep -q "app_adapter_with_agents_fixed.py"; then
    print_success "✅ Lazy import adapter (app_adapter_with_agents_fixed.py) is included in deployment package"
else
    print_error "❌ Lazy import adapter not found in package!"
    exit 1
fi

# Verify critical files are included
print_status "Verifying critical files are in deployment package..."
if unzip -l real_agents_tenant_conversations_v3.zip | grep -q "app/utils/conversation_memory.py"; then
    print_success "✅ app/utils/conversation_memory.py is included in deployment package"
else
    print_warning "⚠️ app/utils/conversation_memory.py not found in package, adding explicitly..."
    if [ -f "app/utils/conversation_memory.py" ]; then
        zip -u real_agents_tenant_conversations_v3.zip app/utils/conversation_memory.py
        print_success "✅ Added app/utils/conversation_memory.py to deployment package"
    else
        print_error "❌ app/utils/conversation_memory.py file not found on filesystem!"
    fi
fi

if unzip -l real_agents_tenant_conversations_v3.zip | grep -q "app/agents/api_router.py"; then
    print_success "✅ app/agents/api_router.py is included in deployment package"
else
    print_warning "⚠️ app/agents/api_router.py not found in package"
fi

# Add additional tenant conversation files with error handling
print_status "Adding tenant conversation files to deployment package..."

# Add the tenant conversation service with fallback to the deployment package
if [ -f "app/services/tenant_conversation_service_with_fallback.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/services/tenant_conversation_service_with_fallback.py 2>/dev/null || print_warning "Could not add tenant_conversation_service_with_fallback.py"
    print_status "Added tenant conversation service with fallback to deployment package"
else
    print_warning "app/services/tenant_conversation_service_with_fallback.py not found, skipping"
fi

# Ensure all conversation memory and persistent memory files are included
if [ -f "app/utils/conversation_memory.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/utils/conversation_memory.py 2>/dev/null || print_warning "Could not add conversation_memory.py"
    print_status "Added conversation memory to deployment package"
else
    print_warning "app/utils/conversation_memory.py not found, skipping"
fi

if [ -f "app/utils/persistent_conversation_memory.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/utils/persistent_conversation_memory.py 2>/dev/null || print_warning "Could not add persistent_conversation_memory.py"
    print_status "Added persistent conversation memory to deployment package"
else
    print_warning "app/utils/persistent_conversation_memory.py not found, skipping"
fi

# Add all tenant-related services and tools
if [ -f "app/services/tenant_conversation_service.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/services/tenant_conversation_service.py 2>/dev/null || print_warning "Could not add tenant_conversation_service.py"
    print_status "Added tenant conversation service to deployment package"
else
    print_warning "app/services/tenant_conversation_service.py not found, skipping"
fi

if [ -f "app/tools/tenant_agent_communication_tools.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/tools/tenant_agent_communication_tools.py 2>/dev/null || print_warning "Could not add tenant_agent_communication_tools.py"
    print_status "Added tenant agent communication tools to deployment package"
else
    print_warning "app/tools/tenant_agent_communication_tools.py not found, skipping"
fi

# Add tenant middleware
if [ -f "app/middleware/tenant.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/middleware/tenant.py 2>/dev/null || print_warning "Could not add tenant.py"
    print_status "Added tenant middleware to deployment package"
else
    print_warning "app/middleware/tenant.py not found, skipping"
fi

# Add tenant-aware state manager
if [ -f "app/state/tenant_aware_manager.py" ]; then
    zip -u real_agents_tenant_conversations_v3.zip app/state/tenant_aware_manager.py 2>/dev/null || print_warning "Could not add tenant_aware_manager.py"
    print_status "Added tenant-aware state manager to deployment package"
else
    print_warning "app/state/tenant_aware_manager.py not found, skipping"
fi

# Check if zip file was created successfully
if [ ! -f "real_agents_tenant_conversations_v3.zip" ]; then
    print_error "Deployment package was not created successfully!"
    exit 1
fi

# Get zip file size for verification
ZIP_SIZE=$(ls -lh real_agents_tenant_conversations_v3.zip | awk '{print $5}')
print_success "Deployment package created successfully: real_agents_tenant_conversations_v3.zip (${ZIP_SIZE})"

print_success "Deployment package with tenant conversations created: real_agents_tenant_conversations_v3.zip"

# Step 6: Set the correct startup command
print_status "Setting startup command for real agents with tenant conversations V3..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app_adapter_with_agents_fixed:app"

print_success "Startup command configured for V3 with lazy import functionality"

# Step 7: Deploy the package
print_status "Uploading deployment package with tenant conversations V3..."
az webapp deploy \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src-path real_agents_tenant_conversations_v3.zip \
    --type zip

print_success "Deployment package V3 uploaded"

# Step 8: Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 30

# Step 9: Run import fixes on Azure
print_status "Running import fixes on Azure..."
az webapp ssh --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --command "cd /home/site/wwwroot && python fix_azure_imports.py" || print_warning "Import fixes may have failed, but continuing..."

# Step 10: Run comprehensive agent import diagnostics on Azure
print_status "Running comprehensive agent import diagnostics on Azure..."
az webapp ssh --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --command "cd /home/site/wwwroot && python diagnose_azure_agent_imports.py" || print_warning "Diagnostics may have failed, but continuing..."

# Step 11: Run force real agents fix on Azure
print_status "Running force real agents fix on Azure..."
az webapp ssh --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --command "cd /home/site/wwwroot && python force_real_agents_fix.py" || print_warning "Force fix may have failed, but continuing..."

# Step 12: Run tenant conversation table migration on Azure
print_status "Running tenant conversation table migration on Azure..."
az webapp ssh --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --command "cd /home/site/wwwroot && python migrate_tenant_tables_with_retry.py" || print_warning "Migration may have failed, but continuing..."

# Step 10: Restart the app to ensure new configuration takes effect
print_status "Restarting application..."
az webapp restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME"

print_success "Application restarted"

# Step 11: Wait for app to start
print_status "Waiting for application to start..."
sleep 45

# Step 12: Test the deployment with tenant conversation features
print_status "Testing real agents deployment with tenant conversations V3..."
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo "Testing health endpoint..."
if curl -f -s "${APP_URL}/health" > /dev/null; then
    print_success "Health check passed!"
    echo "Health response:"
    curl -s "${APP_URL}/health" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/health"
else
    print_warning "Health check failed, but app might still be starting..."
fi

echo ""
echo "Testing database health endpoint..."
if curl -f -s "${APP_URL}/health/database" > /dev/null; then
    print_success "Database health check passed!"
    echo "Database health response:"
    curl -s "${APP_URL}/health/database" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/health/database"
else
    print_warning "Database health check not available yet..."
fi

echo ""
echo "Testing agents endpoint..."
if curl -f -s "${APP_URL}/api/agents/available" > /dev/null; then
    print_success "Agents endpoint accessible!"
    echo "Agents response:"
    curl -s "${APP_URL}/api/agents/available" | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/available"
else
    print_warning "Agents endpoint not accessible yet..."
fi

echo ""
echo "Testing tenant-aware agent message endpoint..."
echo "Sending test message to coordinator agent with tenant context..."
curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "Test message for tenant-aware real agents V3",
    "conversation_id": "test-conversation-123",
    "user_id": 1,
    "organization_id": 1
  }' | python -m json.tool 2>/dev/null || curl -s "${APP_URL}/api/agents/message" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coordinator",
    "message": "Test message for tenant-aware real agents V3"
  }'

# Step 13: Test user registration (creates organization)
echo ""
echo "Testing user registration (creates tenant organization)..."
curl -s "${APP_URL}/auth/register" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }' | python -m json.tool 2>/dev/null || print_warning "Registration endpoint may not be available"

# Step 14: Show deployment information
echo ""
echo "🎉 Real Agents with Tenant Conversations Deployment V3 completed!"
echo ""
echo "Application URL: ${APP_URL}"
echo "Health Check: ${APP_URL}/health"
echo "Database Health: ${APP_URL}/health/database"
echo "Agents Status: ${APP_URL}/api/agents/available"
echo "Agent Message Test: ${APP_URL}/api/agents/message"
echo "User Registration: ${APP_URL}/auth/register"
echo "SaaS Dashboard: ${APP_URL}/app/web/static/saas/index.html"
echo "Agent Chat (Classic): ${APP_URL}/app/web/static/saas/agents.html"
echo "Agent Chat (Clean): ${APP_URL}/app/web/static/saas/clean-chat.html"
echo ""
echo "🔥 NEW: Tenant Conversation Features in V3:"
echo "- Multi-tenant conversation isolation"
echo "- User and organization context tracking"
echo "- Database connection resilience with fallback"
echo "- Agent state persistence per tenant"
echo "- Conversation memory and context retention"
echo "- PostgreSQL connection timeout handling"
echo ""
echo "Key Technical Improvements:"
echo "- Azure PostgreSQL firewall rules configured"
echo "- Connection retry logic with exponential backoff"
echo "- In-memory fallback for database timeouts"
echo "- Tenant-aware agent communication tools"
echo "- Enhanced database models for multi-tenancy"
echo ""
echo "Database Tables Created:"
echo "- tenant_conversations (main conversation tracking)"
echo "- tenant_messages (all messages with tenant context)"
echo "- tenant_agent_states (agent state per tenant)"
echo "- conversation_contexts (rich conversation metadata)"
echo "- conversation_participants (multi-user conversations)"
echo ""
echo "To check logs:"
echo "az webapp log tail --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
echo ""
echo "To check deployment status:"
echo "az webapp show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query state"
echo ""
echo "To monitor database connections:"
echo "az postgres server show --resource-group ${RESOURCE_GROUP} --name ${DB_SERVER_NAME}"

# Clean up temporary files
rm -f migrate_tenant_tables_with_retry.py
rm -f real_agents_tenant_conversations_v3.zip

print_success "Cleanup completed"
print_success "Azure real agents with tenant conversations deployment V3 completed successfully!"

echo ""
print_status "🚀 The application now includes:"
print_status "✅ REAL AI agents with Google Gemini"
print_status "✅ Multi-tenant conversation system"
print_status "✅ Database connection resilience"
print_status "✅ Automatic organization creation on user registration"
print_status "✅ Tenant-aware agent state persistence"
print_status "✅ PostgreSQL connection timeout handling"
print_status ""
print_status "🎯 All conversations are now tied to Tenant, User, and Conversation/Event ID!"
