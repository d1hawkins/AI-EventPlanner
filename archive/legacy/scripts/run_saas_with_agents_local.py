"""
Script to run the SaaS application with integrated agent system locally.

This script starts the FastAPI application with the tenant-aware agent system
using a local SQLite database.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables from local config
load_dotenv(".env.saas.local")

# Force OpenAI as the LLM provider
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "gpt-4"

# Print startup information
print("Starting AI Event Planner SaaS with Agent Integration (Local)")
print("===========================================================")
print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
print(f"Version: {os.getenv('APP_VERSION', '1.0.0')}")
print(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
print(f"Host: {os.getenv('HOST', '0.0.0.0')}")
print(f"Port: {os.getenv('PORT', '8004')}")
print(f"Database: {os.getenv('DATABASE_URL', 'sqlite:///./saas.db')}")
print("-----------------------------------------------------------")

# Run the application
if __name__ == "__main__":
    try:
        # Create the database tables if they don't exist
        print("Setting up database...")
        from app.db.base import Base, engine
        Base.metadata.create_all(bind=engine)
        print("Database setup complete.")
        
        # Run the application
        uvicorn.run(
            "app.main_saas:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8005")),  # Use port 8005 instead
            reload=True
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {str(e)}")
        sys.exit(1)
