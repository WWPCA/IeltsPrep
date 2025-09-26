#!/usr/bin/env python3
"""
Deploy working login using the same pattern as previous successful deployments
"""
import boto3
import zipfile
import os
import tempfile

def create_working_login_lambda():
    """Create Lambda with working login using proven pattern"""
    
    # Use the same working pattern from previous deployments
    lambda_code = '''import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v2 response with Google"""
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
    """Main AWS Lambda handler"""
    try:
        # Get request information
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Parse request body for POST requests
        data = {}
        if body and http_method == 'POST':
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                pass
        
        # Route handling
        if path == '/' or path == '/home':
            return handle_home_page()
        elif path == '/login':
            return handle_login_page()
        elif path == '/dashboard':
            return handle_dashboard_page(headers)
        elif path == '/api/login' and http_method == 'POST':
            user_ip = headers.get('x-forwarded-for', headers.get('x-real-ip', headers.get('remote-addr')))
            if user_ip and ',' in user_ip:
                user_ip = user_ip.split(',')[0].strip()
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
        print(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }

def handle_home_page() -> Dict[str, Any]:
    """Handle home page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>IELTS GenAI Prep</title></head>
<body><h1>IELTS GenAI Prep</h1><p>AI-Powered IELTS Practice</p><a href="/login">Login</a></body></html>'''
    }

def handle_login_page() -> Dict[str, Any]:
    """Handle login page using environment variable for reCAPTCHA"""
    
    # Get reCAPTCHA site key from environment
    recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
    
    # Simple template without f-string formatting
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }
        .form-control:focus {
            border-color: #4361ee;
            box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.15);
        }
        .btn-primary {
            background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%);
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <h2 class="text-center mb-4">Welcome Back</h2>
                    <p class="text-center text-muted mb-4">Sign in to your IELTS GenAI Prep account</p>
                    
                    <form id="loginForm">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" required>
                        </div>
                        
                        <div class="mb-3 d-flex justify-content-center">
                            <div class="g-recaptcha" data-sitekey="''' + recaptcha_site_key + '''"></div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">Sign In</button>
                        
                        <div class="text-center">
                            <small class="text-muted">
                                New user? <a href="#" class="text-primary">Download our mobile app</a>
                            </small>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('loginForm');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const recaptchaResponse = grecaptcha.getResponse();
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password,
                        recaptcha_response: recaptchaResponse
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    alert(result.message || 'Login failed');
                    grecaptcha.reset();
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed. Please try again.');
                grecaptcha.reset();
            }
        });
    });
    </script>
</body>
</html>'''
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html_content
    }

def handle_dashboard_page(headers) -> Dict[str, Any]:
    """Handle dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body><h1>Dashboard</h1><p>Welcome to your IELTS GenAI Prep dashboard!</p></body></html>'''
    }

def handle_user_login(data) -> Dict[str, Any]:
    """Handle user login"""
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    recaptcha_response = data.get('recaptcha_response', '')
    user_ip = data.get('user_ip')
    
    # Verify reCAPTCHA
    if not verify_recaptcha_v2(recaptcha_response, user_ip):
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Please complete the reCAPTCHA verification'})
        }
    
    # Simple test user authentication
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

def handle_privacy_policy() -> Dict[str, Any]:
    """Handle privacy policy page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Privacy Policy - IELTS GenAI Prep</title></head>
<body><h1>Privacy Policy</h1><p>Privacy policy content here.</p></body></html>'''
    }

def handle_terms_of_service() -> Dict[str, Any]:
    """Handle terms of service page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Terms of Service - IELTS GenAI Prep</title></head>
<body><h1>Terms of Service</h1><p>Terms of service content here.</p></body></html>'''
    }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '3.0'
        })
    }
'''
    
    # Create deployment package
    with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as temp_file:
        zip_path = temp_file.name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
    
    return zip_path

def deploy_working_login():
    """Deploy working login using previous successful pattern"""
    try:
        zip_path = create_working_login_lambda()
        
        # Deploy to AWS Lambda
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Deploying working login Lambda...")
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ Working login deployed successfully!")
        print(f"✅ Code size: {response['CodeSize']} bytes")
        print(f"✅ Last modified: {response['LastModified']}")
        print()
        print("🧪 Test the login page:")
        print("   URL: https://www.ieltsaiprep.com/login")
        print("   Email: test@ieltsgenaiprep.com")
        print("   Password: Test123!")
        
        os.unlink(zip_path)
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        if 'zip_path' in locals():
            os.unlink(zip_path)
        return False

if __name__ == "__main__":
    deploy_working_login()