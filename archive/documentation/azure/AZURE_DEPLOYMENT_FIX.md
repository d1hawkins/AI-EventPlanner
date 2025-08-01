# Azure Deployment Fix Documentation

## Problem

The AI Event Planner SaaS application was failing to start after deployment to Azure. The issue was identified in the database connection string configuration.

### Root Cause

1. The PostgreSQL connection string in `.env.azure` was incorrectly formatted:
   ```
   DATABASE_URL=postgresql://dbadmin@ai-event-planner-db:VM*admin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner
   ```

   This format is invalid because:
   - It contains two `@` symbols, which confuses the connection string parser
   - The username and password are not properly separated (using wrong delimiter)
   - Special characters in the password aren't properly URL-encoded

2. This prevented the application from connecting to the database, causing startup failures.

## Solution

1. Fixed the PostgreSQL connection string format:
   ```
   DATABASE_URL=postgresql://dbadmin:VM%2Aadmin@ai-event-planner-db.postgres.database.azure.com:5432/eventplanner
   ```

   The changes include:
   - Using a colon (`:`) instead of `@` to separate username and password
   - URL-encoding special characters in the password (replacing `*` with `%2A`)

2. Created a simplified deployment script (`deploy-simple.sh`) that:
   - Updates the Azure App Service environment variables from `.env.azure`
   - Restarts the web app to apply the changes
   - Runs database migrations to ensure the database schema is up to date

## How to Deploy

To update the deployment and apply the fix:

1. Make sure your `.env.azure` file contains the correct database connection string
2. Run the simplified deployment script:
   ```bash
   ./deploy-simple.sh
   ```

This script will:
1. Update the environment variables in Azure App Service
2. Restart the web application
3. Run database migrations

## Future Considerations

When updating the database connection string in the future:

1. Ensure the connection string follows the correct format: `postgresql://[username]:[password]@[host]:[port]/[database]`
2. URL-encode any special characters in the password
3. Verify the database connection works before deploying

## Additional Resources

- [PostgreSQL Connection String Documentation](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [URL Encoding Reference](https://www.w3schools.com/tags/ref_urlencode.asp)
- [Azure App Service Environment Variables](https://docs.microsoft.com/en-us/azure/app-service/configure-common)
