#!/usr/bin/env python3
"""
Database Configuration Verification Script

This script verifies that the database configuration is correct and
prevents SQLite usage in production environments.

Usage:
    python scripts/verify_database_config.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment_variable(var_name: str, required: bool = False) -> tuple[bool, str]:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    
    if value:
        # Mask sensitive values
        if any(sensitive in var_name.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
            display_value = f"***SET*** (length: {len(value)})"
        else:
            display_value = value[:50] + "..." if len(value) > 50 else value
        return True, display_value
    else:
        return False, "NOT SET"

def verify_database_config():
    """Verify database configuration."""
    print("=" * 70)
    print("DATABASE CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    issues = []
    warnings = []
    
    # Check ENVIRONMENT variable
    print("1. Checking ENVIRONMENT variable...")
    env_set, env_value = check_environment_variable("ENVIRONMENT")
    env = env_value.lower() if env_set else ""
    
    print(f"   ENVIRONMENT: {env_value}")
    
    is_production = env in ["production", "prod", "azure", ""] or not env_set
    
    if is_production:
        print("   ⚠️  Environment detected as PRODUCTION")
    else:
        print(f"   ℹ️  Environment detected as DEVELOPMENT ({env})")
    print()
    
    # Check DATABASE_URL
    print("2. Checking DATABASE_URL...")
    db_url_set, db_url_value = check_environment_variable("DATABASE_URL", required=True)
    
    if not db_url_set:
        issues.append("DATABASE_URL is not set")
        print("   ❌ DATABASE_URL: NOT SET")
        if is_production:
            issues.append("DATABASE_URL is REQUIRED in production environment")
    else:
        print(f"   ✅ DATABASE_URL: {db_url_value}")
        
        # Check database type
        actual_db_url = os.getenv("DATABASE_URL", "")
        if actual_db_url.startswith("sqlite"):
            if is_production:
                issues.append("SQLite database detected in production environment")
                print("   ❌ Database Type: SQLite (NOT ALLOWED IN PRODUCTION)")
            else:
                warnings.append("Using SQLite in development environment")
                print("   ⚠️  Database Type: SQLite (OK for development)")
        elif actual_db_url.startswith("postgresql"):
            print("   ✅ Database Type: PostgreSQL")
        else:
            warnings.append(f"Unknown database type: {actual_db_url.split(':')[0]}")
            print(f"   ⚠️  Database Type: {actual_db_url.split(':')[0]}")
    print()
    
    # Check other required variables
    print("3. Checking other required environment variables...")
    
    required_vars = [
        ("SECRET_KEY", True),
        ("OPENAI_API_KEY", False),
        ("GOOGLE_API_KEY", False),
        ("TAVILY_API_KEY", False),
    ]
    
    for var_name, required in required_vars:
        var_set, var_value = check_environment_variable(var_name, required)
        status = "✅" if var_set else ("❌" if required else "⚠️")
        print(f"   {status} {var_name}: {var_value}")
        
        if required and not var_set:
            issues.append(f"{var_name} is not set")
    print()
    
    # Try to import and validate config
    print("4. Testing application configuration import...")
    try:
        from app.config import DATABASE_URL as config_db_url, validate_config
        print("   ✅ Configuration module imported successfully")
        
        if config_db_url:
            if config_db_url.startswith("sqlite") and is_production:
                issues.append("Config module is using SQLite in production")
                print(f"   ❌ Config DATABASE_URL uses SQLite in production")
            elif config_db_url.startswith("postgresql"):
                print(f"   ✅ Config DATABASE_URL uses PostgreSQL")
            else:
                print(f"   ℹ️  Config DATABASE_URL: {config_db_url[:30]}...")
        else:
            issues.append("Config DATABASE_URL is None/empty")
            print("   ❌ Config DATABASE_URL is None/empty")
        
        # Run config validation
        print("\n5. Running configuration validation...")
        if validate_config():
            print("   ✅ Configuration validation passed")
        else:
            warnings.append("Configuration validation reported warnings")
            print("   ⚠️  Configuration validation completed with warnings")
            
    except Exception as e:
        issues.append(f"Failed to import configuration: {str(e)}")
        print(f"   ❌ Failed to import configuration: {str(e)}")
    print()
    
    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    
    if not issues and not warnings:
        print("✅ All checks passed! Database configuration is correct.")
        return 0
    
    if warnings:
        print(f"⚠️  {len(warnings)} warning(s) found:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
    
    if issues:
        print(f"❌ {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        
        if is_production:
            print("CRITICAL: Issues found in production environment!")
            print("The application will not start with these issues.")
            return 1
        else:
            print("Issues found in development environment.")
            print("These may cause problems when deploying to production.")
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = verify_database_config()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
