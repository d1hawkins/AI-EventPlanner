from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

from app.config import DATABASE_URL

# Create SQLAlchemy engine with database-specific configuration
def create_db_engine(database_url: str):
    # Validate database URL
    if not database_url or database_url.strip() == "":
        print(f"ERROR: DATABASE_URL is empty or not set. Current value: '{database_url}'")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'DATABASE' in key.upper() or 'DB' in key.upper():
                print(f"  {key}={value}")
        
        # Fallback to SQLite for development/testing
        fallback_url = "sqlite:///./fallback_app.db"
        print(f"Using fallback SQLite database: {fallback_url}")
        database_url = fallback_url
    
    try:
        if database_url.startswith("sqlite"):
            # SQLite-specific configuration
            return create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL-specific configuration
            return create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
            )
    except Exception as e:
        print(f"ERROR: Failed to create database engine with URL: {database_url}")
        print(f"Error details: {str(e)}")
        
        # Final fallback to SQLite
        fallback_url = "sqlite:///./emergency_fallback.db"
        print(f"Using emergency fallback SQLite database: {fallback_url}")
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False}
        )

# Log the database type being used
db_type = "PostgreSQL" if DATABASE_URL and DATABASE_URL.startswith("postgresql") else ("SQLite" if DATABASE_URL and DATABASE_URL.startswith("sqlite") else "Unknown")
print(f"Initializing database with URL: {DATABASE_URL}")
print(f"Database type: {db_type}")

# Additional debugging for Azure deployment
if not DATABASE_URL or DATABASE_URL.startswith("sqlite"):
    print("WARNING: Using SQLite database. This may not be intended for production deployment.")
    print("Environment variables check:")
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['DATABASE', 'DB', 'POSTGRES', 'SQL', 'AZURE', 'APPSETTING']):
            # Mask sensitive information
            display_value = value[:20] + "..." if len(value) > 20 and any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY']) else value
            print(f"  {key}={display_value}")

engine = create_db_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()
