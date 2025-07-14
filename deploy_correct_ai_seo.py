#!/usr/bin/env python3
"""
Deploy the CORRECT AI SEO version with comprehensive FAQs and academic assessment sample
"""

import boto3
import json
import zipfile
import io

def create_correct_ai_seo_deployment():
    """Create deployment with correct working_template.html that has comprehensive FAQs"""
    
    # Read the CORRECT working_template.html with comprehensive FAQs
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create the correct Lambda function that serves this template
    lambda_code = f'''
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

def verify_recaptcha_v2(recaptcha_response, user_ip=None):
    if not recaptcha_response:
        return False
    
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    if not secret_key:
        return False
    
    data = {{'secret': secret_key, 'response': recaptcha_response}}
    if user_ip:
        data['remoteip'] = user_ip
    
    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=encoded_data,
            method='POST'
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {{e}}")
        return False

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {{}})
        
        # Check CloudFront security header
        cf_secret = headers.get('cf-secret', '')
        if cf_secret != 'CF-Secret-3140348d':
            return {{
                'statusCode': 403,
                'body': json.dumps({{'error': 'Forbidden - Direct access not allowed'}})
            }}
        
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            if http_method == 'GET':
                return handle_login_page()
            elif http_method == 'POST':
                return handle_login_post(event)
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/dashboard':
            return handle_dashboard()
        elif path == '/robots.txt':
            return handle_robots_txt()
        elif path.startswith('/gdpr/'):
            return handle_gdpr_endpoints(path)
        else:
            return {{
                'statusCode': 404,
                'headers': {{'Content-Type': 'text/html'}},
                'body': '<h1>Page not found</h1>'
            }}
    except Exception as e:
        print(f"Lambda error: {{e}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '<h1>Internal server error</h1>'
        }}

def handle_home_page():
    """Serve the CORRECT AI SEO home page with comprehensive FAQs"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """{template_content}"""
    }}

def handle_login_page():
    """Serve login page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': get_login_template()
    }}

def handle_login_post(event):
    """Handle login POST request"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'application/json'}},
        'body': json.dumps({{'success': True, 'message': 'Login successful', 'session_id': 'test_session'}})
    }}

def handle_privacy_policy():
    """Serve privacy policy"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>Privacy Policy</h1><p>Privacy policy content here</p>'
    }}

def handle_terms_of_service():
    """Serve terms of service"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>Terms of Service</h1><p>Terms of service content here</p>'
    }}

def handle_dashboard():
    """Serve dashboard"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>Dashboard</h1><p>Dashboard content here</p>'
    }}

def handle_robots_txt():
    """Serve robots.txt"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/plain'}},
        'body': 'User-agent: *\\nAllow: /\\n\\nUser-agent: GPTBot\\nAllow: /\\n\\nUser-agent: ClaudeBot\\nAllow: /\\n\\nUser-agent: Google-Extended\\nAllow: /'
    }}

def handle_gdpr_endpoints(path):
    """Handle GDPR endpoints"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': f'<h1>GDPR: {{path}}</h1><p>GDPR functionality here</p>'
    }}

def get_login_template():
    """Login template"""
    return '''<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body>
<div class="container py-5">
<h1>Login</h1>
<form>
<div class="mb-3">
<label for="email" class="form-label">Email</label>
<input type="email" class="form-control" id="email" required>
</div>
<div class="mb-3">
<label for="password" class="form-label">Password</label>
<input type="password" class="form-control" id="password" required>
</div>
<button type="submit" class="btn btn-primary">Sign In</button>
</form>
</div>
</body></html>'''
'''
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def deploy_correct_ai_seo():
    """Deploy the CORRECT AI SEO version"""
    
    print("Deploying CORRECT AI SEO version with comprehensive FAQs and academic assessment sample...")
    zip_content = create_correct_ai_seo_deployment()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ CORRECT AI SEO version deployed successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_correct_ai_seo()
    if success:
        print("\\n✅ CORRECT AI SEO VERSION DEPLOYED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("📚 Comprehensive FAQs included")
        print("📊 Academic Writing Assessment Sample included")
    else:
        print("\\n❌ DEPLOYMENT FAILED")