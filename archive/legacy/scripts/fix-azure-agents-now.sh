#!/bin/bash
# Fix Azure agents by installing missing dependencies and setting correct environment variables

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Fixing Azure Agents - Installing Dependencies and Configuring Environment${NC}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Installing missing Python dependencies...${NC}"

# Set environment variables to ensure dependencies are installed
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
    "ENABLE_ORYX_BUILD=true" \
    "POST_BUILD_SCRIPT_PATH=install_agent_deps.sh"

echo -e "${BLUE}Step 2: Setting agent-specific environment variables...${NC}"

# Set critical environment variables for agents
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    "GOOGLE_API_KEY=your-google-api-key-here" \
    "OPENAI_API_KEY=your-openai-api-key-here" \
    "LLM_PROVIDER=google" \
    "SECRET_KEY=your-secret-key-here-$(date +%s)" \
    "DATABASE_URL=sqlite:///./app.db" \
    "ENABLE_AGENT_LOGGING=true" \
    "AGENT_MEMORY_STORAGE=file" \
    "AGENT_MEMORY_PATH=/home/site/wwwroot/agent_memory" \
    "ENVIRONMENT=production" \
    "APP_VERSION=1.0.0" \
    "APP_NAME=AI Event Planner"

echo -e "${BLUE}Step 3: Creating a dependency installation script...${NC}"

# Create a script to install dependencies during deployment
cat > install_agent_deps.sh << 'EOF'
#!/bin/bash
echo "Installing agent dependencies..."
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.0
pip install langchain==0.0.350
pip install langgraph==0.0.62
pip install google-generativeai==0.3.2
pip install openai==1.3.7
pip install python-dotenv==1.0.0
pip install psycopg2-binary==2.9.9
pip install alembic==1.13.1
echo "Agent dependencies installed successfully"
EOF

chmod +x install_agent_deps.sh

echo -e "${BLUE}Step 4: Uploading dependency script to Azure...${NC}"

# Upload the script to Azure using the Kudu API
# First, get the publishing credentials
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles --resource-group $RESOURCE_GROUP --name $APP_NAME --query "[?publishMethod=='MSDeploy'].{username:userName, password:userPWD}" -o json)
USERNAME=$(echo $PUBLISH_PROFILE | jq -r '.[0].username')
PASSWORD=$(echo $PUBLISH_PROFILE | jq -r '.[0].password')

# Upload the script using curl
echo "Uploading dependency installation script..."
curl -X PUT "https://$APP_NAME.scm.azurewebsites.net/api/vfs/site/wwwroot/install_agent_deps.sh" \
     -u "$USERNAME:$PASSWORD" \
     --data-binary @install_agent_deps.sh \
     -H "Content-Type: application/octet-stream"

echo -e "${BLUE}Step 5: Updating startup command to use enhanced startup script...${NC}"

# Update startup command to use our enhanced startup script
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "bash install_agent_deps.sh && gunicorn app_adapter:app --bind=0.0.0.0:8000 --timeout=300 --workers=1 --log-level=debug"

echo -e "${BLUE}Step 6: Restarting the application...${NC}"

# Restart the app
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

echo -e "${YELLOW}Waiting 45 seconds for restart and dependency installation...${NC}"
sleep 45

echo -e "${BLUE}Step 7: Testing agent endpoints...${NC}"

# Test the agents endpoint
echo "Testing /api/agents/available endpoint..."
AGENTS_RESPONSE=$(curl -s "https://$APP_NAME.azurewebsites.net/api/agents/available" || echo "FAILED")

if [[ "$AGENTS_RESPONSE" == *"agents"* ]]; then
    echo -e "${GREEN}✅ Agents endpoint is responding!${NC}"
    echo "Response preview: $(echo $AGENTS_RESPONSE | head -c 200)..."
else
    echo -e "${RED}❌ Agents endpoint still not working${NC}"
    echo "Response: $AGENTS_RESPONSE"
fi

echo -e "${BLUE}Step 8: Streaming logs to check agent status...${NC}"
echo "Press Ctrl+C to stop log streaming"
echo ""

# Stream logs to see what's happening
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME
