#!/usr/bin/env python3
"""
Script to verify the TypedDict compatibility fix for Azure deployment.

This script tests the creation of coordinator graphs to ensure they work
properly with the dict-based state schema instead of TypedDict.
"""

import sys
import traceback

def test_simple_coordinator_graph():
    """Test the simple coordinator graph creation."""
    try:
        from app.graphs.simple_coordinator_graph import create_coordinator_graph, create_initial_state
        graph = create_coordinator_graph()
        state = create_initial_state()
        print("✅ Simple coordinator graph created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating simple coordinator graph: {str(e)}")
        traceback.print_exc()
        return False

def test_coordinator_graph():
    """Test the main coordinator graph creation."""
    try:
        from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
        graph = create_coordinator_graph()
        state = create_initial_state()
        print("✅ Main coordinator graph created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating main coordinator graph: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run the verification tests."""
    print("Verifying TypedDict compatibility fix...")
    
    simple_success = test_simple_coordinator_graph()
    main_success = test_coordinator_graph()
    
    if simple_success and main_success:
        print("\n✅ All tests passed! The TypedDict compatibility fix is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. The TypedDict compatibility fix may not be working correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
