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

def _construct_azure_postgres_url() -> Optional[str]:
    """Construct PostgreSQL URL from Azure environment variables if available."""
    # Try to get individual components that Azure might provide
    host = (
        os.getenv("POSTGRES_HOST") or 
        os.getenv("AZURE_POSTGRES_HOST") or 
        os.getenv("DB_HOST")
    )
    port = (
        os.getenv("POSTGRES_PORT") or 
        os.getenv("AZURE_POSTGRES_PORT") or 
        os.getenv("DB_PORT", "5432")
    )
    database = (
        os.getenv("POSTGRES_DB") or 
        os.getenv("AZURE_POSTGRES_DB") or 
        os.getenv("DB_NAME") or
        "eventplanner"
    )
    username = (
        os.getenv("POSTGRES_USER") or 
        os.getenv("AZURE_POSTGRES_USER") or 
        os.getenv("DB_USER")
    )
    password = (
        os.getenv("POSTGRES_PASSWORD") or 
        os.getenv("AZURE_POSTGRES_PASSWORD") or 
        os.getenv("DB_PASSWORD")
    )
    
    if host and username and password:
        return f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode=require"
    
    return None

# Database - Handle Azure APPSETTING_ prefix and various Azure environment variable formats
# PostgreSQL is required for ALL environments (local, test, production)
DATABASE_URL: str = (
    os.getenv("DATABASE_URL") or 
    os.getenv("APPSETTING_DATABASE_URL") or
    os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING") or
    os.getenv("POSTGRESQL_URL") or
    os.getenv("POSTGRES_URL") or
    # If we're in Azure and have individual connection parameters, construct the URL
    _construct_azure_postgres_url() or
    None
)

# Validate DATABASE_URL is set - PostgreSQL is required for ALL environments
if not DATABASE_URL:
    error_msg = "DATABASE_URL is not set and could not be constructed from environment variables."
    print(f"ERROR: {error_msg}")
    print("Available environment variables:")
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['DATABASE', 'DB', 'POSTGRES', 'SQL', 'ENVIRONMENT', 'APPSETTING']):
            # Mask sensitive information
            display_value = value[:20] + "..." if len(value) > 20 and any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY']) else value
            print(f"  {key}={display_value}")
    
    # PostgreSQL is REQUIRED for all environments
    env = os.getenv("ENVIRONMENT", "").lower()
    raise ValueError(
        f"DATABASE_URL must be set for ALL environments. Current ENVIRONMENT: '{env}'. "
        "PostgreSQL is required for local development, testing, and production. "
        "Please set DATABASE_URL in your environment or .env file. "
        "For local development, see docs/LOCAL_POSTGRES_SETUP.md"
    )

# Additional validation: Reject non-PostgreSQL databases
if DATABASE_URL and not DATABASE_URL.startswith("postgresql"):
    env = os.getenv("ENVIRONMENT", "").lower()
    raise ValueError(
        f"Only PostgreSQL databases are supported. "
        f"Current ENVIRONMENT: '{env}', DATABASE_URL starts with: {DATABASE_URL.split(':')[0]} "
        "Please configure a PostgreSQL DATABASE_URL. "
        "For local development, see docs/LOCAL_POSTGRES_SETUP.md"
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
