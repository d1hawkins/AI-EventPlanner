#!/usr/bin/env python
"""
Create Tables Direct

This script directly creates database tables using SQLAlchemy models.
It uses hardcoded connection parameters to ensure it works regardless of environment variables.
"""

import os
import sys
import argparse
import traceback

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

def create_tables_direct():
    """Create database tables directly using SQLAlchemy."""
    try:
        # Import SQLAlchemy
        from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, relationship
        
        # Define database connection parameters
        # Try multiple possible database servers
        db_servers = [
            "ai-event-planner-db.postgres.database.azure.com",
            "aieventdb.postgres.database.azure.com",
            "aieventplanner.postgres.database.azure.com"
        ]
        
        db_name = "eventplanner"
        db_user = "dbadmin"
        db_password = "P@ssw0rd"  # This is just a placeholder, will be replaced
        
        # Try to get connection parameters from environment variables
        if "DATABASE_URL" in os.environ:
            print(f"Using DATABASE_URL from environment: {os.environ['DATABASE_URL'].split('@')[0].split(':')[0]}:***@***")
            engine = create_engine(os.environ["DATABASE_URL"])
        else:
            # Try each server until one works
            connected = False
            for server in db_servers:
                try:
                    # Try with different user formats
                    for user_format in [f"{db_user}@{server}", db_user]:
                        try:
                            # Try with and without SSL
                            for ssl_mode in ["require", "prefer", "disable"]:
                                connection_string = f"postgresql://{user_format}:{db_password}@{server}:5432/{db_name}?sslmode={ssl_mode}"
                                print(f"Trying connection: {connection_string.split(':')[0]}:***@{server}")
                                
                                engine = create_engine(connection_string)
                                # Test the connection
                                connection = engine.connect()
                                connection.close()
                                
                                print(f"✅ Connected to PostgreSQL server: {server}")
                                connected = True
                                break
                        except Exception as e:
                            print(f"Failed to connect with user format {user_format}: {str(e)}")
                        
                        if connected:
                            break
                except Exception as e:
                    print(f"Failed to connect to server {server}: {str(e)}")
                
                if connected:
                    break
            
            if not connected:
                print("Failed to connect to any PostgreSQL server. Please check your connection parameters.")
                return False
        
        # Create a base class for declarative models
        Base = declarative_base()
        
        # Define models
        class User(Base):
            __tablename__ = "users"
            
            id = Column(Integer, primary_key=True, index=True)
            email = Column(String, unique=True, index=True)
            hashed_password = Column(String)
            is_active = Column(Boolean, default=True)
            is_superuser = Column(Boolean, default=False)
            full_name = Column(String, nullable=True)
            
        class Organization(Base):
            __tablename__ = "organizations"
            
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String, index=True)
            description = Column(String, nullable=True)
            created_at = Column(DateTime)
            updated_at = Column(DateTime)
            
        class Event(Base):
            __tablename__ = "events"
            
            id = Column(Integer, primary_key=True, index=True)
            title = Column(String, index=True)
            description = Column(Text, nullable=True)
            start_date = Column(DateTime)
            end_date = Column(DateTime)
            location = Column(String, nullable=True)
            organization_id = Column(Integer, ForeignKey("organizations.id"))
            created_at = Column(DateTime)
            updated_at = Column(DateTime)
            
        class Conversation(Base):
            __tablename__ = "conversations"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"))
            agent_type = Column(String)
            title = Column(String)
            created_at = Column(DateTime)
            updated_at = Column(DateTime)
            organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
            
        class Message(Base):
            __tablename__ = "messages"
            
            id = Column(Integer, primary_key=True, index=True)
            conversation_id = Column(Integer, ForeignKey("conversations.id"))
            content = Column(Text)
            role = Column(String)  # 'user' or 'assistant'
            created_at = Column(DateTime)
            
        class SubscriptionPlan(Base):
            __tablename__ = "subscription_plans"
            
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String, unique=True, index=True)
            description = Column(Text, nullable=True)
            price = Column(Float)
            features = Column(Text, nullable=True)
            tier = Column(String)
            
        class Subscription(Base):
            __tablename__ = "subscriptions"
            
            id = Column(Integer, primary_key=True, index=True)
            organization_id = Column(Integer, ForeignKey("organizations.id"))
            plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
            start_date = Column(DateTime)
            end_date = Column(DateTime, nullable=True)
            is_active = Column(Boolean, default=True)
            
        class UserOrganization(Base):
            __tablename__ = "user_organizations"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"))
            organization_id = Column(Integer, ForeignKey("organizations.id"))
            role = Column(String)  # 'admin', 'member', etc.
        
        # Create the tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verify tables were created
        print("Verifying tables were created...")
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        tables = metadata.tables
        print(f"Tables in database: {', '.join(tables.keys())}")
        
        if len(tables) > 0:
            print("✅ Database tables created successfully.")
            return True
        else:
            print("❌ No tables were created.")
            return False
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Tables Direct")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Create the tables
    if not create_tables_direct():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
