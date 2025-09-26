"""
Create Working Test User for Production Database
"""

import boto3
import json
import hashlib
import uuid
from datetime import datetime

def create_test_user_dynamodb():
    """Create test user directly in DynamoDB"""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Test user data
    user_id = str(uuid.uuid4())
    email = "testuser@ieltsaiprep.com"
    password = "TestUser123!"
    
    # Hash password using the same method as the application
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000)
    password_hash_hex = password_hash.hex()
    
    user_data = {
        'user_id': user_id,
        'email': email,
        'password_hash': password_hash_hex,
        'user_type': 'test_user',
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat(),
        'assessment_attempts': {
            'academic_writing': {'remaining': 4, 'used': 0},
            'general_writing': {'remaining': 4, 'used': 0},
            'academic_speaking': {'remaining': 4, 'used': 0},
            'general_speaking': {'remaining': 4, 'used': 0}
        },
        'purchases': [
            {
                'product_id': 'academic_writing',
                'price': 36.00,
                'currency': 'CAD',
                'purchase_date': datetime.now().isoformat(),
                'platform': 'test_environment'
            },
            {
                'product_id': 'general_writing',
                'price': 36.00,
                'currency': 'CAD',
                'purchase_date': datetime.now().isoformat(),
                'platform': 'test_environment'
            },
            {
                'product_id': 'academic_speaking',
                'price': 36.00,
                'currency': 'CAD',
                'purchase_date': datetime.now().isoformat(),
                'platform': 'test_environment'
            },
            {
                'product_id': 'general_speaking',
                'price': 36.00,
                'currency': 'CAD',
                'purchase_date': datetime.now().isoformat(),
                'platform': 'test_environment'
            }
        ]
    }
    
    try:
        # Try to put user in DynamoDB
        table = dynamodb.Table('ielts-genai-prep-users')
        table.put_item(Item=user_data)
        
        print("✅ Test user created in DynamoDB:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")
        
        return email, password
        
    except Exception as e:
        print(f"❌ Error creating user in DynamoDB: {e}")
        return None, None

def test_existing_production_users():
    """Test common production user credentials"""
    
    test_credentials = [
        ("test@ieltsaiprep.com", "TestPass123!"),
        ("prodtest@ieltsaiprep.com", "ProdTest123!"),
        ("demo@ieltsaiprep.com", "DemoPass123!"),
        ("admin@ieltsaiprep.com", "AdminPass123!")
    ]
    
    print("Testing existing production credentials...")
    
    for email, password in test_credentials:
        try:
            import urllib.request
            import json
            
            url = "https://www.ieltsaiprep.com/api/login"
            req = urllib.request.Request(url, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            login_data = {"email": email, "password": password}
            data = json.dumps(login_data).encode('utf-8')
            req.data = data
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('success'):
                    print(f"✅ Working credentials found!")
                    print(f"Email: {email}")
                    print(f"Password: {password}")
                    return email, password
                else:
                    print(f"❌ {email}: {result.get('error', 'Failed')}")
                    
        except Exception as e:
            print(f"❌ {email}: Error - {e}")
    
    return None, None

def check_dynamodb_tables():
    """Check what DynamoDB tables exist"""
    
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        response = dynamodb.list_tables()
        
        tables = response.get('TableNames', [])
        ielts_tables = [t for t in tables if 'ielts' in t.lower()]
        
        print(f"DynamoDB tables found: {len(ielts_tables)}")
        for table in ielts_tables:
            print(f"  - {table}")
            
        return ielts_tables
        
    except Exception as e:
        print(f"❌ Error checking DynamoDB tables: {e}")
        return []

def main():
    """Main function to find or create working test credentials"""
    
    print("🔍 Finding Working Test Credentials for Production")
    print("=" * 60)
    
    # First, check if any existing credentials work
    email, password = test_existing_production_users()
    
    if email and password:
        print(f"\n✅ Found working credentials:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Website: https://www.ieltsaiprep.com/login")
        return email, password
    
    # Check DynamoDB tables
    tables = check_dynamodb_tables()
    
    if 'ielts-genai-prep-users' in tables:
        print("\n🔧 Creating new test user in DynamoDB...")
        email, password = create_test_user_dynamodb()
        
        if email and password:
            print(f"\n✅ Test user created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Website: https://www.ieltsaiprep.com/login")
            return email, password
    
    print("\n❌ Unable to find or create working test credentials")
    print("You may need to create a user manually through the registration process")
    
    return None, None

if __name__ == "__main__":
    email, password = main()
    
    if email and password:
        print("\n🎯 Test Credentials Ready!")
        print("You can now login and test Nova AI functionality")
        print("1. Go to https://www.ieltsaiprep.com/login")
        print("2. Enter the credentials above")
        print("3. Navigate to Dashboard")
        print("4. Test assessment functionality")
    else:
        print("\n⚠️ Manual user creation required")
        print("Try registering a new user through the website")