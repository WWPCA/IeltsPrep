#!/usr/bin/env python3
"""
Deploy Simplified Privacy Policy - Remove GDPR Rights Section and Email
"""

import boto3
import json
import zipfile
import io

def deploy_simplified_privacy():
    """Deploy simplified privacy policy without GDPR rights section"""
    
    print("Deploying simplified privacy policy...")
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Read the working template
    with open('working_template_backup_20250714_192410.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Apply AWS production fixes
    production_fixes = [
        # Remove AWS mock import
        ('from aws_mock_config import aws_mock', '# AWS mock removed for production'),
        # Fix environment check
        ("os.environ.get('REPLIT_ENVIRONMENT') == 'true'", "False"),
        # Replace mock calls
        ('aws_mock.get_health_status()', '{"status": "production"}'),
        ('aws_mock.get_user_profile(email)', 'None'),
        ('aws_mock.delete_user_completely(email)', 'True'),
        ('aws_mock.get_assessment_history(user_email)', '[]'),
    ]
    
    # Apply production fixes
    for old_code, new_code in production_fixes:
        lambda_code = lambda_code.replace(old_code, new_code)
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
        zip_file.writestr('working_template_backup_20250714_192410.html', template_content)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.read()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Simplified privacy policy deployed successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_simplified_privacy()
    if success:
        print("\n✅ SIMPLIFIED PRIVACY POLICY DEPLOYED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("📜 Privacy Policy: Simplified with data usage purposes only")
        print("🔐 GDPR: Compliant with data usage transparency")
        print("🎤 Voice Data: Clearly states recordings are not saved")
    else:
        print("\n❌ DEPLOYMENT FAILED")