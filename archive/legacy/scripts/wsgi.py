"""
WSGI entry point for Azure App Service.
This file dynamically determines which app module to use based on what's available.
"""

import os
import sys
import importlib.util

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Print debugging information
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"WSGI file directory: {current_dir}")
print(f"Python path: {sys.path}")

# List all directories in the current path to help with debugging
print("Listing directories in current path:")
for item in os.listdir('.'):
    if os.path.isdir(item):
        print(f"  - {item}")
        if item == 'app':
            print("    Listing contents of app directory:")
            for subitem in os.listdir(item):
                print(f"      - {subitem}")

# Check if main_saas.py exists in the app directory
main_saas_path = os.path.join('app', 'main_saas.py')
app_adapter_path = 'app_adapter.py'
main_path = os.path.join('app', 'main.py')

print(f"Checking for {main_saas_path}: {os.path.exists(main_saas_path)}")
print(f"Checking for {app_adapter_path}: {os.path.exists(app_adapter_path)}")
print(f"Checking for {main_path}: {os.path.exists(main_path)}")

# Try to import the FastAPI app from the appropriate module
application = None

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

# If that fails, try app.main
if application is None and os.path.exists(main_path):
    try:
        print("Attempting to import from app.main")
        from app.main import app as application
        print("Successfully imported app from app.main")
    except ImportError as e:
        print(f"Error importing app from app.main: {str(e)}")
        application = None

# If that fails too, try app_simplified
if application is None:
    try:
        print("Attempting to import from app_simplified")
        from app_simplified import app as application
        print("Successfully imported app from app_simplified")
    except ImportError as e:
        print(f"Error importing app from app_simplified: {str(e)}")
        application = None

# If that fails too, fall back to app_adapter
if application is None:
    try:
        print("Attempting to import from app_adapter")
        from app_adapter import app as application
        print("Successfully imported app from app_adapter")
    except ImportError as e:
        print(f"Error importing app from app_adapter: {str(e)}")
        print("All import attempts failed. Cannot start the application.")
        raise

# This is for WSGI compatibility
app = application
