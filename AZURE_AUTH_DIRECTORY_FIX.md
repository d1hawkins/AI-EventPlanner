# Azure Auth Directory Fix

## Issue

The Azure deployment was failing with the following error:

```
ModuleNotFoundError: No module named 'app.auth.router'
```

This error occurred when trying to import `from app.auth.router import router as auth_router` in the app/main_saas.py file.

## Root Cause

The issue was in the `update-azure-agents.sh` script, which is responsible for deploying the application to Azure. The script was not including the `auth` directory in the list of directories to copy to the deployment package.

Here's the problematic section in the original script:

```bash
# Copy the entire app directory with proper structure
echo "Copying app directory with proper structure..."
for dir in agents db middleware graphs tools schemas state utils web; do
    if [ -d "app/$dir" ]; then
        echo "Copying app/$dir..."
        mkdir -p $DEPLOY_DIR/app/$dir
        cp -r app/$dir/* $DEPLOY_DIR/app/$dir/
        # Ensure __init__.py exists in each directory
        touch $DEPLOY_DIR/app/$dir/__init__.py
    fi
done
```

As you can see, the `auth` directory was not included in the list of directories to copy.

## Fix

The fix was simple - we added the `auth` directory to the list of directories to copy in the `update-azure-agents.sh` script:

```bash
# Copy the entire app directory with proper structure
echo "Copying app directory with proper structure..."
for dir in agents auth db middleware graphs tools schemas state utils web; do
    if [ -d "app/$dir" ]; then
        echo "Copying app/$dir..."
        mkdir -p $DEPLOY_DIR/app/$dir
        cp -r app/$dir/* $DEPLOY_DIR/app/$dir/
        # Ensure __init__.py exists in each directory
        touch $DEPLOY_DIR/app/$dir/__init__.py
    fi
done
```

## Deployment Instructions

To deploy the fix:

1. Make sure you have the latest version of the update-azure-agents.sh script with the auth directory included in the list of directories to copy.
2. Run the update-azure-agents.sh script to deploy the updated files to Azure:

```bash
./update-azure-agents.sh
```

3. Monitor the deployment logs to ensure that the auth directory is properly copied to the deployment package.
4. Verify that the application is running correctly by accessing the application URL.

## Verification

After deploying the fix, you should see the following in the deployment logs:

1. The auth directory being copied to the deployment package:
   ```
   Copying app/auth...
   ```

2. No ModuleNotFoundError for app.auth.router in the application logs.

### Verification Scripts

Two verification scripts have been created to check if the auth directory and its files are properly deployed to Azure. Both scripts connect to the Azure App Service using SSH and check if the auth directory and its files exist.

#### Bash Script

To run the bash verification script:

```bash
chmod +x verify_auth_directory.sh
./verify_auth_directory.sh
```

#### Python Script

To run the Python verification script:

```bash
chmod +x verify_auth_directory.py
./verify_auth_directory.py
```

Both scripts will check:
1. If the auth directory exists in the deployment
2. If the auth router file exists
3. If the auth dependencies file exists
4. If the auth __init__.py file exists

If all checks pass, the scripts will output a success message. If any check fails, the scripts will output an error message and exit with a non-zero status code.

### Passlib Installation

The passlib package is required by the auth module for password hashing. It is already included in the requirements.txt file:

```
passlib==1.7.4
```

This means that when the application is deployed to Azure, the passlib package should be installed automatically. However, there might be an issue with the installation process.

To ensure that the passlib package is installed in the Azure App Service, a script has been created to check if the passlib package is installed and install it if it's not:

```bash
chmod +x check_passlib_installation.py
./check_passlib_installation.py
```

The script will:
1. Check if the passlib package is installed in the Azure App Service
2. If not installed, install it
3. Verify that the installation was successful

## Deployment Results

The deployment of the fix was attempted, but the site failed to start within the allotted time. The error message was:

```
Status: Starting the site... Time: 584(s)
Status: Starting the site... Time: 600(s)
Status: Starting the site... Time: 616(s)
Status: Site failed to start. Time: 632(s)
Deployment failed because the site failed to start within 10 mins.
InprogressInstances: 0 SuccessfulInstances: 0 FailedInstances: 1
Error: Deployment for site 'ai-event-planner-saas-py' with DeploymentId '806ac7e0-d942-4c60-86f6-62abc1af8835' failed because the worker proccess failed to start within the allotted time.
Please check the runtime logs for more info: https://ai-event-planner-saas-py.scm.azurewebsites.net/api/logs/docker
```

After checking the logs, we found another issue:

```
  File "/home/site/wwwroot/app/auth/router.py", line 10, in <module>
    from app.db.session import get_db
  File "/home/site/wwwroot/app/db/session.py", line 5, in <module>
    from app.db.base import SessionLocal
  File "/home/site/wwwroot/app/db/base.py", line 8, in <module>
    engine = create_engine(
  File "<string>", line 2, in create_engine
  File "/opt/python/3.9.21/lib/python3.9/site-packages/sqlalchemy/util/deprecations.py", line 281, in warned
    return fn(*args, **kwargs)  # type: ignore[no-any-return]
  File "/opt/python/3.9.21/lib/python3.9/site-packages/sqlalchemy/engine/create.py", line 602, in create_engine
    dbapi = dbapi_meth(**dbapi_args)
  File "/opt/python/3.9.21/lib/python3.9/site-packages/sqlalchemy/dialects/postgresql/psycopg2.py", line 696, in import_dbapi
    import psycopg2
ModuleNotFoundError: No module named 'psycopg2'
```

This indicates that the psycopg2 package, which is a PostgreSQL adapter for Python, is not installed in the Azure App Service. This package is required for the SQLAlchemy database connection.

The issues we need to fix are:

1. The auth directory not being included in the deployment package.
2. The passlib package not being installed correctly.
3. The psycopg2 package not being installed correctly.

To troubleshoot these issues, you can:

1. Check the runtime logs at https://ai-event-planner-saas-py.scm.azurewebsites.net/api/logs/docker
2. Run the verification scripts to check if the auth directory, passlib package, and psycopg2 package are properly deployed:
   ```bash
   ./verify_azure_deployment.sh
   ```
3. If the verification scripts show that the auth directory, passlib package, and psycopg2 package are properly deployed, check for other issues in the application logs.

If you still encounter issues, check the application logs for any other missing dependencies or directories and update the update-azure-agents.sh script accordingly.
