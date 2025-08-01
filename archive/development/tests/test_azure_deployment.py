#!/usr/bin/env python3
"""
Test script for Azure deployment of the app_adapter.py file.
This script simulates the Azure environment and tests the import paths.
"""

import os
import sys
import importlib
import traceback

def setup_test_environment():
    """Set up a test environment that simulates Azure's environment."""
    print("Setting up test environment...")
    
    # Create a mock wwwroot directory structure
    wwwroot_dir = os.path.join(os.getcwd(), 'mock_wwwroot')
    os.makedirs(wwwroot_dir, exist_ok=True)
    
    # Create app directory in wwwroot
    app_dir = os.path.join(wwwroot_dir, 'app')
    os.makedirs(app_dir, exist_ok=True)
    
    # Create agents directory in app
    agents_dir = os.path.join(app_dir, 'agents')
    os.makedirs(agents_dir, exist_ok=True)
    
    # Create db directory in app
    db_dir = os.path.join(app_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    
    # Create middleware directory in app
    middleware_dir = os.path.join(app_dir, 'middleware')
    os.makedirs(middleware_dir, exist_ok=True)
    
    # Copy app_adapter.py to wwwroot
    with open('app_adapter.py', 'r') as src_file:
        app_adapter_content = src_file.read()
        
    with open(os.path.join(wwwroot_dir, 'app_adapter.py'), 'w') as dest_file:
        dest_file.write(app_adapter_content)
    
    # Add wwwroot to Python path
    sys.path.insert(0, wwwroot_dir)
    
    return wwwroot_dir

def test_dependencies():
    """Test if required dependencies are installed and working correctly."""
    print("\nTesting required dependencies installation...")
    
    # Test passlib
    print("\n1. Testing passlib...")
    try:
        import passlib
        from passlib.context import CryptContext
        
        # Create a password context
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Test password hashing
        hashed_password = pwd_context.hash("testpassword")
        
        print("SUCCESS: passlib is installed and working correctly!")
        print(f"passlib version: {passlib.__version__}")
        print(f"Test hash: {hashed_password}")
        print("Verification: ", pwd_context.verify("testpassword", hashed_password))
        
        passlib_success = True
        
    except ImportError as e:
        print(f"ERROR: {e}")
        print("The passlib module is not installed or not working correctly.")
        passlib_success = False
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        passlib_success = False
    
    # Test python-dotenv
    print("\n2. Testing python-dotenv...")
    try:
        import dotenv
        
        # Create a test .env file
        with open("test.env", "w") as f:
            f.write("TEST_VAR=test_value\n")
        
        # Load the test .env file
        dotenv.load_dotenv("test.env")
        
        # Check if the variable was loaded
        import os
        test_var = os.getenv("TEST_VAR")
        
        # Clean up
        os.remove("test.env")
        
        if test_var == "test_value":
            print("SUCCESS: python-dotenv is installed and working correctly!")
            print(f"dotenv version: {dotenv.__version__}")
            print(f"Test variable: {test_var}")
            dotenv_success = True
        else:
            print(f"ERROR: python-dotenv did not load the test variable correctly. Got: {test_var}")
            dotenv_success = False
        
    except ImportError as e:
        print(f"ERROR: {e}")
        print("The python-dotenv module is not installed or not working correctly.")
        dotenv_success = False
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        dotenv_success = False
    
    # Return overall success
    return passlib_success and dotenv_success

def test_imports(wwwroot_dir):
    """Test the import paths in the app_adapter.py file."""
    print("\nTesting imports...")
    
    # Save original directory
    original_dir = os.getcwd()
    
    try:
        # Change to wwwroot directory to simulate Azure environment
        os.chdir(wwwroot_dir)
        
        # Try to import app_adapter
        print("Importing app_adapter...")
        app_adapter = importlib.import_module('app_adapter')
        
        # Check if REAL_AGENTS_AVAILABLE is defined
        print(f"REAL_AGENTS_AVAILABLE: {getattr(app_adapter, 'REAL_AGENTS_AVAILABLE', 'Not defined')}")
        
        # Check if app function is defined
        if hasattr(app_adapter, 'app'):
            print("app function is defined")
        else:
            print("app function is NOT defined")
        
        # Test the health endpoint
        print("\nTesting health endpoint...")
        
        # Create a mock WSGI environment
        environ = {'PATH_INFO': '/health'}
        
        # Create a mock start_response function
        response_status = None
        response_headers = None
        
        def start_response(status, headers):
            nonlocal response_status, response_headers
            response_status = status
            response_headers = headers
        
        # Call the app function
        response = app_adapter.app(environ, start_response)
        
        # Print the response
        print(f"Status: {response_status}")
        print(f"Headers: {response_headers}")
        print(f"Response: {response[0].decode('utf-8')}")
        
        print("\nImport test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during import test: {str(e)}")
        traceback.print_exc()
        return False
    
    finally:
        # Restore original directory
        os.chdir(original_dir)

def cleanup(wwwroot_dir):
    """Clean up the test environment."""
    print("\nCleaning up test environment...")
    
    # Remove wwwroot directory
    import shutil
    shutil.rmtree(wwwroot_dir)
    
    print("Cleanup completed!")

def main():
    """Main function."""
    print("Starting Azure deployment test...")
    
    # Test dependencies installation
    print("\n=== Testing Required Dependencies ===")
    dependencies_success = test_dependencies()
    
    if dependencies_success:
        print("\nAll dependency tests PASSED!")
    else:
        print("\nSome dependency tests FAILED!")
        print("Please make sure all required dependencies are installed correctly.")
        print("Check the AZURE_DEPLOYMENT_PASSLIB_FIX.md file for instructions.")
        sys.exit(1)
    
    # Set up test environment
    wwwroot_dir = setup_test_environment()
    
    # Test imports
    success = test_imports(wwwroot_dir)
    
    # Clean up
    cleanup(wwwroot_dir)
    
    # Print result
    if success:
        print("\nAzure deployment test PASSED!")
    else:
        print("\nAzure deployment test FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
