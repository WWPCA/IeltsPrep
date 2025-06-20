#!/usr/bin/env python3
"""
Deploy working Lambda function with comprehensive home page
"""
import boto3
import zipfile

def deploy_working_lambda():
    """Deploy working Lambda with embedded comprehensive template"""
    
    # Read the comprehensive home page
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # Escape the HTML content for Python string
    escaped_content = home_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    # Create working Lambda function
    lambda_code = f'''import json

def lambda_handler(event, context):
    """Working Lambda handler with comprehensive home page"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    print(f"Processing {{method}} {{path}}")
    
    if path == '/' or path == '/index.html':
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            }},
            'body': """{escaped_content}"""
        }}
    
    elif path == '/login':
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '''<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body><div class="container mt-5"><h1>IELTS GenAI Prep Login</h1>
<div class="alert alert-info"><p>Download our mobile app first, then return here to login.</p></div>
</div></body></html>'''
        }}
    
    elif path == '/qr-auth':
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '''<!DOCTYPE html>
<html><head><title>Mobile App Access</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body><div class="container mt-5"><h1>Access IELTS GenAI Prep</h1>
<div class="alert alert-primary"><p>Download IELTS GenAI Prep from App Store or Google Play, purchase assessments ($36 each), then login here.</p></div>
</div></body></html>'''
        }}
    
    elif path == '/privacy-policy':
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '''<!DOCTYPE html><html><head><title>Privacy Policy</title></head><body><h1>Privacy Policy</h1><p>Coming Soon</p></body></html>'''
        }}
    
    elif path == '/terms-of-service':
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '''<!DOCTYPE html><html><head><title>Terms of Service</title></head><body><h1>Terms of Service</h1><p>Coming Soon</p></body></html>'''
        }}
    
    else:
        return {{
            'statusCode': 302,
            'headers': {{'Location': '/'}},
            'body': ''
        }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('working-lambda.zip', 'w') as zip_file:
        zip_file.writestr('simple_lambda.py', lambda_code)
    
    # Deploy to AWS
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('working-lambda.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    response = lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    print(f"Lambda deployed: {response['FunctionArn']}")
    return True

if __name__ == "__main__":
    deploy_working_lambda()
    print("Comprehensive home page deployed successfully!")