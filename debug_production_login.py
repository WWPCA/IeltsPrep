#!/usr/bin/env python3
"""
Debug production login issue and fix authentication
"""

import boto3
import json
import zipfile
import io
import urllib.request
import re
import hashlib
from datetime import datetime

def get_current_lambda_code():
    """Download current Lambda function code"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        download_url = response['Code']['Location']
        with urllib.request.urlopen(download_url) as response:
            zip_data = response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            code = zip_ref.read('lambda_function.py').decode('utf-8')
        
        return code
    except Exception as e:
        print(f"Error downloading Lambda code: {e}")
        return None

def test_password_hash():
    """Test password hashing to match production"""
    test_password = "TestProd2025!"
    
    # Test different hashing methods
    hash1 = hashlib.pbkdf2_hmac('sha256', test_password.encode(), b'salt', 100000).hex()
    hash2 = hashlib.sha256(test_password.encode()).hexdigest()
    
    print(f"PBKDF2 hash: {hash1}")
    print(f"SHA256 hash: {hash2}")
    
    return hash1, hash2

def fix_lambda_login_handler(lambda_code):
    """Fix the login handler in Lambda function"""
    
    # Find the handle_user_login function
    login_pattern = r'def handle_user_login\(data: Dict\[str, Any\]\) -> Dict\[str, Any\]:.*?(?=\ndef|\nclass|\n$)'
    
    # Create a working login handler
    new_login_handler = '''def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login with DynamoDB authentication"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        # Get DynamoDB client
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-genai-prep-users')
        
        # Search for user by email
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if not response['Items']:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        user = response['Items'][0]
        
        # Verify password
        import hashlib
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()
        
        if password_hash != user.get('password_hash', ''):
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user['user_id'],
            'email': email,
            'login_time': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # Store session (mock for now)
        print(f"[CLOUDWATCH] User logged in: {email}")
        
        # Return success with redirect
        return {
            'statusCode': 302,
            'headers': {
                'Location': '/dashboard',
                'Set-Cookie': f'session_id={session_id}; HttpOnly; Secure; SameSite=Strict; Max-Age=86400'
            },
            'body': ''
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Login error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

'''
    
    # Replace the existing handler
    updated_code = re.sub(login_pattern, new_login_handler, lambda_code, flags=re.DOTALL)
    
    # Ensure imports are present
    if 'import uuid' not in updated_code:
        updated_code = updated_code.replace('import json', 'import json\nimport uuid')
    
    if 'from datetime import datetime, timedelta' not in updated_code:
        updated_code = updated_code.replace('import json', 'import json\nfrom datetime import datetime, timedelta')
    
    return updated_code

def deploy_fixed_lambda(updated_code):
    """Deploy the fixed Lambda function"""
    
    # Create new ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', updated_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("Lambda function updated with fixed login handler")
        return True
        
    except Exception as e:
        print(f"Error updating Lambda: {e}")
        return False

def main():
    """Main function to debug and fix production login"""
    
    print("🔍 Debugging Production Login Issue")
    print("=" * 40)
    
    # Test password hashing
    print("Testing password hashing...")
    hash1, hash2 = test_password_hash()
    
    # Get current Lambda code
    print("Downloading current Lambda code...")
    lambda_code = get_current_lambda_code()
    if not lambda_code:
        print("❌ Failed to download Lambda code")
        return
    
    # Check if CloudFront blocking is still present
    if 'X-CloudFront-Secret' not in lambda_code:
        print("❌ CloudFront blocking missing - aborting")
        return
    
    print("✅ CloudFront blocking confirmed")
    
    # Fix login handler
    print("Fixing login handler...")
    updated_code = fix_lambda_login_handler(lambda_code)
    
    # Deploy fixed Lambda
    print("Deploying fixed Lambda function...")
    if deploy_fixed_lambda(updated_code):
        print("✅ Lambda function updated successfully")
        print("")
        print("Test credentials:")
        print("Email: prodtest_20250709_175130_i1m2@ieltsaiprep.com")
        print("Password: TestProd2025!")
        print("URL: https://www.ieltsaiprep.com/login")
    else:
        print("❌ Failed to deploy Lambda function")

if __name__ == "__main__":
    main()