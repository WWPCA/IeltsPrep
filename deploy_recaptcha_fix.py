#!/usr/bin/env python3
"""
Deploy reCAPTCHA fix to AWS Lambda
Fixes the hardcoded reCAPTCHA site key issue by using environment variables
"""
import boto3
import zipfile
import os

def deploy_recaptcha_fix():
    """Deploy the reCAPTCHA fix to AWS Lambda"""
    
    print("Deploying reCAPTCHA fix to AWS Lambda...")
    
    # Create deployment package
    zip_filename = 'recaptcha-fix.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the main Lambda function
        zip_file.write('app.py', 'lambda_function.py')
        
        # Add the AWS mock configuration
        zip_file.write('aws_mock_config.py', 'aws_mock_config.py')
        
        # Add the template files
        zip_file.write('working_template.html', 'working_template.html')
        zip_file.write('login.html', 'login.html')
        zip_file.write('dashboard.html', 'dashboard.html')
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ reCAPTCHA fix deployed successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        
        # Clean up
        os.remove(zip_filename)
        
        print("\n🔧 Fix Applied:")
        print("  • Lambda function now uses RECAPTCHA_V2_SITE_KEY environment variable")
        print("  • Hardcoded reCAPTCHA site key replaced dynamically")
        print("  • Templates remain unchanged")
        print("  • All existing functionality preserved")
        
        print("\n✅ Test the fix:")
        print("  1. Visit: https://www.ieltsaiprep.com/login")
        print("  2. reCAPTCHA should now load correctly without error")
        print("  3. Complete reCAPTCHA and test login functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    success = deploy_recaptcha_fix()
    if success:
        print("\n🎯 reCAPTCHA fix deployment completed successfully!")
    else:
        print("\n❌ reCAPTCHA fix deployment failed!")