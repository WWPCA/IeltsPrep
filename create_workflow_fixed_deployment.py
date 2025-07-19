#!/usr/bin/env python3
"""
Create Updated Production Deployment with Mobile-First Workflow Fixes
"""

import zipfile
import os
from datetime import datetime

def create_deployment_package():
    """Create deployment package with mobile-first workflow fixes"""
    
    package_name = f"mobile_workflow_fixed_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    files_to_include = [
        'app.py',                    # Updated login handler with mobile workflow validation
        'aws_mock_config.py',        # Updated test users with mobile app verification
        'main.py',                   # Flask entry point
        'working_template_backup_20250714_192410.html',  # AI SEO optimized templates
        'test_maya_voice.html',      # Maya voice test page
        'PRODUCTION_TEST_CREDENTIALS.md'  # Mobile workflow compliant test credentials documentation
    ]
    
    print(f"🔧 CREATING MOBILE-FIRST WORKFLOW FIXED DEPLOYMENT")
    print(f"📦 Package: {package_name}")
    print("")
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_size = 0
        
        for file_path in files_to_include:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size
                zipf.write(file_path)
                print(f"✅ {file_path} ({file_size:,} bytes)")
            else:
                print(f"⚠️  {file_path} (not found)")
    
    final_size = os.path.getsize(package_name)
    compression_ratio = round((1 - final_size / total_size) * 100, 1)
    
    print("")
    print(f"📊 DEPLOYMENT PACKAGE CREATED")
    print(f"   Total uncompressed: {total_size:,} bytes")
    print(f"   Final package size: {final_size:,} bytes ({final_size/1024:.1f} KB)")
    print(f"   Compression ratio: {compression_ratio}%")
    
    print("")
    print("🔧 KEY FIXES IN THIS DEPLOYMENT:")
    print("   ✅ Test users configured with mobile_app_verified: True")
    print("   ✅ Test users have purchase_status: completed")
    print("   ✅ Test users have full assessment access")
    print("   ✅ Login handler validates mobile workflow compliance")
    print("   ✅ Proper error messages for non-compliant accounts")
    print("   ✅ Mobile device IDs and app store verification flags")
    
    print("")
    print("🎯 MOBILE-FIRST WORKFLOW COMPLIANCE:")
    print("   - Users must register through mobile app first")  
    print("   - Purchase verification through app store receipts")
    print("   - Website login only works for verified mobile users")
    print("   - Test credentials follow exact production workflow")
    
    return package_name, final_size

if __name__ == "__main__":
    package_name, size = create_deployment_package()
    print(f"\n🚀 READY FOR PRODUCTION DEPLOYMENT: {package_name}")
    print(f"📋 Test Credentials: prodtest@ieltsgenaiprep.com / test123")
