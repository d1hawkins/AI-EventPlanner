#!/usr/bin/env python3
"""
Run the AI Event Planner SaaS application locally without running migrations.
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

def load_env_file():
    """Load environment variables from .env.saas file."""
    env_file = project_root / ".env.saas"
    
    if not env_file.exists():
        print(f"Error: {env_file} not found.")
        return False
    
    # Load environment variables from .env.saas file
    print(f"Loading environment variables from {env_file}...")
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
    
    # Check database
    if not check_database():
        return 1
    
    # Start server
    if not start_server():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
