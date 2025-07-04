#!/usr/bin/env python3
"""
Restore Working Production Lambda
Deploy the exact app.py code that works locally to production
"""

import boto3
import json
import zipfile
import io
from datetime import datetime

def create_working_lambda():
    """Create Lambda deployment using the working app.py code"""
    
    # Read the working app.py code
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_code = f.read()
    except FileNotFoundError:
        print("Error: app.py not found")
        return None
    
    # Read AWS mock config
    try:
        with open('aws_mock_config.py', 'r', encoding='utf-8') as f:
            mock_code = f.read()
    except FileNotFoundError:
        print("Error: aws_mock_config.py not found")
        return None
    
    # Read enhanced template
    try:
        with open('working_template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print("Error: working_template.html not found")
        return None
    
    # Create production version of app.py without .replit dependencies
    production_code = app_code.replace(
        "# Set environment for .replit testing\nos.environ['REPLIT_ENVIRONMENT'] = 'true'\n\n# Import AWS mock services\nfrom aws_mock_config import aws_mock",
        "# Production environment - no mock services needed"
    )
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the working Lambda code as lambda_function.py
        zip_file.writestr('lambda_function.py', production_code)
        
        # Add the enhanced template as a separate file
        zip_file.writestr('working_template.html', template_content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def restore_production():
    """Restore the working production Lambda"""
    
    print("🔄 Restoring working production Lambda...")
    
    # Create deployment package
    zip_content = create_working_lambda()
    if not zip_content:
        print("Failed to create deployment package")
        return False
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update Lambda function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Production Lambda restored successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        
        # Test the function
        print("🧪 Testing restored function...")
        test_response = lambda_client.invoke(
            FunctionName='ielts-genai-prep-api',
            Payload=json.dumps({
                'httpMethod': 'GET',
                'path': '/',
                'headers': {},
                'queryStringParameters': None,
                'body': None
            })
        )
        
        if test_response['StatusCode'] == 200:
            print("✅ Lambda function test successful!")
        else:
            print(f"⚠️ Lambda test returned status: {test_response['StatusCode']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 RESTORING WORKING PRODUCTION LAMBDA...")
    success = restore_production()
    
    if success:
        print("\n✅ PRODUCTION RESTORED!")
        print("🌐 Website should be working at: https://www.ieltsaiprep.com")
        print("💚 Enhanced template included")
    else:
        print("\n❌ RESTORE FAILED!")
        print("Manual intervention required")