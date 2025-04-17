# Azure Migration Script Fix (Updated)

## Issue

After fixing the auth directory, psycopg2 package, email-validator, and icalendar issues, we encountered another error with the migration script:

```
/opt/python/3/bin/python: No module named scripts.run_azure_migrations_fixed
```

This error occurred when the startup script was trying to run the migration script from the scripts directory, but the scripts directory was not being included in the deployment package.

## Root Cause

The migration script was being referenced in the startup.sh script, but it was looking for it in the scripts directory, which was not being included in the deployment package. Additionally, the startup script was trying to run the migration script using the Python module syntax (`python -m scripts.run_azure_migrations_fixed`), but this requires the scripts directory to be in the Python path.

## Fix

We made the following changes to fix the migration script issue:

1. Created a copy of the migration script (`run_azure_migrations_fixed.py`) in the root directory of the project, so it can be included in the deployment package.

2. Modified the `update-azure-agents.sh` script to include the migration script and the scripts directory in the deployment package:

```bash
# Copy the updated files to the deployment directory
echo "Copying updated files to deployment directory..."
mkdir -p $DEPLOY_DIR
cp startup.py $DEPLOY_DIR/
cp startup.sh $DEPLOY_DIR/
cp wsgi.py $DEPLOY_DIR/
cp web.config $DEPLOY_DIR/
cp app_adapter.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp run_azure_migrations_fixed.py $DEPLOY_DIR/
chmod +x $DEPLOY_DIR/startup.sh

# Copy the scripts directory
echo "Copying scripts directory..."
mkdir -p $DEPLOY_DIR/scripts
if [ -d "scripts" ]; then
    cp -r scripts/* $DEPLOY_DIR/scripts/
    # Ensure __init__.py exists in scripts directory
    touch $DEPLOY_DIR/scripts/__init__.py
fi
```

3. Modified the `startup.sh` script to check for the migration script in the current directory first, and then fall back to the scripts directory:

```bash
# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    # Check if the migration script exists in the current directory
    if [ -f "run_azure_migrations_fixed.py" ]; then
        echo "Migration script found in current directory, running..."
        python run_azure_migrations_fixed.py
    # Check if the scripts directory exists
    elif [ -d "scripts" ]; then
        echo "Scripts directory found, running migrations..."
        python -m scripts.run_azure_migrations_fixed
    else
        echo "Migration script not found, skipping migrations."
    fi
fi
```

## Deployment Instructions

To deploy the fix:

1. Make sure you have the latest versions of the `update-azure-agents.sh` and `startup.sh` scripts with the fixes included.
2. Make sure you have the `run_azure_migrations_fixed.py` file in the root directory of the project.
3. Run the update-azure-agents.sh script to deploy the updated files to Azure:

```bash
./update-azure-agents.sh
```

4. Monitor the deployment logs to ensure that the migration script is properly executed.
5. Verify that the application is running correctly by accessing the application URL.

## Verification

After deploying the fix, you should see the following in the deployment logs:

1. The migration script being found in the current directory:
   ```
   Migration script found in current directory, running...
   ```

2. The migration script being executed successfully.

## Conclusion

The issue was caused by the migration script not being included in the deployment package and the startup script not being able to find it. By including the migration script in the deployment package and modifying the startup script to check for it in the current directory first, we were able to fix the issue and ensure that the migration script is properly executed during the application startup.
