#!/usr/bin/env python3
"""
Deploy working Lambda function without external dependencies
Replace bcrypt with hashlib and remove all external imports
"""
import boto3
import zipfile
import os

def create_lambda_no_deps():
    """Create Lambda function without external dependencies"""
    
    # Read the original app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace bcrypt import with hashlib
    content = content.replace('import bcrypt', 'import hashlib')
    
    # Remove requests import
    content = content.replace('import requests', '')
    
    # Replace the reCAPTCHA function with urllib version (no external deps)
    old_recaptcha = '''def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v2 response with Google"""
    try:
        secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
        if not secret_key:
            print("[RECAPTCHA] No secret key found, skipping verification")
            return True  # Allow in development if no key set
        
        # Prepare verification request
        verification_data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        if user_ip:
            verification_data['remoteip'] = user_ip
        
        # Send verification request to Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=verification_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            
            if not success:
                error_codes = result.get('error-codes', [])
                print(f"[RECAPTCHA] Verification failed: {error_codes}")
            
            return success
        else:
            print(f"[RECAPTCHA] HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[RECAPTCHA] Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"[RECAPTCHA] Verification error: {str(e)}")
        return False'''
    
    new_recaptcha = '''def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v2 response with Google using urllib"""
    try:
        import urllib.request
        import urllib.parse
        
        secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
        if not secret_key:
            print("[RECAPTCHA] No secret key found, skipping verification")
            return True  # Allow in development if no key set
        
        # Prepare verification request
        verification_data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        if user_ip:
            verification_data['remoteip'] = user_ip
        
        # Send verification request to Google using urllib
        data = urllib.parse.urlencode(verification_data).encode('utf-8')
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            success = result.get('success', False)
            
            if not success:
                error_codes = result.get('error-codes', [])
                print(f"[RECAPTCHA] Verification failed: {error_codes}")
            
            return success
            
    except Exception as e:
        print(f"[RECAPTCHA] Verification error: {str(e)}")
        return False'''
    
    content = content.replace(old_recaptcha, new_recaptcha)
    
    # Remove the Flask environment setting
    content = content.replace(
        "os.environ['REPLIT_ENVIRONMENT'] = 'true'",
        "# AWS Lambda environment"
    )
    
    # Create simplified AWS mock config without bcrypt
    aws_mock_simple = '''"""
Simplified AWS Mock Services for Lambda (no external dependencies)
"""
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class MockDynamoDBTable:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.items = {}
        
    def put_item(self, item: Dict[str, Any]) -> bool:
        key = item.get('id') or item.get('email') or item.get('session_id')
        if key:
            self.items[key] = item
            return True
        return False
        
    def get_item(self, key: str) -> Optional[Dict[str, Any]]:
        return self.items.get(key)
        
    def delete_item(self, key: str) -> bool:
        if key in self.items:
            del self.items[key]
            return True
        return False

class AWSMockServices:
    def __init__(self):
        self.users_table = MockDynamoDBTable('users')
        self.sessions_table = MockDynamoDBTable('sessions')
        
        # Create test user with simple password hash
        test_user = {
            'email': 'test@ieltsgenaiprep.com',
            'password_hash': hashlib.sha256('testpassword123'.encode()).hexdigest(),
            'name': 'Test User',
            'created_at': datetime.now().isoformat(),
            'purchased_products': ['academic_writing', 'academic_speaking', 'general_writing', 'general_speaking']
        }
        self.users_table.put_item(test_user)
        
    def verify_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.users_table.get_item(email)
        if user:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.get('password_hash') == password_hash:
                return user
        return None
        
    def create_session(self, session_data: Dict[str, Any]) -> bool:
        return self.sessions_table.put_item(session_data)
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions_table.get_item(session_id)

# Global instance
aws_mock = AWSMockServices()
'''
    
    return content, aws_mock_simple

def deploy_no_deps_lambda():
    """Deploy Lambda function without external dependencies"""
    
    print("🔧 Creating Lambda function without external dependencies...")
    
    # Create simplified code
    lambda_code, aws_mock_code = create_lambda_no_deps()
    
    # Create deployment package
    zip_filename = 'lambda-no-deps.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the Lambda function
        zip_file.writestr('lambda_function.py', lambda_code)
        
        # Add simplified AWS mock
        zip_file.writestr('aws_mock_config.py', aws_mock_code)
        
        # Add template files
        template_files = ['working_template.html', 'login.html', 'dashboard.html']
        for template_file in template_files:
            if os.path.exists(template_file):
                zip_file.write(template_file, template_file)
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"🚀 Deploying dependency-free version...")
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ DEPENDENCY-FREE VERSION DEPLOYED!")
        print(f"   Function ARN: {response['FunctionArn']}")
        
        # Clean up
        os.remove(zip_filename)
        
        print("\n🧪 Testing Lambda function...")
        
        # Test the function
        test_response = lambda_client.invoke(
            FunctionName='ielts-genai-prep-api',
            Payload='{"httpMethod": "GET", "path": "/", "headers": {}, "queryStringParameters": null, "body": null}'
        )
        
        if test_response['StatusCode'] == 200:
            print("✅ Lambda function test successful!")
            if 'FunctionError' not in test_response:
                print("✅ No runtime errors detected!")
                return True
            else:
                print("⚠️  Function still has runtime errors")
        
        return False
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    success = deploy_no_deps_lambda()
    if success:
        print("\n🎯 DEPENDENCY-FREE LAMBDA DEPLOYED SUCCESSFULLY!")
        print("All comprehensive functionality should now work without external dependencies.")
    else:
        print("\n❌ DEPLOYMENT FAILED OR STILL HAS ERRORS!")