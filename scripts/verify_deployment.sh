#!/bin/bash

# Azure Deployment Verification Script
# This script verifies the deployed application is working correctly with real agents

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Azure Deployment Verification            ║${NC}"
echo -e "${BLUE}║  AI Event Planner SaaS                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Configuration
APP_NAME="ai-event-planner-saas-py"
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo -e "${BLUE}Testing deployment at:${NC} $APP_URL"
echo ""

# Test 1: Basic connectivity
echo -e "${YELLOW}[1/5]${NC} Testing basic connectivity..."
if curl -s -o /dev/null -w "%{http_code}" "$APP_URL" | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓${NC} Site is accessible"
else
    echo -e "${RED}✗${NC} Site is not accessible"
    echo "   The site may still be starting up. Wait a few minutes and try again."
    exit 1
fi

# Test 2: Health endpoint
echo ""
echo -e "${YELLOW}[2/5]${NC} Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s "${APP_URL}/health" || echo "{}")

if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
    echo -e "${GREEN}✓${NC} Health endpoint is responding"
    
    # Parse health response
    STATUS=$(echo "$HEALTH_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    REAL_AGENTS=$(echo "$HEALTH_RESPONSE" | grep -o '"real_agents_available":[^,}]*' | cut -d':' -f2)
    AGENT_TEST=$(echo "$HEALTH_RESPONSE" | grep -o '"using_real_agent":[^,}]*' | cut -d':' -f2 | tr -d ' ')
    
    echo "   Status: $STATUS"
    echo "   Real agents available: $REAL_AGENTS"
    echo "   Agent test result: $AGENT_TEST"
    
    if [ "$AGENT_TEST" = "true" ]; then
        echo -e "   ${GREEN}✓${NC} Real agents are working!"
    elif [ "$AGENT_TEST" = "false" ]; then
        echo -e "   ${YELLOW}⚠${NC}  Agents are running but may be using mock responses"
        echo "   Check that API keys are configured correctly in Azure"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Health endpoint not responding as expected"
    echo "   Response: $HEALTH_RESPONSE"
fi

# Test 3: Debug endpoint for environment variables
echo ""
echo -e "${YELLOW}[3/5]${NC} Checking environment configuration..."
DEBUG_RESPONSE=$(curl -s "${APP_URL}/debug/env" || echo "{}")

if echo "$DEBUG_RESPONSE" | grep -q '"tavily_key_present"'; then
    echo -e "${GREEN}✓${NC} Debug endpoint is responding"
    
    TAVILY_PRESENT=$(echo "$DEBUG_RESPONSE" | grep -o '"tavily_key_present":[^,}]*' | cut -d':' -f2)
    GOOGLE_PRESENT=$(echo "$DEBUG_RESPONSE" | grep -o '"google_key_present":[^,}]*' | cut -d':' -f2)
    LLM_MODEL=$(echo "$DEBUG_RESPONSE" | grep -o '"llm_model_value":"[^"]*"' | cut -d'"' -f4)
    
    echo "   Tavily API Key: $TAVILY_PRESENT"
    echo "   Google API Key: $GOOGLE_PRESENT"
    echo "   LLM Model: $LLM_MODEL"
    
    if [ "$TAVILY_PRESENT" = "true" ] && [ "$GOOGLE_PRESENT" = "true" ]; then
        echo -e "   ${GREEN}✓${NC} All required API keys are configured"
    else
        echo -e "   ${YELLOW}⚠${NC}  Some API keys are missing"
        echo "   Run: az webapp config appsettings set to add missing keys"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Debug endpoint not responding as expected"
fi

# Test 4: Azure App Service status
echo ""
echo -e "${YELLOW}[4/5]${NC} Checking Azure Web App status..."
if command -v az &> /dev/null; then
    APP_STATE=$(az webapp show --name "$APP_NAME" --resource-group "ai-event-planner-rg" --query "state" -o tsv 2>/dev/null || echo "Unknown")
    
    if [ "$APP_STATE" = "Running" ]; then
        echo -e "${GREEN}✓${NC} Azure Web App is running"
    else
        echo -e "${YELLOW}⊘${NC}  Azure Web App state: $APP_STATE"
    fi
else
    echo -e "${YELLOW}⊘${NC}  Azure CLI not available, skipping Azure status check"
fi

# Test 5: Recent logs check
echo ""
echo -e "${YELLOW}[5/5]${NC} Checking recent deployment logs..."
if command -v az &> /dev/null; then
    echo "Fetching last 20 log entries..."
    echo ""
    az webapp log tail --name "$APP_NAME" --resource-group "ai-event-planner-rg" --only-show-errors 2>/dev/null | head -20 || echo "Unable to fetch logs"
else
    echo -e "${YELLOW}⊘${NC}  Azure CLI not available, skipping log check"
    echo "   Install Azure CLI to view logs: brew install azure-cli"
fi

# Summary
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Verification Summary                     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo "Application URL: $APP_URL"
echo ""

if [ "$AGENT_TEST" = "true" ]; then
    echo -e "${GREEN}✓${NC} Deployment successful with real agents working!"
    echo ""
    echo "Next steps:"
    echo "  1. Visit: $APP_URL"
    echo "  2. Test the agent chat interface"
    echo "  3. Monitor logs: az webapp log tail --name $APP_NAME --resource-group ai-event-planner-rg"
else
    echo -e "${YELLOW}⚠${NC}  Deployment is live but agents may not be fully configured"
    echo ""
    echo "To enable real agents, ensure these secrets are set:"
    echo "  • OPENAI_API_KEY"
    echo "  • GOOGLE_API_KEY"  
    echo "  • TAVILY_API_KEY"
    echo ""
    echo "Run: ./scripts/setup_github_secrets.sh"
    echo "Then: ./scripts/deploy_via_github.sh"
fi

echo ""
echo "For detailed logs, run:"
echo -e "  ${BLUE}az webapp log tail --name $APP_NAME --resource-group ai-event-planner-rg${NC}"
echo ""
