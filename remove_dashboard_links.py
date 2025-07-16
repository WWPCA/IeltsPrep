#!/usr/bin/env python3
"""
Remove GDPR Dashboard Links from Production
"""

import boto3
import json
import zipfile
import io

def remove_dashboard_links():
    """Remove GDPR dashboard links from production Lambda"""
    
    print("Removing GDPR dashboard links from production...")
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Read the working template
    with open('working_template_backup_20250714_192410.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Remove dashboard links from privacy policy
    lambda_code = lambda_code.replace(
        'You can manage your data rights through your <a href="/gdpr/my-data">GDPR Dashboard</a> or contact us directly.',
        'To exercise these rights, please contact us directly at privacy@ieltsaiprep.com'
    )
    
    # Remove any other dashboard references
    lambda_code = lambda_code.replace(
        '<a href="/gdpr/my-data">GDPR Dashboard</a>',
        'contact us directly at privacy@ieltsaiprep.com'
    )
    
    # Remove dashboard route handlers that might exist
    lambda_code = lambda_code.replace(
        'elif path == "/gdpr/my-data":',
        'elif path == "/gdpr/my-data-disabled":'
    )
    
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
        
        print(f"✅ Dashboard links removed successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = remove_dashboard_links()
    if success:
        print("\n✅ DASHBOARD LINKS REMOVED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("📜 Privacy Policy: No dashboard links, contact email provided")
        print("🔐 GDPR: Comprehensive compliance with direct contact instructions")
    else:
        print("\n❌ REMOVAL FAILED")