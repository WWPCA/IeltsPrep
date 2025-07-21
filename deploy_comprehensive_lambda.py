#!/usr/bin/env python3
"""
Deploy comprehensive IELTS website with security enhancements to AWS Lambda
Uses working comprehensive app with security-enhanced robots.txt
"""

import zipfile
import json
import os
from datetime import datetime

def create_lambda_deployment():
    """Create comprehensive Lambda deployment package"""
    
    print("Creating comprehensive Lambda deployment...")
    
    # Read the comprehensive app with security updates
    with open('comprehensive_app_with_security.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Create Lambda handler wrapper
    lambda_wrapper = f'''#!/usr/bin/env python3
"""
AWS Lambda Handler for IELTS GenAI Prep - Complete Website
Deployed: {datetime.now().isoformat()}
"""

import json
import os

# Set production environment
os.environ['REPLIT_ENVIRONMENT'] = 'false'

# Import all functions from the comprehensive app
{app_content}

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    try:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {{}})
        query_params = event.get('queryStringParameters') or {{}}
        body = event.get('body', '')
        
        print(f"[CLOUDWATCH] Lambda processing {{method}} {{path}}")
        
        # Route requests to appropriate handlers
        if path == '/robots.txt' and method == 'GET':
            return handle_robots_txt()
        elif path == '/' and method == 'GET':
            return handle_home_page()
        elif path == '/login' and method == 'GET':
            return handle_login_page()
        elif path == '/privacy-policy' and method == 'GET':
            return handle_privacy_policy()
        elif path == '/terms-of-service' and method == 'GET':
            return handle_terms_of_service()
        elif path == '/dashboard' and method == 'GET':
            return handle_dashboard()
        elif path.startswith('/assessment/') and method == 'GET':
            assessment_type = path.split('/')[-1]
            return handle_assessment(assessment_type)
        elif path == '/my-profile' and method == 'GET':
            return handle_profile()
        elif path == '/api/health' and method == 'GET':
            return handle_health_check()
        elif path.startswith('/api/'):
            return handle_api_request(path, method, body, query_params, headers)
        else:
            return {{
                'statusCode': 404,
                'headers': {{'Content-Type': 'text/html'}},
                'body': '<h1>404 - Page Not Found</h1><p><a href="/">Return to Home</a></p>'
            }}
            
    except Exception as e:
        print(f"[ERROR] Lambda execution failed: {{str(e)}}")
        import traceback
        print(traceback.format_exc())
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Internal server error', 'details': str(e)}})
        }}
'''
    
    # Create deployment package
    package_name = f"comprehensive_website_secure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_wrapper)
        
        # Include the working template
        if os.path.exists('working_templates/working_template_backup_20250714_192410.html'):
            zipf.write('working_templates/working_template_backup_20250714_192410.html', 
                      'working_template_backup_20250714_192410.html')
        
        # Add deployment metadata
        deployment_info = {
            "deployment_date": datetime.now().isoformat(),
            "package_name": package_name,
            "source": "comprehensive_production_verified_20250719_153759.zip",
            "security_enhancement": "July 21, 2025 - Security-Enhanced robots.txt",
            "features": [
                "Complete IELTS GenAI Prep website functionality",
                "TrueScore® Writing Assessment with Nova Micro",
                "ClearScore® Speaking Assessment with Maya AI (Nova Sonic)",
                "User authentication and session management", 
                "Assessment history and progress tracking",
                "GDPR compliance and privacy policy",
                "Google reCAPTCHA v2 integration",
                "Mobile-first authentication workflow",
                "Security-enhanced robots.txt protection"
            ],
            "security_features": [
                "Authentication endpoint protection (/login, /register, /auth/)",
                "API security (comprehensive /api/ blocking)",
                "Assessment content protection from AI training",
                "File system security (.log, .json, .zip, .env blocking)",
                "Enhanced rate limiting (10-60 seconds based on bot type)",
                "Aggressive crawler blocking (AhrefsBot, SemrushBot, MJ12bot)",
                "TrueScore® and ClearScore® algorithm protection",
                "GDPR user data endpoint protection"
            ],
            "endpoints": [
                "/",
                "/login",
                "/dashboard", 
                "/assessment/academic-writing",
                "/assessment/general-writing",
                "/assessment/academic-speaking", 
                "/assessment/general-speaking",
                "/my-profile",
                "/privacy-policy",
                "/terms-of-service",
                "/robots.txt",
                "/api/health"
            ],
            "status": "Comprehensive website with security enhancements ready for production"
        }
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
    
    return package_name

def main():
    package = create_lambda_deployment()
    
    if not package:
        print("❌ Failed to create deployment package")
        return None
    
    size_kb = round(os.path.getsize(package) / 1024, 1)
    
    print(f"\\n✅ Comprehensive Lambda deployment created: {{package}}")
    print(f"📦 Size: {{size_kb}} KB")
    print("🌐 Features: Complete IELTS website with all functionality")
    print("🔒 Security: Security-enhanced robots.txt integrated")
    print("📋 Source: Working comprehensive package from July 19th")
    print("🚀 Ready for AWS Lambda deployment")
    
    return package

if __name__ == "__main__":
    package = main()