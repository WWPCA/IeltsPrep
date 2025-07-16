
import json
import boto3
import bcrypt
from datetime import datetime

def create_production_test_user():
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        # Create test user with proper password hash
        password = 'testpassword123'
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        user_data = {
            'email': 'test@ieltsgenaiprep.com',
            'password_hash': hashed.decode('utf-8'),
            'created_at': datetime.utcnow().isoformat(),
            'attempts_remaining': 4,
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'test_user',
            'account_status': 'active'
        }
        
        # Put user in DynamoDB
        users_table.put_item(Item=user_data)
        
        print('✅ Production test user created successfully')
        print('Email: test@ieltsgenaiprep.com')
        print('Password: testpassword123')
        
        return True
        
    except Exception as e:
        print(f'❌ Error creating production user: {str(e)}')
        return False

if __name__ == '__main__':
    create_production_test_user()
