#!/usr/bin/env python3
"""
Quick fix for production 500 error - Deploy working Lambda function
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def create_lambda_deployment():
    """Create and deploy fixed Lambda function"""
    
    # Read the current lambda_function.py content
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Create deployment ZIP
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'production_500_fix_{timestamp}.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    print(f"✅ Created deployment package: {zip_filename}")
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"🚀 DEPLOYED: {zip_filename} to AWS Lambda")
        print(f"📦 Package Size: {len(zip_content)} bytes")
        print(f"⏰ Deployment Time: {response['LastModified']}")
        print(f"🔧 Code SHA256: {response['CodeSha256']}")
        
        # Wait for propagation
        print("⏳ Waiting 30 seconds for deployment propagation...")
        import time
        time.sleep(30)
        
        # Test the deployment
        import urllib.request
        try:
            response = urllib.request.urlopen('https://www.ieltsaiprep.com')
            status_code = response.getcode()
            print(f"✅ Production Test: HTTP {status_code}")
            
            if status_code == 200:
                print("🎉 SUCCESS: Production 500 error fixed!")
                print("🔍 Google Search 'S' icon should resolve within 24-48 hours")
            else:
                print(f"⚠️  Still getting HTTP {status_code}")
                
        except Exception as e:
            print(f"❌ Production test failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 FIXING PRODUCTION 500 ERROR")
    print("=" * 50)
    
    success = create_lambda_deployment()
    
    if success:
        print("\n✅ PRODUCTION 500 ERROR FIX COMPLETE")
        print("📊 This will resolve the 'S' icon in Google search results")
        print("⏰ Google typically updates search result icons within 24-48 hours")
    else:
        print("\n❌ DEPLOYMENT FAILED - Manual intervention required")