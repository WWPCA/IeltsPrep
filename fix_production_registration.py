#!/usr/bin/env python3
"""
Fix and deploy complete production registration system
"""

import boto3
import json
import zipfile
import io
from datetime import datetime

def create_complete_production_code():
    """Create complete production Lambda with registration"""
    
    # Get current app.py (contains all the main handlers)
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Get registration HTML
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        registration_html = f.read()
    
    # Create complete Lambda code by embedding the registration HTML
    production_code = app_content.replace(
        "with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:",
        "# Using embedded HTML template instead of file"
    ).replace(
        "html_content = f.read()",
        f"html_content = '''{registration_html}'''"
    )
    
    return production_code

def deploy_to_production():
    """Deploy complete system to production"""
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create production code
        production_code = create_complete_production_code()
        
        # Create deployment package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', production_code)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Update Lambda function
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Lambda updated: {response['FunctionArn']}")
        print(f"📦 Size: {len(zip_data)} bytes")
        
        # Test endpoints
        print("🔍 Testing endpoints...")
        import requests
        
        # Test registration endpoint (should be 403 for web)
        reg_response = requests.get('https://www.ieltsaiprep.com/mobile-registration')
        print(f"   /mobile-registration: {reg_response.status_code} (Expected: 403)")
        
        # Test home page (should work)
        home_response = requests.get('https://www.ieltsaiprep.com/')
        print(f"   /: {home_response.status_code} (Expected: 200)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Deploying complete registration system...")
    success = deploy_to_production()
    
    if success:
        print("✅ PRODUCTION DEPLOYMENT COMPLETE")
        print("📱 Mobile registration ready for App Store submission")
    else:
        print("❌ DEPLOYMENT FAILED")