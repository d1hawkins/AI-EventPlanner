#!/bin/bash
# Script to enable detailed logging for Azure App Service Docker container

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to log messages
log() {
  local level=$1
  local message=$2
  local color=$NC
  
  case $level in
    "INFO") color=$GREEN ;;
    "WARN") color=$YELLOW ;;
    "ERROR") color=$RED ;;
  esac
  
  echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message${NC}"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
  log "ERROR" "Azure CLI is not installed. Please install it first."
  exit 1
fi

# Check if user is logged in to Azure
az account show &> /dev/null
if [ $? -ne 0 ]; then
  log "ERROR" "You are not logged in to Azure. Please run 'az login' first."
  exit 1
fi

# Resource group and app name
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas"

# Enable logging
log "INFO" "Enabling detailed logging for $APP_NAME in resource group $RESOURCE_GROUP..."
az webapp log config --name $APP_NAME --resource-group $RESOURCE_GROUP --docker-container-logging filesystem

# Enable log streaming
log "INFO" "Enabling log streaming..."
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

log "INFO" "Logging has been enabled for $APP_NAME."
log "INFO" "You can view the logs using the following command:"
log "INFO" "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
