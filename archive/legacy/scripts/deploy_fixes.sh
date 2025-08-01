#!/bin/bash
# Deploy fixes for the Azure deployment issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying fixes for Azure deployment issues...${NC}"

# Make scripts executable
chmod +x create_tables_direct.sh
chmod +x fix_agent_mock_responses.py

# Fix 1: Database Tables Not Being Created
echo -e "${YELLOW}Fix 1: Creating database tables...${NC}"
echo "This will create the necessary database tables in your Azure PostgreSQL database."
echo "You will need to provide your database connection details."

# Run the database creation script
./create_tables_direct.sh

# Fix 2: Agents Giving Mock Responses
echo -e "${YELLOW}Fix 2: Fixing agent mock responses...${NC}"
echo "This will modify the agent code to use real agents instead of mock responses."

# Run the agent fix script
./fix_agent_mock_responses.py

# Deploy the fixed files to Azure
echo -e "${YELLOW}Deploying fixed files to Azure...${NC}"
echo "Do you want to deploy the fixed files to Azure? (y/n)"
read DEPLOY_TO_AZURE

if [[ "$DEPLOY_TO_AZURE" == "y" || "$DEPLOY_TO_AZURE" == "Y" ]]; then
    # Check if azure-deploy-saas-complete-fixed.sh exists
    if [ -f "azure-deploy-saas-complete-fixed.sh" ]; then
        chmod +x azure-deploy-saas-complete-fixed.sh
        ./azure-deploy-saas-complete-fixed.sh
    else
        # Create a deployment script
        cat > azure-deploy-saas-complete-fixed.sh << 'EOF'
#!/bin/bash
# Deploy the fixed SaaS application to Azure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying fixed SaaS application to Azure...${NC}"

# Copy the fixed app_adapter_with_agents.py to the deployment directory
cp app_adapter_with_agents_fixed.py app_adapter_with_agents.py

# Deploy to Azure
if [ -f "azure-deploy-saas-complete.sh" ]; then
    chmod +x azure-deploy-saas-complete.sh
    ./azure-deploy-saas-complete.sh
else
    echo -e "${RED}Error: azure-deploy-saas-complete.sh not found${NC}"
    exit 1
fi

echo -e "${GREEN}Deployment complete!${NC}"
EOF
        chmod +x azure-deploy-saas-complete-fixed.sh
        ./azure-deploy-saas-complete-fixed.sh
    fi
fi

echo -e "${GREEN}Fixes deployed successfully!${NC}"
echo "Please verify that:"
echo "1. Database tables have been created"
echo "2. Agents are giving real responses instead of mock responses"
echo ""
echo "To verify database tables, you can connect to your PostgreSQL database and run:"
echo "  SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
echo ""
echo "To verify agents are giving real responses, check for the 'using_real_agent': true flag in API responses."
