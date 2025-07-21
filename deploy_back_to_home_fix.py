#!/usr/bin/env python3
"""
Deploy Back to Home Button Fix for Production
Fixes Flask url_for template syntax causing internal server errors in Lambda environment
"""
import zipfile
import os

def create_deployment_package():
    """Create deployment package with Back to Home button fix"""
    
    # Read the fixed lambda function
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Create deployment package
    package_name = 'back_to_home_fix_production.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the fixed lambda function
        zipf.writestr('lambda_function.py', lambda_code)
        
        print(f"✅ Added fixed lambda_function.py ({len(lambda_code)} bytes)")
    
    file_size = os.path.getsize(package_name)
    print(f"\n🎯 DEPLOYMENT PACKAGE CREATED: {package_name}")
    print(f"📦 Package size: {file_size:,} bytes")
    print(f"🔧 Fix: Replaced Flask url_for('index') with direct '/' links")
    print(f"✅ Back to Home buttons will now work correctly on privacy policy and terms of service pages")
    
    return package_name

if __name__ == "__main__":
    package_name = create_deployment_package()
    print(f"\n🚀 Ready for AWS Lambda deployment: {package_name}")
    print("✅ This fixes the internal server error when clicking 'Back to Home' buttons")