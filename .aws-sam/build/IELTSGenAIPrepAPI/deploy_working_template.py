#!/usr/bin/env python3
import boto3
import zipfile
import base64

def deploy_working_template():
    # Read the working template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Encode the template as base64 to avoid string escaping issues
    template_b64 = base64.b64encode(template_content.encode('utf-8')).decode('ascii')
    
    # Create Lambda function
    lambda_code = f'''
import json
import base64

def lambda_handler(event, context):
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
    # Decode the working template
    template_b64 = "{template_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_login_page():
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title></head>
<body style="padding: 40px;">
<h2>Login</h2>
<p>Test: test@ieltsgenaiprep.com / testpassword123</p>
<a href="/">← Back to Home</a>
</body></html>"""
    }}

def serve_dashboard_page():
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body style="padding: 40px;">
<h2>Dashboard</h2>
<p>Your assessments are ready!</p>
<a href="/">← Back to Home</a>
</body></html>"""
    }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('exact-working-template.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('exact-working-template.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying exact working template from Replit preview...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Working template deployed successfully!')

if __name__ == "__main__":
    deploy_working_template()