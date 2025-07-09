#!/usr/bin/env python3
"""
Fix syntax error in Lambda function by properly handling urllib replacement
"""
import boto3
import zipfile
import os

def create_fixed_lambda_code():
    """Create properly fixed Lambda code"""
    
    # Read the original app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the entire reCAPTCHA function with urllib-compatible version
    old_function = '''def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
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
    
    new_function = '''def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
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
        
        # Send verification request to Google using urllib
        import urllib.request
        import urllib.parse
        
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
    
    # Replace the function
    content = content.replace(old_function, new_function)
    
    # Remove requests import
    content = content.replace('import requests', '')
    
    # Clean up the imports section
    content = content.replace('\nimport requests\n', '\n')
    
    # Remove Flask-specific environment setting
    content = content.replace(
        "os.environ['REPLIT_ENVIRONMENT'] = 'true'",
        "# AWS Lambda environment"
    )
    
    return content

def deploy_fixed_lambda():
    """Deploy the fixed Lambda function"""
    
    print("🔧 Creating syntax-corrected Lambda function...")
    
    # Create fixed Lambda code
    lambda_code = create_fixed_lambda_code()
    
    # Create deployment package
    zip_filename = 'lambda-syntax-fixed.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the Lambda function
        zip_file.writestr('lambda_function.py', lambda_code)
        
        # Add AWS mock configuration
        zip_file.write('aws_mock_config.py', 'aws_mock_config.py')
        
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
        
        print(f"🚀 Deploying syntax-corrected version...")
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ SYNTAX-CORRECTED VERSION DEPLOYED!")
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
    success = deploy_fixed_lambda()
    if success:
        print("\n🎯 SYNTAX-CORRECTED VERSION DEPLOYED SUCCESSFULLY!")
    else:
        print("\n❌ DEPLOYMENT FAILED OR STILL HAS ERRORS!")