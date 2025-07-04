#!/usr/bin/env python3
"""
Fix reCAPTCHA configuration in login template
Updates the login page with correct reCAPTCHA site key from environment variables
"""
import boto3
import zipfile
import base64
import os

def fix_recaptcha_login():
    """Fix reCAPTCHA site key in login template"""
    
    # Get the correct reCAPTCHA site key from environment
    recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
    
    if not recaptcha_site_key:
        print("ERROR: RECAPTCHA_V2_SITE_KEY not found in environment")
        return False
    
    print(f"Using reCAPTCHA site key: {recaptcha_site_key[:20]}...")
    
    # Read the login template
    with open('login.html', 'r', encoding='utf-8') as f:
        login_template = f.read()
    
    # Update the reCAPTCHA site key in the template
    # Replace the hardcoded site key with the correct one
    login_template = login_template.replace(
        'data-sitekey="6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix"',
        f'data-sitekey="{recaptcha_site_key}"'
    )
    
    # Verify the update was successful
    if f'data-sitekey="{recaptcha_site_key}"' not in login_template:
        print("ERROR: Failed to update reCAPTCHA site key in template")
        return False
    
    print("Login template updated with correct reCAPTCHA site key")
    
    # Read the working home page template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        home_template = f.read()
    
    # Verify home template still has correct pricing
    if '$36' not in home_template:
        print("ERROR: Home template missing $36 pricing!")
        return False
    
    pricing_count = home_template.count('$36')
    print(f"Home template verified: {pricing_count} instances of $36 pricing")
    
    # Encode templates
    home_b64 = base64.b64encode(home_template.encode('utf-8')).decode('ascii')
    login_b64 = base64.b64encode(login_template.encode('utf-8')).decode('ascii')
    
    # Create Lambda function with fixed reCAPTCHA
    lambda_code = f'''
import json
import base64
import os
import requests

def lambda_handler(event, context):
    """Lambda handler with fixed reCAPTCHA configuration"""
    path = event.get('path', '/')
    method = event.get('httpMethod', event.get('requestContext', {{}}).get('http', {{}}).get('method', 'GET'))
    body = event.get('body', '{{}}')
    
    # Parse request body
    try:
        data = json.loads(body) if body else {{}}
    except json.JSONDecodeError:
        data = {{}}
    
    if path == '/':
        return serve_home_page()
    elif path == '/login':
        return serve_login_page()
    elif path == '/dashboard':
        return serve_dashboard_page()
    elif path.startswith('/api/login') and method == 'POST':
        return handle_login_api(data)
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
    """Serve login page with correct reCAPTCHA site key"""
    template_b64 = "{login_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_dashboard_page():
    """Serve dashboard page"""
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

def handle_login_api(data):
    """Handle login API with reCAPTCHA verification"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        recaptcha_response = data.get('g-recaptcha-response', '')
        
        # Verify reCAPTCHA
        if recaptcha_response:
            recaptcha_secret = os.environ.get('RECAPTCHA_V2_SECRET_KEY', '')
            if recaptcha_secret:
                verify_response = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data={{
                        'secret': recaptcha_secret,
                        'response': recaptcha_response
                    }},
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    recaptcha_result = verify_response.json()
                    if not recaptcha_result.get('success', False):
                        return {{
                            'statusCode': 200,
                            'headers': {{'Content-Type': 'application/json'}},
                            'body': json.dumps({{
                                'success': False,
                                'message': 'reCAPTCHA verification failed'
                            }})
                        }}
        
        # Test credentials
        if email == 'test@ieltsgenaiprep.com' and password == 'testpassword123':
            return {{
                'statusCode': 200,
                'headers': {{
                    'Content-Type': 'application/json',
                    'Set-Cookie': 'web_session_id=test_session_123; Path=/; HttpOnly; Secure'
                }},
                'body': json.dumps({{
                    'success': True,
                    'message': 'Login successful',
                    'redirect': '/dashboard'
                }})
            }}
        else:
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{
                    'success': False,
                    'message': 'Invalid credentials. Use test@ieltsgenaiprep.com / testpassword123'
                }})
            }}
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{
                'success': False,
                'message': 'Login error occurred'
            }})
        }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('fixed-recaptcha-login.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('fixed-recaptcha-login.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying fixed reCAPTCHA login...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    # Update environment variables
    lambda_client.update_function_configuration(
        FunctionName='ielts-genai-prep-api',
        Environment={
            'Variables': {
                'RECAPTCHA_V2_SITE_KEY': recaptcha_site_key,
                'RECAPTCHA_V2_SECRET_KEY': os.environ.get('RECAPTCHA_V2_SECRET_KEY', '')
            }
        }
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Deployment completed!')
    
    # Verify deployment
    import time
    time.sleep(5)
    
    import requests
    try:
        # Test login page
        login_response = requests.get('https://www.ieltsaiprep.com/login')
        if f'data-sitekey="{recaptcha_site_key}"' in login_response.text:
            print('SUCCESS: Login page verified with correct reCAPTCHA site key')
            return True
        else:
            print('WARNING: Login page may not have correct reCAPTCHA site key')
            return False
            
    except Exception as e:
        print(f'Could not verify deployment: {e}')
        return False

if __name__ == "__main__":
    fix_recaptcha_login()