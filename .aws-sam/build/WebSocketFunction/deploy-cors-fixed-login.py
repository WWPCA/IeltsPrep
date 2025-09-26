#!/usr/bin/env python3
"""
Deploy Lambda with CORS-enabled login that works from browser
"""
import boto3
import zipfile
import os

def create_cors_fixed_lambda():
    """Create Lambda with proper CORS headers and working login"""
    
    lambda_code = '''import json
import hashlib
from datetime import datetime

# Shared user database
class MockDynamoDBUsers:
    def __init__(self):
        self.users = {
            'test@ieltsgenaiprep.com': {
                'user_id': 'user_123',
                'email': 'test@ieltsgenaiprep.com',
                'password_hash': self.hash_password('testpassword123'),
                'created_at': '2025-01-01T00:00:00Z',
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

def get_cors_headers():
    """Return CORS headers for browser requests"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Max-Age': '86400'
    }

def lambda_handler(event, context):
    """Lambda handler with CORS support"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    body = event.get('body', '')
    
    # Handle preflight OPTIONS requests
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                **get_cors_headers(),
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    if path == '/api/login' and method == 'POST':
        try:
            data = json.loads(body) if body else {}
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return {
                    'statusCode': 400,
                    'headers': {
                        **get_cors_headers(),
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'success': False, 'message': 'Email and password required'})
                }
            
            user = user_db.get_user(email)
            if not user or not user_db.verify_password(password, user['password_hash']):
                return {
                    'statusCode': 401,
                    'headers': {
                        **get_cors_headers(),
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    **get_cors_headers(),
                    'Content-Type': 'application/json',
                    'Set-Cookie': f'web_session_id=session123; Path=/; HttpOnly; Secure'
                },
                'body': json.dumps({
                    'success': True, 
                    'message': 'Login successful',
                    'user_id': user['user_id']
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    **get_cors_headers(),
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'success': False, 'message': str(e)})
            }
    
    elif path == '/login':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': """<!DOCTYPE html>
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
                        <h6>New to IELTS GenAI Prep?</h6>
                        <p class="mb-2">To get started, you need to:</p>
                        <ol class="mb-2">
                            <li>Download our mobile app (iOS/Android)</li>
                            <li>Create an account and purchase assessments</li>
                            <li>Return here to access your assessments on desktop</li>
                        </ol>
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
        
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showMessage('Please fill in all fields', 'danger');
                return;
            }
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            
            try {
                // Use same-origin /api/login endpoint with CORS support
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
                
                const result = await response.json();
                
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
                showMessage('Please check your credentials and try again.', 'danger');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Sign In';
            }
        });
    });
    </script>
</body>
</html>"""
        }
    
    elif path == '/dashboard':
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
    </div>
</body>
</html>"""
        }
    
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {
                **get_cors_headers(),
                'Content-Type': 'application/json'
            },
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
        }'''
    
    with zipfile.ZipFile('lambda-cors-fixed.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    return 'lambda-cors-fixed.zip'

def deploy_cors_fixed():
    """Deploy Lambda with CORS-enabled login"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        zip_path = create_cors_fixed_lambda()
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Deploying CORS-fixed login Lambda...")
        
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        os.remove(zip_path)
        print("CORS-fixed login deployed!")
        return True
        
    except Exception as e:
        print(f"Deploy failed: {e}")
        return False

if __name__ == "__main__":
    deploy_cors_fixed()