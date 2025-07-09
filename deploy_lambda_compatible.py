#!/usr/bin/env python3
"""
Deploy Lambda-compatible version of app.py without requests dependency
Replace requests with urllib for reCAPTCHA verification
"""
import boto3
import zipfile
import os

def create_lambda_compatible_code():
    """Create Lambda-compatible version of app.py"""
    
    # Read the original app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace requests import with urllib
    content = content.replace(
        'import requests',
        'import urllib.request\nimport urllib.parse\nimport urllib.error'
    )
    
    # Replace requests.post with urllib equivalent for reCAPTCHA
    old_recaptcha_code = '''        # Send verification request to Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=verification_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()'''
    
    new_recaptcha_code = '''        # Send verification request to Google
        data = urllib.parse.urlencode(verification_data).encode('utf-8')
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))'''
    
    content = content.replace(old_recaptcha_code, new_recaptcha_code)
    
    # Replace requests.exceptions.RequestException with urllib.error.URLError
    content = content.replace(
        'except requests.exceptions.RequestException as e:',
        'except urllib.error.URLError as e:'
    )
    
    # Remove the Flask-specific parts that won't work in Lambda
    content = content.replace(
        "# Set environment for .replit testing\nos.environ['REPLIT_ENVIRONMENT'] = 'true'",
        "# AWS Lambda environment"
    )
    
    return content

def deploy_lambda_compatible():
    """Deploy Lambda-compatible version"""
    
    print("🔧 Creating Lambda-compatible version without requests dependency...")
    
    # Create Lambda-compatible code
    lambda_code = create_lambda_compatible_code()
    
    # Create deployment package
    zip_filename = 'lambda-compatible-comprehensive.zip'
    
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
        
        print(f"🚀 Deploying Lambda-compatible version...")
        print(f"   Package size: {len(zip_content)} bytes")
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ LAMBDA-COMPATIBLE VERSION DEPLOYED!")
        print(f"   Function ARN: {response['FunctionArn']}")
        print(f"   Last Modified: {response['LastModified']}")
        
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
            else:
                print("⚠️  Function executed with errors")
        else:
            print(f"❌ Lambda test failed with status: {test_response['StatusCode']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    success = deploy_lambda_compatible()
    if success:
        print("\n🎯 LAMBDA-COMPATIBLE VERSION DEPLOYED!")
        print("All comprehensive functionality should now work without requests dependency.")
    else:
        print("\n❌ DEPLOYMENT FAILED!")