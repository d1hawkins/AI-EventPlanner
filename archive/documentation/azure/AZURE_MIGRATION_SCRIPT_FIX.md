# Azure Migration Script Fix

## Issue

After fixing the auth directory and psycopg2 package issues, we encountered another error:

```
/opt/python/3/bin/python: No module named scripts.run_azure_migrations_fixed
```

This error occurred when trying to run the database migrations during the application startup. The migration script was not being found in the expected location.

## Root Cause

The migration script was expected to be in the `scripts` directory, but this directory might not be included in the deployment package or might be located in a different path than expected. The startup script was not checking if the directory or script exists before trying to run it.

## Fix

We modified the `startup.sh` script to check if the scripts directory and migration script exist before trying to run them:

```bash
# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    # Check if the scripts directory exists
    if [ -d "scripts" ]; then
        echo "Scripts directory found, running migrations..."
        python -m scripts.run_azure_migrations_fixed
    else
        echo "Scripts directory not found, checking for migration script in current directory..."
        # Check if the migration script exists in the current directory
        if [ -f "run_azure_migrations_fixed.py" ]; then
            echo "Migration script found in current directory, running..."
            python run_azure_migrations_fixed.py
        else
            echo "Migration script not found, skipping migrations."
        fi
    fi
fi
```

This change makes the startup script more robust by:

1. Checking if the scripts directory exists before trying to run the migration script from it.
2. If the scripts directory doesn't exist, checking if the migration script exists in the current directory.
3. If neither the scripts directory nor the migration script in the current directory exist, skipping the migrations.

## Deployment Instructions

To deploy the fix:

1. Make sure you have the latest version of the startup.sh script with the migration script check.
2. Run the update-azure-agents.sh script to deploy the updated files to Azure:

```bash
./update-azure-agents.sh
```

3. Monitor the deployment logs to ensure that the migration script is properly handled.
4. Verify that the application is running correctly by accessing the application URL.

## Verification

After deploying the fix, you should see one of the following in the deployment logs:

1. If the scripts directory exists:
   ```
   Scripts directory found, running migrations...
   ```

2. If the scripts directory doesn't exist but the migration script exists in the current directory:
   ```
   Scripts directory not found, checking for migration script in current directory...
   Migration script found in current directory, running...
   ```

3. If neither the scripts directory nor the migration script in the current directory exist:
   ```
   Scripts directory not found, checking for migration script in current directory...
   Migration script not found, skipping migrations.
   ```

## Conclusion

The issue was caused by the startup script not checking if the scripts directory and migration script exist before trying to run them. By adding these checks, we made the startup script more robust and able to handle different deployment scenarios.

This fix ensures that the application can start even if the migration script is not found, which is important for the application to be able to run in Azure.
