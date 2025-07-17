#!/usr/bin/env python3
"""
Deploy complete production package with privacy policy and terms of service
"""

import boto3
import json
from datetime import datetime

def deploy_complete_production():
    """Deploy the complete production Lambda package"""
    
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Read the complete production package
        with open('complete_production_lambda.zip', 'rb') as f:
            zip_content = f.read()
        
        print("🚀 Deploying complete production package...")
        print(f"📦 Package size: {len(zip_content):,} bytes")
        
        # Deploy to Lambda
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Deployment successful!")
        print(f"📝 Function ARN: {response['FunctionArn']}")
        print(f"⏰ Last Modified: {response['LastModified']}")
        
        # Wait for function to be updated
        print("⏳ Waiting for function update...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        print("🎉 Production deployment complete!")
        print("\n📋 Available endpoints:")
        print("   • https://www.ieltsaiprep.com/ (Home page)")
        print("   • https://www.ieltsaiprep.com/login (Login page)")
        print("   • https://www.ieltsaiprep.com/privacy-policy (Privacy policy)")
        print("   • https://www.ieltsaiprep.com/terms-of-service (Terms of service)")
        print("   • https://www.ieltsaiprep.com/api/health (Health check)")
        print("   • https://www.ieltsaiprep.com/robots.txt (AI SEO robots)")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    deploy_complete_production()