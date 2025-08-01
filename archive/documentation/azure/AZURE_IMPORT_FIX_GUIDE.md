# Azure Deployment Fix Guide

This document explains the fixes for deployment issues in the Azure environment and provides instructions on how to deploy the fixes to Azure.

## Backend Import Error

### Problem

The application was encountering the following error in the Azure environment:

```
ModuleNotFoundError: No module named 'agents.agent_router'
```

And then:

```
ModuleNotFoundError: No module named 'app.agents.agent_router'
```

This error occurred because the Python module path was not set up correctly in the Azure environment. The file was being run from `/home/site/wwwroot/app_adapter.py` but it couldn't find the agent_router module.

### Solution

The fix involves two main changes to the `app_adapter.py` and `app_adapter_with_agents.py` files:

1. Adding the `/home/site/wwwroot` directory to the Python path to ensure imports work in the Azure environment.
2. Implementing a more robust import mechanism that tries multiple import paths until it finds one that works.

These changes make the application more resilient to different deployment environments and ensure that the imports work correctly regardless of where the file is being run from.

## Frontend API Connection Error

### Problem

After deploying to Azure, the frontend JavaScript was encountering connection errors when trying to access the API endpoints:

```
Failed to load resource: net::ERR_CONNECTION_REFUSED
Error getting available agents: TypeError: Failed to fetch
Error loading agents: TypeError: Failed to fetch
Error listing conversations: TypeError: Failed to fetch
Error loading conversations: TypeError: Failed to fetch
```

This occurred because the frontend JavaScript was configured to connect to a hardcoded local API endpoint (`http://localhost:8002/api`), which doesn't work in the Azure environment.

### Solution

The fix involves updating the `agent-service.js` file to use a relative URL instead of a hardcoded localhost URL:

```javascript
// Before
this.apiBaseUrl = 'http://localhost:8002/api';

// After
this.apiBaseUrl = '/api';
```

This change ensures that the frontend can connect to the API endpoints in any environment, including Azure.

## Testing the Fix

A test script (`test_azure_deployment.py`) has been created to simulate the Azure environment and test the import paths. This script:

1. Creates a mock wwwroot directory structure
2. Copies the app_adapter.py file to the mock wwwroot directory
3. Simulates the Azure environment by changing to the wwwroot directory
4. Tests the imports to ensure they work correctly
5. Tests the health endpoint to ensure the application works correctly

To run the test:

```bash
python test_azure_deployment.py
```

If the test passes, the fix is working correctly and can be deployed to Azure.

## Deploying to Azure

There are several ways to deploy the fixed `app_adapter.py` file to Azure:

### Option 1: Using the Azure CLI

1. Install the Azure CLI if you haven't already:
   - [Azure CLI Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

2. Log in to Azure:
   ```bash
   az login
   ```

3. Deploy the file to your Azure Web App:
   ```bash
   az webapp deploy --resource-group <resource-group-name> \
                   --name <app-name> \
                   --src-path app_adapter.py \
                   --target-path /home/site/wwwroot/app_adapter.py
   ```

4. Restart the Azure Web App:
   ```bash
   az webapp restart --name <app-name> --resource-group <resource-group-name>
   ```

### Option 2: Using the Azure Portal

1. Log in to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Web App
3. Go to "Advanced Tools" (Kudu)
4. Click on "Debug Console" > "CMD"
5. Navigate to the `/home/site/wwwroot` directory
6. Upload the fixed `app_adapter.py` file using the file upload feature
7. Restart the Web App from the Azure Portal

### Option 3: Using GitHub Actions

If you're using GitHub Actions for deployment, you can simply commit the fixed `app_adapter.py` file to your repository and let the GitHub Actions workflow deploy it to Azure.

## Verifying the Deployment

After deploying the fix, you can verify that it works correctly by:

1. Checking the logs in the Azure portal:
   ```bash
   az webapp log tail --name <app-name> --resource-group <resource-group-name>
   ```

2. Accessing the health endpoint of your application:
   ```
   https://<app-name>.azurewebsites.net/health
   ```

   This should return a JSON response with `"real_agents_available": true` if the fix is working correctly.

## Understanding the Fix

The key parts of the fix are:

1. Adding the wwwroot directory to the Python path:
   ```python
   # Add wwwroot directory to path for Azure deployment
   wwwroot_dir = '/home/site/wwwroot'
   if os.path.exists(wwwroot_dir):
       sys.path.insert(0, wwwroot_dir)
       sys.path.insert(0, os.path.join(wwwroot_dir, 'app'))
   ```

2. Implementing a more robust import mechanism:
   ```python
   # Try all possible import paths
   import_paths = [
       # Direct import
       {
           'router': 'agents.agent_router',
           'factory': 'agents.agent_factory',
           'session': 'db.session',
           'tenant': 'middleware.tenant'
       },
       # With app prefix
       {
           'router': 'app.agents.agent_router',
           'factory': 'app.agents.agent_factory',
           'session': 'app.db.session',
           'tenant': 'app.middleware.tenant'
       },
       # From wwwroot
       {
           'router': 'app_adapter.app.agents.agent_router',
           'factory': 'app_adapter.app.agents.agent_factory',
           'session': 'app_adapter.app.db.session',
           'tenant': 'app_adapter.app.middleware.tenant'
       }
   ]
   
   imported = False
   for path in import_paths:
       try:
           # Try to import using this path
           # ...
           imported = True
           break
       except ImportError as e:
           # Continue to the next path
           continue
   ```

This approach ensures that the application can find the required modules regardless of the environment it's running in.

## Conclusion

The fix makes the application more resilient to different deployment environments and ensures that the imports work correctly in the Azure environment. By adding the wwwroot directory to the Python path and implementing a more robust import mechanism, we've fixed the import error and made the application more robust.
