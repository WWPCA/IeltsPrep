#!/usr/bin/env python3
"""
Deploy Chart Fix to AWS Lambda Production
Updates the Lambda function with chart display functionality
"""

import json
import boto3
import zipfile
import io
import os
from datetime import datetime

def create_deployment_package():
    """Create Lambda deployment package with chart fixes"""
    
    # Create zip file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main Lambda function
        zip_file.write('app.py', 'lambda_function.py')
        
        # Add AWS mock configuration
        zip_file.write('aws_mock_config.py', 'aws_mock_config.py')
        
        # Add any additional files if needed
        try:
            zip_file.write('working_template.html', 'working_template.html')
        except FileNotFoundError:
            print("⚠️  working_template.html not found - skipping")
        
        try:
            zip_file.write('login.html', 'login.html')
        except FileNotFoundError:
            print("⚠️  login.html not found - skipping")
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def update_lambda_function():
    """Update Lambda function with chart display functionality"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Get current function configuration
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        current_config = response['Configuration']
        
        print(f"📋 Current Lambda function size: {current_config.get('CodeSize', 0)} bytes")
        print(f"📋 Current runtime: {current_config.get('Runtime', 'unknown')}")
        
        # Create deployment package
        print("📦 Creating deployment package with chart fixes...")
        zip_content = create_deployment_package()
        
        print(f"📦 Deployment package size: {len(zip_content)} bytes")
        
        # Update function code
        print("🚀 Updating Lambda function...")
        update_response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ Lambda function updated successfully!")
        print(f"📋 New code size: {update_response.get('CodeSize', 0)} bytes")
        print(f"📋 Last modified: {update_response.get('LastModified', 'unknown')}")
        
        # Test the function
        print("\n🧪 Testing updated function...")
        
        # Test academic writing assessment
        test_event = {
            'httpMethod': 'GET',
            'path': '/assessment/academic-writing',
            'headers': {'Host': 'www.ieltsaiprep.com'},
            'body': None,
            'isBase64Encoded': False
        }
        
        test_response = lambda_client.invoke(
            FunctionName='ielts-genai-prep-api',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(test_response['Payload'].read())
        
        if payload.get('statusCode') == 200:
            print("✅ Academic writing assessment test passed")
            
            # Check if chart content is present
            body = payload.get('body', '')
            if 'chart-container' in body and 'svg' in body:
                print("✅ Chart content detected in response")
                print("🎯 Chart display functionality deployed successfully!")
            else:
                print("⚠️  Chart content not found in response")
                print("Body preview:", body[:200] + "...")
        else:
            print(f"❌ Test failed with status: {payload.get('statusCode')}")
            print(f"Error: {payload.get('body', 'No error message')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
        return False

def main():
    """Main deployment function"""
    
    print("📊 Deploying Chart Fix to AWS Lambda")
    print("=" * 50)
    print(f"🕐 Deployment started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"📋 AWS Account: {identity.get('Account', 'unknown')}")
        print(f"📋 AWS User: {identity.get('UserId', 'unknown')}")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return False
    
    # Update Lambda function
    if update_lambda_function():
        print("\n🎉 Chart Fix Deployment Complete!")
        print("🌐 Production website: https://www.ieltsaiprep.com/assessment/academic-writing")
        print("📊 Charts should now display properly in academic writing assessments")
        print("\n🧪 Test the fixes:")
        print("1. Visit https://www.ieltsaiprep.com/assessment/academic-writing")
        print("2. Check if charts are now visible in Task 1 questions")
        print("3. Verify both Task 1 and Task 2 display correctly")
        return True
    else:
        print("\n❌ Deployment failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)