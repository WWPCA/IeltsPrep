#!/usr/bin/env python3
"""
Deploy comprehensive login template to AWS Lambda production
Fixes the login page to match the approved comprehensive design
"""
import boto3
import json
import zipfile
import base64

def deploy_complete_login_template():
    """Deploy Lambda with comprehensive login template matching approved design"""
    
    # Read the comprehensive login template
    with open('login.html', 'r', encoding='utf-8') as f:
        login_template = f.read()
    
    # Verify login template has proper styling
    if 'bootstrap' not in login_template.lower():
        print("ERROR: Login template missing Bootstrap styling!")
        return False
    
    if 'mobile app' not in login_template.lower():
        print("ERROR: Login template missing mobile app instructions!")
        return False
    
    print("Login template verified with comprehensive design")
    
    # Read the working home page template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        home_template = f.read()
    
    # Verify home template has correct pricing
    if '$49.99' not in home_template:
        print("ERROR: Home template does not contain correct $49.99 pricing!")
        return False
    
    pricing_count = home_template.count('$49.99')
    if pricing_count < 4:
        print(f"ERROR: Home template only has {pricing_count} instances of $49.99!")
        return False
    
    print(f"Home template verified: Found {pricing_count} instances of $49.99 pricing")
    
    # Encode templates
    home_b64 = base64.b64encode(home_template.encode('utf-8')).decode('ascii')
    login_b64 = base64.b64encode(login_template.encode('utf-8')).decode('ascii')
    
    # Create comprehensive dashboard template
    dashboard_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
        }
        .dashboard-container {
            padding: 40px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .dashboard-header {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .assessment-card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        .assessment-card:hover {
            transform: translateY(-2px);
        }
        .assessment-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        .assessment-description {
            color: #666;
            margin-bottom: 15px;
        }
        .assessment-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .assessment-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        .back-button {
            background: #6c757d;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <a href="/" class="back-button">
            <i class="fas fa-arrow-left"></i> Back to Home
        </a>
        
        <div class="dashboard-header">
            <h1><i class="fas fa-tachometer-alt"></i> Your Assessment Dashboard</h1>
            <p>Welcome back! Your purchased assessments are ready to use.</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="assessment-card">
                    <div class="assessment-title">
                        <i class="fas fa-pen-fancy text-primary"></i> Academic Writing Assessment
                    </div>
                    <div class="assessment-description">
                        TrueScore® GenAI powered writing evaluation with detailed feedback
                    </div>
                    <button class="assessment-button">
                        <i class="fas fa-play"></i> Start Assessment
                    </button>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="assessment-card">
                    <div class="assessment-title">
                        <i class="fas fa-comments text-success"></i> Academic Speaking Assessment
                    </div>
                    <div class="assessment-description">
                        ClearScore® GenAI conversation with Maya AI examiner
                    </div>
                    <button class="assessment-button">
                        <i class="fas fa-play"></i> Start Assessment
                    </button>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="assessment-card">
                    <div class="assessment-title">
                        <i class="fas fa-edit text-warning"></i> General Writing Assessment
                    </div>
                    <div class="assessment-description">
                        TrueScore® GenAI evaluation for General Training writing
                    </div>
                    <button class="assessment-button">
                        <i class="fas fa-play"></i> Start Assessment
                    </button>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="assessment-card">
                    <div class="assessment-title">
                        <i class="fas fa-microphone text-info"></i> General Speaking Assessment
                    </div>
                    <div class="assessment-description">
                        ClearScore® GenAI conversation for General Training speaking
                    </div>
                    <button class="assessment-button">
                        <i class="fas fa-play"></i> Start Assessment
                    </button>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-4">
            <p class="text-white">
                <i class="fas fa-info-circle"></i> 
                Each assessment provides detailed feedback and scoring
            </p>
        </div>
    </div>
</body>
</html>"""
    
    dashboard_b64 = base64.b64encode(dashboard_template.encode('utf-8')).decode('ascii')
    
    # Create Lambda function with comprehensive templates
    lambda_code = f'''
import json
import base64
import hashlib
import bcrypt
import time
import uuid
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """AWS Lambda handler with comprehensive templates"""
    try:
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {{}}).get('http', {{}}).get('method', 'GET'))
        body = event.get('body', '{{}}')
        headers = event.get('headers', {{}})
        
        # Parse request body
        try:
            data = json.loads(body) if body else {{}}
        except json.JSONDecodeError:
            data = {{}}
        
        print(f"[LAMBDA] Processing {{method}} {{path}}")
        
        # Route handling
        if path == '/':
            return serve_home_page()
        elif path == '/login':
            return serve_login_page()
        elif path == '/dashboard':
            return serve_dashboard_page(headers)
        elif path.startswith('/api/login') and method == 'POST':
            return handle_login_api(data, headers)
        elif path == '/health':
            return handle_health_check()
        else:
            return serve_home_page()
            
    except Exception as e:
        print(f"[ERROR] Lambda error: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Internal server error'}})
        }}

def serve_home_page():
    """Serve comprehensive home page with correct $49.99 pricing"""
    template_b64 = "{home_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_login_page():
    """Serve comprehensive login page with mobile-first design"""
    template_b64 = "{login_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_dashboard_page(headers):
    """Serve comprehensive dashboard page"""
    template_b64 = "{dashboard_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def handle_login_api(data, headers):
    """Handle login API with test credentials"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Test credentials
        if email == 'test@ieltsgenaiprep.com' and password == 'testpassword123':
            return {{
                'statusCode': 200,
                'headers': {{
                    'Content-Type': 'application/json',
                    'Set-Cookie': 'web_session_id=test_session_123; Path=/; HttpOnly; Secure'
                }},
                'body': json.dumps({{
                    'success': True,
                    'message': 'Login successful',
                    'redirect': '/dashboard'
                }})
            }}
        else:
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{
                    'success': False,
                    'message': 'Invalid credentials. Use test@ieltsgenaiprep.com / testpassword123'
                }})
            }}
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{
                'success': False,
                'message': 'Login error occurred'
            }})
        }}

def handle_health_check():
    """Health check endpoint"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'application/json'}},
        'body': json.dumps({{
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }})
    }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('complete-login-template.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('complete-login-template.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying comprehensive login template...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Deployment completed!')
    
    # Verify deployment
    import time
    time.sleep(5)
    
    import requests
    try:
        # Test home page
        home_response = requests.get('https://www.ieltsaiprep.com/')
        if '$49.99' in home_response.text and home_response.text.count('$49.99') >= 4:
            print('SUCCESS: Home page verified with correct $49.99 pricing')
        else:
            print('WARNING: Home page pricing may be incorrect')
        
        # Test login page
        login_response = requests.get('https://www.ieltsaiprep.com/login')
        if 'bootstrap' in login_response.text.lower() and 'mobile-first' in login_response.text.lower():
            print('SUCCESS: Login page verified with comprehensive design')
        else:
            print('WARNING: Login page may not have comprehensive design')
            
        return True
        
    except Exception as e:
        print(f'Could not verify deployment: {e}')
        return False

if __name__ == "__main__":
    deploy_complete_login_template()