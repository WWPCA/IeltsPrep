#!/usr/bin/env python3
"""
Deploy minimal working Lambda to get site back online
Uses only built-in Python modules
"""

import boto3
import json
import zipfile
import io

def create_minimal_lambda():
    """Create minimal working Lambda with enhanced template"""
    
    # Read the enhanced template
    try:
        with open('working_template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except:
        template_content = "Error loading template"
    
    # Create minimal Lambda code
    lambda_code = '''import json

def lambda_handler(event, context):
    """Minimal Lambda handler for IELTS GenAI Prep"""
    
    # Enhanced template content
    template = """''' + template_content.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Get request details
    path = event.get('path', '/')
    
    # Handle home page
    if path == '/' or path == '':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': template
        }
    
    # Handle login page
    elif path == '/login':
        login_html = """<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="bg-light">
<div class="container mt-5"><div class="row justify-content-center">
<div class="col-md-6"><div class="card">
<div class="card-header text-center"><h3>Login to IELTS GenAI Prep</h3></div>
<div class="card-body">
<p class="text-center">Please download the mobile app first to create your account and purchase assessments.</p>
<p class="text-center"><a href="/" class="btn btn-primary">Back to Home</a></p>
</div></div></div></div></div></body></html>"""
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'body': login_html
        }
    
    # Handle API health check
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy'})
        }
    
    # Handle 404
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>404 Not Found</h1><p><a href="/">Return to Home</a></p>'
        }
'''
    
    return lambda_code

def deploy_minimal():
    """Deploy minimal working Lambda"""
    
    print("Deploying minimal working Lambda...")
    
    # Create Lambda code
    lambda_code = create_minimal_lambda()
    
    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Deploy
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda deployed: {response['LastModified']}")
        return True
        
    except Exception as e:
        print(f"Deploy failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_minimal()
    if success:
        print("SUCCESS: Minimal Lambda deployed")
        print("Website should be working at: https://www.ieltsaiprep.com")
    else:
        print("FAILED: Could not deploy minimal Lambda")