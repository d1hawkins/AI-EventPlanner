#!/bin/bash
# Final fix for Azure agents - wait for dependencies and restart

set -e

APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Final Agent Fix - Completing Installation${NC}"

echo -e "${BLUE}Step 1: Waiting for current dependency installation to complete...${NC}"
sleep 30

echo -e "${BLUE}Step 2: Restarting application to reload with new dependencies...${NC}"
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

echo -e "${YELLOW}Waiting 45 seconds for restart...${NC}"
sleep 45

echo -e "${BLUE}Step 3: Testing agents endpoint...${NC}"

# Test the agents endpoint multiple times
for i in {1..3}; do
    echo "Test attempt $i..."
    AGENTS_RESPONSE=$(curl -s "https://$APP_NAME.azurewebsites.net/api/agents/available" || echo "FAILED")
    
    if [[ "$AGENTS_RESPONSE" == *"agents"* ]] && [[ "$AGENTS_RESPONSE" != *"not implemented"* ]]; then
        echo -e "${GREEN}✅ Agents endpoint is working!${NC}"
        echo "Response preview: $(echo $AGENTS_RESPONSE | head -c 300)..."
        break
    else
        echo -e "${YELLOW}⏳ Still loading... (attempt $i/3)${NC}"
        if [ $i -lt 3 ]; then
            sleep 20
        fi
    fi
done

echo -e "${BLUE}Step 4: Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "https://$APP_NAME.azurewebsites.net/health" || echo "FAILED")
echo "Health check: $HEALTH_RESPONSE"

echo -e "${BLUE}Step 5: Final status check...${NC}"

# Final test
FINAL_TEST=$(curl -s "https://$APP_NAME.azurewebsites.net/api/agents/available" || echo "FAILED")

if [[ "$FINAL_TEST" == *"agents"* ]] && [[ "$FINAL_TEST" != *"not implemented"* ]]; then
    echo -e "${GREEN}🎉 SUCCESS! Agents are now working on Azure!${NC}"
    echo ""
    echo -e "${GREEN}✅ SaaS Site: RUNNING${NC}"
    echo -e "${GREEN}✅ Agents: WORKING${NC}"
    echo ""
    echo "You can now:"
    echo "1. Visit your SaaS site: https://$APP_NAME.azurewebsites.net"
    echo "2. Go to the Agents page and start chatting with AI agents"
    echo "3. Test different agent types (Coordinator, Resource Planner, etc.)"
else
    echo -e "${RED}❌ Agents still not fully working${NC}"
    echo "Response: $FINAL_TEST"
    echo ""
    echo "Try running the comprehensive logging setup:"
    echo "./setup-azure-logging-comprehensive.sh"
fi

echo -e "${GREEN}✅ Final agent fix completed!${NC}"
