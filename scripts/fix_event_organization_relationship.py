#!/usr/bin/env python
"""
Fix Event-Organization Relationship Script

This script fixes the relationship between Event and Organization models.
"""

import os
import sys
import argparse
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

def fix_relationship():
    """Fix the relationship between Event and Organization models."""
    print("Fixing Event-Organization relationship...")
    
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)
    
    try:
        # Import the Event model
        from app.db.models import Event
        
        # Add organization_id column to Event model
        print("Adding organization_id column to Event model...")
        Event.organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
        
        # Add organization relationship to Event model
        print("Adding organization relationship to Event model...")
        Event.organization = relationship("Organization", back_populates="events")
        
        print("✅ Event-Organization relationship fixed successfully.")
        return True
    except ImportError as e:
        print(f"Error importing models: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        print(f"Error fixing relationship: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fix Event-Organization Relationship Script")
    
    # Fix the relationship
    if not fix_relationship():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
