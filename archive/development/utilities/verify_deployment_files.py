#!/usr/bin/env python3
"""
Script to verify that all required files are present for Azure deployment.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING {description}: {filepath}")
        return False

def main():
    """Check all required files for Azure deployment."""
    print("Azure Deployment File Verification")
    print("=" * 50)
    
    required_files = [
        ("startup.py", "Main startup script"),
        ("startup_app.py", "Alternative startup script"),
        ("web.config", "IIS configuration"),
        ("Procfile", "Process file"),
        ("requirements.txt", "Python dependencies"),
        ("create_tables.py", "Database table creation"),
        ("create_subscription_plans.py", "Subscription plans setup"),
        ("app/main_saas.py", "Main SaaS application"),
        ("app/config.py", "Application configuration"),
        ("app/db/base.py", "Database base"),
        ("app/db/models.py", "Database models"),
        ("app/db/models_updated.py", "Updated database models"),
    ]
    
    missing_files = []
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            missing_files.append(filepath)
    
    print("\n" + "=" * 50)
    
    if missing_files:
        print(f"❌ {len(missing_files)} files are missing:")
        for filepath in missing_files:
            print(f"   - {filepath}")
        print("\nDeployment may fail due to missing files.")
        return 1
    else:
        print("✅ All required files are present!")
        
    # Check file contents
    print("\nFile Content Verification:")
    print("-" * 30)
    
    # Check startup.py has main function
    try:
        with open("startup.py", "r") as f:
            content = f.read()
            if "def main():" in content:
                print("✓ startup.py contains main() function")
            else:
                print("✗ startup.py missing main() function")
    except Exception as e:
        print(f"✗ Error reading startup.py: {e}")
    
    # Check web.config points to startup.py
    try:
        with open("web.config", "r") as f:
            content = f.read()
            if "startup.py" in content:
                print("✓ web.config points to startup.py")
            else:
                print("✗ web.config does not point to startup.py")
    except Exception as e:
        print(f"✗ Error reading web.config: {e}")
    
    # Check Procfile points to startup.py
    try:
        with open("Procfile", "r") as f:
            content = f.read()
            if "startup.py" in content:
                print("✓ Procfile points to startup.py")
            else:
                print("✗ Procfile does not point to startup.py")
    except Exception as e:
        print(f"✗ Error reading Procfile: {e}")
    
    print("\n" + "=" * 50)
    print("Verification complete!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
