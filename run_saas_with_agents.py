"""
Script to run the SaaS application with integrated agent system.

This script starts the FastAPI application with the tenant-aware agent system.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.saas")

# Set default environment variables if not present
if not os.getenv("HOST"):
    os.environ["HOST"] = "0.0.0.0"
if not os.getenv("PORT"):
    os.environ["PORT"] = "8002"
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "development"
if not os.getenv("APP_VERSION"):
    os.environ["APP_VERSION"] = "1.0.0"

# Set LLM provider if not specified
if not os.getenv("LLM_PROVIDER"):
    os.environ["LLM_PROVIDER"] = "openai"  # or "google" or "azure_openai"

# Print startup information
print("Starting AI Event Planner SaaS with Agent Integration")
print("====================================================")
print(f"Environment: {os.getenv('ENVIRONMENT')}")
print(f"Version: {os.getenv('APP_VERSION')}")
print(f"LLM Provider: {os.getenv('LLM_PROVIDER')}")
print(f"Host: {os.getenv('HOST')}")
print(f"Port: {os.getenv('PORT')}")
print("----------------------------------------------------")

# Run the application
if __name__ == "__main__":
    try:
        uvicorn.run(
            "app.main_saas:app",
            host=os.getenv("HOST"),
            port=int(os.getenv("PORT")),
            reload=True
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {str(e)}")
        sys.exit(1)
