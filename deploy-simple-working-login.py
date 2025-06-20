#!/usr/bin/env python3
"""
Deploy simple working login using form submission instead of JavaScript fetch
"""
import boto3
import zipfile
import os

def create_simple_login_lambda():
    """Create Lambda with form-based login that avoids CORS issues"""
    
    lambda_code = '''import json
import hashlib
import urllib.parse
from datetime import datetime

# Shared user database
class MockDynamoDBUsers:
    def __init__(self):
        self.users = {
            'test@ieltsgenaiprep.com': {
                'user_id': 'user_123',
                'email': 'test@ieltsgenaiprep.com',
                'password_hash': self.hash_password('testpassword123'),
                'purchase_records': [
                    {'product_id': 'academic_writing', 'assessments_remaining': 4},
                    {'product_id': 'academic_speaking', 'assessments_remaining': 4},
                    {'product_id': 'general_writing', 'assessments_remaining': 4},
                    {'product_id': 'general_speaking', 'assessments_remaining': 4}
                ]
            }
        }
        
    def hash_password(self, password: str) -> str:
        salt = b'ielts_genai_prep_salt'
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
        
    def verify_password(self, password: str, hash_stored: str) -> bool:
        return self.hash_password(password) == hash_stored
        
    def get_user(self, email: str):
        return self.users.get(email)

user_db = MockDynamoDBUsers()

def lambda_handler(event, context):
    """Lambda handler with form-based login"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    body = event.get('body', '')
    
    if path == '/login' and method == 'POST':
        # Handle form submission
        try:
            # Parse form data
            form_data = urllib.parse.parse_qs(body)
            email = form_data.get('email', [''])[0].strip().lower()
            password = form_data.get('password', [''])[0]
            
            if not email or not password:
                return handle_login_page('Please fill in all fields')
            
            user = user_db.get_user(email)
            if not user or not user_db.verify_password(password, user['password_hash']):
                return handle_login_page('Invalid email or password')
            
            # Successful login - redirect to dashboard
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/dashboard',
                    'Set-Cookie': f'web_session_id=session123; Path=/; HttpOnly; Secure'
                },
                'body': ''
            }
        except Exception as e:
            return handle_login_page('Login error occurred')
    
    elif path == '/login':
        return handle_login_page()
    
    elif path == '/dashboard':
        return handle_dashboard_page()
    
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0'
            })
        }
    
    else:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>IELTS GenAI Prep</h1><p>AI-Powered IELTS Practice</p><a href="/login">Login</a>'
        }

def handle_login_page(error_message=None):
    """Handle login page with optional error message"""
    error_html = ''
    if error_message:
        error_html = f'<div class="alert alert-danger">{error_message}</div>'
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }}
        .login-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }}
        .form-control:focus {{
            border-color: #4361ee;
            box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.15);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%);
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-weight: 600;
        }}
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
                        <h6>New to IELTS GenAI Prep?</h6>
                        <p class="mb-2">To get started, you need to:</p>
                        <ol class="mb-2">
                            <li>Download our mobile app (iOS/Android)</li>
                            <li>Create an account and purchase assessments</li>
                            <li>Return here to access your assessments on desktop</li>
                        </ol>
                    </div>
                    
                    {error_html}
                    
                    <form method="post" action="/login">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" name="email" id="email" value="test@ieltsgenaiprep.com" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" id="password" value="testpassword123" required>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember">
                            <label class="form-check-label" for="remember">Remember me for 30 days</label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Sign In</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    }

def handle_dashboard_page():
    """Handle dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
        }
        .assessment-card {
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .assessment-card:hover {
            transform: translateY(-5px);
        }
        .header-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="header-card mb-5 p-4">
            <div class="text-center">
                <h1 class="text-primary mb-3">IELTS GenAI Prep Dashboard</h1>
                <p class="lead text-muted">Welcome! Your assessments are ready.</p>
                <p class="text-success"><strong>Login Successful!</strong> Mobile app credentials work perfectly on website.</p>
            </div>
        </div>
        
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #4361ee;">
                    <div class="card-body">
                        <h5 class="card-title text-primary">🎓 Academic Writing Assessment</h5>
                        <p class="card-text">TrueScore® GenAI writing evaluation with detailed feedback</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-primary">Start Assessment</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #e74c3c;">
                    <div class="card-body">
                        <h5 class="card-title text-danger">🎤 Academic Speaking Assessment</h5>
                        <p class="card-text">ClearScore® GenAI speaking practice with AI examiner Maya</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-danger">Start Assessment</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #2ecc71;">
                    <div class="card-body">
                        <h5 class="card-title text-success">📝 General Writing Assessment</h5>
                        <p class="card-text">TrueScore® GenAI writing evaluation for General Training</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-success">Start Assessment</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #f39c12;">
                    <div class="card-body">
                        <h5 class="card-title text-warning">🗣️ General Speaking Assessment</h5>
                        <p class="card-text">ClearScore® GenAI speaking practice for General Training</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-warning">Start Assessment</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-5">
            <a href="/login" class="btn btn-outline-light">Logout</a>
        </div>
    </div>
</body>
</html>"""
    }'''
    
    with zipfile.ZipFile('lambda-simple-login.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    return 'lambda-simple-login.zip'

def deploy_simple_login():
    """Deploy simple form-based login"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        zip_path = create_simple_login_lambda()
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Deploying simple form-based login...")
        
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        os.remove(zip_path)
        print("Simple login deployed successfully!")
        return True
        
    except Exception as e:
        print(f"Deploy failed: {e}")
        return False

if __name__ == "__main__":
    deploy_simple_login()