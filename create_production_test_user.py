#!/usr/bin/env python3
"""
Create test user in AWS DynamoDB production database
Allows testing of production website www.ieltsaiprep.com
"""

import boto3
import json
import hashlib
import secrets
import string
from datetime import datetime, timezone

def create_production_test_user():
    """Create test user in AWS DynamoDB for production testing"""
    
    # Generate unique test credentials
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    
    test_email = f'prodtest_{timestamp}_{random_suffix}@ieltsaiprep.com'
    test_password = 'TestProd2025!'
    
    # Create password hash using same method as production Lambda
    password_hash = hashlib.pbkdf2_hmac('sha256', test_password.encode(), b'salt', 100000).hex()
    
    # AWS DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('ielts-genai-prep-users')
    
    # Generate unique user ID
    user_id = f"user_{timestamp}_{random_suffix}"
    
    # Create test user item
    user_item = {
        'user_id': user_id,  # Primary key required by DynamoDB
        'email': test_email,
        'password_hash': password_hash,
        'region': 'us-east-1',
        'join_date': datetime.now(timezone.utc).isoformat(),
        'assessment_package_status': 'active',
        'is_active': True,
        'account_activated': True,
        'email_verified': True,
        'assessment_counts': {
            'academic_writing': {'remaining': 4, 'used': 0},
            'general_writing': {'remaining': 4, 'used': 0},
            'academic_speaking': {'remaining': 4, 'used': 0},
            'general_speaking': {'remaining': 4, 'used': 0}
        }
    }
    
    try:
        # Put item in DynamoDB
        table.put_item(Item=user_item)
        
        print("✓ Production test user created successfully!")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print(f"Region: us-east-1")
        print(f"Status: Active with 4 assessments each")
        print(f"Test at: https://www.ieltsaiprep.com/login")
        
        return {
            'email': test_email,
            'password': test_password,
            'success': True
        }
        
    except Exception as e:
        print(f"✗ Error creating production test user: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    create_production_test_user()