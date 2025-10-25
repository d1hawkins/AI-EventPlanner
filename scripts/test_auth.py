#!/usr/bin/env python3
"""Test user registration and login functionality with PostgreSQL."""

import sys
import os
import requests
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8002"

def test_registration():
    """Test user registration."""
    print("\n=== Testing User Registration ===")
    
    # Registration data
    register_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "is_active": True
    }
    
    print(f"Registering user: {register_data['username']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Registration successful!")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False


def test_login():
    """Test user login."""
    print("\n=== Testing User Login ===")
    
    # Login data (OAuth2 form format)
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    
    print(f"Logging in as: {login_data['username']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data=login_data,  # Use data instead of json for form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful!")
            print(f"   Access token: {token_data.get('access_token')[:50]}...")
            print(f"   Token type: {token_data.get('token_type')}")
            return token_data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_authenticated_request(token):
    """Test an authenticated request."""
    print("\n=== Testing Authenticated Request ===")
    
    if not token:
        print("❌ No token available for authenticated request")
        return False
    
    print("Fetching current user info...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authenticated request successful!")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Active: {user_data.get('is_active')}")
            return True
        else:
            print(f"❌ Authenticated request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authenticated request error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PostgreSQL Authentication Tests")
    print("=" * 60)
    
    # Test registration
    registration_success = test_registration()
    
    # Test login
    if registration_success:
        token = test_login()
        
        # Test authenticated request
        if token:
            auth_success = test_authenticated_request(token)
        else:
            auth_success = False
    else:
        print("\n⚠️  Skipping login test due to registration failure")
        token = None
        auth_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Registration: {'✅ PASSED' if registration_success else '❌ FAILED'}")
    print(f"Login:        {'✅ PASSED' if token else '❌ FAILED'}")
    print(f"Auth Request: {'✅ PASSED' if auth_success else '❌ FAILED'}")
    print("=" * 60)
    
    # Overall result
    if registration_success and token and auth_success:
        print("\n🎉 All tests passed! PostgreSQL authentication is working correctly!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
