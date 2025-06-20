#!/usr/bin/env python3
"""
Deploy working Lambda function with correct syntax
"""
import boto3
import zipfile
import os

def create_working_package():
    """Create deployment package with working Lambda code"""
    
    # Read the working Lambda code
    with open('working-lambda.py', 'r') as f:
        lambda_code = f.read()
    
    # Read HTML files
    html_files = {}
    file_mappings = {
        'login.html': 'complete-login-template.html',
        'dashboard.html': 'dashboard.html',
        'public_home.html': 'public_home.html'
    }
    
    for target, source in file_mappings.items():
        try:
            with open(source, 'r', encoding='utf-8') as f:
                html_files[target] = f.read()
        except FileNotFoundError:
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    html_files[target] = f.read()
            except FileNotFoundError:
                html_files[target] = f'<html><head><title>IELTS GenAI Prep</title></head><body><h1>{target}</h1></body></html>'
    
    # Create deployment package
    with zipfile.ZipFile('lambda-working.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main handler
        zip_file.writestr('lambda_function.py', lambda_code)
        
        # Add HTML files
        for filename, content in html_files.items():
            zip_file.writestr(filename, content)
    
    print("Created working Lambda package")
    return 'lambda-working.zip'

def deploy_working_lambda():
    """Deploy the working Lambda function"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'ielts-genai-prep-api'
    
    try:
        # Create package
        zip_file_path = create_working_package()
        
        # Read package
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"Deploying working Lambda function...")
        print(f"Package size: {len(zip_content)} bytes")
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print("Lambda function updated successfully!")
        
        # Wait for update to complete
        print("Waiting for function update...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        print("Deployment completed!")
        
        # Clean up
        os.remove(zip_file_path)
        
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if deploy_working_lambda():
        print("Testing website...")
        
        import time
        time.sleep(15)
        
        # Test the endpoint
        import urllib.request
        try:
            with urllib.request.urlopen('https://www.ieltsaiprep.com/login', timeout=10) as response:
                status = response.getcode()
                print(f"Website status: {status}")
                
                if status == 200:
                    print("Website is working! You can now:")
                    print("1. Go to https://www.ieltsaiprep.com/login")
                    print("2. Use test credentials:")
                    print("   Email: test@ieltsgenaiprep.com")
                    print("   Password: testpassword123")
                    print("3. Take screenshots for App Store submission")
                else:
                    print(f"Website returned status: {status}")
        except Exception as e:
            print(f"Website test error: {e}")
    else:
        print("Deployment failed")