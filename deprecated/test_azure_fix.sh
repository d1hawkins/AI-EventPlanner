#!/bin/bash
# Script to test the TypedDict compatibility fix locally
# This script verifies that the fix works before deploying to Azure

set -e  # Exit immediately if a command exits with a non-zero status

echo "=== Testing TypedDict Compatibility Fix ==="
echo ""

# Check if the simple_coordinator_graph.py file exists
if [ ! -f "app/graphs/simple_coordinator_graph.py" ]; then
    echo "ERROR: simple_coordinator_graph.py not found!"
    echo "Please create this file before testing."
    exit 1
fi

# Run the verification script
echo "Verifying TypedDict fix..."
python3 verify_typeddict_fix.py
if [ $? -ne 0 ]; then
    echo "Verification failed! Please fix the issues before testing."
    exit 1
fi

# Create a test directory
TEST_DIR="./test_azure_fix"
echo "Creating test directory: $TEST_DIR"
mkdir -p $TEST_DIR

# Copy necessary files to test directory
echo "Copying files to test directory..."
cp -r app $TEST_DIR/
cp app_adapter.py $TEST_DIR/
cp startup.py $TEST_DIR/
cp startup.sh $TEST_DIR/
cp requirements.txt $TEST_DIR/
cp wsgi.py $TEST_DIR/

# Create a simple test script
echo "Creating test script..."
cat > $TEST_DIR/test_import.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify that the TypedDict compatibility fix works.
This script attempts to import the simple_coordinator_graph module
and use its functions to create a coordinator graph.
"""

import os
import sys
import importlib.util
import traceback

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_simple_coordinator_graph():
    """Test importing the simple_coordinator_graph module."""
    try:
        from app.graphs.simple_coordinator_graph import create_coordinator_graph, create_initial_state
        print("✓ Successfully imported simple_coordinator_graph")
        return True
    except ImportError as e:
        print(f"ERROR: Failed to import simple_coordinator_graph: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error importing simple_coordinator_graph: {str(e)}")
        traceback.print_exc()
        return False

def test_create_coordinator_graph():
    """Test creating a coordinator graph."""
    try:
        from app.graphs.simple_coordinator_graph import create_coordinator_graph, create_initial_state
        
        # Create a coordinator graph
        graph = create_coordinator_graph()
        print("✓ Successfully created coordinator graph")
        
        # Create initial state
        state = create_initial_state()
        print("✓ Successfully created initial state")
        
        # Check if the graph has the expected attributes
        if hasattr(graph, 'compile'):
            print("✓ Graph has compile method")
        else:
            print("ERROR: Graph does not have compile method")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to create coordinator graph: {str(e)}")
        traceback.print_exc()
        return False

def test_app_adapter():
    """Test importing app_adapter."""
    try:
        import app_adapter
        print("✓ Successfully imported app_adapter")
        
        # Check if app_adapter has the app function
        if hasattr(app_adapter, 'app'):
            print("✓ app_adapter has app function")
        else:
            print("ERROR: app_adapter does not have app function")
            return False
        
        return True
    except ImportError as e:
        print(f"ERROR: Failed to import app_adapter: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error importing app_adapter: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main function to run all tests."""
    print("=== Testing TypedDict Compatibility Fix ===")
    print("")
    
    # Test importing simple_coordinator_graph
    if not test_import_simple_coordinator_graph():
        return False
    
    # Test creating a coordinator graph
    if not test_create_coordinator_graph():
        return False
    
    # Test importing app_adapter
    if not test_app_adapter():
        return False
    
    print("")
    print("All tests passed! The TypedDict compatibility fix is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

# Make the test script executable
chmod +x $TEST_DIR/test_import.py

# Run the test script
echo "Running test script..."
cd $TEST_DIR
python3 test_import.py
TEST_RESULT=$?

# Clean up
echo "Cleaning up..."
cd ..
rm -rf $TEST_DIR

# Check the test result
if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "All tests passed! The TypedDict compatibility fix is working correctly."
    echo "You can now deploy the fix to Azure using: ./azure-deploy-fixed.sh"
    echo ""
    echo "For more information about the fix, see AZURE_TYPEDDICT_FIX.md"
    exit 0
else
    echo ""
    echo "Tests failed! Please fix the issues before deploying to Azure."
    exit 1
fi
