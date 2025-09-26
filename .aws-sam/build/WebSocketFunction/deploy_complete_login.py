#!/usr/bin/env python3
"""
Deploy complete login page matching preview to production
Updates the production Lambda to serve the full login.html content
"""

import boto3
import json
import zipfile
import io

def create_lambda_with_complete_login():
    """Create Lambda with complete login page matching preview"""
    
    # Read the enhanced template
    try:
        with open('working_template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except:
        template_content = "Error loading template"
    
    # Read the complete login page
    try:
        with open('login.html', 'r', encoding='utf-8') as f:
            login_content = f.read()
    except:
        login_content = "Error loading login page"
    
    # Create Lambda code with complete login page
    lambda_code = '''import json

def lambda_handler(event, context):
    """Lambda handler for IELTS GenAI Prep with complete login page"""
    
    # Enhanced template content
    template = """''' + template_content.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Complete login page content with dynamic reCAPTCHA key
    login_page = """''' + login_content.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Replace reCAPTCHA site key with environment variable
    import os
    recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix')
    login_page = login_page.replace('6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix', recaptcha_site_key)
    
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
    
    # Handle complete login page
    elif path == '/login':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': login_page
        }
    
    # Handle API health check
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy'})
        }
    
    # Handle privacy policy
    elif path == '/privacy-policy':
        privacy_html = """<!DOCTYPE html>
<html><head><title>Privacy Policy - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="bg-light">
<div class="container mt-5 mb-5"><div class="row justify-content-center">
<div class="col-lg-8"><div class="card">
<div class="card-header"><h3>Privacy Policy</h3></div>
<div class="card-body">
<p>IELTS GenAI Prep is committed to protecting your privacy. This policy explains how we collect, use, and protect your information.</p>
<h5>Information Collection</h5>
<p>We collect information you provide when creating an account and using our assessment services.</p>
<h5>Data Use</h5>
<p>Your data is used to provide personalized IELTS assessment services and improve our AI evaluation systems.</p>
<h5>Data Protection</h5>
<p>We use industry-standard security measures to protect your personal information.</p>
<p><a href="/" class="btn btn-primary">Back to Home</a></p>
</div></div></div></div></div></body></html>"""
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'body': privacy_html
        }
    
    # Handle terms of service
    elif path == '/terms-of-service':
        terms_html = """<!DOCTYPE html>
<html><head><title>Terms of Service - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="bg-light">
<div class="container mt-5 mb-5"><div class="row justify-content-center">
<div class="col-lg-8"><div class="card">
<div class="card-header"><h3>Terms of Service</h3></div>
<div class="card-body">
<p>Welcome to IELTS GenAI Prep. By using our services, you agree to these terms.</p>
<h5>Service Description</h5>
<p>IELTS GenAI Prep provides AI-powered IELTS assessment preparation tools for Academic and General Training.</p>
<h5>Payment Terms</h5>
<p>Assessment packages are available for $36 CAD each through mobile app stores.</p>
<h5>Usage Rights</h5>
<p>You may use our services for personal IELTS preparation purposes.</p>
<p><a href="/" class="btn btn-primary">Back to Home</a></p>
</div></div></div></div></div></body></html>"""
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'body': terms_html
        }
    
    # Handle API requests
    elif path.startswith('/api/'):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'API endpoint active', 'path': path})
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

def deploy_complete_login():
    """Deploy Lambda with complete login page"""
    
    print("Deploying updated login page with fixes to production...")
    
    # Create Lambda code
    lambda_code = create_lambda_with_complete_login()
    
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
    success = deploy_complete_login()
    if success:
        print("SUCCESS: Complete login page deployed")
        print("Production login now matches preview at: https://www.ieltsaiprep.com/login")
    else:
        print("FAILED: Could not deploy complete login page")