"""
Create a working production user by directly interfacing with the Lambda system
"""

import boto3
import json
from decimal import Decimal
from datetime import datetime
import bcrypt
import uuid

def create_production_user_complete():
    """Create a complete production user with all required fields"""
    
    # User credentials
    email = "livetest@ieltsaiprep.com"
    password = "LiveTest123!"
    
    # Create bcrypt hash
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create complete user record matching the DynamoDB structure
    user_record = {
        'user_id': str(uuid.uuid4()),
        'email': email,
        'password_hash': password_hash.decode('utf-8'),
        'name': 'Live Test User',
        'user_type': 'test_user',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'assessment_attempts': {
            'academic_writing': {'remaining': Decimal('4'), 'used': Decimal('0')},
            'general_writing': {'remaining': Decimal('4'), 'used': Decimal('0')},
            'academic_speaking': {'remaining': Decimal('4'), 'used': Decimal('0')},
            'general_speaking': {'remaining': Decimal('4'), 'used': Decimal('0')}
        },
        'purchases': [
            {
                'product_id': 'academic_writing',
                'price': Decimal('36.00'),
                'currency': 'CAD',
                'purchase_date': datetime.utcnow().isoformat(),
                'platform': 'test_environment'
            },
            {
                'product_id': 'general_writing',
                'price': Decimal('36.00'),
                'currency': 'CAD',
                'purchase_date': datetime.utcnow().isoformat(),
                'platform': 'test_environment'
            },
            {
                'product_id': 'academic_speaking',
                'price': Decimal('36.00'),
                'currency': 'CAD',
                'purchase_date': datetime.utcnow().isoformat(),
                'platform': 'test_environment'
            },
            {
                'product_id': 'general_speaking',
                'price': Decimal('36.00'),
                'currency': 'CAD',
                'purchase_date': datetime.utcnow().isoformat(),
                'platform': 'test_environment'
            }
        ]
    }
    
    try:
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-genai-prep-users')
        
        # Insert the user
        table.put_item(Item=user_record)
        
        print("✅ Production user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user_record['user_id']}")
        
        return email, password
        
    except Exception as e:
        print(f"❌ Error creating production user: {e}")
        return None, None

def test_production_login(email, password):
    """Test login on production website"""
    
    import urllib.request
    import urllib.error
    
    try:
        # Test login
        url = "https://www.ieltsaiprep.com/api/login"
        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        login_data = {
            "email": email,
            "password": password,
            "g-recaptcha-response": "test-token"  # May need to skip reCAPTCHA
        }
        
        data = json.dumps(login_data).encode('utf-8')
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                print(f"✅ Login successful!")
                print(f"Session ID: {result.get('session_id', 'Not provided')}")
                return True
            else:
                print(f"❌ Login failed: {result.get('error', 'Unknown error')}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code}")
        return False
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 Creating Production Test User")
    print("=" * 40)
    
    # Create the user
    email, password = create_production_user_complete()
    
    if email and password:
        print(f"\n📝 Test Credentials:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Website: https://www.ieltsaiprep.com/login")
        
        # Test login
        print(f"\n🧪 Testing login...")
        if test_production_login(email, password):
            print(f"\n🎉 Success! You can now use these credentials to test Nova AI functionality.")
            return True
        else:
            print(f"\n⚠️ User created but login test failed. You can still try logging in manually.")
            return False
    
    else:
        print(f"\n❌ Failed to create production user")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Ready for Nova AI Testing!")
        print("1. Go to https://www.ieltsaiprep.com/login")
        print("2. Use the credentials above")
        print("3. Navigate to Dashboard")
        print("4. Test Nova AI functionality")
    else:
        print("\n💡 Try using the credentials manually on the website")