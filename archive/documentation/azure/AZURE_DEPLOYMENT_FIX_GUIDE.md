# Azure Deployment Fix Guide

This document explains the changes made to fix the error "Failed to find attribute 'app' in 'app'" when deploying the application to Azure App Service without Docker.

## Problem Analysis

The error occurs because Azure is trying to import an object named `app` from a module named `app`, but there's a mismatch between:

1. What Azure is expecting to import (`app` from the main application file)
2. What's actually being exported in the application files

## Additional Challenge

We also discovered that the required packages (like FastAPI) were not being installed properly in the Azure environment, leading to import errors:

```
ModuleNotFoundError: No module named 'fastapi'
```

## Solution Implemented

We've implemented a comprehensive solution to address these issues:

### 1. Created a Flask Proxy in app.py

Modified `app.py` to create a Flask application that acts as a proxy to the FastAPI application:

```python
from flask import Flask, request, Response
import requests
import subprocess
import threading
import os
import time

# Install required packages
subprocess.call(["./install_packages.sh"], shell=True)

# Create a Flask application
app = Flask(__name__)

# Define the FastAPI application URL (running locally)
FASTAPI_URL = "http://localhost:8001"  # FastAPI will run on a different port

# Start the FastAPI application in a separate process
def run_fastapi():
    # Wait a moment to ensure packages are installed
    time.sleep(2)
    subprocess.Popen(["gunicorn", "app_simplified:app", "--bind", "0.0.0.0:8001", "--workers", "2"])

# Start FastAPI in a separate thread
threading.Thread(target=run_fastapi, daemon=True).start()
```

This approach:
- Creates a Flask application that Azure can detect and run
- Installs the required packages using a shell script
- Starts the FastAPI application in a separate process
- Forwards all requests from the Flask application to the FastAPI application
- Returns the FastAPI responses through the Flask application

### 2. Created a Package Installation Script

Created a shell script `install_packages.sh` that installs the required packages:

```bash
#!/bin/bash
# Install required packages
pip install -r requirements.txt
```

### 3. Updated Requirements

Added Flask and requests to the requirements file:

```
fastapi==0.95.0
uvicorn==0.21.1
gunicorn==20.1.0
jinja2==3.1.2
python-dotenv==1.0.0
flask==2.2.3
requests==2.28.2
```

### 4. Created a Simplified Deployment Script

Created a new deployment script `azure-deploy-simple-fix.sh` that:

1. Deploys all the essential files: `app.py`, `app_simplified.py`, `wsgi.py`, `install_packages.sh`, and `requirements_simplified.txt`
2. Lets Azure use its auto-detection to run the application

## How to Deploy

To deploy the application with this fix, run the new deployment script:

```bash
chmod +x azure-deploy-simple-fix.sh
./azure-deploy-simple-fix.sh
```

This script will:

1. Create or update the necessary Azure resources (Resource Group, App Service Plan, Web App)
2. Package the essential application files
3. Deploy the package to Azure App Service
4. Enable logging for troubleshooting

## Why This Approach Works

The previous approaches tried to make Azure find the FastAPI app directly, but Azure was determined to run a Flask application with `gunicorn app:app`.

This new approach works with Azure's auto-detection instead of against it:
- We provide a real Flask application in app.py that Azure can detect and run
- We ensure all required packages are installed using a shell script
- The Flask application acts as a proxy to the FastAPI application
- We added a static home page and health check endpoint to ensure the application is responsive even if the FastAPI application fails to start
- This is a more robust solution that works with Azure's auto-detection

## Troubleshooting

If you still encounter issues after deploying with the new script, you can check the logs in the Azure Portal:

1. Go to the Azure Portal
2. Navigate to your App Service
3. Select "Log stream" under the "Monitoring" section
4. Check for any errors in the logs

You can also use the Kudu console to check the deployed files and logs:

1. Go to the Azure Portal
2. Navigate to your App Service
3. Select "Advanced Tools" under the "Development Tools" section
4. Click "Go" to open the Kudu console
5. Navigate to "Debug console" > "CMD"
6. Check the files in the `site/wwwroot` directory
7. Check the logs in the `LogFiles` directory
