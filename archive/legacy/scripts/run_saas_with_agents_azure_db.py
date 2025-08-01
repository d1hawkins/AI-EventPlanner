#!/usr/bin/env python3
"""
Script to run the SaaS application with integrated agent system locally,
but connected to the Azure PostgreSQL database for debugging purposes.

This script starts the FastAPI application with the tenant-aware agent system
and connects to the Azure database instead of a local database.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create a logger for this script
logger = logging.getLogger("run_saas_with_agents_azure_db")

# Load environment variables from .env.azure
logger.info("Loading environment variables from .env.azure")
load_dotenv(".env.azure")

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

# Enable agent logging
os.environ["ENABLE_AGENT_LOGGING"] = "true"
os.environ["AGENT_MEMORY_STORAGE"] = "file"
os.environ["AGENT_MEMORY_PATH"] = "./agent_memory"

# Print startup information
print("\n" + "=" * 80)
print("Starting AI Event Planner SaaS with Agent Integration (Azure DB)")
print("=" * 80)
print(f"Environment: {os.getenv('ENVIRONMENT')}")
print(f"Version: {os.getenv('APP_VERSION')}")
print(f"LLM Provider: {os.getenv('LLM_PROVIDER')}")
print(f"Host: {os.getenv('HOST')}")
print(f"Port: {os.getenv('PORT')}")
print(f"Database URL: {os.getenv('DATABASE_URL')}")
print("-" * 80)

# Check if the DATABASE_URL is set and points to Azure
db_url = os.getenv("DATABASE_URL", "")
if not db_url or "azure" not in db_url.lower():
    logger.warning("DATABASE_URL is not set or does not point to an Azure database.")
    logger.warning("Please ensure your .env.azure file contains the correct DATABASE_URL.")
    
    # Ask the user if they want to continue
    response = input("Do you want to continue anyway? (y/n): ")
    if response.lower() != "y":
        logger.info("Exiting...")
        sys.exit(0)

# Run the application
if __name__ == "__main__":
    try:
        # Add additional debugging information
        logger.info("Starting FastAPI application with uvicorn")
        logger.info("Using app.main_saas:app as the application module")
        
        # Run with reload=True for development
        uvicorn.run(
            "app.main_saas:app",
            host=os.getenv("HOST"),
            port=int(os.getenv("PORT")),
            reload=True,
            log_level="debug"
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1)
