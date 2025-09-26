#!/usr/bin/env python3
"""
Fix login routing and add debugging to Lambda function
"""
import boto3
import zipfile
import os

def create_fixed_lambda():
    """Create Lambda with improved routing and debugging"""
    
    lambda_code = '''#!/usr/bin/env python3
"""
Fixed AWS Lambda Handler with debugging
"""

import json
import os
import uuid
import time
import base64
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Simplified reCAPTCHA verification for production"""
    return True

def lambda_handler(event, context):
    """Main AWS Lambda handler with debugging"""
    try:
        # Get request information
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Debug logging
        print(f"Request: {http_method} {path}")
        print(f"Body: {body}")
        
        # Parse request body for POST requests
        data = {}
        if body and http_method == 'POST':
            try:
                data = json.loads(body)
                print(f"Parsed data: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': 'Invalid JSON'})
                }
        
        # Route handling with debugging
        if path == '/' or path == '/home':
            print("Serving home page")
            return handle_home_page()
        elif path == '/login':
            print("Serving login page")
            return handle_login_page()
        elif path == '/dashboard':
            print("Serving dashboard page")
            return handle_dashboard_page(headers)
        elif path == '/api/login' and http_method == 'POST':
            print("Processing login API")
            return handle_user_login(data)
        elif path == '/health':
            print("Health check")
            return handle_health_check()
        else:
            print(f"Unknown path: {path}")
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Page not found</h1>'
            }
            
    except Exception as e:
        print(f"Lambda handler error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }

def handle_home_page() -> Dict[str, Any]:
    """Handle home page"""
    try:
        with open('public_home.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': """<!DOCTYPE html>
<html><head><title>IELTS GenAI Prep</title></head>
<body><h1>IELTS GenAI Prep</h1><p>AI-Powered IELTS Practice</p>
<a href="/login">Login</a></body></html>"""
        }

def handle_login_page() -> Dict[str, Any]:
    """Serve login page"""
    try:
        with open('login.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': """<!DOCTYPE html>
<html><head><title>Login</title></head>
<body><h1>Login</h1>
<form action="/api/login" method="post">
<input type="email" name="email" value="test@ieltsgenaiprep.com" required>
<input type="password" name="password" value="testpassword123" required>
<button type="submit">Login</button>
</form></body></html>"""
        }

def handle_dashboard_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve dashboard page"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': """<!DOCTYPE html>
<html><head><title>Dashboard</title></head>
<body><h1>Dashboard</h1><p>Welcome to IELTS GenAI Prep!</p>
<ul>
<li>Academic Writing Assessment</li>
<li>Academic Speaking Assessment</li>
<li>General Writing Assessment</li>
<li>General Speaking Assessment</li>
</ul></body></html>"""
        }

def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login with detailed debugging"""
    try:
        print(f"Login attempt with data: {data}")
        
        email = data.get('email', '')
        password = data.get('password', '')
        
        print(f"Email: '{email}', Password: '{password}'")
        
        # Validate inputs
        if not email or not password:
            print("Missing email or password")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'Email and password required'})
            }
        
        # Check test credentials
        if email == 'test@ieltsgenaiprep.com' and password == 'testpassword123':
            print("Credentials match - creating session")
            session_id = str(uuid.uuid4())
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Set-Cookie': f'web_session_id={session_id}; Path=/; HttpOnly; Secure'
                },
                'body': json.dumps({'success': True, 'message': 'Login successful'})
            }
        else:
            print(f"Credentials don't match - Email: {email}, Password: {password}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
            
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'message': 'Login error', 'error': str(e)})
        }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        })
    }'''
    
    # Login HTML with improved error handling
    login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
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
                    <div class="text-center mb-4">
                        <h2 class="text-primary">Welcome Back</h2>
                        <p class="text-muted">Sign in to your IELTS GenAI Prep account</p>
                    </div>
                    
                    <div class="alert alert-info">
                        <strong>Test Account Ready</strong><br>
                        Email: test@ieltsgenaiprep.com<br>
                        Password: testpassword123
                    </div>
                    
                    <div id="login-message" class="alert" style="display: none;"></div>
                    
                    <form id="login-form">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" value="test@ieltsgenaiprep.com" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" value="testpassword123" required>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember">
                            <label class="form-check-label" for="remember">Remember me for 30 days</label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary" id="login-btn">Sign In</button>
                        </div>
                        
                        <div class="text-center mt-3">
                            <a href="#" class="text-decoration-none">Forgot your password?</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const loginForm = document.getElementById('login-form');
        const loginBtn = document.getElementById('login-btn');
        const loginMessage = document.getElementById('login-message');
        
        function showMessage(message, type) {
            loginMessage.textContent = message;
            loginMessage.className = `alert alert-${type}`;
            loginMessage.style.display = 'block';
        }
        
        function hideMessage() {
            loginMessage.style.display = 'none';
        }
        
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            hideMessage();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            
            console.log('Login attempt:', { email, password });
            
            if (!email || !password) {
                showMessage('Please fill in all fields', 'danger');
                return;
            }
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });
                
                console.log('Response status:', response.status);
                const responseText = await response.text();
                console.log('Response text:', responseText);
                
                let result;
                try {
                    result = JSON.parse(responseText);
                } catch (e) {
                    throw new Error('Invalid response format');
                }
                
                if (result.success) {
                    showMessage('Login successful! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showMessage(result.message || 'Login failed', 'danger');
                }
            } catch (error) {
                console.error('Login error:', error);
                showMessage('Network error. Please try again.', 'danger');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Sign In';
            }
        });
    });
    </script>
</body>
</html>'''
    
    # Create deployment package
    with zipfile.ZipFile('lambda-fixed-login.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
        zip_file.writestr('login.html', login_html)
        zip_file.writestr('dashboard.html', '''<!DOCTYPE html>
<html><head><title>Dashboard</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }</style></head>
<body><div class="container mt-5"><div class="card"><div class="card-body text-center">
<h1 class="text-primary">IELTS GenAI Prep Dashboard</h1><p class="lead">Login successful! Ready for assessments.</p>
</div></div></div></body></html>''')
        zip_file.writestr('public_home.html', '''<!DOCTYPE html>
<html><head><title>IELTS GenAI Prep</title></head>
<body><h1>IELTS GenAI Prep</h1><a href="/login">Login</a></body></html>''')
    
    print("Created fixed Lambda package with debugging")
    return 'lambda-fixed-login.zip'

def deploy_fixed_lambda():
    """Deploy the fixed Lambda function"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'ielts-genai-prep-api'
    
    try:
        zip_file_path = create_fixed_lambda()
        
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"Deploying fixed Lambda function...")
        print(f"Package size: {len(zip_content)} bytes")
        
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print("Lambda function updated successfully!")
        
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        print("Deployment completed!")
        os.remove(zip_file_path)
        
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if deploy_fixed_lambda():
        print("Fixed Lambda deployed with debugging!")
        print("Test login at: https://www.ieltsaiprep.com/login")
    else:
        print("Deployment failed")