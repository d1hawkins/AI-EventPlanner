from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

from app.config import DATABASE_URL

# Create SQLAlchemy engine with PostgreSQL-specific configuration
def create_db_engine(database_url: str):
    """
    Create a database engine. Only PostgreSQL is supported.
    
    Args:
        database_url: PostgreSQL connection URL
        
    Returns:
        SQLAlchemy engine instance
        
    Raises:
        ValueError: If database_url is invalid or not PostgreSQL
    """
    # Validate database URL
    if not database_url or database_url.strip() == "":
        print(f"ERROR: DATABASE_URL is empty or not set. Current value: '{database_url}'")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['DATABASE', 'DB', 'POSTGRES', 'SQL', 'ENVIRONMENT']):
                # Mask sensitive information
                display_value = value[:20] + "..." if len(value) > 20 and 'PASSWORD' in key.upper() else value
                print(f"  {key}={display_value}")
        
        raise ValueError(
            "DATABASE_URL is required but is not set. "
            "PostgreSQL is required for all environments. "
            "Please configure DATABASE_URL in your environment or .env file. "
            "For local development, see docs/LOCAL_POSTGRES_SETUP.md"
        )
    
    # Validate PostgreSQL URL
    # Accept both 'postgres://' and 'postgresql://' URL schemes (both are valid for PostgreSQL)
    if not (database_url.startswith("postgresql") or database_url.startswith("postgres://")):
        raise ValueError(
            f"Only PostgreSQL databases are supported. "
            f"DATABASE_URL starts with: {database_url.split(':')[0]} "
            "Please configure a PostgreSQL DATABASE_URL. "
            "For local development, see docs/LOCAL_POSTGRES_SETUP.md"
        )
    
    try:
        # PostgreSQL-specific configuration
        env = os.getenv("ENVIRONMENT", "").lower() or "production"
        print(f"INFO: Connecting to PostgreSQL database for {env} environment")
        return create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
    except Exception as e:
        print(f"ERROR: Failed to create database engine")
        print(f"Error details: {str(e)}")
        print("This is a fatal error. The application cannot start without a valid database connection.")
        raise

# Log the database connection
print(f"Initializing PostgreSQL database connection")
print(f"Database URL: {DATABASE_URL[:50]}...")

engine = create_db_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()
