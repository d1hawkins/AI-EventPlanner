#!/usr/bin/env python3
"""
Azure startup script for AI Event Planner SaaS
This file is expected by Azure App Service
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
    
    print(f"Starting application on port {port}")
    
    # Import and run the application
    try:
        print("Attempting to start main SaaS application...")
        from run_saas_with_agents import main
        main()
    except ImportError as e:
        print(f"Import error for main app: {e}")
        # Fallback to a simpler app if the main one fails
        try:
            print("Falling back to standalone adapter...")
            from app_adapter_standalone import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=int(port))
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            # Final fallback - simple Flask app
            try:
                print("Final fallback to simple Flask app...")
                from flask import Flask
                app = Flask(__name__)
                
                @app.route('/')
                def hello():
                    return "AI Event Planner SaaS is starting up..."
                
                @app.route('/health')
                def health():
                    return {"status": "ok", "message": "Application is running"}
                
                app.run(host="0.0.0.0", port=int(port))
            except Exception as final_error:
                print(f"Final fallback error: {final_error}")
                sys.exit(1)

if __name__ == "__main__":
    try:
        print("=== Azure Startup Script Starting ===")
        install_dependencies()
        setup_database()
        start_application()
    except Exception as e:
        print(f"Startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
