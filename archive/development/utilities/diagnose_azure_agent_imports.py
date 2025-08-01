#!/usr/bin/env python3
"""
Comprehensive diagnostic script to understand why agent imports are failing on Azure.
This script will check all possible import paths and provide detailed feedback.
"""

import os
import sys
import importlib
import traceback
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_environment():
    """Check the Python environment and paths."""
    print_section("ENVIRONMENT DIAGNOSTICS")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.abspath(__file__)}")
    
    print(f"\nPython path ({len(sys.path)} entries):")
    for i, path in enumerate(sys.path):
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {i+1:2d}. {exists} {path}")

def check_directory_structure():
    """Check if all required directories and files exist."""
    print_section("DIRECTORY STRUCTURE")
    
    required_dirs = [
        'app',
        'app/agents',
        'app/utils', 
        'app/db',
        'app/middleware',
        'app/services'
    ]
    
    required_files = [
        'app/__init__.py',
        'app/agents/__init__.py',
        'app/agents/api_router.py',
        'app/agents/agent_factory.py',
        'app/utils/__init__.py',
        'app/utils/conversation_memory.py',
        'app/db/__init__.py',
        'app/db/session.py',
        'app/middleware/__init__.py',
        'app/middleware/tenant.py'
    ]
    
    print("Required directories:")
    for dir_path in required_dirs:
        exists = "✅" if os.path.exists(dir_path) else "❌"
        print(f"  {exists} {dir_path}")
    
    print("\nRequired files:")
    for file_path in required_files:
        exists = "✅" if os.path.exists(file_path) else "❌"
        if exists == "✅":
            size = os.path.getsize(file_path)
            print(f"  {exists} {file_path} ({size} bytes)")
        else:
            print(f"  {exists} {file_path}")

def check_imports():
    """Test all possible import paths for agent modules."""
    print_section("IMPORT TESTING")
    
    import_tests = [
        # Direct imports with app prefix
        ('app.agents.api_router', 'get_agent_response'),
        ('app.agents.agent_factory', 'get_agent_factory'),
        ('app.db.session', 'get_db'),
        ('app.middleware.tenant', 'get_tenant_id'),
        ('app.utils.conversation_memory', 'ConversationMemory'),
        
        # Direct module imports (when in sys.path)
        ('api_router', 'get_agent_response'),
        ('agent_factory', 'get_agent_factory'),
        ('session', 'get_db'),
        ('tenant', 'get_tenant_id'),
        ('conversation_memory', 'ConversationMemory'),
        
        # Without app prefix
        ('agents.api_router', 'get_agent_response'),
        ('agents.agent_factory', 'get_agent_factory'),
        ('db.session', 'get_db'),
        ('middleware.tenant', 'get_tenant_id'),
        ('utils.conversation_memory', 'ConversationMemory'),
    ]
    
    successful_imports = []
    failed_imports = []
    
    for module_name, function_name in import_tests:
        try:
            print(f"\nTesting: {module_name} -> {function_name}")
            module = importlib.import_module(module_name)
            print(f"  ✅ Module imported successfully")
            print(f"  📍 Module file: {getattr(module, '__file__', 'Unknown')}")
            
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                print(f"  ✅ Function '{function_name}' found: {func}")
                successful_imports.append((module_name, function_name))
            else:
                print(f"  ❌ Function '{function_name}' not found")
                print(f"  📋 Available attributes: {[attr for attr in dir(module) if not attr.startswith('_')]}")
                failed_imports.append((module_name, function_name, "Function not found"))
                
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            failed_imports.append((module_name, function_name, f"ImportError: {e}"))
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            failed_imports.append((module_name, function_name, f"Error: {e}"))
    
    print(f"\n📊 IMPORT SUMMARY:")
    print(f"  ✅ Successful: {len(successful_imports)}")
    print(f"  ❌ Failed: {len(failed_imports)}")
    
    if successful_imports:
        print(f"\n✅ SUCCESSFUL IMPORTS:")
        for module, func in successful_imports:
            print(f"  - {module} -> {func}")
    
    if failed_imports:
        print(f"\n❌ FAILED IMPORTS:")
        for module, func, error in failed_imports:
            print(f"  - {module} -> {func}: {error}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print_section("DEPENDENCY CHECK")
    
    required_packages = [
        'fastapi',
        'sqlalchemy',
        'psycopg2',
        'google',
        'langchain',
        'langgraph'
    ]
    
    for package in required_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"  ✅ {package}: {version}")
        except ImportError:
            print(f"  ❌ {package}: Not installed")

def check_environment_variables():
    """Check relevant environment variables."""
    print_section("ENVIRONMENT VARIABLES")
    
    env_vars = [
        'USE_REAL_AGENTS',
        'LLM_PROVIDER',
        'GOOGLE_API_KEY',
        'DATABASE_URL',
        'PYTHONPATH',
        'PYTHONUNBUFFERED'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'PASSWORD' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")

def simulate_lazy_import():
    """Simulate the lazy import process from the adapter."""
    print_section("LAZY IMPORT SIMULATION")
    
    print("Simulating the lazy import process...")
    
    # Initialize variables
    get_agent_response = None
    get_conversation_history = None
    list_conversations = None
    delete_conversation = None
    get_agent_factory = None
    get_db = None
    get_tenant_id = None
    real_agents_available = False
    
    # Try import paths in order of preference
    import_paths = [
        {
            'router': 'app.agents.api_router',
            'factory': 'app.agents.agent_factory',
            'session': 'app.db.session',
            'tenant': 'app.middleware.tenant'
        },
        {
            'router': 'api_router',
            'factory': 'agent_factory',
            'session': 'session',
            'tenant': 'tenant'
        },
        {
            'router': 'agents.api_router',
            'factory': 'agents.agent_factory',
            'session': 'db.session',
            'tenant': 'middleware.tenant'
        }
    ]
    
    for i, path in enumerate(import_paths, 1):
        print(f"\nAttempt {i}: {path['router']}")
        try:
            router_module = importlib.import_module(path['router'])
            factory_module = importlib.import_module(path['factory'])
            session_module = importlib.import_module(path['session'])
            tenant_module = importlib.import_module(path['tenant'])
            
            # Get the functions from the modules
            get_agent_response = getattr(router_module, 'get_agent_response', None)
            get_conversation_history = getattr(router_module, 'get_conversation_history', None)
            list_conversations = getattr(router_module, 'list_conversations', None)
            delete_conversation = getattr(router_module, 'delete_conversation', None)
            get_agent_factory = getattr(factory_module, 'get_agent_factory', None)
            get_db = getattr(session_module, 'get_db', None)
            get_tenant_id = getattr(tenant_module, 'get_tenant_id', None)
            
            # Check if we got all required functions
            if all([get_agent_response, get_agent_factory, get_db]):
                real_agents_available = True
                print(f"  ✅ SUCCESS! All required functions found")
                print(f"  📋 Functions: get_agent_response={get_agent_response is not None}, "
                      f"get_agent_factory={get_agent_factory is not None}, "
                      f"get_db={get_db is not None}")
                break
            else:
                print(f"  ⚠️ Missing functions:")
                print(f"    - get_agent_response: {get_agent_response is not None}")
                print(f"    - get_agent_factory: {get_agent_factory is not None}")
                print(f"    - get_db: {get_db is not None}")
                continue
                
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            continue
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            traceback.print_exc()
            continue
    
    print(f"\n🎯 FINAL RESULT: {'REAL AGENTS AVAILABLE' if real_agents_available else 'MOCK RESPONSES ONLY'}")
    
    return real_agents_available

def main():
    """Run all diagnostics."""
    print(f"🔍 Azure Agent Import Diagnostics")
    print(f"⏰ Started at: {datetime.now()}")
    
    try:
        check_environment()
        check_directory_structure()
        check_dependencies()
        check_environment_variables()
        check_imports()
        real_agents_available = simulate_lazy_import()
        
        print_section("SUMMARY")
        if real_agents_available:
            print("🎉 SUCCESS: Real agents should be available!")
            print("   The lazy import process should work correctly.")
        else:
            print("⚠️  ISSUE: Real agents are not available")
            print("   The system will fall back to mock responses.")
            print("   Check the failed imports above for specific issues.")
        
    except Exception as e:
        print(f"\n❌ Diagnostic script failed: {e}")
        traceback.print_exc()
    
    print(f"\n⏰ Completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
