#!/bin/bash
# Complete the deployment process with the fixed files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Make the scripts executable
chmod +x deploy-saas-with-fixes.sh
chmod +x run_azure_migrations_fixed_updated.py
chmod +x scripts/create_azure_tables_direct_fixed_updated.py

# Copy the fixed app_adapter_with_agents.py to the deployment directory
echo "Copying the fixed app_adapter_with_agents.py..."
cp app_adapter_with_agents_fixed.py app_adapter_with_agents.py

# Run the deployment script
echo -e "${YELLOW}Running the deployment script with fixes...${NC}"
./deploy-saas-with-fixes.sh

echo -e "${GREEN}Deployment completed successfully.${NC}"
echo -e "The fixes for database tables and real agents have been applied."
echo -e "1. Database tables will now be created using environment variables for connection."
echo -e "2. Agents will now use real implementations with better error handling."
echo -e "Please allow a few minutes for the changes to take effect."
