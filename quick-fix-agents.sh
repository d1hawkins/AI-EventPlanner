#!/bin/bash
# Quick fix for Azure agents - simpler approach

set -e

APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Fix for Azure Agents${NC}"

echo -e "${BLUE}Step 1: Setting essential environment variables...${NC}"

# Set the most critical environment variables
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    "GOOGLE_API_KEY=your-google-api-key-here" \
    "SECRET_KEY=ai-event-planner-secret-$(date +%s)" \
    "DATABASE_URL=sqlite:///./app.db" \
    "LLM_PROVIDER=google" \
    "ENVIRONMENT=production"

echo -e "${BLUE}Step 2: Updating startup command with dependency installation...${NC}"

# Update startup to install dependencies first
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "pip install fastapi uvicorn sqlalchemy pydantic langchain langgraph google-generativeai python-dotenv && gunicorn app_adapter:app --bind=0.0.0.0:8000 --timeout=300 --workers=1 --log-level=debug"

echo -e "${BLUE}Step 3: Restarting application...${NC}"

az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

echo -e "${YELLOW}Waiting 60 seconds for restart and dependency installation...${NC}"
sleep 60

echo -e "${BLUE}Step 4: Testing agents endpoint...${NC}"

# Test the agents endpoint
AGENTS_RESPONSE=$(curl -s "https://$APP_NAME.azurewebsites.net/api/agents/available" || echo "FAILED")

if [[ "$AGENTS_RESPONSE" == *"agents"* ]] || [[ "$AGENTS_RESPONSE" == *"["* ]]; then
    echo -e "${GREEN}✅ Agents endpoint is responding!${NC}"
    echo "Response: $AGENTS_RESPONSE"
else
    echo -e "${RED}❌ Agents endpoint still not working${NC}"
    echo "Response: $AGENTS_RESPONSE"
    
    echo -e "${YELLOW}Checking logs for more details...${NC}"
    az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME --lines 20
fi

echo -e "${GREEN}✅ Quick fix completed!${NC}"
