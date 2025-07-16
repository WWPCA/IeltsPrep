#!/usr/bin/env python3
"""
Check Production User Database and Create Working Credentials
"""

import boto3
import json
import hashlib
import base64
from datetime import datetime

def check_production_users():
    """Check what users exist in production DynamoDB"""
    try:
        # Connect to production DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Check users table
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        print("🔍 Scanning production users table...")
        response = users_table.scan()
        
        users = response.get('Items', [])
        print(f"📊 Found {len(users)} users in production database")
        
        for user in users:
            email = user.get('email', 'Unknown')
            created_at = user.get('created_at', 'Unknown')
            print(f"  - {email} (created: {created_at})")
        
        return users
        
    except Exception as e:
        print(f"❌ Error checking production users: {e}")
        return []

def create_working_test_user():
    """Create a working test user in production"""
    try:
        # Connect to production DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        # Create test user with proper password hashing
        test_email = "workingtest@ieltsgenaiprep.com"
        test_password = "test123"
        
        # Hash password using the same method as the application
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          test_password.encode('utf-8'), 
                                          b'salt', 
                                          100000)
        password_hash_str = base64.b64encode(password_hash).decode('utf-8')
        
        # Create user record
        user_data = {
            'email': test_email,
            'password_hash': password_hash_str,
            'created_at': datetime.utcnow().isoformat(),
            'assessment_attempts': {
                'academic_writing': 4,
                'general_writing': 4,
                'academic_speaking': 4,
                'general_speaking': 4
            },
            'purchase_verified': True,
            'active': True
        }
        
        # Insert user
        users_table.put_item(Item=user_data)
        
        print(f"✅ Created working test user: {test_email}")
        print(f"🔑 Password: {test_password}")
        print(f"📊 Assessment attempts: 4 for each type")
        
        return test_email, test_password
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None, None

def verify_user_login():
    """Verify the test user can login"""
    try:
        import urllib.request
        import urllib.parse
        
        # Test credentials
        test_email = "workingtest@ieltsgenaiprep.com"
        test_password = "test123"
        
        # Prepare login data
        login_data = {
            'email': test_email,
            'password': test_password,
            'privacy_policy': 'on',
            'terms_of_service': 'on',
            'g-recaptcha-response': 'test'  # Mock recaptcha for testing
        }
        
        # Encode form data
        data = urllib.parse.urlencode(login_data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            'https://www.ieltsaiprep.com/api/login',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        # Test login
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            
        if 'success' in result.lower():
            print(f"✅ Login test successful for {test_email}")
            return True
        else:
            print(f"⚠️ Login test result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking production user database...")
    
    # Check existing users
    existing_users = check_production_users()
    
    if not existing_users:
        print("📝 No users found, creating test user...")
        email, password = create_working_test_user()
        
        if email:
            print(f"""
🎯 WORKING PRODUCTION CREDENTIALS CREATED:

Email: {email}
Password: {password}

✅ User created in production DynamoDB
✅ Assessment attempts: 4 for each type
✅ Purchase verified: True
✅ Account active: True

🔗 Test at: https://www.ieltsaiprep.com/login
""")
        else:
            print("❌ Failed to create test user")
    else:
        print("📋 Using existing production users")
        
    # Verify login works
    print("\n🔐 Testing login functionality...")
    verify_user_login()