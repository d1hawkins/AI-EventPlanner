# Azure Deployment Package Dependencies Fix

## Issues

The Azure deployment was failing with the following errors:

1. First error:
```
ModuleNotFoundError: No module named 'passlib'
```
This error occurred when trying to import `from passlib.context import CryptContext` in the auth router.

2. Second error:
```
ModuleNotFoundError: No module named 'dotenv'
```
This error occurred when trying to import `from dotenv import load_dotenv` in the config.py file.

## Root Cause

Although these packages are included in the requirements.txt file, they were not being properly installed during the Azure deployment process. This was because:

1. The requirements.txt file was not being included in the deployment package.
2. The startup.sh script did not explicitly install these packages.

## Fix

The following changes were made to fix the issues:

1. Updated the update-azure-agents.sh script to include the requirements.txt file in the deployment package:

```bash
# Copy the updated files to the deployment directory
echo "Copying updated files to deployment directory..."
mkdir -p $DEPLOY_DIR
cp startup.py $DEPLOY_DIR/
cp startup.sh $DEPLOY_DIR/
cp wsgi.py $DEPLOY_DIR/
cp web.config $DEPLOY_DIR/
cp app_adapter.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/  # Added this line
chmod +x $DEPLOY_DIR/startup.sh
```

2. Updated the startup.sh script to explicitly install passlib, python-dotenv, and other required packages:

```bash
# Install required dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install fastapi uvicorn gunicorn sqlalchemy pydantic langchain langgraph google-generativeai openai passlib python-jose python-multipart bcrypt python-dotenv
```

## Deployment Instructions

To deploy the fix:

1. Make sure you have the latest version of the following files:
   - update-azure-agents.sh
   - startup.sh (with the package installation fixes)
   - wsgi.py (with the package installation fixes)
   - requirements.txt

2. Run the update-azure-agents.sh script to deploy the updated files to Azure:

```bash
./update-azure-agents.sh
```

3. Monitor the deployment logs to ensure that the required packages are installed correctly.
4. Verify that the application is running correctly by accessing the application URL.

### What the Fix Does

The fix works in two ways to ensure that all required packages are installed:

1. **startup.sh**: Explicitly installs passlib, python-dotenv, and other required packages:

```bash
# Install required dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install fastapi uvicorn gunicorn sqlalchemy pydantic langchain langgraph google-generativeai openai passlib python-jose python-multipart bcrypt python-dotenv
```

2. **wsgi.py**: Ensures that required packages are installed before trying to import from app.main_saas:

```python
# Ensure required packages are installed
try:
    print("Ensuring required packages are installed...")
    import subprocess
    
    # Install passlib, python-dotenv, and other auth-related packages
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "passlib", "python-jose", "python-multipart", "bcrypt", "python-dotenv"
    ])
    print("Successfully installed required packages")
except Exception as e:
    print(f"Error installing required packages: {str(e)}")

# First try app.main_saas
if os.path.exists(main_saas_path):
    try:
        print("Attempting to import from app.main_saas")
        # Try to import passlib first to check if it's installed
        try:
            import passlib
            print(f"passlib is installed (version: {passlib.__version__})")
        except ImportError:
            print("passlib is not installed, falling back to app_adapter")
            raise ImportError("passlib is not installed")
            
        from app.main_saas import app as application
        print("Successfully imported app from app.main_saas")
    except ImportError as e:
        print(f"Error importing app from app.main_saas: {str(e)}")
        application = None
```

This dual approach ensures that all required packages are installed and available when the application tries to import them.

## Verification

After deploying the fix, you should see the following in the deployment logs:

1. The requirements.txt file being copied to the deployment directory.
2. The passlib and python-dotenv packages being installed during the startup process.
3. No ModuleNotFoundError for passlib or dotenv in the application logs.

### Verification Methods

#### Method 1: Using the test_azure_deployment.py Script

The `test_azure_deployment.py` script has been updated to include a test for the passlib module. This script will verify that passlib is installed and working correctly.

To run the test:

```bash
python test_azure_deployment.py
```

The script will:
1. Test if passlib is installed and working correctly
2. Set up a test environment that simulates Azure's environment
3. Test the import paths in the app_adapter.py file
4. Clean up the test environment

If the script outputs "Passlib test PASSED!" and "Azure deployment test PASSED!", then the fix has been applied successfully.

#### Method 2: Manual Verification

You can also manually verify that passlib is installed and working correctly by running the following Python code:

```python
#!/usr/bin/env python
"""
Simple script to verify that passlib is installed and working correctly.
This can be used to test the fix for the passlib import error in Azure.
"""

try:
    import passlib
    from passlib.context import CryptContext
    
    # Create a password context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Test password hashing
    hashed_password = pwd_context.hash("testpassword")
    
    print("SUCCESS: passlib is installed and working correctly!")
    print(f"passlib version: {passlib.__version__}")
    print(f"Test hash: {hashed_password}")
    print("Verification: ", pwd_context.verify("testpassword", hashed_password))
    
except ImportError as e:
    print(f"ERROR: {e}")
    print("The passlib module is not installed or not working correctly.")
    print("Please make sure the fix has been applied correctly.")

except Exception as e:
    print(f"ERROR: An unexpected error occurred: {e}")
```

To verify the fix on Azure, you can upload this script to your Azure App Service and run it:

```bash
# Upload the script to Azure
az webapp deploy --resource-group ai-event-planner-rg --name ai-event-planner-saas-py --src-path verify_passlib.py --type static --target-path /home/site/wwwroot/verify_passlib.py

# Run the script on Azure
az webapp ssh --resource-group ai-event-planner-rg --name ai-event-planner-saas-py --command "cd /home/site/wwwroot && python verify_passlib.py"
```

If the script outputs "SUCCESS: passlib is installed and working correctly!", then the fix has been applied successfully.

If you still encounter issues, check the application logs for any other missing dependencies and update the startup.sh script accordingly.
