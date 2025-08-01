#!/usr/bin/env python3
"""
Azure startup script for AI Event Planner SaaS
This file is referenced by web.config for Azure App Service
"""
import os
import sys
import subprocess
import time

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        # Continue anyway as some dependencies might already be installed

def setup_database():
    """Setup database tables"""
    try:
        print("Setting up database...")
        # Import after dependencies are installed
        from create_tables import main as create_tables_main
        from create_subscription_plans import main as create_plans_main
        
        create_tables_main()
        create_plans_main()
        print("Database setup completed")
    except Exception as e:
        print(f"Database setup error (continuing anyway): {e}")

def start_application():
    """Start the SaaS application"""
    print("Starting AI Event Planner SaaS...")
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", "/home/site/wwwroot")
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    
    # Get the port from environment (Azure sets this)
    port = os.environ.get("PORT", "8000")
    os.environ["PORT"] = port
    
    # Import and run the application
    try:
        from run_saas_with_agents import main
        main()
    except ImportError as e:
        print(f"Import error: {e}")
        # Fallback to a simpler app if the main one fails
        try:
            from app_adapter_standalone import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=int(port))
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        install_dependencies()
        setup_database()
        start_application()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
