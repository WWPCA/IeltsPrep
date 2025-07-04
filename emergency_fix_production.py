#!/usr/bin/env python3
"""
Emergency Fix for Production Lambda - Template Update Only
Fixes internal server error by updating only the home page template
while preserving the existing complex Lambda handler structure
"""

import boto3
import json
import zipfile
import io
from datetime import datetime

def get_enhanced_template():
    """Load the enhanced template from working_template.html"""
    try:
        with open('working_template.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Error: working_template.html not found")
        return None

def get_current_lambda_code():
    """Get the current working Lambda code from app.py"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Error: app.py not found")
        return None

def create_fixed_lambda_code():
    """Create fixed Lambda code by updating only the home page template"""
    
    current_code = get_current_lambda_code()
    template_content = get_enhanced_template()
    
    if not current_code or not template_content:
        return None
    
    # Escape the template content for Python string
    escaped_template = template_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    # Find and replace the home page template in the handle_home_page function
    # Look for the existing template assignment
    start_marker = 'def handle_home_page() -> Dict[str, Any]:'
    end_marker = 'def handle_login_page() -> Dict[str, Any]:'
    
    start_idx = current_code.find(start_marker)
    end_idx = current_code.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find home page handler function boundaries")
        return None
    
    # Create the new home page handler
    new_home_handler = f'''def handle_home_page() -> Dict[str, Any]:
    """Handle home page - serve updated working template for preview"""
    
    # Enhanced template with all improvements
    enhanced_template = """{escaped_template}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }},
        'body': enhanced_template
    }}

'''
    
    # Replace the home page handler
    fixed_code = current_code[:start_idx] + new_home_handler + current_code[end_idx:]
    
    return fixed_code

def deploy_emergency_fix():
    """Deploy emergency fix to production"""
    
    print("🚨 Creating emergency fix for production...")
    
    # Create fixed Lambda code
    fixed_code = create_fixed_lambda_code()
    if not fixed_code:
        print("Failed to create fixed Lambda code")
        return False
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add fixed Lambda function code
        zip_file.writestr('lambda_function.py', fixed_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update Lambda function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ Emergency fix deployed successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 EMERGENCY FIX - Deploying corrected Lambda...")
    success = deploy_emergency_fix()
    
    if success:
        print("\n✅ EMERGENCY FIX SUCCESSFUL!")
        print("🌐 Website should be working again at: https://www.ieltsaiprep.com")
        print("💚 Enhanced template preserved with all improvements")
    else:
        print("\n❌ EMERGENCY FIX FAILED!")
        print("Manual intervention required")