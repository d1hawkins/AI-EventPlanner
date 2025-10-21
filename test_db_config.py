#!/usr/bin/env python3
"""
Test script to verify database configuration and dependencies.
This script tests the database URL construction and module imports.
"""

import os
import sys
import importlib.util

def test_stripe_import():
    """Test if stripe module can be imported."""
    try:
        import stripe
        print("✅ Stripe module imported successfully")
        try:
            # Try to get version from different possible locations
            version = getattr(stripe, '__version__', 'unknown')
            if version == 'unknown':
                version = getattr(stripe, 'version', 'unknown')
            print(f"   Stripe version: {version}")
        except:
            print("   Stripe version: unknown")
        return True
    except ImportError as e:
        print(f"❌ Failed to import stripe: {e}")
        return False

def test_database_config():
    """Test database configuration."""
    print("\n=== Database Configuration Test ===")
    
    # Test different environment variable scenarios
    test_cases = [
        {
            "name": "No database env vars (should fallback to SQLite in development)",
            "env_vars": {"ENVIRONMENT": "development"}
        },
        {
            "name": "DATABASE_URL set",
            "env_vars": {"DATABASE_URL": "postgresql://user:pass@host:5432/db"}
        },
        {
            "name": "APPSETTING_DATABASE_URL set (Azure format)",
            "env_vars": {"APPSETTING_DATABASE_URL": "postgresql://azureuser:azurepass@azure-host:5432/azuredb"}
        },
        {
            "name": "Individual PostgreSQL components",
            "env_vars": {
                "POSTGRES_HOST": "testhost",
                "POSTGRES_USER": "testuser", 
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_DB": "testdb",
                "POSTGRES_PORT": "5432"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        # Clear existing database-related env vars
        for key in list(os.environ.keys()):
            if any(keyword in key.upper() for keyword in ['DATABASE', 'DB', 'POSTGRES', 'SQL']):
                del os.environ[key]
        
        # Set test environment variables
        for key, value in test_case['env_vars'].items():
            os.environ[key] = value
        
        try:
            # Import config module to test database URL construction
            if 'app.config' in sys.modules:
                del sys.modules['app.config']
            
            # Reload the module to pick up new environment variables
            spec = importlib.util.spec_from_file_location("app.config", "app/config.py")
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            database_url = config_module.DATABASE_URL
            print(f"   Result: {database_url}")
            
            if database_url:
                if database_url.startswith("postgresql"):
                    print("   ✅ PostgreSQL URL detected")
                elif database_url.startswith("sqlite"):
                    print("   ⚠️ SQLite URL detected")
                else:
                    print("   ❓ Unknown database type")
            else:
                print("   ❌ No DATABASE_URL generated")
                
        except Exception as e:
            print(f"   ❌ Error testing configuration: {e}")

def test_azure_env_vars():
    """Test Azure-specific environment variable detection."""
    print("\n=== Azure Environment Variables ===")
    azure_related_vars = []
    
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['AZURE', 'APPSETTING', 'DATABASE', 'DB', 'POSTGRES', 'SQL']):
            # Mask sensitive values
            display_value = value[:20] + "..." if len(value) > 20 and any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY']) else value
            azure_related_vars.append(f"  {key}={display_value}")
    
    if azure_related_vars:
        print("Found Azure/Database related environment variables:")
        for var in azure_related_vars:
            print(var)
    else:
        print("No Azure/Database related environment variables found")

def main():
    """Run all tests."""
    print("=== Database Configuration and Dependencies Test ===")
    
    # Test stripe import
    stripe_ok = test_stripe_import()
    
    # Test database configuration
    test_database_config()
    
    # Test Azure environment variables
    test_azure_env_vars()
    
    print("\n=== Test Summary ===")
    print(f"Stripe module: {'✅ OK' if stripe_ok else '❌ FAILED'}")
    print("\nIf running in Azure, make sure the following environment variables are set:")
    print("- DATABASE_URL or APPSETTING_DATABASE_URL with full PostgreSQL connection string")
    print("- Or individual components: POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, etc.")

if __name__ == "__main__":
    main()
