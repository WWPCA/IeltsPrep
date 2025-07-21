#!/usr/bin/env python3
"""
Deploy Second Text Update - Remove "The World's ONLY" from section heading
"""

import zipfile
import os
import boto3
import json
from datetime import datetime

def deploy_second_text_update():
    """Deploy second text update to production"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"text_update_2_{timestamp}.zip"
    
    print(f"🔧 DEPLOYING SECOND TEXT UPDATE")
    print(f"📝 Changing: 'The World's ONLY Standardized...' → 'Standardized...'")
    print(f"📦 Package: {package_name}")
    
    # Read the updated lambda function
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Create the deployment package
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
        
        # Add deployment info
        deployment_info = {
            "deployment_date": datetime.now().isoformat(),
            "package_name": package_name,
            "change": "Removed 'The World's ONLY' from section heading",
            "old_heading": "The World's ONLY Standardized IELTS GenAI Assessment System",
            "new_heading": "Standardized IELTS GenAI Assessment System"
        }
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
    
    file_size = os.path.getsize(package_name) / 1024
    print(f"✅ Second text update package created: {file_size:.1f} KB")
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(package_name, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ SECOND TEXT UPDATE DEPLOYED SUCCESSFULLY")
        print(f"📊 Function ARN: {response['FunctionArn']}")
        print(f"📅 Last Modified: {response['LastModified']}")
        print(f"📦 Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ DEPLOYMENT FAILED: {str(e)}")
        return False

def verify_second_text_update():
    """Verify the second text update is live"""
    
    print(f"\n🔍 VERIFYING SECOND TEXT UPDATE")
    
    import time
    time.sleep(5)  # Wait for propagation
    
    import requests
    
    try:
        response = requests.get("https://www.ieltsaiprep.com/", timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Check if old text is removed
            old_text_present = "The World's ONLY Standardized IELTS GenAI Assessment System" in content
            
            # Check if new text is present
            new_text_present = "Standardized IELTS GenAI Assessment System" in content
            
            if not old_text_present and new_text_present:
                print(f"✅ SECOND TEXT UPDATE VERIFIED")
                print(f"✅ 'The World's ONLY' removed successfully")
                print(f"✅ Updated heading displaying correctly")
                return True
            else:
                print(f"⚠️ Second text update verification:")
                print(f"   Old text removed: {'✅' if not old_text_present else '❌'}")
                print(f"   New text present: {'✅' if new_text_present else '❌'}")
                return False
                
        else:
            print(f"❌ Website returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

if __name__ == "__main__":
    print("📝 SECOND TEXT UPDATE DEPLOYMENT STARTING...")
    print("=" * 55)
    
    # Deploy second text update
    success = deploy_second_text_update()
    
    if success:
        # Verify second text update
        verified = verify_second_text_update()
        
        if verified:
            print(f"\n🎉 SECOND TEXT UPDATE COMPLETE")
            print(f"✅ Section heading updated successfully")
            print(f"✅ Removed 'The World's ONLY' claim")
            print(f"🌐 www.ieltsaiprep.com showing updated content")
        else:
            print(f"\n⚠️ Update deployed but needs manual verification")
    else:
        print(f"\n❌ Second text update deployment failed")