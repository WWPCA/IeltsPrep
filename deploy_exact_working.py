#!/usr/bin/env python3
"""
Deploy the exact working version with all triggers and workflows
"""

import boto3
import json
import zipfile
import io

def create_working_deployment():
    """Create deployment with exact working app.py and working_template.html"""
    
    # Read app.py (the working Lambda function)
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Read working_template.html
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_code = f.read()
    
    # Read aws_mock_config.py
    with open('aws_mock_config.py', 'r', encoding='utf-8') as f:
        aws_mock_code = f.read()
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', app_code)
        zip_file.writestr('working_template.html', template_code)
        zip_file.writestr('aws_mock_config.py', aws_mock_code)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def deploy_to_production():
    """Deploy to production Lambda"""
    
    print("Creating deployment package...")
    zip_content = create_working_deployment()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Deployment successful!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_to_production()
    if success:
        print("\n✅ WORKING VERSION DEPLOYED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
    else:
        print("\n❌ DEPLOYMENT FAILED")