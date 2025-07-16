#!/usr/bin/env python3
"""
Emergency redeployment script for the working IELTS GenAI Prep template
Run this if the production website ever shows incorrect pricing or content
"""
import boto3
import zipfile
import base64

def emergency_redeploy():
    """Redeploy the confirmed working template"""
    
    # Read the working template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Verify template has correct pricing
    if '$49.99' not in template_content:
        print("ERROR: Template does not contain correct $49.99 pricing!")
        return False
    
    pricing_count = template_content.count('$49.99')
    if pricing_count < 4:
        print(f"ERROR: Template only has {pricing_count} instances of $49.99, expected at least 4!")
        return False
    
    print(f"Template verified: Found {pricing_count} instances of $49.99 pricing")
    
    # Encode template
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
    with zipfile.ZipFile('emergency-redeploy.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('emergency-redeploy.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying working template...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Emergency redeployment completed!')
    
    # Verify deployment
    import time
    time.sleep(5)  # Wait for deployment
    
    import requests
    try:
        response = requests.get('https://www.ieltsaiprep.com/')
        if '$49.99' in response.text and response.text.count('$49.99') >= 4:
            print('SUCCESS: Website verified with correct $49.99 pricing')
            return True
        else:
            print('ERROR: Website deployment may have failed')
            return False
    except Exception as e:
        print(f'Could not verify website: {e}')
        return False

if __name__ == "__main__":
    emergency_redeploy()
