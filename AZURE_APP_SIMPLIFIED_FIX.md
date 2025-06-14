# Azure App Service Import Fix for app_simplified.py

## Problem

The application was failing to start on Azure App Service with the following error:

```
ModuleNotFoundError: No module named 'app_simplified'
```

This error occurs because the application is trying to import the `app_simplified` module, but it can't find it in the Python path.

## Root Cause Analysis

After investigating the deployment scripts and startup files, we found that:

1. The `azure-deploy-simplified.sh` script creates a custom startup.sh file that specifically uses `gunicorn app_simplified:app`, which tries to import the app from app_simplified.py.

2. However, none of the main application startup files (wsgi.py, startup.py, startup.sh) were configured to try importing from app_simplified.py. They were only looking for app.main_saas, app.main, or app_adapter.

## Solution

We've updated three key startup files to include app_simplified.py in their import attempts:

1. **wsgi.py**: Added a new import attempt for app_simplified.py between the app.main and app_adapter import attempts.

2. **startup.py**: Added a check for app_simplified.py in the module determination logic.

3. **startup.sh**: Added a check for app_simplified.py in the module determination logic.

These changes ensure that the application can find and import app_simplified.py regardless of which startup method is used.

## Files Modified

- wsgi.py
- startup.py
- startup.sh

## How to Deploy

To deploy these changes to Azure App Service:

1. Push the updated files to your repository.
2. Redeploy the application using one of your existing deployment scripts.

## Verification

After deploying, check the application logs to verify that it's successfully importing app_simplified.py. You should see a message like:

```
Attempting to import from app_simplified
Successfully imported app from app_simplified
```

If you're still seeing the same error, check the application logs for more details and ensure that app_simplified.py is being included in the deployment package.
