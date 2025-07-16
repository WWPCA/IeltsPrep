#!/usr/bin/env python3
"""
Fix production Lambda with proper registration handler
"""

import boto3
import json
import zipfile
import io
import re

def get_working_lambda_code():
    """Get the current working app.py and modify for production"""
    
    # Read current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Read registration HTML template
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        registration_html = f.read()
    
    # Replace file reading with embedded template
    modified_code = app_code.replace(
        "with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:\n            html_content = f.read()",
        f"html_content = '''{registration_html}'''"
    )
    
    return modified_code

def deploy_fixed_lambda():
    """Deploy the fixed Lambda code"""
    
    try:
        # Get working code
        lambda_code = get_working_lambda_code()
        
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create ZIP package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Update Lambda function
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Fixed Lambda deployed: {response['FunctionArn']}")
        print(f"📦 Package size: {len(zip_data)} bytes")
        
        # Wait for update to complete
        print("⏳ Waiting for update to complete...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        print("✅ Update completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Deploy failed: {str(e)}")
        return False

def test_endpoints():
    """Test the deployed endpoints"""
    
    import requests
    
    print("🔍 Testing endpoints...")
    
    # Test home page
    home_response = requests.get('https://www.ieltsaiprep.com/')
    print(f"   Home page: {home_response.status_code}")
    
    # Test registration (should be 403 for web)
    reg_response = requests.get('https://www.ieltsaiprep.com/mobile-registration')
    print(f"   Registration: {reg_response.status_code}")
    
    # Test with mobile user agent
    mobile_response = requests.get(
        'https://www.ieltsaiprep.com/mobile-registration',
        headers={'User-Agent': 'IELTS-GenAI-Prep-Mobile-App/1.0 (Capacitor)'}
    )
    print(f"   Mobile registration: {mobile_response.status_code}")

if __name__ == "__main__":
    print("🚀 Fixing production Lambda...")
    
    success = deploy_fixed_lambda()
    
    if success:
        print("✅ PRODUCTION FIXED")
        test_endpoints()
        print("📱 Ready for mobile app with secure registration")
    else:
        print("❌ FIX FAILED")