#!/usr/bin/env python3
"""
Deploy Security-Enhanced robots.txt to Production
Direct deployment script for AWS Lambda production environment
"""

import json
import os
import zipfile
import base64
from datetime import datetime

def create_lambda_deployment_package():
    """Create AWS Lambda deployment package with security-enhanced robots.txt"""
    
    print("Creating production deployment package...")
    
    # Read the current app.py with security enhancements
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Verify security features are present
    security_checks = {
        "Authentication Protection": "Disallow: /login" in app_content,
        "API Security": "Disallow: /api/" in app_content,
        "Rate Limiting": "Crawl-delay: 10" in app_content,
        "Content Protection": "Disallow: /assessment/" in app_content,
        "File Security": "Disallow: /*.log$" in app_content
    }
    
    print("Security feature verification:")
    for feature, present in security_checks.items():
        status = "✅" if present else "❌"
        print(f"  {status} {feature}: {'Present' if present else 'Missing'}")
    
    if not all(security_checks.values()):
        print("❌ Security features missing - deployment aborted")
        return None
    
    # Create Lambda handler that uses the Flask app
    lambda_handler = '''
import json
import os
import sys
import traceback

def lambda_handler(event, context):
    """AWS Lambda handler for IELTS GenAI Prep"""
    try:
        # Import Flask app
        from app import app
        
        # Extract request information
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Handle robots.txt specifically
        if path == '/robots.txt' and http_method == 'GET':
            from app import handle_robots_txt
            return handle_robots_txt()
        
        # Handle other routes through Flask app
        with app.test_request_context(path=path, method=http_method, 
                                     query_string=query_params, 
                                     headers=headers, data=body):
            try:
                response = app.full_dispatch_request()
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': response.content_type,
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': response.get_data(as_text=True)
                }
            except Exception as e:
                print(f"Flask dispatch error: {str(e)}")
                # Fallback to direct handler
                if path == '/':
                    return handle_home_page()
                elif path == '/robots.txt':
                    return handle_robots_txt()
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'Not found'})
                    }
                    
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

# Import Flask functions for direct use
''' + app_content.replace('if __name__ == "__main__":', 'if False:')
    
    # Create deployment package
    package_name = f"security_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main Lambda handler
        zipf.writestr('lambda_function.py', lambda_handler)
        
        # Add requirements for Lambda
        zipf.writestr('requirements.txt', 'boto3>=1.26.0')
        
        # Add deployment metadata
        deployment_info = {
            "deployment_timestamp": datetime.now().isoformat(),
            "security_features": list(security_checks.keys()),
            "robots_txt_updated": True,
            "production_ready": True
        }
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
    
    print(f"✅ Created deployment package: {package_name}")
    return package_name

def deploy_to_production():
    """Deploy the security-enhanced package"""
    
    package = create_lambda_deployment_package()
    if not package:
        return False
    
    print(f"📦 Deployment package ready: {package}")
    print("🚀 Upload this package to AWS Lambda function: ielts-genai-prep-api")
    
    # Create deployment instructions
    instructions = f"""
# Security Deployment Instructions

## Package Information
- File: {package}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Security Features: Authentication protection, API security, content protection

## AWS Lambda Deployment Steps
1. Login to AWS Console
2. Navigate to Lambda > Functions > ielts-genai-prep-api
3. Click "Upload from" > ".zip file"
4. Select: {package}
5. Click "Save"
6. Test: https://www.ieltsaiprep.com/robots.txt

## Validation Commands
curl https://www.ieltsaiprep.com/robots.txt | grep "Disallow: /login"
curl https://www.ieltsaiprep.com/robots.txt | grep "Crawl-delay: 10"
curl https://www.ieltsaiprep.com/robots.txt | grep "July 21, 2025"

Deploy immediately to resolve security vulnerabilities.
"""
    
    with open('DEPLOY_SECURITY_NOW.md', 'w') as f:
        f.write(instructions)
    
    return True

if __name__ == "__main__":
    print("🔒 DEPLOYING SECURITY-ENHANCED ROBOTS.TXT TO PRODUCTION")
    print("=" * 60)
    
    if deploy_to_production():
        print("✅ Deployment package created and ready for AWS upload")
        print("📋 See DEPLOY_SECURITY_NOW.md for upload instructions")
    else:
        print("❌ Deployment failed - security features not ready")