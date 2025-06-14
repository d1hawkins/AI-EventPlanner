#!/bin/bash
# Comprehensive Azure Logging Setup Script
# This script sets up Application Insights, enhanced logging, and diagnostic tools

set -e

# Configuration
APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"
LOCATION="eastus"
INSIGHTS_NAME="ai-event-planner-insights"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up comprehensive logging for Azure App Service...${NC}"

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

echo -e "${BLUE}📊 Step 1: Setting up Azure Application Insights...${NC}"

# Create Application Insights instance
echo "Creating Application Insights instance..."
INSIGHTS_EXISTS=$(az monitor app-insights component show --app $INSIGHTS_NAME --resource-group $RESOURCE_GROUP 2>/dev/null || echo "not_found")

if [ "$INSIGHTS_EXISTS" = "not_found" ]; then
    echo "Creating new Application Insights instance: $INSIGHTS_NAME"
    az monitor app-insights component create \
        --app $INSIGHTS_NAME \
        --location $LOCATION \
        --resource-group $RESOURCE_GROUP \
        --application-type web \
        --retention-time 90
else
    echo "Application Insights instance already exists: $INSIGHTS_NAME"
fi

# Get the instrumentation key and connection string
echo "Retrieving Application Insights configuration..."
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app $INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey -o tsv)

CONNECTION_STRING=$(az monitor app-insights component show \
    --app $INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query connectionString -o tsv)

echo -e "${GREEN}✅ Application Insights created successfully${NC}"
echo "Instrumentation Key: $INSTRUMENTATION_KEY"
echo "Connection String: $CONNECTION_STRING"

echo -e "${BLUE}📝 Step 2: Configuring enhanced Azure App Service logging...${NC}"

# Enable detailed logging
echo "Enabling comprehensive logging..."
az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem \
    --level verbose

echo -e "${BLUE}⚙️ Step 3: Setting up environment variables...${NC}"

# Set comprehensive environment variables for logging
echo "Configuring application settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY" \
    "APPLICATIONINSIGHTS_CONNECTION_STRING=$CONNECTION_STRING" \
    "APPINSIGHTS_PROFILERFEATURE_VERSION=1.0.0" \
    "APPINSIGHTS_SNAPSHOTFEATURE_VERSION=1.0.0" \
    "ApplicationInsightsAgent_EXTENSION_VERSION=~3" \
    "DiagnosticServices_EXTENSION_VERSION=~3" \
    "ENABLE_COMPREHENSIVE_LOGGING=true" \
    "LOG_LEVEL=DEBUG" \
    "AZURE_LOG_LEVEL=INFO" \
    "PYTHONUNBUFFERED=1" \
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7" \
    "WEBSITE_ENABLE_SYNC_UPDATE_SITE=true" \
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE=true"

echo -e "${BLUE}🔍 Step 4: Setting up diagnostic endpoints...${NC}"

# Create health check endpoint configuration
echo "Configuring health check endpoints..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    "ENABLE_HEALTH_CHECK=true" \
    "HEALTH_CHECK_PATH=/health" \
    "STARTUP_DIAGNOSTICS=true" \
    "DETAILED_STARTUP_LOGGING=true"

echo -e "${BLUE}📋 Step 5: Creating log monitoring commands...${NC}"

# Create a script for easy log access
cat > azure-log-commands.sh << 'EOF'
#!/bin/bash
# Azure Logging Commands for AI Event Planner

APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

echo "=== Azure Logging Commands ==="
echo "1. Stream live logs:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo ""
echo "2. Download all logs:"
echo "   az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file app-logs.zip"
echo ""
echo "3. Check app status:"
echo "   az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query '{state: state, defaultHostName: defaultHostName}'"
echo ""
echo "4. View environment variables:"
echo "   az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo ""
echo "5. SSH into container (when running):"
echo "   az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo ""
echo "6. Restart application:"
echo "   az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo ""
echo "7. View Application Insights:"
echo "   https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/ai-event-planner-insights/overview"

# Function to stream logs with colors
stream_logs() {
    echo "Streaming logs for $APP_NAME..."
    az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME
}

# Function to download logs
download_logs() {
    echo "Downloading logs for $APP_NAME..."
    az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file "app-logs-$(date +%Y%m%d-%H%M%S).zip"
    echo "Logs downloaded successfully!"
}

# Function to check app health
check_health() {
    echo "Checking application health..."
    az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query '{state: state, defaultHostName: defaultHostName, lastModifiedTimeUtc: lastModifiedTimeUtc}'
    
    echo "Testing HTTP response..."
    curl -I "https://$APP_NAME.azurewebsites.net" || echo "Application not responding"
}

# Function to view recent errors
view_errors() {
    echo "Checking for recent errors..."
    az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file temp-logs.zip
    unzip -q temp-logs.zip
    echo "Recent error logs:"
    find LogFiles -name "*.log" -exec grep -l "ERROR\|Exception\|Traceback" {} \; | head -5 | xargs tail -20
    rm -rf LogFiles temp-logs.zip
}

# Check command line arguments
case "$1" in
    "stream")
        stream_logs
        ;;
    "download")
        download_logs
        ;;
    "health")
        check_health
        ;;
    "errors")
        view_errors
        ;;
    *)
        echo "Usage: $0 {stream|download|health|errors}"
        echo ""
        echo "Commands:"
        echo "  stream   - Stream live application logs"
        echo "  download - Download all logs as ZIP file"
        echo "  health   - Check application health status"
        echo "  errors   - View recent error logs"
        ;;
esac
EOF

chmod +x azure-log-commands.sh

echo -e "${BLUE}🚀 Step 6: Creating enhanced startup script with logging...${NC}"

# Create enhanced startup script
cat > enhanced-startup-with-logging.sh << 'EOF'
#!/bin/bash
# Enhanced startup script with comprehensive logging

# Set up logging
LOG_FILE="/home/site/wwwroot/startup.log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "=== STARTUP LOG $(date) ==="
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

cd /home/site/wwwroot

# Print environment variables (excluding sensitive ones)
echo "=== ENVIRONMENT VARIABLES ==="
env | grep -v -E "(SECRET|KEY|PASSWORD|TOKEN)" | sort

# Print directory structure
echo "=== DIRECTORY STRUCTURE ==="
ls -la
echo "App directory contents:"
ls -la app/ 2>/dev/null || echo "App directory not found"

# Check Python path
echo "=== PYTHON CONFIGURATION ==="
echo "Python path: $PYTHONPATH"
echo "Python executable: $(which python)"
echo "Site packages:"
python -c "import site; print(site.getsitepackages())" 2>/dev/null || echo "Could not get site packages"

# Install dependencies with detailed logging
echo "=== INSTALLING DEPENDENCIES ==="
echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --verbose
else
    echo "No requirements.txt found, installing basic dependencies..."
    pip install fastapi uvicorn gunicorn sqlalchemy pydantic python-dotenv
fi

# Test imports
echo "=== TESTING IMPORTS ==="
python -c "
import sys
import traceback

modules_to_test = [
    'fastapi', 'uvicorn', 'gunicorn', 'sqlalchemy', 
    'pydantic', 'dotenv', 'app', 'app.main_saas'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f'✅ {module} imported successfully')
    except Exception as e:
        print(f'❌ {module} import failed: {e}')
        if module.startswith('app'):
            traceback.print_exc()
"

# Check database connectivity (if DATABASE_URL is set)
echo "=== DATABASE CONNECTIVITY ==="
if [ -n "$DATABASE_URL" ]; then
    echo "Testing database connection..."
    python -c "
import os
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
else
    echo "No DATABASE_URL set, skipping database test"
fi

# Determine which app module to use
echo "=== DETERMINING APP MODULE ==="
APP_MODULE=""

if [ -f "app/main_saas.py" ]; then
    echo "Found app/main_saas.py, testing import..."
    python -c "from app.main_saas import app; print('✅ app.main_saas:app is available')" 2>/dev/null && APP_MODULE="app.main_saas:app"
fi

if [ -z "$APP_MODULE" ] && [ -f "app/main.py" ]; then
    echo "Found app/main.py, testing import..."
    python -c "from app.main import app; print('✅ app.main:app is available')" 2>/dev/null && APP_MODULE="app.main:app"
fi

if [ -z "$APP_MODULE" ] && [ -f "app_adapter.py" ]; then
    echo "Found app_adapter.py, testing import..."
    python -c "from app_adapter import app; print('✅ app_adapter:app is available')" 2>/dev/null && APP_MODULE="app_adapter:app"
fi

if [ -z "$APP_MODULE" ]; then
    echo "❌ No valid app module found!"
    echo "Available Python files:"
    find . -name "*.py" -type f | head -10
    APP_MODULE="app_adapter:app"  # fallback
fi

echo "Using app module: $APP_MODULE"

# Set up Python path
export PYTHONPATH=$PYTHONPATH:/home/site/wwwroot

# Create a simple health check endpoint test
echo "=== TESTING APP STARTUP ==="
python -c "
import sys
sys.path.insert(0, '/home/site/wwwroot')
try:
    module_name, app_name = '$APP_MODULE'.split(':')
    module = __import__(module_name, fromlist=[app_name])
    app = getattr(module, app_name)
    print(f'✅ Successfully loaded {module_name}:{app_name}')
    print(f'App type: {type(app)}')
except Exception as e:
    print(f'❌ Failed to load app: {e}')
    import traceback
    traceback.print_exc()
"

# Start the application with comprehensive logging
echo "=== STARTING APPLICATION ==="
echo "Starting gunicorn with module: $APP_MODULE"
echo "Command: gunicorn $APP_MODULE --bind=0.0.0.0:8000 --workers=2 --timeout=120 --access-logfile=- --error-logfile=- --log-level=info"

# Start gunicorn with logging
exec gunicorn $APP_MODULE \
    --bind=0.0.0.0:8000 \
    --workers=2 \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info \
    --capture-output \
    --enable-stdio-inheritance
EOF

chmod +x enhanced-startup-with-logging.sh

echo -e "${BLUE}🔧 Step 7: Creating Python logging configuration...${NC}"

# Create Python logging configuration
cat > logging_config.py << 'EOF'
import logging
import os
import sys
from datetime import datetime

def setup_comprehensive_logging():
    """Set up comprehensive logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = "/home/site/wwwroot/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG if os.getenv('LOG_LEVEL') == 'DEBUG' else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"{log_dir}/application.log"),
            logging.FileHandler(f"{log_dir}/startup_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )
    
    # Set up specific loggers
    loggers = {
        'uvicorn': logging.INFO,
        'uvicorn.error': logging.INFO,
        'uvicorn.access': logging.INFO,
        'fastapi': logging.INFO,
        'sqlalchemy.engine': logging.WARNING,
        'app': logging.DEBUG,
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Application Insights integration
    if os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY'):
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            
            azure_handler = AzureLogHandler(
                connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
            )
            azure_handler.setLevel(logging.WARNING)
            
            # Add Azure handler to root logger
            logging.getLogger().addHandler(azure_handler)
            logging.info("Azure Application Insights logging enabled")
            
        except ImportError:
            logging.warning("Azure Application Insights SDK not available")
    
    logging.info("Comprehensive logging setup completed")
    return logging.getLogger(__name__)

# Health check logging
def log_health_check():
    """Log application health status"""
    logger = logging.getLogger("health_check")
    
    try:
        # Log system info
        import psutil
        logger.info(f"CPU usage: {psutil.cpu_percent()}%")
        logger.info(f"Memory usage: {psutil.virtual_memory().percent}%")
    except ImportError:
        logger.info("psutil not available for system monitoring")
    
    # Log environment status
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    return True

if __name__ == "__main__":
    setup_comprehensive_logging()
    log_health_check()
EOF

echo -e "${BLUE}🩺 Step 8: Creating diagnostic tools...${NC}"

# Create diagnostic script
cat > azure-diagnostic-tools.sh << 'EOF'
#!/bin/bash
# Azure Diagnostic Tools

APP_NAME="ai-event-planner-saas-py"
RESOURCE_GROUP="ai-event-planner-rg"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🩺 Azure App Service Diagnostic Tools${NC}"

# Function to check app status
check_app_status() {
    echo -e "${BLUE}📊 Checking application status...${NC}"
    
    # Get app details
    APP_INFO=$(az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query '{state: state, defaultHostName: defaultHostName, lastModifiedTimeUtc: lastModifiedTimeUtc}' -o json)
    echo "App Info: $APP_INFO"
    
    # Test HTTP response
    echo "Testing HTTP response..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$APP_NAME.azurewebsites.net" || echo "000")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✅ Application is responding (HTTP $HTTP_STATUS)${NC}"
    else
        echo -e "${RED}❌ Application not responding properly (HTTP $HTTP_STATUS)${NC}"
    fi
}

# Function to check environment variables
check_environment() {
    echo -e "${BLUE}⚙️ Checking environment configuration...${NC}"
    
    # Get critical environment variables
    CRITICAL_VARS=("DATABASE_URL" "SECRET_KEY" "LLM_PROVIDER" "APPINSIGHTS_INSTRUMENTATIONKEY")
    
    for var in "${CRITICAL_VARS[@]}"; do
        VALUE=$(az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME --query "[?name=='$var'].value" -o tsv)
        if [ -n "$VALUE" ]; then
            echo -e "${GREEN}✅ $var is set${NC}"
        else
            echo -e "${RED}❌ $var is missing${NC}"
        fi
    done
}

# Function to analyze recent logs
analyze_logs() {
    echo -e "${BLUE}📋 Analyzing recent logs...${NC}"
    
    # Download recent logs
    az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file temp-diagnostic-logs.zip
    
    if [ -f "temp-diagnostic-logs.zip" ]; then
        unzip -q temp-diagnostic-logs.zip
        
        echo "Recent errors:"
        find LogFiles -name "*.log" -exec grep -l "ERROR\|Exception\|Traceback\|Failed" {} \; | head -3 | while read file; do
            echo "--- $file ---"
            tail -10 "$file"
            echo ""
        done
        
        echo "Recent startup logs:"
        find LogFiles -name "*startup*" -o -name "*application*" | head -2 | while read file; do
            echo "--- $file ---"
            tail -15 "$file"
            echo ""
        done
        
        # Cleanup
        rm -rf LogFiles temp-diagnostic-logs.zip
    else
        echo "Could not download logs"
    fi
}

# Function to test database connectivity
test_database() {
    echo -e "${BLUE}🗄️ Testing database connectivity...${NC}"
    
    DATABASE_URL=$(az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME --query "[?name=='DATABASE_URL'].value" -o tsv)
    
    if [ -n "$DATABASE_URL" ]; then
        echo "Database URL is configured"
        # Note: Actual connectivity test would need to be done from within the app
        echo "To test connectivity, check application logs for database connection attempts"
    else
        echo -e "${RED}❌ DATABASE_URL not configured${NC}"
    fi
}

# Function to restart app with monitoring
restart_with_monitoring() {
    echo -e "${BLUE}🔄 Restarting application with monitoring...${NC}"
    
    echo "Restarting app..."
    az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME
    
    echo "Waiting for restart..."
    sleep 10
    
    echo "Monitoring startup logs..."
    timeout 60 az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME &
    
    sleep 30
    check_app_status
}

# Function to show Application Insights info
show_app_insights() {
    echo -e "${BLUE}📊 Application Insights Information${NC}"
    
    INSIGHTS_INFO=$(az monitor app-insights component show --app ai-event-planner-insights --resource-group $RESOURCE_GROUP --query '{instrumentationKey: instrumentationKey, connectionString: connectionString}' -o json 2>/dev/null || echo "{}")
    
    if [ "$INSIGHTS_INFO" != "{}" ]; then
        echo "Application Insights is configured:"
        echo "$INSIGHTS_INFO"
        echo ""
        echo "View in Azure Portal:"
        echo "https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/ai-event-planner-insights/overview"
    else
        echo "Application Insights not found or not configured"
    fi
}

# Main menu
case "$1" in
    "status")
        check_app_status
        ;;
    "env")
        check_environment
        ;;
    "logs")
        analyze_logs
        ;;
    "db")
        test_database
        ;;
    "restart")
        restart_with_monitoring
        ;;
    "insights")
        show_app_insights
        ;;
    "full")
        echo -e "${BLUE}🔍 Running full diagnostic...${NC}"
        check_app_status
        echo ""
        check_environment
        echo ""
        test_database
        echo ""
        show_app_insights
        echo ""
        analyze_logs
        ;;
    *)
        echo "Azure Diagnostic Tools"
        echo ""
        echo "Usage: $0 {status|env|logs|db|restart|insights|full}"
        echo ""
        echo "Commands:"
        echo "  status   - Check application status and HTTP response"
        echo "  env      - Check environment variable configuration"
        echo "  logs     - Analyze recent logs for errors"
        echo "  db       - Test database configuration"
        echo "  restart  - Restart app with monitoring"
        echo "  insights - Show Application Insights information"
        echo "  full     - Run complete diagnostic"
        ;;
esac
EOF

chmod +x azure-diagnostic-tools.sh

echo -e "${BLUE}📚 Step 9: Creating documentation...${NC}"

# Create comprehensive documentation
cat > AZURE_LOGGING_GUIDE.md << 'EOF'
# Azure Comprehensive Logging Guide

This guide provides complete instructions for monitoring and troubleshooting your AI Event Planner application deployed on Azure App Service.

## 🚀 Quick Start

### Immediate Troubleshooting Commands

```bash
# Stream live logs
./azure-log-commands.sh stream

# Check application health
./azure-diagnostic-tools.sh status

# Run full diagnostic
./azure-diagnostic-tools.sh full
```

## 📊 Logging Components

### 1. Azure Application Insights
- **Purpose**: Production monitoring, performance tracking, error analytics
- **Access**: Azure Portal → Application Insights → ai-event-planner-insights
- **Features**: 
  - Real-time performance monitoring
  - Exception tracking
  - Custom telemetry
  - Dependency tracking

### 2. Azure App Service Logs
- **Purpose**: Application and web server logs
- **Location**: `/home/LogFiles/` in the container
- **Types**: Application logs, HTTP logs, detailed error messages

### 3. Custom Application Logs
- **Purpose**: Application-specific logging
- **Location**: `/home/site/wwwroot/logs/`
- **Files**: 
  - `application.log` - General application logs
  - `startup_YYYYMMDD.log` - Daily startup logs

## 🔧 Available Tools

### azure-log-commands.sh
Quick access to common logging operations:

```bash
./azure-log-commands.sh stream     # Stream live logs
./azure-log-commands.sh download   # Download all logs
./azure-log-commands.sh health     # Check app health
./azure-log-commands.sh errors     # View recent errors
```

### azure-diagnostic-tools.sh
Comprehensive diagnostic utilities:

```bash
./azure-diagnostic-tools.sh status    # App status check
./azure-diagnostic-tools.sh env       # Environment variables
./azure-diagnostic-tools.sh logs      # Log analysis
./azure-diagnostic-tools.sh db        # Database connectivity
./azure-diagnostic-tools.sh restart   # Restart with monitoring
./azure-diagnostic-tools.sh insights  # Application Insights info
./azure-diagnostic-tools.sh full      # Complete diagnostic
```

## 🩺 Troubleshooting Common Issues

### Application Won't Start (504 Timeout)

1. **Check startup logs**:
   ```bash
   ./azure-log-commands.sh stream
   ```

2. **Run diagnostics**:
   ```bash
   ./azure-diagnostic-tools.sh full
   ```

3. **Common causes**:
   - Missing environment variables
   - Database connection issues
   - Import errors
   - Dependency conflicts

### Application Starts But Errors Occur

1. **Check Application Insights**:
   - Go to Azure Portal → Application Insights
   - View Failures and Performance tabs

2. **Analyze recent errors**:
   ```bash
   ./azure-log-commands.sh errors
   ```

### Database Connection Issues

1. **Test database configuration**:
   ```bash
   ./azure-diagnostic-tools.sh db
   ```

2. **Check environment variables**:
   ```bash
   ./azure-diagnostic-tools.sh env
   ```

## 📈 Monitoring Best Practices

### 1. Regular Health Checks
```bash
# Set up a cron job or scheduled task
./azure-diagnostic-tools.sh status
```

### 2. Log Rotation
- Application Insights: 90-day retention
- App Service logs: 7-day retention
- Custom logs: Manual cleanup recommended

### 3. Performance Monitoring
- Monitor Application Insights dashboards
- Set up alerts for critical metrics
- Review dependency performance

## 🔍 Advanced Debugging

### SSH into Container
```bash
az webapp ssh --resource-group ai-event-planner-rg --name ai-event-planner-saas-py
```

### Manual Log Analysis
```bash
# Download logs
az webapp log download --resource-group ai-event-planner-rg --name ai-event-planner-saas-py --log-file logs.zip

# Extract and analyze
unzip logs.zip
grep -r "ERROR\|Exception" LogFiles/
```

### Environment Variable Management
```bash
# List all settings
az webapp config appsettings list --resource-group ai-event-planner-rg --name ai-event-planner-saas-py

# Set new variable
az webapp config appsettings set --resource-group ai-event-planner-rg --name ai-event-planner-saas-py --settings "NEW_VAR=value"
```

## 🚨 Alert Configuration

### Application Insights Alerts
1. Go to Azure Portal → Application Insights → Alerts
2. Create new alert rules for:
   - High error rate (>5% in 5 minutes)
   - Slow response time (>2 seconds average)
   - Dependency failures

### Log-based Alerts
1. Use Azure Monitor to create log queries
2. Set up notifications for critical errors
3. Configure action groups for team notifications

## 📞 Support Information

### Log Locations
- **Application Insights**: Azure Portal → Application Insights
- **App Service Logs**: Kudu console → LogFiles
- **Custom Logs**: SSH → /home/site/wwwroot/logs/

### Key Metrics to Monitor
- Response time
- Error rate
- Memory usage
- CPU usage
- Database connection health

### Emergency Procedures
1. **Application Down**: Run `./azure-diagnostic-tools.sh restart`
2. **High Error Rate**: Check Application Insights → Failures
3. **Performance Issues**: Review Application Insights → Performance
4. **Database Issues**: Check connection strings and database status

## 🔗 Useful Links

- [Application Insights Portal](https://portal.azure.com/#@/resource/subscriptions/YOUR_SUBSCRIPTION/resourceGroups/ai-event-planner-rg/providers/Microsoft.Insights/components/ai-event-planner-insights/overview)
- [App Service Portal](https://portal.azure.com/#@/resource/subscriptions/YOUR_SUBSCRIPTION/resourceGroups/ai-event-planner-rg/providers/Microsoft.Web/sites/ai-event-planner-saas-py/appServices)
- [Kudu Console](https://ai-event-planner-saas-py.scm.azurewebsites.net/)

Replace `YOUR_SUBSCRIPTION` with your actual Azure subscription ID.
EOF

echo -e "${GREEN}✅ Comprehensive logging setup completed!${NC}"
echo ""
echo -e "${BLUE}📋 Summary of created files:${NC}"
echo "  ✓ azure-log-commands.sh - Quick logging commands"
echo "  ✓ azure-diagnostic-tools.sh - Diagnostic utilities"
echo "  ✓ enhanced-startup-with-logging.sh - Enhanced startup script"
echo "  ✓ logging_config.py - Python logging configuration"
echo "  ✓ AZURE_LOGGING_GUIDE.md - Complete documentation"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "1. Update your app to use the enhanced startup script:"
echo "   az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file 'enhanced-startup-with-logging.sh'"
echo ""
echo "2. Test the logging setup:"
echo "   ./azure-log-commands.sh stream"
echo ""
echo "3. Run diagnostics:"
echo "   ./azure-diagnostic-tools.sh full"
echo ""
echo "4.
