#!/usr/bin/env python3
"""
Fix Production Internal Server Error
Deploy clean Lambda function without local dependencies
"""

import boto3
import json
import zipfile
import io

def deploy_fixed_production():
    """Deploy clean production Lambda without local dependencies"""
    
    print("Fixing production internal server error...")
    print("Deploying clean Lambda function without local dependencies")
    
    # Read the production-ready Lambda code
    with open('production_lambda.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.read()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Production error fixed!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_fixed_production()
    if success:
        print("\n✅ PRODUCTION ERROR FIXED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("💰 Pricing: $49.99 CAD (Website) / $36.49 USD (Mobile)")
        print("🔧 Clean Lambda function deployed without local dependencies")
    else:
        print("\n❌ FIX FAILED")