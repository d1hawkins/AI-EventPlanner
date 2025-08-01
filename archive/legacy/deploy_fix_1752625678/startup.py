#!/usr/bin/env python3
"""
Azure startup script for AI Event Planner SaaS
"""
import os
import sys
import subprocess
import time

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("Dependencies installed successfully")

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
    
    # Import and run the application
    from run_saas_with_agents import main
    main()

if __name__ == "__main__":
    try:
        install_dependencies()
        setup_database()
        start_application()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)
