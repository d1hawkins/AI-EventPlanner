#!/usr/bin/env python
"""
Script to create the saas.db file with the correct schema.
This script loads environment variables from .env.saas and creates the database.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env.saas
load_dotenv(".env.saas")

# Explicitly set the database URL to use SQLite
os.environ["DATABASE_URL"] = "sqlite:///./saas.db"
DATABASE_URL = "sqlite:///./saas.db"
print(f"Using database URL: {DATABASE_URL}")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

# Import the Base and models
sys.path.append(".")  # Add current directory to path
from app.db.base import Base
from app.db.models_updated import *  # Import all models from base models
from app.db.models_updated import *  # Import all models from SaaS models

# Create tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Verify tables were created
print("Verifying tables...")
from sqlalchemy import inspect
inspector = inspect(engine)
for table_name in inspector.get_table_names():
    print(f"- {table_name}")

print("Database initialization complete!")
