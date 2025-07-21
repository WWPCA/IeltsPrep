#!/usr/bin/env python3
"""
Deploy Text Update - Remove specific text from home page
"""

import zipfile
import os
import boto3
import json
from datetime import datetime

def deploy_text_update():
    """Deploy updated text to production"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"text_update_{timestamp}.zip"
    
    print(f"🔧 DEPLOYING TEXT UPDATE")
    print(f"📝 Removing: 'IELTS GenAI Prep is the only AI-based...' text")
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
            "change": "Removed specific text from home page subtitle",
            "text_removed": "IELTS GenAI Prep is the only AI-based IELTS preparation platform offering instant band-aligned feedback on Writing and Speaking. ",
            "new_text": "Powered by TrueScore® and ClearScore®, we replicate official examiner standards using GenAI technology."
        }
        zipf.writestr('deployment_info.json', json.dumps(deployment_info, indent=2))
    
    file_size = os.path.getsize(package_name) / 1024
    print(f"✅ Text update package created: {file_size:.1f} KB")
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(package_name, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ TEXT UPDATE DEPLOYED SUCCESSFULLY")
        print(f"📊 Function ARN: {response['FunctionArn']}")
        print(f"📅 Last Modified: {response['LastModified']}")
        print(f"📦 Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ DEPLOYMENT FAILED: {str(e)}")
        return False

def verify_text_update():
    """Verify the text has been updated on the website"""
    
    print(f"\n🔍 VERIFYING TEXT UPDATE")
    
    import time
    time.sleep(5)  # Wait for propagation
    
    import requests
    
    try:
        response = requests.get("https://www.ieltsaiprep.com/", timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Check if old text is removed
            old_text_present = "IELTS GenAI Prep is the only AI-based IELTS preparation platform" in content
            
            # Check if new text is present
            new_text_present = "Powered by TrueScore® and ClearScore®, we replicate official examiner standards" in content
            
            if not old_text_present and new_text_present:
                print(f"✅ TEXT UPDATE VERIFIED")
                print(f"✅ Old text removed successfully")
                print(f"✅ New text displaying correctly")
                return True
            else:
                print(f"⚠️ Text update verification:")
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
    print("📝 TEXT UPDATE DEPLOYMENT STARTING...")
    print("=" * 50)
    
    # Deploy text update
    success = deploy_text_update()
    
    if success:
        # Verify text update
        verified = verify_text_update()
        
        if verified:
            print(f"\n🎉 TEXT UPDATE COMPLETE")
            print(f"✅ Specific text removed from home page")
            print(f"✅ Website updated successfully")
            print(f"🌐 www.ieltsaiprep.com showing updated content")
        else:
            print(f"\n⚠️ Update deployed but needs manual verification")
    else:
        print(f"\n❌ Text update deployment failed")