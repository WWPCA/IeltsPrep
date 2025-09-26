#!/usr/bin/env python3
"""
Redeploy Lambda function with correct structure and files
"""
import boto3
import zipfile
import os
import json

def create_complete_lambda_package():
    """Create deployment package with correct structure"""
    
    # Read the Lambda handler code from app.py
    with open('app.py', 'r') as f:
        lambda_code = f.read()
    
    # Read all necessary HTML files
    files_to_include = {
        'login.html': 'complete-login-template.html',
        'dashboard.html': 'dashboard.html', 
        'public_home.html': 'complete-home-template.html',
        'privacy-policy.html': 'complete-privacy-policy.html',
        'terms-of-service.html': 'complete-terms-of-service.html'
    }
    
    file_contents = {}
    
    # Try to read each file, use fallback if not found
    for target_name, source_file in files_to_include.items():
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                file_contents[target_name] = f.read()
                print(f"✓ Found {source_file}")
        except FileNotFoundError:
            try:
                with open(target_name, 'r', encoding='utf-8') as f:
                    file_contents[target_name] = f.read()
                    print(f"✓ Found {target_name}")
            except FileNotFoundError:
                print(f"⚠ Warning: {target_name} not found, using minimal template")
                file_contents[target_name] = f"<html><head><title>{target_name}</title></head><body><h1>IELTS GenAI Prep</h1></body></html>"
    
    # Create deployment package
    with zipfile.ZipFile('lambda-complete.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main Lambda handler
        zip_file.writestr('lambda_function.py', lambda_code)
        
        # Add all HTML files
        for filename, content in file_contents.items():
            zip_file.writestr(filename, content)
    
    print("Created lambda-complete.zip with all files")
    return 'lambda-complete.zip'

def deploy_fixed_lambda():
    """Deploy the complete Lambda function"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'ielts-genai-prep-api'
    
    try:
        # Create the deployment package
        zip_file_path = create_complete_lambda_package()
        
        # Read the deployment package
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"Deploying to Lambda function {function_name}...")
        print(f"Package size: {len(zip_content)} bytes")
        
        # Update the Lambda function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print("Lambda function code updated successfully!")
        
        # Ensure correct handler configuration
        config_response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Handler='lambda_function.lambda_handler',
            Environment={
                'Variables': {
                    'DYNAMODB_TABLE_PREFIX': 'ielts-genai-prep',
                    'ENVIRONMENT': 'production',
                    'RECAPTCHA_V2_SITE_KEY': os.environ.get('RECAPTCHA_V2_SITE_KEY', ''),
                    'RECAPTCHA_V2_SECRET_KEY': os.environ.get('RECAPTCHA_V2_SECRET_KEY', '')
                }
            }
        )
        
        print("Lambda configuration updated!")
        print(f"Handler: {config_response['Handler']}")
        print(f"Runtime: {config_response['Runtime']}")
        
        # Wait for function to be updated
        print("Waiting for function update to complete...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        print("Lambda deployment completed successfully!")
        print("Website: https://www.ieltsaiprep.com/login")
        
        # Clean up
        os.remove(zip_file_path)
        
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    print("Redeploying Lambda function with complete structure...")
    
    if deploy_fixed_lambda():
        print("Deployment successful! Testing website...")
        
        # Test the website
        import requests
        try:
            response = requests.get('https://www.ieltsaiprep.com/login', timeout=10)
            if response.status_code == 200:
                print("✓ Website is working correctly!")
            else:
                print(f"⚠ Website returned status code: {response.status_code}")
        except Exception as e:
            print(f"⚠ Error testing website: {e}")
    else:
        print("Deployment failed")