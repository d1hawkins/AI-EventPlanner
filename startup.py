import os
import subprocess
import sys
import importlib.util

# Print Python version and path for debugging
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")

# Get the port from environment variable
port = os.environ.get('PORT', '8000')

# Install dependencies
print("Installing dependencies...")
subprocess.call(["pip", "install", "-r", "requirements.txt"])
subprocess.call(["pip", "install", "fastapi", "uvicorn", "gunicorn", "sqlalchemy", "pydantic", "langchain", "langgraph", "google-generativeai", "openai"])

# Print environment for debugging
print("Environment variables:")
for key, value in os.environ.items():
    if not key.startswith('PATH') and not key.startswith('PYTHONPATH'):
        print(f"{key}: {value}")

# Add current directory to Python path
sys.path.insert(0, os.getcwd())
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

# Run database migrations if needed
if os.environ.get('RUN_MIGRATIONS', 'false').lower() == 'true':
    print("Running database migrations...")
    subprocess.call(["python", "-m", "scripts.run_azure_migrations_fixed"])

# Check if main_saas.py exists in the app directory
main_saas_path = os.path.join('app', 'main_saas.py')
app_adapter_path = 'app_adapter.py'
main_path = os.path.join('app', 'main.py')

print(f"Checking for {main_saas_path}: {os.path.exists(main_saas_path)}")
print(f"Checking for {app_adapter_path}: {os.path.exists(app_adapter_path)}")
print(f"Checking for {main_path}: {os.path.exists(main_path)}")

# Try to determine which module to use
if os.path.exists(main_saas_path):
    print("Found main_saas.py, using app.main_saas:app")
    app_module = "app.main_saas:app"
elif os.path.exists(main_path):
    print("Found main.py, using app.main:app")
    app_module = "app.main:app"
else:
    print("Using app_adapter:app as fallback")
    app_module = "app_adapter:app"

# Run gunicorn with the determined app module
print(f"Starting application with {app_module}...")
cmd = f'gunicorn {app_module} --bind=0.0.0.0:{port} --workers=4 --timeout=120'
subprocess.call(cmd, shell=True)
