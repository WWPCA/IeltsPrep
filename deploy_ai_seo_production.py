#!/usr/bin/env python3
"""
Deploy the AI SEO Lambda with GDPR compliance - This is the working version
"""

import boto3
import json
import zipfile
import io

def create_ai_seo_deployment():
    """Create deployment with ai_seo_lambda.py (the working version with GDPR)"""
    
    # Read ai_seo_lambda.py (the working Lambda function with GDPR)
    with open('ai_seo_lambda.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def deploy_ai_seo_production():
    """Deploy the working AI SEO Lambda with GDPR compliance"""
    
    print("Deploying working AI SEO Lambda with GDPR compliance...")
    zip_content = create_ai_seo_deployment()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ AI SEO Lambda with GDPR deployed successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_ai_seo_production()
    if success:
        print("\n✅ WORKING AI SEO VERSION WITH GDPR DEPLOYED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("🔒 GDPR endpoints: /gdpr/my-data, /gdpr/consent-settings, etc.")
    else:
        print("\n❌ DEPLOYMENT FAILED")