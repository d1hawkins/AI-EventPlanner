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
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(".env.saas")
    
    # Set default environment variables if not present
    if not os.getenv("HOST"):
        os.environ["HOST"] = "0.0.0.0"
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "production"
    if not os.getenv("APP_VERSION"):
        os.environ["APP_VERSION"] = "1.0.0"
    
    # Set LLM provider if not specified
    if not os.getenv("LLM_PROVIDER"):
        os.environ["LLM_PROVIDER"] = "openai"
    
    # Print startup information
    print("Starting AI Event Planner SaaS with Agent Integration")
    print("====================================================")
    print(f"Environment: {os.getenv('ENVIRONMENT')}")
    print(f"Version: {os.getenv('APP_VERSION')}")
    print(f"LLM Provider: {os.getenv('LLM_PROVIDER')}")
    print(f"Host: {os.getenv('HOST')}")
    print(f"Port: {port}")
    print("----------------------------------------------------")
    
    # Import and run the application
    try:
        import uvicorn
        uvicorn.run(
            "app.main_saas:app",
            host=os.getenv("HOST"),
            port=int(port),
            reload=False  # Set to False for production
        )
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

def main():
    """Main function for Azure startup"""
    try:
        install_dependencies()
        setup_database()
        start_application()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
