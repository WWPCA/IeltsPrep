#!/usr/bin/env python3
"""
Deploy working registration system to production
"""

import boto3
import json
import zipfile
import io

def create_production_lambda():
    """Create working production Lambda"""
    
    # Start with a working base from current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Get the registration template
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        reg_html = f.read()
    
    # Clean up the registration HTML (remove triple quotes that might cause issues)
    reg_html_clean = reg_html.replace('"""', '\\"\\"\\"').replace("'''", "\\'\\'\\'")
    
    # Create the production Lambda code
    production_code = f'''#!/usr/bin/env python3
"""
IELTS GenAI Prep Production Lambda with Mobile Registration
"""

import json
import base64
import hashlib
import hmac
import os
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import unquote, parse_qs
import urllib.request
import urllib.parse

# Include all the original functions from app.py
{app_content}

# Override the registration page handler for production
def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Mobile registration page - requires mobile app"""
    try:
        # Get user agent and origin
        user_agent = headers.get('User-Agent', '').lower()
        origin = headers.get('Origin', '')
        
        # Check if this is a mobile app request
        is_mobile_app = (
            'capacitor' in user_agent or 
            'ionic' in user_agent or
            'cordova' in user_agent or
            'ieltsaiprep' in user_agent or
            origin.startswith('capacitor://') or
            origin.startswith('ionic://') or
            headers.get('X-Capacitor-Platform') is not None
        )
        
        # Block web browser access
        if not is_mobile_app:
            return {{
                'statusCode': 403,
                'headers': {{'Content-Type': 'text/html'}},
                'body': '<h1>Access Restricted</h1><p>Registration requires mobile app and App Store purchase.</p><a href="/">Return Home</a>'
            }}
        
        # Return the registration page for mobile app
        registration_html = """{reg_html_clean}"""
        
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache',
                'X-Frame-Options': 'DENY'
            }},
            'body': registration_html
        }}
        
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'text/html'}},
            'body': f'<h1>Registration Error</h1><p>{{str(e)}}</p>'
        }}
'''
    
    return production_code

def deploy_lambda():
    """Deploy the Lambda function"""
    
    try:
        # Create the code
        lambda_code = create_production_lambda()
        
        # Create AWS Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create ZIP package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Deploy to Lambda
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Lambda deployed successfully")
        print(f"   Function: {response['FunctionName']}")
        print(f"   Size: {len(zip_data)} bytes")
        print(f"   Version: {response['Version']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

def test_deployment():
    """Test the deployed Lambda"""
    
    print("🔍 Testing deployment...")
    
    import requests
    
    # Test home page
    try:
        home_response = requests.get('https://www.ieltsaiprep.com/', timeout=10)
        print(f"   Home page: {home_response.status_code}")
    except Exception as e:
        print(f"   Home page: Error - {str(e)}")
    
    # Test registration endpoint (should be blocked for web)
    try:
        reg_response = requests.get('https://www.ieltsaiprep.com/mobile-registration', timeout=10)
        print(f"   Registration (web): {reg_response.status_code}")
    except Exception as e:
        print(f"   Registration (web): Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 Deploying working registration system...")
    
    success = deploy_lambda()
    
    if success:
        print("✅ PRODUCTION DEPLOYMENT COMPLETE")
        test_deployment()
        print("📱 Mobile registration system ready for App Store submission")
    else:
        print("❌ DEPLOYMENT FAILED")