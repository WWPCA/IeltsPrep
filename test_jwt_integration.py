#!/usr/bin/env python3
"""
Test script to verify JWT authentication integration
Tests both mobile API endpoints and web session compatibility
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v1"

def test_api_health():
    """Test API health endpoint"""
    print("Testing API health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_mobile_register():
    """Test mobile registration endpoint"""
    print("\nTesting mobile registration...")
    test_user = {
        "username": "testuser_jwt",
        "email": "test@ieltsgenaiprep.com",
        "password": "testpass123",
        "full_name": "JWT Test User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            return response.json().get('data', {}).get('token')
        return None
    except Exception as e:
        print(f"Registration failed: {e}")
        return None

def test_mobile_login():
    """Test mobile login endpoint"""
    print("\nTesting mobile login...")
    login_data = {
        "email": "test@ieltsgenaiprep.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json().get('data', {}).get('token')
        return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint with JWT token"""
    print(f"\nTesting protected endpoint with JWT token...")
    
    if not token:
        print("No token provided!")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/user/profile", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Protected endpoint test failed: {e}")
        return False

def test_web_homepage():
    """Test that web interface still works"""
    print(f"\nTesting web homepage...")
    try:
        response = requests.get(BASE_URL)
        print(f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Web homepage test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== JWT Authentication Integration Test ===\n")
    
    # Test 1: API Health
    health_ok = test_api_health()
    
    # Test 2: Mobile Registration
    token = test_mobile_register()
    
    # Test 3: Mobile Login (fallback if registration failed)
    if not token:
        token = test_mobile_login()
    
    # Test 4: Protected Endpoint
    profile_ok = test_protected_endpoint(token) if token else False
    
    # Test 5: Web Interface Compatibility
    web_ok = test_web_homepage()
    
    # Summary
    print("\n=== Test Results ===")
    print(f"API Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Mobile Auth: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Protected Endpoint: {'✅ PASS' if profile_ok else '❌ FAIL'}")
    print(f"Web Interface: {'✅ PASS' if web_ok else '❌ FAIL'}")
    
    all_passed = all([health_ok, token is not None, profile_ok, web_ok])
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    main()