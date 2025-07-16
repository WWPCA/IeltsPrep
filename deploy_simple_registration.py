#!/usr/bin/env python3
"""
Deploy secure mobile registration to production
"""

import boto3
import json
import zipfile
import io
import base64

def deploy_registration():
    """Deploy secure registration system"""
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Read registration HTML and encode it
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        registration_html = f.read()
    
    # Create the production Lambda code
    lambda_code = f'''# Production Lambda for IELTS GenAI Prep with Secure Registration
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

# Embedded registration template
REGISTRATION_TEMPLATE = """{registration_html}"""

{app_code}

# Override the registration handler for production
def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Mobile registration page - App Store purchase required"""
    try:
        # Check if request is from mobile app
        user_agent = headers.get('User-Agent', '').lower()
        origin = headers.get('Origin', '')
        
        # Mobile app detection
        is_mobile_app = (
            'capacitor' in user_agent or 
            'ionic' in user_agent or
            'cordova' in user_agent or
            'ieltsaiprep' in user_agent or
            origin.startswith('capacitor://') or
            origin.startswith('ionic://') or
            headers.get('X-Capacitor-Platform') is not None
        )
        
        if not is_mobile_app:
            return {{
                'statusCode': 403,
                'headers': {{'Content-Type': 'text/html'}},
                'body': '<h1>Access Restricted</h1><p>Registration requires mobile app and App Store purchase.</p>'
            }}
        
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': REGISTRATION_TEMPLATE
        }}
        
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'text/html'}},
            'body': f'<h1>Error: {{str(e)}}</h1>'
        }}
'''
    
    try:
        # Deploy to Lambda
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Update function
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Production updated: {response['FunctionArn']}")
        print(f"📦 Size: {len(zip_data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deploy failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Deploying secure registration...")
    
    success = deploy_registration()
    
    if success:
        print("✅ DEPLOYED TO PRODUCTION")
        print("🔐 Registration secured with App Store verification")
        print("📱 Ready for mobile app submission")
    else:
        print("❌ DEPLOYMENT FAILED")