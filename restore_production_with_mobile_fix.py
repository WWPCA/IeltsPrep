#!/usr/bin/env python3
"""
Restore original production Lambda with ONLY mobile registration security fix
"""

import boto3
import json
import zipfile
import io

def restore_production_lambda():
    """Restore original production Lambda with mobile registration fix"""
    
    # Read the current working app.py (original production code)
    with open('app.py', 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # Read the mobile registration template
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        mobile_reg_html = f.read()
    
    # Modify ONLY the mobile registration handler to add security
    # Find the existing handle_mobile_registration_page function and replace it
    mobile_registration_handler = '''def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Mobile registration page - App Store purchase required"""
    try:
        # Check for mobile app user agent
        user_agent = headers.get('User-Agent', '').lower()
        origin = headers.get('Origin', '')
        
        # Detect mobile app
        is_mobile_app = (
            'capacitor' in user_agent or 
            'ionic' in user_agent or
            'cordova' in user_agent or
            'ieltsaiprep' in user_agent or
            origin.startswith('capacitor://') or
            origin.startswith('ionic://') or
            headers.get('X-Capacitor-Platform') is not None
        )
        
        # Block web browser access - only allow mobile app
        if not is_mobile_app:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'text/html'},
                'body': '<html><head><title>Access Restricted</title></head><body><h1>Access Restricted</h1><p>Registration is only available through the mobile app after completing an App Store or Google Play purchase.</p><p><a href="/">Return to Home</a></p></body></html>'
            }
        
        # Load and return the mobile registration template for mobile app users
        try:
            with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            # Fallback if template not found
            html_content = """<!DOCTYPE html>
<html><head><title>Mobile Registration</title></head>
<body><h1>Mobile Registration</h1>
<p>Registration page for mobile app users with App Store purchases.</p>
</body></html>"""
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<html><body><h1>Registration Error</h1><p>{str(e)}</p></body></html>'
        }'''
    
    # Replace the existing mobile registration handler
    import re
    
    # Find and replace the mobile registration handler
    pattern = r'def handle_mobile_registration_page\(headers: Dict\[str, Any\]\) -> Dict\[str, Any\]:.*?(?=\n\ndef|\nclass|\n# |$)'
    
    if re.search(pattern, original_code, re.DOTALL):
        modified_code = re.sub(pattern, mobile_registration_handler, original_code, flags=re.DOTALL)
    else:
        # If handler doesn't exist, add it
        modified_code = original_code + '\n\n' + mobile_registration_handler
    
    # Embed the mobile registration template in the Lambda
    template_embed = f'''
# Mobile registration HTML template
MOBILE_REGISTRATION_HTML = """{mobile_reg_html}"""
'''
    
    # Add template at the top after imports
    lines = modified_code.split('\n')
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i + 1
        elif line.strip() == '' and insert_index > 0:
            break
    
    lines.insert(insert_index, template_embed)
    
    # Update the handler to use embedded template
    final_code = '\n'.join(lines).replace(
        "with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:\n            html_content = f.read()",
        "html_content = MOBILE_REGISTRATION_HTML"
    )
    
    return final_code

def deploy_to_lambda():
    """Deploy to production Lambda"""
    
    try:
        # Create the restored code with mobile security fix
        lambda_code = restore_production_lambda()
        
        # Create AWS client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create ZIP package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Deploy to Lambda
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Production restored with mobile security fix")
        print(f"📦 Size: {len(zip_data)} bytes")
        print(f"🔒 Mobile registration now requires App Store purchase")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

def test_production():
    """Test the restored production"""
    
    import requests
    import time
    
    print("⏳ Testing restored production...")
    time.sleep(3)
    
    # Test home page (should work)
    try:
        home_response = requests.get('https://www.ieltsaiprep.com/', timeout=10)
        print(f"   Home page: {home_response.status_code}")
    except Exception as e:
        print(f"   Home page: Error - {str(e)}")
    
    # Test mobile registration (should be 403 for web)
    try:
        reg_response = requests.get('https://www.ieltsaiprep.com/mobile-registration', timeout=10)
        print(f"   Mobile registration (web): {reg_response.status_code}")
    except Exception as e:
        print(f"   Mobile registration (web): Error - {str(e)}")

if __name__ == "__main__":
    print("🔄 Restoring production Lambda with mobile security fix...")
    
    success = deploy_to_lambda()
    
    if success:
        print("✅ PRODUCTION RESTORED")
        test_production()
        print("📱 Original templates preserved, mobile security added")
    else:
        print("❌ RESTORE FAILED")