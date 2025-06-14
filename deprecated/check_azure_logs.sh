#!/bin/bash
# Script to check Azure logs for TypedDict compatibility errors
# This script downloads the latest logs from Azure App Service and checks for errors

set -e  # Exit immediately if a command exits with a non-zero status

echo "=== Checking Azure Logs for TypedDict Compatibility Errors ==="
echo ""

# Set variables
RESOURCE_GROUP="ai-event-planner-rg"
APP_NAME="ai-event-planner-saas-py"
LOG_DIR="./azure_logs"
LOG_FILE="$LOG_DIR/azure_logs.txt"

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR

# Download the latest logs from Azure
echo "Downloading logs from Azure App Service..."
az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file $LOG_FILE

# Check if the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Failed to download logs from Azure App Service."
    exit 1
fi

# Check for TypedDict compatibility errors
echo "Checking for TypedDict compatibility errors..."
TYPEDDICT_ERRORS=$(grep -i "issubclass() arg 1 must be a class" $LOG_FILE || true)

if [ -n "$TYPEDDICT_ERRORS" ]; then
    echo "ERROR: TypedDict compatibility errors found in the logs:"
    echo "$TYPEDDICT_ERRORS"
    echo ""
    echo "The fix is not working correctly. Please check the logs for more details."
    exit 1
else
    echo "✓ No TypedDict compatibility errors found in the logs."
fi

# Check for other errors
echo "Checking for other errors..."
OTHER_ERRORS=$(grep -i "error\|exception\|traceback" $LOG_FILE | grep -v "INFO\|DEBUG\|WARNING" || true)

if [ -n "$OTHER_ERRORS" ]; then
    echo "WARNING: Other errors found in the logs:"
    echo "$OTHER_ERRORS"
    echo ""
    echo "These errors may not be related to the TypedDict compatibility fix."
    echo "Please check the logs for more details."
fi

# Check for successful startup messages
echo "Checking for successful startup messages..."
STARTUP_SUCCESS=$(grep -i "Starting application with app.main_saas:app" $LOG_FILE || true)

if [ -n "$STARTUP_SUCCESS" ]; then
    echo "✓ Application started successfully."
else
    echo "WARNING: No startup success message found in the logs."
    echo "The application may not have started correctly."
fi

# Check for successful import of simple_coordinator_graph
echo "Checking for successful import of simple_coordinator_graph..."
IMPORT_SUCCESS=$(grep -i "Successfully imported simple_coordinator_graph" $LOG_FILE || true)

if [ -n "$IMPORT_SUCCESS" ]; then
    echo "✓ simple_coordinator_graph imported successfully."
else
    echo "WARNING: No import success message found in the logs."
    echo "The simple_coordinator_graph may not have been imported correctly."
fi

# Print summary
echo ""
echo "=== Summary ==="
if [ -z "$TYPEDDICT_ERRORS" ] && [ -n "$STARTUP_SUCCESS" ] && [ -n "$IMPORT_SUCCESS" ]; then
    echo "✓ The TypedDict compatibility fix is working correctly!"
    echo "✓ The application is running without TypedDict compatibility errors."
    echo "✓ The simple_coordinator_graph is being used instead of coordinator_graph."
else
    echo "WARNING: The TypedDict compatibility fix may not be working correctly."
    echo "Please check the logs for more details."
fi

echo ""
echo "For more information about the fix, see AZURE_TYPEDDICT_FIX.md"
