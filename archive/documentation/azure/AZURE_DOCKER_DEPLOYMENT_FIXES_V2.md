# Azure Docker Deployment Fixes V2

This document explains the additional fixes made to resolve the Docker container startup issues in Azure.

## Issues Identified

1. **Port Configuration Issue**: Azure sets `PORT=8002` but expects the application to listen on port 8000 (`WEBSITES_PORT=8000`). This mismatch was causing the container to fail to respond to health checks.

2. **Database Connection Issues**: The tenant middleware was trying to connect to the database for every request, including health checks. If there were issues with the database connection, this could cause the application to hang.

3. **Middleware Error Handling**: The tenant middleware didn't have proper error handling, which could cause the application to crash silently if there was an issue with the database connection.

4. **Startup Timeout**: The database setup script might be taking too long to run, causing the container to exceed Azure's startup timeout.

## Files Fixed

1. **entrypoint.sh**:
   - Added handling for `WEBSITES_PORT` environment variable
   - Added a simple health check server that runs during database setup
   - Improved error handling and logging

2. **app/middleware/tenant.py**:
   - Added special handling for health check requests to skip database operations
   - Added error handling to prevent the application from crashing if there are database connection issues
   - Added special handling for static files to continue serving them even if there are database issues

3. **enable_azure_logging.sh**:
   - Created a script to enable detailed logging in Azure App Service
   - Added commands to view the logs in real-time

## How to Apply the Fixes

1. Make sure you've applied the previous fixes using the `apply_docker_security_fixes.sh` script.

2. The new fixes are already included in the updated files:
   - entrypoint.sh
   - app/middleware/tenant.py

3. Enable detailed logging in Azure:
   ```bash
   ./enable_azure_logging.sh
   ```

4. Rebuild and redeploy the Docker container:
   ```bash
   ./azure-deploy-docker.sh
   ```

## Troubleshooting

If you still encounter issues:

1. **Check the logs**: Use the Azure Portal or the Azure CLI to view the logs:
   ```bash
   az webapp log tail --name ai-event-planner-saas --resource-group ai-event-planner-rg
   ```

2. **Check the environment variables**: Make sure all required environment variables are set in App Service settings, especially:
   - `DATABASE_URL`: The connection string to the PostgreSQL database
   - `WEBSITES_PORT`: Should be set to 8000
   - `PORT`: Should be set to 8000 (or not set at all, as the entrypoint script will handle it)

3. **Check the database connection**: Verify that the database is accessible from Azure and that the connection string is correct.

4. **Check the container registry**: Verify that the container image was pushed successfully.

## Key Improvements

1. **Port Configuration**: The entrypoint script now correctly handles the port configuration, ensuring that the application listens on the port that Azure expects.

2. **Health Check**: A simple health check server runs during database setup to respond to Azure's health checks, preventing the container from being terminated prematurely.

3. **Error Handling**: The tenant middleware now has better error handling, preventing the application from crashing if there are database connection issues.

4. **Static Files**: Static files can now be served even if there are database connection issues, ensuring that the application's UI is still accessible.

5. **Logging**: Detailed logging has been enabled, making it easier to diagnose issues.

## Next Steps

1. Monitor the application in Azure to ensure it's running correctly.

2. If you encounter any issues, check the logs and make any necessary adjustments.

3. Consider adding more robust error handling and monitoring to the application to prevent similar issues in the future.
