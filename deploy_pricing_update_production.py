#!/usr/bin/env python3
"""
Deploy Updated Pricing to Production Lambda
Updates the production Lambda function with the corrected $36.49 USD pricing
"""

import boto3
import json
import zipfile
import io

def create_pricing_deployment():
    """Create deployment with updated app.py containing corrected pricing"""
    
    # Read app.py (the main Lambda function with updated pricing)
    with open('app.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def deploy_pricing_production():
    """Deploy the Lambda function with updated pricing"""
    
    print("Deploying updated pricing to production Lambda...")
    print("Mobile App: $36.49 USD")
    print("Website: $49.99 CAD")
    
    zip_content = create_pricing_deployment()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Pricing update deployed successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_pricing_production()
    if success:
        print("\n✅ PRICING UPDATE DEPLOYED TO PRODUCTION!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("💰 Mobile App: $36.49 USD")
        print("💰 Website: $49.99 CAD")
    else:
        print("\n❌ DEPLOYMENT FAILED")