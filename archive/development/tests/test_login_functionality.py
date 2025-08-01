#!/usr/bin/env python3
"""
Script to test login functionality for the SaaS application.
"""

import requests
import json
import sys

def test_login_endpoint(base_url="http://localhost:8002"):
    """Test the login endpoint with various scenarios."""
    
    print("Testing SaaS Login Functionality")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid username login",
            "username": "testuser",
            "password": "testpass123",
            "should_succeed": True
        },
        {
            "name": "Valid email login", 
            "username": "test@example.com",
            "password": "testpass123",
            "should_succeed": True
        },
        {
            "name": "Invalid password",
            "username": "testuser",
            "password": "wrongpassword",
            "should_succeed": False
        },
        {
            "name": "Non-existent user",
            "username": "nonexistent",
            "password": "password123",
            "should_succeed": False
        },
        {
            "name": "Empty credentials",
            "username": "",
            "password": "",
            "should_succeed": False
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        try:
            # Prepare form data
            form_data = {
                "username": test_case["username"],
                "password": test_case["password"]
            }
            
            # Make request to login endpoint
            response = requests.post(
                f"{base_url}/auth/token",
                data=form_data,
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success and test_case["should_succeed"]:
                print("✅ PASS - Login successful as expected")
                token_data = response.json()
                print(f"   Token type: {token_data.get('token_type')}")
                print(f"   Token received: {'Yes' if token_data.get('access_token') else 'No'}")
                results.append({"test": test_case["name"], "result": "PASS"})
                
            elif not success and not test_case["should_succeed"]:
                print("✅ PASS - Login failed as expected")
                print(f"   Status code: {response.status_code}")
                results.append({"test": test_case["name"], "result": "PASS"})
                
            elif success and not test_case["should_succeed"]:
                print("❌ FAIL - Login succeeded when it should have failed")
                results.append({"test": test_case["name"], "result": "FAIL"})
                
            else:
                print("❌ FAIL - Login failed when it should have succeeded")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({"test": test_case["name"], "result": "FAIL"})
                
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR - Request failed: {e}")
            results.append({"test": test_case["name"], "result": "ERROR"})
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for r in results if r["result"] == "PASS")
    failed = sum(1 for r in results if r["result"] == "FAIL") 
    errors = sum(1 for r in results if r["result"] == "ERROR")
    
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    
    if failed > 0 or errors > 0:
        print("\n❌ Some tests failed. Please check the login implementation.")
        return False
    else:
        print("\n✅ All tests passed! Login functionality is working correctly.")
        return True

if __name__ == "__main__":
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    success = test_login_endpoint(base_url)
    sys.exit(0 if success else 1)
