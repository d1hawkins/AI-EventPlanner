# Azure TypedDict Compatibility Fix

This document provides instructions for deploying the TypedDict compatibility fix to Azure. The fix addresses an issue where LangGraph's StateGraph initialization fails in the Azure environment when using TypedDict for state schema typing.

## Background

When deploying the AI-EventPlanner application to Azure, we encountered the following error:

```
TypeError: issubclass() arg 1 must be a class
```

This error occurs in the LangGraph framework when using TypedDict for state schema typing. The issue is related to how TypedDict is implemented and how it interacts with LangGraph's StateGraph class in the Azure environment.

## The Fix

The solution is to use a regular Python dictionary (`dict`) for the state schema instead of TypedDict. This avoids the compatibility issue while still providing the necessary structure for the state.

### Files Modified:

1. `app/graphs/simple_coordinator_graph.py`
2. `app/graphs/coordinator_graph.py`

## Verification

We've created a verification script (`verify_typeddict_fix.py`) that tests the creation of coordinator graphs to ensure they work properly with the dict-based state schema instead of TypedDict.

To verify the fix locally:

```bash
python3 verify_typeddict_fix.py
```

## Deployment

We've provided a deployment script (`azure-deploy-typeddict-fix.sh`) that automates the process of deploying the fix to Azure.

### Prerequisites:

1. Azure CLI installed
2. Logged in to Azure (`az login`)
3. Proper permissions to deploy to the Azure Web App

### Deployment Steps:

1. Make the deployment script executable:
   ```bash
   chmod +x azure-deploy-typeddict-fix.sh
   ```

2. Run the deployment script:
   ```bash
   ./azure-deploy-typeddict-fix.sh
   ```

3. The script will:
   - Verify the fix locally
   - Create a temporary deployment package
   - Deploy the fix to Azure
   - Optionally verify the fix on Azure

## Manual Verification on Azure

If you want to manually verify the fix on Azure after deployment:

```bash
az webapp ssh --resource-group "ai-event-planner-rg" --name "ai-event-planner-saas-py" --command "python test_fix.py"
```

## Troubleshooting

If you encounter issues with the deployment:

1. Check the Azure Web App logs:
   ```bash
   az webapp log tail --resource-group "ai-event-planner-rg" --name "ai-event-planner-saas-py"
   ```

2. Verify that the files were properly deployed:
   ```bash
   az webapp ssh --resource-group "ai-event-planner-rg" --name "ai-event-planner-saas-py" --command "ls -la app/graphs/"
   ```

3. Check if the test script is present:
   ```bash
   az webapp ssh --resource-group "ai-event-planner-rg" --name "ai-event-planner-saas-py" --command "ls -la"
   ```

## Additional Notes

- The warning about TAVILY_API_KEY being unset is expected and doesn't affect the functionality of the application.
- This fix is specific to the Azure environment and doesn't affect the local development environment.
