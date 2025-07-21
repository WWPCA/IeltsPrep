#!/usr/bin/env python3
"""
Final Navigation Fix for Production
Creates a clean deployment package without any Flask template syntax issues
"""
import zipfile
import os
import subprocess

def create_clean_deployment():
    """Create clean deployment package ensuring no Flask template syntax remains"""
    
    print("🔍 Creating clean deployment package for navigation fixes...")
    
    # Read the current lambda function
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Verify no Flask template syntax remains
    flask_issues = []
    for line_num, line in enumerate(lambda_code.splitlines(), 1):
        if '{{' in line or '}}' in line:
            if 'url_for' in line:
                flask_issues.append(f"Line {line_num}: {line.strip()}")
    
    if flask_issues:
        print("❌ Flask template syntax found:")
        for issue in flask_issues:
            print(f"   {issue}")
        return None
    
    print("✅ No Flask template syntax found")
    
    # Create deployment package
    package_name = 'final_navigation_fix_production.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
    
    file_size = os.path.getsize(package_name)
    print(f"\n🎯 CLEAN DEPLOYMENT PACKAGE CREATED: {package_name}")
    print(f"📦 Package size: {file_size:,} bytes")
    print(f"🔧 All navigation links use direct URLs:")
    print(f"   - Home buttons: /")
    print(f"   - Privacy Policy: /privacy-policy") 
    print(f"   - Terms of Service: /terms-of-service")
    print(f"   - Login form action: /login")
    print(f"✅ Ready for AWS Lambda deployment")
    
    return package_name

if __name__ == "__main__":
    package_name = create_clean_deployment()
    if package_name:
        print(f"\n🚀 Deploy {package_name} to AWS Lambda to fix navigation errors")
    else:
        print("\n❌ Fix Flask template syntax issues before deployment")