#!/usr/bin/env python3
"""
Fix mobile alignment for academic writing assessment sample badge
Deploy corrected template to production
"""

import json
import zipfile
import os
from datetime import datetime

def create_fixed_lambda_deployment():
    """Create Lambda deployment with fixed mobile alignment"""
    
    # Read the corrected template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        corrected_template = f.read()
    
    # Create the Lambda function code with embedded template
    lambda_code = f'''#!/usr/bin/env python3
"""
AWS Lambda Handler for IELTS GenAI Prep - Mobile Alignment Fixed
Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import json
import os
import uuid
import time
import base64
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {{}}).get('http', {{}}).get('method', 'GET'))
        
        # Route requests
        if path == '/' and method == 'GET':
            return handle_home_page()
        elif path == '/login' and method == 'GET':
            return handle_login_page()
        elif path == '/dashboard' and method == 'GET':
            return handle_dashboard_page(event.get('headers', {{}}))
        elif path == '/privacy-policy' and method == 'GET':
            return handle_privacy_policy()
        elif path == '/terms-of-service' and method == 'GET':
            return handle_terms_of_service()
        elif path == '/api/login' and method == 'POST':
            return handle_user_login(json.loads(event.get('body', '{{}}')))
        else:
            return {{
                'statusCode': 404,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'error': 'Endpoint not found'}})
            }}
            
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': f'Internal server error: {{str(e)}}'}})
        }}

def handle_home_page() -> Dict[str, Any]:
    """Handle home page with fixed mobile alignment"""
    
    template = """{corrected_template}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }},
        'body': template
    }}

def handle_login_page() -> Dict[str, Any]:
    """Handle login page"""
    login_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header text-center">
                        <h3>Login to IELTS GenAI Prep</h3>
                    </div>
                    <div class="card-body">
                        <form action="/api/login" method="POST">
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        }},
        'body': login_template
    }}

def handle_dashboard_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle dashboard page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>Dashboard - Coming Soon</h1>'
    }}

def handle_privacy_policy() -> Dict[str, Any]:
    """Handle privacy policy page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>Privacy Policy - Coming Soon</h1>'
    }}

def handle_terms_of_service() -> Dict[str, Any]:
    """Handle terms of service page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>Terms of Service - Coming Soon</h1>'
    }}

def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'application/json'}},
        'body': json.dumps({{'success': True, 'message': 'Login successful'}})
    }}
'''
    
    # Create deployment package
    lambda_filename = 'mobile-alignment-fixed-lambda.py'
    
    # Write the Lambda function
    with open(lambda_filename, 'w', encoding='utf-8') as f:
        f.write(lambda_code)
    
    # Create ZIP package
    zip_filename = 'mobile-alignment-fixed.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(lambda_filename, 'lambda_function.py')
    
    # Clean up
    os.remove(lambda_filename)
    
    return zip_filename

def deploy_to_aws_lambda():
    """Deploy the fixed Lambda function to AWS"""
    
    # Create deployment package
    zip_file = create_fixed_lambda_deployment()
    
    print("=== Mobile Alignment Fix - Lambda Deployment ===")
    print()
    print("📱 Issue Fixed:")
    print("   Academic writing assessment sample badge now properly centered in mobile view")
    print("   Added d-flex justify-content-center classes for better mobile alignment")
    print()
    print("📦 Deployment Package Created:")
    print(f"   File: {zip_file}")
    print("   Contains: Lambda function with corrected mobile template")
    print()
    print("🚀 AWS Lambda Deployment Commands:")
    print("   1. aws lambda update-function-code \\")
    print("        --function-name ielts-genai-prep-prod \\")
    print(f"        --zip-file fileb://{zip_file}")
    print()
    print("   2. Test the deployment:")
    print("      curl -X GET https://your-api-gateway-url/prod/")
    print()
    print("✅ Expected Result:")
    print("   The academic writing assessment sample badge should now be properly")
    print("   centered in mobile view without alignment issues")
    print()
    print("🔧 Changes Made:")
    print("   • Added d-flex justify-content-center to badge container")
    print("   • Added display: inline-block and text-align: center to badge")
    print("   • Improved mobile responsiveness for the assessment sample section")
    
    return zip_file

def main():
    """Main deployment function"""
    zip_file = deploy_to_aws_lambda()
    
    print()
    print("📋 Next Steps:")
    print("1. Upload the deployment package to AWS Lambda")
    print("2. Test the mobile alignment on www.ieltsaiprep.com")
    print("3. Verify the badge is properly centered in mobile view")
    print()
    print("💡 Note: This fix ensures consistent mobile user experience")
    print("   across all devices and screen sizes.")

if __name__ == "__main__":
    main()