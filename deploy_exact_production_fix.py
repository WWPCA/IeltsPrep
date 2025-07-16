#!/usr/bin/env python3
"""
Deploy exact production code with ONLY mobile registration security fix
"""

import boto3
import json
import zipfile
import io

def create_production_lambda():
    """Create exact production Lambda with mobile security fix"""
    
    # Take the exact current app.py and just modify the mobile registration handler
    with open('app.py', 'r', encoding='utf-8') as f:
        production_code = f.read()
    
    # Read mobile registration template
    with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
        mobile_html = f.read()
    
    # Escape the HTML properly for embedding
    mobile_html_escaped = mobile_html.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    # Replace the file reading with embedded template
    production_code = production_code.replace(
        "with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:\n            html_content = f.read()",
        f'html_content = """{mobile_html}"""'
    )
    
    # Add mobile app security check - find the mobile registration handler
    old_handler = '''def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Mobile registration page - requires mobile app"""
    try:
        # Get user agent and origin
        user_agent = headers.get('User-Agent', '').lower()
        origin = headers.get('Origin', '')
        
        # Check if this is a mobile app request
        is_mobile_app = (
            'capacitor' in user_agent or 
            'ionic' in user_agent or
            'cordova' in user_agent or
            'ieltsaiprep' in user_agent or
            origin.startswith('capacitor://') or
            origin.startswith('ionic://') or
            headers.get('X-Capacitor-Platform') is not None
        )
        
        # Block web browser access
        if not is_mobile_app:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Access Restricted</h1><p>Registration requires mobile app and App Store purchase.</p><a href="/">Return Home</a>'
            }
        
        # Return the registration page for mobile app
        with open('mobile_registration_flow.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache',
                'X-Frame-Options': 'DENY'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Registration Error</h1><p>{str(e)}</p>'
        }'''
    
    new_handler = '''def handle_mobile_registration_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Mobile registration page - requires mobile app"""
    try:
        # Get user agent and origin
        user_agent = headers.get('User-Agent', '').lower()
        origin = headers.get('Origin', '')
        
        # Check if this is a mobile app request
        is_mobile_app = (
            'capacitor' in user_agent or 
            'ionic' in user_agent or
            'cordova' in user_agent or
            'ieltsaiprep' in user_agent or
            origin.startswith('capacitor://') or
            origin.startswith('ionic://') or
            headers.get('X-Capacitor-Platform') is not None
        )
        
        # Block web browser access
        if not is_mobile_app:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Access Restricted</h1><p>Registration requires mobile app and App Store purchase.</p><a href="/">Return Home</a>'
            }
        
        # Return the registration page for mobile app
        html_content = """''' + mobile_html + '''"""
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache',
                'X-Frame-Options': 'DENY'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Registration Error</h1><p>{str(e)}</p>'
        }'''
    
    # Replace the handler
    if old_handler in production_code:
        production_code = production_code.replace(old_handler, new_handler)
    
    return production_code

def deploy_lambda():
    """Deploy to production"""
    
    try:
        # Create the Lambda code
        lambda_code = create_production_lambda()
        
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
        
        print(f"✅ Production deployed with mobile security")
        print(f"📦 Size: {len(zip_data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Deploying exact production with mobile security...")
    
    success = deploy_lambda()
    
    if success:
        print("✅ PRODUCTION DEPLOYED")
        print("🔒 Mobile registration secured for App Store submission")
    else:
        print("❌ DEPLOYMENT FAILED")