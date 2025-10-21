import os
from typing import Optional, Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# LLM Provider
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # Default to OpenAI

# OpenAI API Key
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
# Don't raise an error if OPENAI_API_KEY is not set
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable is not set. OpenAI features may be disabled.")

# Google AI API Key
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
# Don't raise an error if GOOGLE_API_KEY is not set
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable is not set. Google AI features may be disabled.")

# JWT Authentication
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = "development_secret_key"  # Default for development
    print("WARNING: Using default SECRET_KEY. This is insecure for production.")

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database - Handle Azure APPSETTING_ prefix
DATABASE_URL: str = (
    os.getenv("DATABASE_URL") or 
    os.getenv("APPSETTING_DATABASE_URL") or 
    "sqlite:///./app.db"
)

# Server
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# LLM Configuration
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")  # OpenAI model
GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-pro")  # Google AI model

# Search API Configuration
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
if not TAVILY_API_KEY:
    print("WARNING: TAVILY_API_KEY environment variable is not set. Internet search functionality will be disabled.")

def validate_config():
    """Validate configuration and print warnings for missing values."""
    validation_errors = []
    warnings = []
    
    # Critical authentication settings
    if not SECRET_KEY or SECRET_KEY == "development_secret_key":
        if SECRET_KEY == "development_secret_key":
            warnings.append("Using default SECRET_KEY. This is insecure for production.")
        else:
            validation_errors.append("SECRET_KEY environment variable is not set. Authentication will not work.")
    
    if not DATABASE_URL:
        warnings.append("DATABASE_URL environment variable is not set. Using default SQLite database.")
    
    # LLM Provider validation
    if LLM_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
        warnings.append("OPENAI_API_KEY environment variable is not set but LLM_PROVIDER is 'openai'. OpenAI features may be disabled.")
    
    if LLM_PROVIDER.lower() == "google" and not GOOGLE_API_KEY:
        warnings.append("GOOGLE_API_KEY environment variable is not set but LLM_PROVIDER is 'google'. Google AI features may be disabled.")
    
    # Print warnings
    for warning in warnings:
        print(f"WARNING: {warning}")
    
    # Print errors
    for error in validation_errors:
        print(f"ERROR: {error}")
    
    if validation_errors:
        print("Configuration validation failed. Please fix the above errors.")
        return False
    
    print("Configuration validation check complete.")
    return True
