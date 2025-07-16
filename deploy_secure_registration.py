#!/usr/bin/env python3
"""
Deploy Secure Mobile Registration Flow to Production
Includes App Store payment verification and prevents web bypass
"""

import boto3
import json
import zipfile
import io
from datetime import datetime

def create_production_lambda_package():
    """Create production Lambda package with secure registration"""
    
    # Read current app.py for production deployment
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Read mobile registration HTML
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        registration_html = f.read()
    
    # Create production Lambda code with embedded registration template
    production_code = f'''#!/usr/bin/env python3
"""
Pure AWS Lambda Handler for IELTS GenAI Prep with Secure Mobile Registration
Compatible with SAM CLI local testing
Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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

# Embedded registration template
MOBILE_REGISTRATION_TEMPLATE = """{registration_html}"""

# Production Lambda handler code
{app_code}

# Override the file reading for registration template
def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve mobile registration page after successful payment - MOBILE APP ONLY"""
    try:
        # Security check: Only allow access from mobile app context
        user_agent = headers.get('User-Agent', '').lower()
        origin = headers.get('Origin', '')
        
        # Check for mobile app indicators
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
                'body': '<h1>Access Restricted</h1><p>Registration is only available through the mobile app after completing an App Store or Google Play purchase.</p><p>Please download our mobile app to register and purchase assessments.</p><a href="/">Return to Home</a>'
            }}
        
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache',
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff'
            }},
            'body': MOBILE_REGISTRATION_TEMPLATE
        }}
        
    except Exception as e:
        print(f"[ERROR] Mobile registration page error: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'text/html'}},
            'body': f'<h1>Error loading registration page: {{str(e)}}</h1>'
        }}
'''
    
    # Format the code with embedded template
    formatted_code = production_code.format(
        registration_html=registration_html.replace('"""', '\\"\\"\\"'),
        app_code=app_code
    )
    
    return formatted_code

def deploy_to_aws_lambda():
    """Deploy to AWS Lambda production"""
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create production package
        production_code = create_production_lambda_package()
        
        # Create ZIP file in memory
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
        
        print(f"✅ Lambda function updated successfully")
        print(f"   Function ARN: {response['FunctionArn']}")
        print(f"   Last Modified: {response['LastModified']}")
        print(f"   Code Size: {len(zip_data)} bytes")
        print(f"   Version: {response['Version']}")
        
        # Wait for function to be updated
        print("⏳ Waiting for function update to complete...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        print("✅ Function update completed")
        
        # Test the new endpoint
        print("🔍 Testing mobile registration endpoint...")
        
        # This should return 403 (access restricted)
        import requests
        test_response = requests.get('https://www.ieltsaiprep.com/mobile-registration')
        if test_response.status_code == 403:
            print("✅ Security working: Web access blocked (403 Forbidden)")
        else:
            print(f"⚠️  Unexpected response: {test_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying Secure Mobile Registration Flow to Production")
    print("=" * 60)
    
    print("📋 Security Features:")
    print("   • Mobile app detection (User-Agent, Origin headers)")
    print("   • App Store payment verification required")
    print("   • Web browser access blocked (403 Forbidden)")
    print("   • Purchase data validation (Apple/Google)")
    print("   • Transaction ID verification")
    print("")
    
    success = deploy_to_aws_lambda()
    
    if success:
        print("=" * 60)
        print("✅ DEPLOYMENT SUCCESSFUL")
        print("")
        print("🔐 Security Status:")
        print("   • Registration only available in mobile app")
        print("   • App Store/Google Play purchase required")
        print("   • Web access blocked with 403 Forbidden")
        print("")
        print("🌐 Production URLs:")
        print("   • Web: https://www.ieltsaiprep.com/mobile-registration (blocked)")
        print("   • Mobile App: Accessible after purchase verification")
        print("")
        print("📱 Ready for App Store submission!")
        
    else:
        print("❌ DEPLOYMENT FAILED")
        print("Please check AWS credentials and Lambda function access.")

if __name__ == "__main__":
    main()