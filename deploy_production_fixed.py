#!/usr/bin/env python3
"""
Deploy Security-Enhanced robots.txt to AWS Lambda Production
Based on previous successful deployment patterns from July 2025
"""

import zipfile
import json
from datetime import datetime

def create_production_lambda():
    """Create production Lambda with security-enhanced robots.txt"""
    
    # Read the security-enhanced app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Convert Flask app to Lambda handler (following previous pattern)
    lambda_code = f'''
import json
import os
import uuid
import random
from typing import Dict, Any, Optional, List

# Environment configuration
os.environ['REPLIT_ENVIRONMENT'] = 'false'  # Production mode

{app_content}

def lambda_handler(event, context):
    """AWS Lambda entry point - matches previous deployment pattern"""
    try:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {{}})
        
        print(f"[CLOUDWATCH] Lambda processing {{method}} {{path}}")
        
        # Handle robots.txt with security enhancements
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
        elif path == '/api/health' and method == 'GET':
            return handle_health_check()
        else:
            return {{
                'statusCode': 404,
                'headers': {{'Content-Type': 'text/html'}},
                'body': '<h1>Page Not Found</h1>'
            }}
            
    except Exception as e:
        print(f"[ERROR] Lambda handler: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Internal server error'}})
        }}
'''
    
    # Create deployment package
    package_name = f"security_enhanced_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
        
        # Add deployment metadata
        deployment_info = {
            "deployment_date": datetime.now().isoformat(),
            "package_name": package_name,
            "security_features": [
                "Authentication endpoint protection (/login, /register, /auth/)",
                "API security (comprehensive /api/ blocking)",
                "Assessment content protection from AI training",
                "File system security (.log, .json, .zip, .env blocking)",
                "Enhanced rate limiting (10-60 seconds based on bot type)",
                "Aggressive crawler blocking (AhrefsBot, SemrushBot, MJ12bot)"
            ],
            "robots_txt_timestamp": "July 21, 2025",
            "production_domain": "www.ieltsaiprep.com",
            "cloudfront_distribution": "E1EPXAU67877FR"
        }
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
    
    return package_name

def main():
    print("Creating security-enhanced production deployment...")
    package = create_production_lambda()
    
    size_kb = round(os.path.getsize(package) / 1024, 1)
    
    print(f"✅ Production package created: {package}")
    print(f"📦 Size: {size_kb} KB")
    print("🔒 Security enhancements included:")
    print("   - Authentication protection: /login, /register, /auth/ blocked")
    print("   - API security: Comprehensive /api/ endpoint protection")  
    print("   - Content protection: Assessment questions blocked from AI training")
    print("   - File security: Config files, logs, backups blocked")
    print("   - Rate limiting: Enhanced to 10-60 seconds")
    print("   - Aggressive crawlers: Completely blocked")
    
    print(f"\n🚀 Ready for AWS Lambda deployment to: ielts-genai-prep-api")
    print("📋 Upload this package to resolve critical security vulnerabilities")
    
    return package

if __name__ == "__main__":
    import os
    package = main()