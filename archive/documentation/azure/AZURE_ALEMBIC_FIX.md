# Azure Alembic Fix

## Issue

After fixing the auth directory, psycopg2 package, email-validator, and icalendar issues, we encountered another error with the alembic command:

```
Error running migrations: [Errno 2] No such file or directory: 'alembic'
```

This error occurred when the migration script was trying to run the alembic command to perform database migrations. The alembic package was not installed in the Azure App Service.

## Root Cause

The alembic package was not being installed correctly in the Azure App Service. The startup.sh script was installing several packages, but it was not explicitly installing the alembic package.

## Fix

We made the following changes to fix the alembic package issue:

1. Modified the `startup.sh` script to include the alembic package in the list of packages to install:

```bash
# Install required dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install fastapi uvicorn gunicorn sqlalchemy pydantic langchain langgraph google-generativeai openai passlib python-jose python-multipart bcrypt python-dotenv psycopg2-binary email-validator icalendar alembic
```

2. Created a script to check if the alembic package is installed in the Azure App Service and install it if it's not.

3. Updated the verification scripts to check if the alembic package is installed.

## Deployment Instructions

To deploy the fix:

1. Make sure you have the latest version of the startup.sh script with the alembic package included in the list of packages to install.
2. Run the update-azure-agents.sh script to deploy the updated files to Azure:

```bash
./update-azure-agents.sh
```

3. Monitor the deployment logs to ensure that the alembic package is properly installed.
4. Verify that the application is running correctly by accessing the application URL.

## Verification

After deploying the fix, you should see the following in the deployment logs:

1. The alembic package being installed:
   ```
   Installing alembic...
   ```

2. No error about the alembic command not being found in the application logs.

### Verification Scripts

A verification script has been created to check if the alembic package is installed in the Azure App Service. The script connects to the Azure App Service using SSH and checks if the alembic package is installed.

To run the verification script:

```bash
chmod +x check_alembic_installation.py
./check_alembic_installation.py
```

The script will:
1. Check if the alembic package is installed in the Azure App Service
2. If not installed, install it
3. Verify that the installation was successful

## Conclusion

The issue was caused by a missing dependency in the Azure App Service. By adding the alembic package to the list of packages to install in the startup.sh script, we were able to fix the issue and ensure that the application can properly run database migrations.

The verification script provides an additional tool to ensure that the alembic package is installed correctly in the Azure App Service.
