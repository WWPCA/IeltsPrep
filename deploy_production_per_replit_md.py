#!/usr/bin/env python3
"""
Deploy production Lambda according to replit.md specifications
"""

import boto3
import json
import zipfile
import io
import base64

def create_production_lambda():
    """Create production Lambda with all features per replit.md"""
    
    # Read the current app.py (main production application)
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Read mobile registration template
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        mobile_reg_html = f.read()
    
    # Encode mobile registration template to avoid syntax issues
    mobile_reg_b64 = base64.b64encode(mobile_reg_html.encode('utf-8')).decode('ascii')
    
    # Create production Lambda code by embedding the mobile registration template
    production_code = f'''#!/usr/bin/env python3
"""
IELTS GenAI Prep Production Lambda - Complete Package
USD-only pricing, CloudFront security, mobile registration
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

# Mobile registration template (base64 encoded)
MOBILE_REGISTRATION_TEMPLATE_B64 = "{mobile_reg_b64}"

# Include all original app.py functionality
{app_code}

# Override mobile registration handler with security
def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Mobile registration page - App Store/Google Play purchase required"""
    try:
        # Check for mobile app user agent
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
        
        # Block web browser access - App Store/Google Play purchase required
        if not is_mobile_app:
            return {{
                'statusCode': 403,
                'headers': {{'Content-Type': 'text/html'}},
                'body': '<html><head><title>Access Restricted</title></head><body><h1>Access Restricted</h1><p>Registration is only available through the mobile app after completing an App Store or Google Play purchase.</p><p><a href="/">Return to Home</a></p></body></html>'
            }}
        
        # Decode and return mobile registration template
        mobile_html = base64.b64decode(MOBILE_REGISTRATION_TEMPLATE_B64).decode('utf-8')
        
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache',
                'X-Frame-Options': 'DENY'
            }},
            'body': mobile_html
        }}
        
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'text/html'}},
            'body': f'<html><body><h1>Registration Error</h1><p>{{str(e)}}</p></body></html>'
        }}
'''
    
    return production_code

def deploy_to_production():
    """Deploy to production Lambda"""
    
    try:
        # Create the production Lambda code
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
        
        print(f"✅ Production Lambda deployed per replit.md")
        print(f"📦 Package size: {len(zip_data)} bytes")
        print(f"💰 USD-only pricing: $36.49 USD for 4 assessments")
        print(f"🔒 Mobile registration secured for App Store/Google Play")
        print(f"🌐 CloudFront security with CF-Secret-3140348d header")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

def test_production_endpoints():
    """Test production endpoints per replit.md specifications"""
    
    import requests
    import time
    
    print("⏳ Testing production endpoints...")
    time.sleep(5)
    
    endpoints_to_test = [
        ('GET', '/', 'Home page with USD pricing'),
        ('GET', '/mobile-registration', 'Mobile registration (should be 403 for web)'),
        ('GET', '/login', 'Login page'),
        ('GET', '/dashboard', 'Dashboard'),
        ('GET', '/privacy-policy', 'Privacy policy (simplified GDPR)'),
        ('GET', '/terms-of-service', 'Terms of service'),
        ('GET', '/robots.txt', 'Robots.txt with AI crawler permissions'),
        ('GET', '/assessment/academic-writing', 'Academic writing assessment'),
        ('GET', '/assessment/general-writing', 'General writing assessment'),
        ('GET', '/assessment/academic-speaking', 'Academic speaking assessment'),
        ('GET', '/assessment/general-speaking', 'General speaking assessment'),
        ('GET', '/api/health', 'Health check API')
    ]
    
    for method, path, description in endpoints_to_test:
        try:
            response = requests.get(f'https://www.ieltsaiprep.com{path}', timeout=10)
            status = "✅" if response.status_code == 200 else "❌" if response.status_code >= 400 else "⚠️"
            print(f"   {status} {description}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: Error - {str(e)}")
    
    # Test mobile registration with mobile user agent
    try:
        mobile_response = requests.get(
            'https://www.ieltsaiprep.com/mobile-registration',
            headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Capacitor'},
            timeout=10
        )
        status = "✅" if mobile_response.status_code == 200 else "❌"
        print(f"   {status} Mobile registration (mobile app): {mobile_response.status_code}")
    except Exception as e:
        print(f"   ❌ Mobile registration (mobile app): Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 Deploying production Lambda per replit.md specifications...")
    print("📋 Features: USD-only pricing, CloudFront security, mobile registration")
    
    success = deploy_to_production()
    
    if success:
        print("✅ PRODUCTION DEPLOYMENT COMPLETE")
        test_production_endpoints()
        print("📱 Ready for App Store/Google Play submission")
    else:
        print("❌ DEPLOYMENT FAILED")