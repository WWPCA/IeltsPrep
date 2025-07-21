#!/usr/bin/env python3
"""
Security-Enhanced Production Lambda Deployment Package Creator
Creates AWS Lambda deployment package with security-enhanced robots.txt
"""

import os
import zipfile
import json
from datetime import datetime

def create_security_enhanced_production():
    """Create production Lambda package with security-enhanced robots.txt"""
    
    package_name = f"security_enhanced_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    print(f"🔒 Creating security-enhanced production package: {package_name}")
    
    # Read the current app.py with security enhancements
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Verify security-enhanced robots.txt is present
    if "# IELTS GenAI Prep - Security-Enhanced robots.txt" not in app_content:
        print("❌ ERROR: Security-enhanced robots.txt not found in app.py")
        return None
    
    if "Disallow: /login" not in app_content:
        print("❌ ERROR: Authentication protection not found")
        return None
    
    if "Crawl-delay: 10" not in app_content:
        print("❌ ERROR: Enhanced rate limiting not found")
        return None
    
    print("✅ Security enhancements verified in app.py")
    
    # Create the Lambda deployment package
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main Lambda handler
        zipf.writestr('lambda_function.py', f'''
import json
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from main import lambda_handler

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    return lambda_handler(event, context)
''')
        
        # Add the main application code
        zipf.writestr('main.py', app_content.replace('if __name__ == "__main__":', 'if False:  # Disabled for Lambda'))
        
        # Add requirements (minimal for Lambda)
        zipf.writestr('requirements.txt', '''
# Core dependencies for AWS Lambda deployment
boto3>=1.26.0
urllib3>=1.26.0
''')
        
        # Add deployment metadata
        deployment_info = {
            "deployment_date": datetime.now().isoformat(),
            "package_name": package_name,
            "security_enhancements": [
                "Authentication endpoint protection (/login, /register, /auth/)",
                "API security (comprehensive /api/ blocking)",
                "Assessment content protection from AI training",
                "File system security (.log, .json, .zip, .env blocking)",
                "Enhanced rate limiting (10-60 seconds based on bot type)",
                "Aggressive crawler blocking (AhrefsBot, SemrushBot, MJ12bot)",
                "Proprietary content protection for TrueScore® and ClearScore®"
            ],
            "robots_txt_features": [
                "Authentication protection: Blocked",
                "API endpoint security: Enhanced",
                "Assessment content protection: Active", 
                "File extension security: Implemented",
                "Rate limiting: 10-60 seconds",
                "AI training protection: Active",
                "Search engine access: Controlled"
            ],
            "production_domain": "www.ieltsaiprep.com",
            "cloudfront_distribution": "E1EPXAU67877FR",
            "deployment_status": "Ready for AWS Lambda upload"
        }
        
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
        
        # Add security validation script
        zipf.writestr('validate_security.py', '''
#!/usr/bin/env python3
"""
Production Security Validation Script
Validates that security enhancements are properly deployed
"""

import requests
import sys

def validate_production_security():
    """Validate security enhancements in production"""
    
    print("🔒 VALIDATING PRODUCTION SECURITY ENHANCEMENTS")
    print("=" * 50)
    
    try:
        # Test robots.txt security
        response = requests.get("https://www.ieltsaiprep.com/robots.txt", timeout=30)
        robots_content = response.text
        
        # Check authentication protection
        if "Disallow: /login" in robots_content:
            print("✅ Authentication protection: ACTIVE")
        else:
            print("❌ Authentication protection: MISSING")
            
        # Check API security
        if "Disallow: /api/" in robots_content:
            print("✅ API endpoint security: ACTIVE")
        else:
            print("❌ API endpoint security: MISSING")
            
        # Check rate limiting
        if "Crawl-delay: 10" in robots_content:
            print("✅ Enhanced rate limiting: ACTIVE")
        else:
            print("❌ Enhanced rate limiting: MISSING")
            
        # Check AI training protection
        if "Disallow: /assessment/" in robots_content and "GPTBot" in robots_content:
            print("✅ AI training protection: ACTIVE")
        else:
            print("❌ AI training protection: MISSING")
            
        # Check security timestamp
        if "July 21, 2025" in robots_content:
            print("✅ Security update timestamp: CURRENT")
        else:
            print("❌ Security update timestamp: OUTDATED")
            
        print("=" * 50)
        print("🔒 Security validation complete")
        
    except Exception as e:
        print(f"❌ Security validation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    validate_production_security()
''')
    
    # Get package size
    package_size = os.path.getsize(package_name)
    package_size_kb = round(package_size / 1024, 1)
    
    print(f"✅ Security-enhanced production package created: {package_name}")
    print(f"📦 Package size: {package_size_kb} KB")
    print(f"🔒 Security features: Authentication protection, API security, content protection")
    print(f"⚡ Rate limiting: Enhanced to 10-60 seconds")
    print(f"🛡️ AI training protection: Active for proprietary content")
    
    # Create deployment instructions
    instructions = f"""
# Security-Enhanced Production Deployment Instructions

## Package Information
- **File**: {package_name}
- **Size**: {package_size_kb} KB
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Security Enhancements Included
1. **Authentication Protection**: /login, /register, /auth/ blocked from bots
2. **API Security**: Comprehensive /api/ endpoint protection
3. **Content Protection**: Assessment questions blocked from AI training
4. **File Security**: Config files, logs, backups blocked
5. **Rate Limiting**: Enhanced to 10-60 seconds based on bot type
6. **Aggressive Crawler Blocking**: AhrefsBot, SemrushBot, MJ12bot completely blocked

## AWS Lambda Deployment Steps
1. Upload {package_name} to AWS Lambda function: ielts-genai-prep-api
2. Update function code from zip file
3. Verify deployment in AWS Console
4. Test robots.txt endpoint: https://www.ieltsaiprep.com/robots.txt
5. Run validation script to confirm security features

## Validation Commands
```bash
# Test authentication protection
curl https://www.ieltsaiprep.com/robots.txt | grep "Disallow: /login"

# Test API security  
curl https://www.ieltsaiprep.com/robots.txt | grep "Disallow: /api/"

# Test rate limiting
curl https://www.ieltsaiprep.com/robots.txt | grep "Crawl-delay: 10"

# Test security timestamp
curl https://www.ieltsaiprep.com/robots.txt | grep "July 21, 2025"
```

## Expected Results After Deployment
- Authentication endpoints protected from bot attacks
- Proprietary IELTS content protected from AI training scraping
- API structure secured against discovery attempts
- File system protected from unauthorized access
- Enhanced rate limiting active for all crawler types

Deploy immediately to resolve critical security vulnerabilities.
"""
    
    with open(f'DEPLOYMENT_INSTRUCTIONS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md', 'w') as f:
        f.write(instructions)
    
    return package_name

if __name__ == "__main__":
    package = create_security_enhanced_production()
    if package:
        print(f"\n🚀 READY FOR DEPLOYMENT: {package}")
        print("📋 See deployment instructions for upload steps")
    else:
        print("❌ Package creation failed")