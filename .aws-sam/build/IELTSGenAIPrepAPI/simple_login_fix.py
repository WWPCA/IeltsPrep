#!/usr/bin/env python3
"""
Simple fix for login by updating the Lambda function routing
"""

import boto3
import json
import zipfile
import io
import urllib.request
import re

def fix_lambda_routing():
    """Fix Lambda function routing to handle login properly"""
    
    # Download current Lambda code
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
    download_url = response['Code']['Location']
    
    with urllib.request.urlopen(download_url) as response:
        zip_data = response.read()
    
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
        code = zip_ref.read('lambda_function.py').decode('utf-8')
    
    # Create a completely new login handler that works
    new_login_handler = '''
def handle_login(data, headers):
    """Handle login with proper authentication"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        print(f"[LOGIN] Login attempt for: {email}")
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cookie',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                'body': json.dumps({'success': False, 'message': 'Email and password required'})
            }
        
        # Get user from DynamoDB
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-genai-prep-users')
        
        # Search for user by email
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if not response['Items']:
            print(f"[LOGIN] User not found: {email}")
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cookie',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        user = response['Items'][0]
        
        # Check if user is active
        if not user.get('is_active', True):
            print(f"[LOGIN] User not active: {email}")
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cookie',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                'body': json.dumps({'success': False, 'message': 'Account not active'})
            }
        
        # Verify password
        import hashlib
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()
        
        if password_hash != user.get('password_hash', ''):
            print(f"[LOGIN] Invalid password for: {email}")
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cookie',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        print(f"[LOGIN] Successful login for: {email}")
        
        # Create session
        session_id = str(uuid.uuid4())
        
        # Return success with redirect
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cookie',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Set-Cookie': f'session_id={session_id}; HttpOnly; Secure; SameSite=Strict; Max-Age=86400; Path=/'
            },
            'body': json.dumps({
                'success': True, 
                'message': 'Login successful',
                'redirect': '/dashboard',
                'user_id': user['user_id'],
                'email': email
            })
        }
        
    except Exception as e:
        print(f"[LOGIN] Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cookie',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps({'success': False, 'message': 'Internal server error'})
        }
'''
    
    # Replace the existing handle_login function
    login_pattern = r'def handle_login\(data, headers\):.*?(?=\ndef|\nclass|\n$)'
    updated_code = re.sub(login_pattern, new_login_handler.strip(), code, flags=re.DOTALL)
    
    # Ensure imports are present
    if 'import uuid' not in updated_code:
        updated_code = updated_code.replace('import json', 'import json\nimport uuid')
    
    # Create new ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', updated_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("✅ Lambda function updated with new login handler")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda: {e}")
        return False

def test_login():
    """Test the login after fixing Lambda"""
    import requests
    import time
    
    print("\n🧪 Testing login...")
    
    # Wait for Lambda to update
    time.sleep(3)
    
    try:
        response = requests.post(
            'https://www.ieltsaiprep.com/api/login',
            json={
                'email': 'prodtest_20250709_175130_i1m2@ieltsaiprep.com',
                'password': 'TestProd2025!'
            },
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Lambda login handler...")
    
    if fix_lambda_routing():
        if test_login():
            print("\n✅ Login is now working!")
            print("You can log in at: https://www.ieltsaiprep.com/login")
            print("Credentials: prodtest_20250709_175130_i1m2@ieltsaiprep.com / TestProd2025!")
        else:
            print("❌ Login test failed - may need additional debugging")
    else:
        print("❌ Failed to update Lambda function")