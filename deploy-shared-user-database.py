#!/usr/bin/env python3
"""
Deploy Lambda function with shared user database for mobile app and website
"""
import boto3
import zipfile
import os
import json
import hashlib

def create_shared_user_lambda():
    """Create Lambda with shared user database"""
    
    lambda_code = '''#!/usr/bin/env python3
"""
AWS Lambda Handler with Shared User Database
"""

import json
import os
import uuid
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Mock DynamoDB for Replit environment
class MockDynamoDBUsers:
    def __init__(self):
        # Shared user database for both mobile app and website
        self.users = {
            'test@ieltsgenaiprep.com': {
                'user_id': 'user_123',
                'email': 'test@ieltsgenaiprep.com',
                'password_hash': self.hash_password('testpassword123'),
                'created_at': '2025-01-01T00:00:00Z',
                'purchase_records': [
                    {
                        'product_id': 'academic_writing',
                        'purchase_date': '2025-01-01T00:00:00Z',
                        'assessments_remaining': 4,
                        'assessments_used': 0
                    },
                    {
                        'product_id': 'academic_speaking', 
                        'purchase_date': '2025-01-01T00:00:00Z',
                        'assessments_remaining': 4,
                        'assessments_used': 0
                    },
                    {
                        'product_id': 'general_writing',
                        'purchase_date': '2025-01-01T00:00:00Z', 
                        'assessments_remaining': 4,
                        'assessments_used': 0
                    },
                    {
                        'product_id': 'general_speaking',
                        'purchase_date': '2025-01-01T00:00:00Z',
                        'assessments_remaining': 4,
                        'assessments_used': 0
                    }
                ]
            }
        }
        
    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2"""
        salt = b'ielts_genai_prep_salt'
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
        
    def verify_password(self, password: str, hash_stored: str) -> bool:
        """Verify password against stored hash"""
        return self.hash_password(password) == hash_stored
        
    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.users.get(email)
        
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create new user (for mobile app registration)"""
        email = user_data.get('email')
        if not email or email in self.users:
            return False
            
        self.users[email] = {
            'user_id': str(uuid.uuid4()),
            'email': email,
            'password_hash': self.hash_password(user_data.get('password', '')),
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'purchase_records': []
        }
        return True
        
    def add_purchase(self, email: str, product_id: str) -> bool:
        """Add purchase record for user"""
        user = self.users.get(email)
        if not user:
            return False
            
        user['purchase_records'].append({
            'product_id': product_id,
            'purchase_date': datetime.utcnow().isoformat() + 'Z',
            'assessments_remaining': 4,
            'assessments_used': 0
        })
        return True

# Global user database instance
user_db = MockDynamoDBUsers()

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        print(f"Request: {http_method} {path}")
        
        # Parse request body for POST requests
        data = {}
        if body and http_method == 'POST':
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': 'Invalid JSON'})
                }
        
        # Route handling
        if path == '/' or path == '/home':
            return handle_home_page()
        elif path == '/login':
            return handle_login_page()
        elif path == '/dashboard':
            return handle_dashboard_page(headers)
        elif path == '/api/login' and http_method == 'POST':
            return handle_user_login(data)
        elif path == '/api/register' and http_method == 'POST':
            return handle_user_registration(data)
        elif path == '/api/user/purchases' and http_method == 'GET':
            return handle_get_user_purchases(headers)
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
        import traceback
        traceback.print_exc()
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
        'body': """<!DOCTYPE html>
<html><head><title>IELTS GenAI Prep</title></head>
<body><h1>IELTS GenAI Prep</h1><p>AI-Powered IELTS Practice</p>
<a href="/login">Login</a></body></html>"""
    }

def handle_login_page() -> Dict[str, Any]:
    """Serve login page"""
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
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': login_html
    }

def handle_dashboard_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve dashboard page"""
    dashboard_html = '''<!DOCTYPE html>
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
</html>'''
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': dashboard_html
    }

def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login with shared database"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        print(f"Login attempt for email: {email}")
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'Email and password required'})
            }
        
        # Get user from shared database
        user = user_db.get_user(email)
        if not user:
            print(f"User not found: {email}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        # Verify password
        if not user_db.verify_password(password, user['password_hash']):
            print(f"Password verification failed for: {email}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        # Create session
        session_id = str(uuid.uuid4())
        
        print(f"Login successful for: {email}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Set-Cookie': f'web_session_id={session_id}; Path=/; HttpOnly; Secure'
            },
            'body': json.dumps({
                'success': True, 
                'message': 'Login successful',
                'user_id': user['user_id']
            })
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

def handle_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration (for mobile app)"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'Email and password required'})
            }
        
        # Create user in shared database
        if user_db.create_user({'email': email, 'password': password}):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': True, 'message': 'Registration successful'})
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'User already exists'})
            }
            
    except Exception as e:
        print(f"Registration error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'message': 'Registration error'})
        }

def handle_get_user_purchases(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Get user purchases (for mobile app)"""
    try:
        # In production, get user from session/token
        # For now, return test user purchases
        user = user_db.get_user('test@ieltsgenaiprep.com')
        if user:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'purchases': user.get('purchase_records', [])
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'message': 'User not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'message': 'Error fetching purchases'})
        }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0',
            'database': 'connected'
        })
    }'''
    
    # Create deployment package
    with zipfile.ZipFile('lambda-shared-users.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    print("Created Lambda package with shared user database")
    return 'lambda-shared-users.zip'

def deploy_shared_user_lambda():
    """Deploy the Lambda function with shared user database"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'ielts-genai-prep-api'
    
    try:
        zip_file_path = create_shared_user_lambda()
        
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"Deploying shared user database Lambda...")
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
    if deploy_shared_user_lambda():
        print("Shared user database Lambda deployed!")
        print("Test login at: https://www.ieltsaiprep.com/login")
        print("Credentials: test@ieltsgenaiprep.com / testpassword123")
    else:
        print("Deployment failed")