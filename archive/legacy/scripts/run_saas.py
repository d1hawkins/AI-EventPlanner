#!/usr/bin/env python3
"""
Run the AI Event Planner SaaS application locally.
This script sets up the environment and starts the FastAPI server.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Ensure we're in the project root directory
project_root = Path(__file__).resolve().parent
os.chdir(project_root)

def check_environment():
    """Check if the required environment variables are set."""
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: The following environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in a .env file or in your environment.")
        print("You can use .env.saas.example as a template.")
        return False
    
    return True

def load_env_file():
    """Load environment variables from .env file."""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        # Try to copy from example file if it exists
        example_file = project_root / ".env.saas.example"
        if example_file.exists():
            print("No .env file found. Creating one from .env.saas.example...")
            with open(example_file, "r") as src, open(env_file, "w") as dst:
                for line in src:
                    if not line.strip().startswith("#") and "=" in line:
                        dst.write(line)
            print(".env file created. Please edit it with your configuration.")
        else:
            print("No .env file found. Please create one based on .env.saas.example.")
        return False
    
    # Load environment variables from .env file
    print("Loading environment variables from .env file...")
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()
    
    return True

def check_database():
    """Check if the database is accessible."""
    try:
        from app.db.session import SessionLocal
        
        # Try to connect to the database
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        print("Database connection successful.")
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

def run_migrations():
    """Run database migrations."""
    try:
        print("Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migrations completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return False
    except FileNotFoundError:
        print("Error: alembic command not found. Make sure it's installed.")
        return False

def start_server():
    """Start the FastAPI server."""
    try:
        print("Starting server...")
        
        # Start the server
        server_process = subprocess.Popen(
            ["uvicorn", "app.main_saas:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        
        # Wait for the server to start
        time.sleep(2)
        
        # Open the browser
        webbrowser.open("http://localhost:8000/static/saas/index.html")
        
        print("Server started. Press Ctrl+C to stop.")
        
        # Print server output
        try:
            while True:
                output = server_process.stdout.readline()
                if output:
                    print(output.strip())
                if server_process.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("Server stopped.")
        
        return True
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def main():
    """Main function."""
    print("Starting AI Event Planner SaaS application...")
    
    # Load environment variables
    if not load_env_file():
        return 1
    
    # Check environment
    if not check_environment():
        return 1
    
    # Check database
    if not check_database():
        return 1
    
    # Run migrations
    if not run_migrations():
        return 1
    
    # Start server
    if not start_server():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
