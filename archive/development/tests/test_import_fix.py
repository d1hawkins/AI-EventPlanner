#!/usr/bin/env python3
"""
Test script to verify that the import issues have been fixed.
"""

import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test all the problematic imports."""
    
    print("Testing imports...")
    
    try:
        print("1. Testing app.utils.llm_factory import...")
        from app.utils.llm_factory import get_llm
        print("   ✅ app.utils.llm_factory imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import app.utils.llm_factory: {e}")
        return False
    
    try:
        print("2. Testing app.agents.agent_factory import...")
        from app.agents.agent_factory import get_agent_factory
        print("   ✅ app.agents.agent_factory imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import app.agents.agent_factory: {e}")
        return False
    
    try:
        print("3. Testing app.agents.api_router import...")
        from app.agents.api_router import get_agent_response
        print("   ✅ app.agents.api_router imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import app.agents.api_router: {e}")
        return False
    
    try:
        print("4. Testing config import...")
        from app import config
        print("   ✅ app.config imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import app.config: {e}")
        return False
    
    print("\n🎉 All imports successful! The import issues have been fixed.")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
