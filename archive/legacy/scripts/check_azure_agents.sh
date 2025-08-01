#!/bin/bash
# Script to check if the AI agents are working correctly in the Azure deployment

set -e

# Configuration
APP_URL="https://ai-event-planner-saas-py.azurewebsites.net"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Checking if the AI agents are working correctly in the Azure deployment..."

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Output will not be formatted.${NC}"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Check the health endpoint
echo -e "\n${YELLOW}Checking health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "${APP_URL}/health")
echo "Health response:"
if [ "$JQ_AVAILABLE" = true ]; then
    echo "$HEALTH_RESPONSE" | jq
else
    echo "$HEALTH_RESPONSE"
fi

# Check if real agents are available
if [[ "$HEALTH_RESPONSE" == *"real_agents_available\":true"* ]]; then
    echo -e "${GREEN}Real agents are available!${NC}"
else
    echo -e "${RED}Real agents are not available.${NC}"
fi

# Check the available agents endpoint
echo -e "\n${YELLOW}Checking available agents endpoint...${NC}"
AGENTS_RESPONSE=$(curl -s "${APP_URL}/api/agents/available")
echo "Available agents response:"
if [ "$JQ_AVAILABLE" = true ]; then
    echo "$AGENTS_RESPONSE" | jq
else
    echo "$AGENTS_RESPONSE"
fi

# Send a test message to the coordinator agent
echo -e "\n${YELLOW}Sending a test message to the coordinator agent...${NC}"
MESSAGE_RESPONSE=$(curl -s -X POST "${APP_URL}/api/agents/message" \
    -H "Content-Type: application/json" \
    -d '{"agent_type":"coordinator","message":"Hello, I need help planning an event."}')
echo "Message response:"
if [ "$JQ_AVAILABLE" = true ]; then
    echo "$MESSAGE_RESPONSE" | jq
else
    echo "$MESSAGE_RESPONSE"
fi

# Check if the response is a mock response or a real response
if [[ "$MESSAGE_RESPONSE" == *"This is a mock response"* ]]; then
    echo -e "${RED}The agent is still using mock responses.${NC}"
else
    echo -e "${GREEN}The agent is using real responses!${NC}"
fi

echo -e "\n${GREEN}Check completed.${NC}"
echo "Your application is available at: ${APP_URL}"
