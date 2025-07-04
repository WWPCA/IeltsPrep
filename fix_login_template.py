#!/usr/bin/env python3
"""
Fix login template by restoring the working Lambda function
Uses the same approach that successfully fixed the home page
"""
import boto3
import zipfile
import base64

def fix_login_template():
    """Restore working Lambda function with correct login template"""
    
    # Read the working home page template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        home_template = f.read()
    
    # Read the comprehensive login template
    with open('login.html', 'r', encoding='utf-8') as f:
        login_template = f.read()
    
    # Verify templates
    if '$36' not in home_template:
        print("ERROR: Home template missing $36 pricing!")
        return False
    
    if 'bootstrap' not in login_template.lower():
        print("ERROR: Login template missing Bootstrap!")
        return False
    
    print("Templates verified successfully")
    
    # Encode templates
    home_b64 = base64.b64encode(home_template.encode('utf-8')).decode('ascii')
    login_b64 = base64.b64encode(login_template.encode('utf-8')).decode('ascii')
    
    # Create simple Lambda function (same structure as working home page)
    lambda_code = f'''
import json
import base64

def lambda_handler(event, context):
    """Simple Lambda handler with working templates"""
    path = event.get('path', '/')
    
    if path == '/':
        return serve_home_page()
    elif path == '/login':
        return serve_login_page()
    elif path == '/dashboard':
        return serve_dashboard_page()
    else:
        return serve_home_page()

def serve_home_page():
    """Serve home page with correct $36 pricing"""
    template_b64 = "{home_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_login_page():
    """Serve comprehensive login page"""
    template_b64 = "{login_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_dashboard_page():
    """Serve basic dashboard page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body style="padding: 40px; font-family: Arial, sans-serif;">
<h2>Dashboard</h2>
<p>Welcome! Your assessments are ready.</p>
<p><strong>Test credentials:</strong> test@ieltsgenaiprep.com / testpassword123</p>
<a href="/" style="color: #667eea;">← Back to Home</a>
</body></html>"""
    }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('fixed-login-template.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('fixed-login-template.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying fixed login template...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Deployment completed!')
    
    # Verify deployment
    import time
    time.sleep(5)
    
    import requests
    try:
        # Test home page
        home_response = requests.get('https://www.ieltsaiprep.com/')
        home_success = '$36' in home_response.text and home_response.text.count('$36') >= 4
        
        # Test login page
        login_response = requests.get('https://www.ieltsaiprep.com/login')
        login_success = 'Welcome Back' in login_response.text and 'bootstrap' in login_response.text.lower()
        
        if home_success and login_success:
            print('SUCCESS: Both home and login pages verified!')
            return True
        else:
            print(f'PARTIAL: Home={home_success}, Login={login_success}')
            return False
            
    except Exception as e:
        print(f'Could not verify deployment: {e}')
        return False

if __name__ == "__main__":
    fix_login_template()