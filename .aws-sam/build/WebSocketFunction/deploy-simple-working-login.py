#!/usr/bin/env python3
"""
Deploy simple working login following successful pattern from previous deployments
"""
import boto3
import zipfile
import os
import tempfile

def create_simple_working_lambda():
    """Create simple working Lambda without complex CSS"""
    
    lambda_code = '''import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

def verify_recaptcha_v2(recaptcha_response, user_ip=None):
    """Verify reCAPTCHA v2 response"""
    if not recaptcha_response:
        return False
    
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    if not secret_key:
        return False
    
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
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
        print(f"reCAPTCHA verification error: {e}")
        return False

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        data = {}
        if body and http_method == 'POST':
            try:
                data = json.loads(body)
            except:
                pass
        
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            return handle_login_page()
        elif path == '/dashboard':
            return handle_dashboard_page()
        elif path == '/api/login' and http_method == 'POST':
            user_ip = headers.get('x-forwarded-for', '').split(',')[0].strip()
            data['user_ip'] = user_ip
            return handle_user_login(data)
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/health':
            return handle_health_check()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Page not found</h1>'
            }
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Internal server error</h1>'
        }

def handle_home_page():
    """Handle home page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>IELTS GenAI Prep</title></head>
<body><h1>IELTS GenAI Prep</h1><p>AI-Powered IELTS Practice</p><a href="/login">Login</a></body></html>'''
    }

def handle_login_page():
    """Handle login page with environment variable for reCAPTCHA"""
    recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h2 class="card-title text-center mb-4">Login</h2>
                        
                        <form id="loginForm">
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" required>
                            </div>
                            
                            <div class="mb-3 text-center">
                                <div class="g-recaptcha" data-sitekey="{recaptcha_site_key}"></div>
                            </div>
                            
                            <button type="submit" class="btn btn-primary w-100">Sign In</button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">Test: test@ieltsgenaiprep.com / Test123!</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    document.getElementById('loginForm').addEventListener('submit', async function(e) {{
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const recaptchaResponse = grecaptcha.getResponse();
        
        try {{
            const response = await fetch('/api/login', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    email: email,
                    password: password,
                    recaptcha_response: recaptchaResponse
                }})
            }});
            
            const result = await response.json();
            
            if (response.ok) {{
                window.location.href = '/dashboard';
            }} else {{
                alert(result.message || 'Login failed');
                grecaptcha.reset();
            }}
        }} catch (error) {{
            alert('Login failed. Please try again.');
            grecaptcha.reset();
        }}
    }});
    </script>
</body>
</html>'''
    }

def handle_dashboard_page():
    """Handle dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body><h1>Dashboard</h1><p>Welcome to your IELTS GenAI Prep dashboard!</p></body></html>'''
    }

def handle_user_login(data):
    """Handle user login with reCAPTCHA verification"""
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    recaptcha_response = data.get('recaptcha_response', '')
    user_ip = data.get('user_ip')
    
    if not verify_recaptcha_v2(recaptcha_response, user_ip):
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Please complete the reCAPTCHA verification'})
        }
    
    if email == 'test@ieltsgenaiprep.com' and password == 'Test123!':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Login successful', 'redirect': '/dashboard'})
        }
    else:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Invalid email or password'})
        }

def handle_privacy_policy():
    """Handle privacy policy page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Privacy Policy - IELTS GenAI Prep</title></head>
<body><h1>Privacy Policy</h1><p>Privacy policy content here.</p></body></html>'''
    }

def handle_terms_of_service():
    """Handle terms of service page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Terms of Service - IELTS GenAI Prep</title></head>
<body><h1>Terms of Service</h1><p>Terms of service content here.</p></body></html>'''
    }

def handle_health_check():
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({{'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}})
    }
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as temp_file:
        zip_path = temp_file.name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
    
    return zip_path

def deploy_simple_working_login():
    """Deploy simple working login"""
    try:
        zip_path = create_simple_working_lambda()
        
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Deploying simple working login...")
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ Simple working login deployed!")
        print(f"Code size: {response['CodeSize']} bytes")
        print()
        print("Test at: https://www.ieltsaiprep.com/login")
        print("Email: test@ieltsgenaiprep.com")
        print("Password: Test123!")
        
        os.unlink(zip_path)
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        if 'zip_path' in locals():
            os.unlink(zip_path)
        return False

if __name__ == "__main__":
    deploy_simple_working_login()