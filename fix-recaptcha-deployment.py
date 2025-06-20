#!/usr/bin/env python3
"""
Deploy Lambda function with fixed reCAPTCHA configuration
"""
import boto3
import zipfile
import os
import time

def create_lambda_package_with_recaptcha_fix():
    """Create deployment package with reCAPTCHA environment variable fix"""
    
    # Read the updated app.py with reCAPTCHA fix
    with open('app.py', 'r') as f:
        lambda_code = f.read()
    
    # Read static files
    login_html = ""
    try:
        with open('login.html', 'r') as f:
            login_html = f.read()
    except FileNotFoundError:
        print("Warning: login.html not found, using template fallback")
        login_html = """<!DOCTYPE html>
<html>
<head><title>Login - IELTS GenAI Prep</title></head>
<body><h1>Login page - reCAPTCHA will be configured</h1></body>
</html>"""
    
    dashboard_html = ""
    try:
        with open('dashboard.html', 'r') as f:
            dashboard_html = f.read()
    except FileNotFoundError:
        print("Warning: dashboard.html not found")
    
    public_home_html = ""
    try:
        with open('public_home.html', 'r') as f:
            public_home_html = f.read()
    except FileNotFoundError:
        print("Warning: public_home.html not found")
    
    # Create deployment package
    with zipfile.ZipFile('lambda-recaptcha-fix.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main Lambda handler
        zip_file.writestr('lambda_function.py', lambda_code)
        
        # Add static HTML files
        if login_html:
            zip_file.writestr('login.html', login_html)
        if dashboard_html:
            zip_file.writestr('dashboard.html', dashboard_html)
        if public_home_html:
            zip_file.writestr('public_home.html', public_home_html)
    
    print("Created lambda-recaptcha-fix.zip with reCAPTCHA environment variable fix")
    return 'lambda-recaptcha-fix.zip'

def deploy_recaptcha_fix():
    """Deploy the reCAPTCHA fix to production Lambda"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'ielts-genai-prep-api'
    
    try:
        # Create the deployment package
        zip_file_path = create_lambda_package_with_recaptcha_fix()
        
        # Read the deployment package
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"Updating Lambda function {function_name}...")
        print(f"Package size: {len(zip_content)} bytes")
        
        # Update the Lambda function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print("Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Runtime: {response['Runtime']}")
        print(f"Handler: {response['Handler']}")
        print(f"Code size: {response['CodeSize']} bytes")
        print(f"Last modified: {response['LastModified']}")
        
        # Wait for function to be updated
        print("Waiting for function update to complete...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        print("✅ reCAPTCHA fix deployed successfully!")
        print("🌐 Website: https://www.ieltsaiprep.com/login")
        print("📝 The login page now uses the correct reCAPTCHA site key from environment variables")
        
        # Clean up
        os.remove(zip_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    print("Deploying reCAPTCHA fix to production Lambda...")
    
    if deploy_recaptcha_fix():
        print("\n🎉 Deployment completed successfully!")
        print("The reCAPTCHA error should now be resolved on www.ieltsaiprep.com")
    else:
        print("\n💥 Deployment failed. Check error messages above.")