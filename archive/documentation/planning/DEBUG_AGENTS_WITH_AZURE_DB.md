# Debugging SaaS and Agents Locally with Azure Database

This guide explains how to run the SaaS application and agents locally while connecting to the Azure database for debugging purposes.

## Overview

The `run_saas_with_agents_azure_db.py` script allows you to:

1. Run the SaaS application locally on your machine
2. Connect to the Azure PostgreSQL database (instead of a local database)
3. Enable detailed logging for agent functionality
4. Debug issues with the agent integration

This approach is useful when the SaaS portion of the application runs in Azure for the homepage but errors when trying to access the agents page.

## Prerequisites

- Python 3.9 or higher
- All required dependencies installed (`pip install -r requirements.txt`)
- Access to the Azure PostgreSQL database
- `.env.azure` file with the correct database connection string

## Running the Application

1. Make sure your `.env.azure` file contains the correct `DATABASE_URL` pointing to your Azure PostgreSQL database:

```
DATABASE_URL=postgresql://dbadmin:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner
```

2. Run the script:

```bash
python run_saas_with_agents_azure_db.py
```

You can also run it directly if you've made it executable:

```bash
./run_saas_with_agents_azure_db.py
```

3. The script will:
   - Load environment variables from `.env.azure`
   - Enable detailed logging
   - Check if the database URL points to Azure
   - Start the FastAPI application with uvicorn
   - Connect to the Azure database

4. Access the application at: http://localhost:8002

## Debugging Agent Functionality

### Checking for Errors

1. **Console Output**: The script enables detailed logging, so check the console output for any errors or warnings.

2. **Database Connection**: Verify that the application can connect to the Azure database. Look for any database connection errors in the logs.

3. **Agent Initialization**: Look for logs related to agent initialization. The script tries to import agent modules from various paths.

4. **API Endpoints**: Check if the agent API endpoints are working correctly. Try accessing:
   - http://localhost:8002/api/agents/available
   - http://localhost:8002/health (should show `"real_agents_available": true` if agents are working)

### Common Issues and Solutions

#### 1. Database Connection Issues

**Symptoms**: 
- Error messages about connection failures
- `OperationalError` or `ConnectionRefusedError`

**Solutions**:
- Verify the `DATABASE_URL` in `.env.azure` is correct
- Check if the Azure PostgreSQL server is running
- Ensure your IP address is allowed in the Azure PostgreSQL firewall rules
- Check if the database user has the correct permissions

#### 2. Agent Import Errors

**Symptoms**:
- `ImportError` messages in the console
- `"real_agents_available": false` in the health endpoint

**Solutions**:
- Check the Python path and ensure all agent modules are in the correct locations
- Verify that all required agent dependencies are installed
- Look for any syntax errors in the agent modules
- Check if the agent factory is correctly initialized

#### 3. Agent API Errors

**Symptoms**:
- The homepage works but the agents page shows errors
- API calls to `/api/agents/*` endpoints return errors

**Solutions**:
- Check the browser console for JavaScript errors
- Look for any API errors in the network tab of the browser developer tools
- Verify that the agent router is correctly handling API requests
- Check if the agent factory is correctly creating agent instances

#### 4. Missing Dependencies

**Symptoms**:
- `ModuleNotFoundError` or `ImportError` messages
- Application crashes on startup

**Solutions**:
- Install any missing dependencies: `pip install -r requirements.txt`
- Check if all required packages are installed with the correct versions
- Verify that all required Python modules are available

## Debugging with Browser Developer Tools

1. Open your browser's developer tools (F12 or right-click and select "Inspect")
2. Go to the "Console" tab to see any JavaScript errors
3. Go to the "Network" tab to see API requests and responses
4. Check for any failed requests to `/api/agents/*` endpoints
5. Look at the response data for any error messages

## Debugging with Python Debugger

You can use the Python debugger (pdb) to debug the application:

1. Add breakpoints in your code using `import pdb; pdb.set_trace()`
2. Run the script as usual
3. The debugger will stop at the breakpoints
4. Use the debugger commands to inspect variables and step through the code

## Logging Agent Activity

The script enables agent logging by setting:

```python
os.environ["ENABLE_AGENT_LOGGING"] = "true"
os.environ["AGENT_MEMORY_STORAGE"] = "file"
os.environ["AGENT_MEMORY_PATH"] = "./agent_memory"
```

This will save agent conversations to the `./agent_memory` directory, which you can inspect for debugging.

## Next Steps

If you identify issues with the agent functionality:

1. Fix the issues in your local code
2. Test the fixes locally using this script
3. Once everything works locally, deploy the fixes to Azure using the appropriate deployment script

## Conclusion

By running the SaaS application and agents locally while connecting to the Azure database, you can more easily debug issues with the agent functionality. This approach allows you to use local debugging tools while still working with the same data as the Azure deployment.
