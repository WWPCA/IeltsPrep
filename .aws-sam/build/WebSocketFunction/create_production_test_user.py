"""
Create Production Test User for Website Login Testing
"""

import urllib.request
import json
import hashlib
import os
from datetime import datetime

def create_test_user():
    """Create test user in production database"""
    
    # Test user data
    test_user_data = {
        "email": "test@ieltsaiprep.com",
        "password": "TestPass123!",
        "user_type": "test_user",
        "created_at": datetime.now().isoformat(),
        "assessment_attempts": {
            "academic_writing": {"remaining": 4, "used": 0},
            "general_writing": {"remaining": 4, "used": 0},
            "academic_speaking": {"remaining": 4, "used": 0},
            "general_speaking": {"remaining": 4, "used": 0}
        },
        "purchases": [
            {
                "product_id": "academic_writing",
                "price": 36.00,
                "currency": "CAD",
                "purchase_date": datetime.now().isoformat(),
                "platform": "test_environment"
            },
            {
                "product_id": "general_writing", 
                "price": 36.00,
                "currency": "CAD",
                "purchase_date": datetime.now().isoformat(),
                "platform": "test_environment"
            },
            {
                "product_id": "academic_speaking",
                "price": 36.00,
                "currency": "CAD", 
                "purchase_date": datetime.now().isoformat(),
                "platform": "test_environment"
            },
            {
                "product_id": "general_speaking",
                "price": 36.00,
                "currency": "CAD",
                "purchase_date": datetime.now().isoformat(),
                "platform": "test_environment"
            }
        ]
    }
    
    print("Creating production test user...")
    print(f"Email: {test_user_data['email']}")
    print(f"Password: {test_user_data['password']}")
    
    try:
        # Try to register the user
        url = "https://www.ieltsaiprep.com/api/register"
        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        registration_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "confirm_password": test_user_data["password"],
            "user_type": "test_user"
        }
        
        data = json.dumps(registration_data).encode('utf-8')
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                print("✅ Test user created successfully!")
                return True
            else:
                print(f"⚠️ Registration response: {result}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code}")
        if e.code == 409:
            print("User may already exist - testing login...")
            return test_login()
        return False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def test_login():
    """Test login with credentials"""
    
    print("\nTesting login credentials...")
    
    try:
        url = "https://www.ieltsaiprep.com/api/login"
        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        login_data = {
            "email": "test@ieltsaiprep.com",
            "password": "TestPass123!"
        }
        
        data = json.dumps(login_data).encode('utf-8')
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                print("✅ Login successful!")
                print(f"Session ID: {result.get('session_id', 'Not provided')}")
                return True
            else:
                print(f"❌ Login failed: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def check_database_health():
    """Check production database health"""
    
    print("Checking production database health...")
    
    try:
        url = "https://www.ieltsaiprep.com/api/health"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"Database status: {result.get('database_status', 'Unknown')}")
            print(f"Database users: {result.get('database_users', 'Not reported')}")
            
            return result.get('database_status') == 'connected'
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main function to create test user and verify login"""
    
    print("🔧 Production Test User Setup")
    print("=" * 50)
    
    # Check database health first
    if not check_database_health():
        print("❌ Database health check failed")
        return False
    
    # Try to create test user
    user_created = create_test_user()
    
    if user_created:
        print("\n✅ Test user setup complete!")
        print("You can now login to the production website with:")
        print("Email: test@ieltsaiprep.com")
        print("Password: TestPass123!")
        print("\nWebsite: https://www.ieltsaiprep.com/login")
        return True
    else:
        # Try login anyway in case user already exists
        if test_login():
            print("\n✅ Test user already exists and login works!")
            print("You can login to the production website with:")
            print("Email: test@ieltsaiprep.com") 
            print("Password: TestPass123!")
            print("\nWebsite: https://www.ieltsaiprep.com/login")
            return True
        else:
            print("\n❌ Test user setup failed")
            return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Ready for Nova AI Testing!")
        print("1. Login to https://www.ieltsaiprep.com/login")
        print("2. Go to Dashboard")
        print("3. Click 'Start Assessment' on any assessment type")
        print("4. Test Nova AI functionality")
    else:
        print("\n⚠️ Test user setup incomplete")
        print("You may need to create the user manually")