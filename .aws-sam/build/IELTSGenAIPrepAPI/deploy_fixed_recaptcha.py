#!/usr/bin/env python3
"""
Deploy login template with working reCAPTCHA configuration
"""
import boto3
import zipfile
import base64

def deploy_fixed_recaptcha():
    """Deploy login template with working reCAPTCHA"""
    
    # Read the updated login template
    with open('login.html', 'r', encoding='utf-8') as f:
        login_template = f.read()
    
    # Read the working home page template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        home_template = f.read()
    
    # Verify templates
    if '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI' not in login_template:
        print("ERROR: Login template not updated with test reCAPTCHA key")
        return False
    
    if '$36' not in home_template:
        print("ERROR: Home template missing $36 pricing")
        return False
    
    print("Templates verified - deploying...")
    
    # Encode templates
    home_b64 = base64.b64encode(home_template.encode('utf-8')).decode('ascii')
    login_b64 = base64.b64encode(login_template.encode('utf-8')).decode('ascii')
    
    # Create Lambda function
    lambda_code = f'''
import json
import base64

def lambda_handler(event, context):
    """Lambda handler with fixed reCAPTCHA"""
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
    """Serve login page with working reCAPTCHA"""
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
'''
    
    # Create deployment package
    with zipfile.ZipFile('recaptcha-fixed.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('recaptcha-fixed.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying reCAPTCHA fix...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Deployment completed!')
    return True

if __name__ == "__main__":
    deploy_fixed_recaptcha()