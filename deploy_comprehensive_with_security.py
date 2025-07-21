#!/usr/bin/env python3
"""
Deploy comprehensive IELTS website with security-enhanced robots.txt
Uses working templates from July 19th comprehensive package
"""

import zipfile
import json
from datetime import datetime

def create_comprehensive_secure_deployment():
    """Create deployment using working comprehensive package + security"""
    
    print("Creating comprehensive deployment with security enhancements...")
    
    # Read the comprehensive app.py from extracted package
    with open('working_templates/app.py', 'r', encoding='utf-8') as f:
        comprehensive_app = f.read()
    
    # Read the current app.py with security-enhanced robots.txt
    with open('app.py', 'r', encoding='utf-8') as f:
        current_app = f.read()
    
    # Extract security-enhanced robots.txt from current app
    start_marker = '# IELTS GenAI Prep - Security-Enhanced robots.txt'
    end_marker = 'Crawl-delay: 2"""'
    
    if start_marker in current_app and end_marker in current_app:
        start_idx = current_app.find(start_marker)
        end_idx = current_app.find(end_marker) + len(end_marker)
        security_robots = current_app[start_idx:end_idx]
        print("✅ Security-enhanced robots.txt extracted")
    else:
        print("❌ Security-enhanced robots.txt not found")
        return None
    
    # Replace the robots.txt in comprehensive app with security-enhanced version
    # Find the old robots.txt in comprehensive app
    old_robots_start = comprehensive_app.find('User-agent: *')
    if old_robots_start > 0:
        # Find the end of the robots.txt (look for the triple quotes)
        search_start = old_robots_start
        old_robots_end = comprehensive_app.find('"""', search_start)
        if old_robots_end > 0:
            # Replace the old robots.txt with security-enhanced version
            new_comprehensive_app = (
                comprehensive_app[:old_robots_start] + 
                security_robots + 
                comprehensive_app[old_robots_end + 3:]
            )
            print("✅ Security-enhanced robots.txt integrated into comprehensive app")
        else:
            print("❌ Could not find end of robots.txt in comprehensive app")
            return None
    else:
        print("❌ Could not find robots.txt in comprehensive app")
        return None
    
    # Convert to Lambda deployment format
    lambda_code = f'''
import json
import os
import uuid
import random
from typing import Dict, Any, Optional, List

# Environment configuration for production
os.environ['REPLIT_ENVIRONMENT'] = 'false'

{new_comprehensive_app}

def lambda_handler(event, context):
    """AWS Lambda entry point for comprehensive IELTS website"""
    try:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {{}})
        query_params = event.get('queryStringParameters') or {{}}
        body = event.get('body', '')
        
        print(f"[CLOUDWATCH] Lambda processing {{method}} {{path}}")
        
        # Call the Flask app handlers directly
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
            # Handle other API endpoints
            return handle_api_request(path, method, body, query_params)
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
    package_name = f"comprehensive_secure_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
        
        # Add deployment metadata
        deployment_info = {
            "deployment_date": datetime.now().isoformat(),
            "package_name": package_name,
            "source": "comprehensive_production_verified_20250719_153759.zip",
            "security_enhancement": "July 21, 2025 robots.txt protection",
            "features": [
                "Complete IELTS GenAI Prep website functionality",
                "TrueScore® Writing Assessment with Nova Micro",
                "ClearScore® Speaking Assessment with Maya AI (Nova Sonic)",
                "User authentication and session management",
                "Assessment history and progress tracking",
                "GDPR compliance and privacy policy",
                "Google reCAPTCHA v2 integration",
                "Mobile-first authentication workflow"
            ],
            "security_features": [
                "Authentication endpoint protection (/login, /register, /auth/)",
                "API security (comprehensive /api/ blocking)",
                "Assessment content protection from AI training",
                "File system security (.log, .json, .zip, .env blocking)",
                "Enhanced rate limiting (10-60 seconds based on bot type)",
                "Aggressive crawler blocking (AhrefsBot, SemrushBot, MJ12bot)"
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
            "status": "Comprehensive website with security enhancements"
        }
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
    
    return package_name

def main():
    package = create_comprehensive_secure_deployment()
    
    if not package:
        print("❌ Failed to create deployment package")
        return None
    
    size_kb = round(os.path.getsize(package) / 1024, 1)
    
    print(f"\\n✅ Comprehensive secure deployment created: {package}")
    print(f"📦 Size: {size_kb} KB")
    print("🌐 Features: Complete IELTS website with all functionality")
    print("🔒 Security: Security-enhanced robots.txt integrated")
    print("📋 Source: Working comprehensive package from July 19th")
    
    return package

if __name__ == "__main__":
    import os
    package = main()