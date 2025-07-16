#!/usr/bin/env python3
"""
Create Direct Production User with Working Credentials
"""

import boto3
import hashlib
import base64
from datetime import datetime
import json

def create_production_test_user():
    """Create a working test user directly in production"""
    try:
        # Connect to production DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        # Create test user credentials
        test_email = "prodtest2@ieltsaiprep.com"
        test_password = "test123"
        
        # Create password hash using PBKDF2 (same as production)
        password_bytes = test_password.encode('utf-8')
        salt = b'ielts-genai-prep-salt'
        
        # Hash with PBKDF2 HMAC SHA256
        password_hash = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
        password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
        
        # Create user record
        user_data = {
            'email': test_email,
            'password_hash': password_hash_b64,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'active': True,
            'purchase_verified': True,
            'assessment_attempts': {
                'academic_writing': 4,
                'general_writing': 4,
                'academic_speaking': 4,
                'general_speaking': 4
            },
            'gdpr_consent': {
                'privacy_policy': True,
                'terms_of_service': True,
                'consent_date': datetime.utcnow().isoformat()
            }
        }
        
        # Insert user into production table
        users_table.put_item(Item=user_data)
        
        print(f"✅ Created production test user successfully")
        print(f"📧 Email: {test_email}")
        print(f"🔑 Password: {test_password}")
        print(f"🔒 Password hash: {password_hash_b64[:20]}...")
        print(f"📊 Assessment attempts: 4 for each type")
        
        return test_email, test_password
        
    except Exception as e:
        print(f"❌ Error creating production user: {e}")
        return None, None

def verify_production_user(email, password):
    """Verify the user exists and can be authenticated"""
    try:
        # Connect to production DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        # Get user
        response = users_table.get_item(Key={'email': email})
        
        if 'Item' in response:
            user = response['Item']
            stored_hash = user.get('password_hash', '')
            
            # Verify password
            password_bytes = password.encode('utf-8')
            salt = b'ielts-genai-prep-salt'
            calculated_hash = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
            calculated_hash_b64 = base64.b64encode(calculated_hash).decode('utf-8')
            
            if stored_hash == calculated_hash_b64:
                print(f"✅ Password verification successful for {email}")
                return True
            else:
                print(f"❌ Password verification failed for {email}")
                return False
        else:
            print(f"❌ User {email} not found in production")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        return False

if __name__ == "__main__":
    print("👤 Creating production test user...")
    
    # Create test user
    email, password = create_production_test_user()
    
    if email:
        print(f"""
🎯 PRODUCTION LOGIN CREDENTIALS:

Email: {email}
Password: {password}

✅ User created in production DynamoDB
✅ Password properly hashed with PBKDF2
✅ Assessment attempts: 4 for each type
✅ GDPR consent: Pre-approved
✅ Account status: Active

🔗 Test at: https://www.ieltsaiprep.com/login

Note: The production system is now working with enhanced robots.txt
""")
        
        # Verify the user works
        print("🔐 Verifying user credentials...")
        if verify_production_user(email, password):
            print("✅ User verification successful - ready for production login")
        else:
            print("❌ User verification failed")
    else:
        print("❌ Failed to create production user")