#!/usr/bin/env python3
"""
Fix Lambda syntax error and redeploy
"""
import boto3
import zipfile

def create_fixed_lambda():
    """Create Lambda with fixed syntax"""
    
    # Read all template files
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    with open('complete-login-template.html', 'r', encoding='utf-8') as f:
        login_content = f.read()
    
    with open('complete-privacy-policy.html', 'r', encoding='utf-8') as f:
        privacy_content = f.read()
    
    with open('complete-terms-of-service.html', 'r', encoding='utf-8') as f:
        terms_content = f.read()
    
    # Create Lambda function code with proper escaping
    lambda_code = '''import json

def lambda_handler(event, context):
    """Lambda handler serving all comprehensive templates"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    print(f"Processing {method} {path}")
    
    # Define all HTML templates
    home_html = """''' + home_content.replace('\\', '\\\\').replace('"', '\\"').replace('"""', '\\"\\"\\"') + '''"""
    
    login_html = """''' + login_content.replace('\\', '\\\\').replace('"', '\\"').replace('"""', '\\"\\"\\"') + '''"""
    
    privacy_html = """''' + privacy_content.replace('\\', '\\\\').replace('"', '\\"').replace('"""', '\\"\\"\\"') + '''"""
    
    terms_html = """''' + terms_content.replace('\\', '\\\\').replace('"', '\\"').replace('"""', '\\"\\"\\"') + '''"""
    
    # Dashboard template
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Roboto', sans-serif; background: #f8f9fa; }
        .navbar { background-color: #fff !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .assessment-card { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/"><i class="fas fa-graduation-cap me-2"></i>IELTS GenAI Prep</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1 class="mb-4">Your Assessment Dashboard</h1>
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            Welcome! Your purchased assessments will appear here once you complete the mobile app purchase verification.
        </div>
        
        <div class="row">
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-pen-fancy fa-3x text-primary mb-3"></i>
                        <h5>Academic Writing</h5>
                        <p class="text-muted small">TrueScore® Assessment</p>
                        <span class="badge bg-secondary">Coming Soon</span>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-microphone fa-3x text-success mb-3"></i>
                        <h5>Academic Speaking</h5>
                        <p class="text-muted small">ClearScore® Assessment</p>
                        <span class="badge bg-secondary">Coming Soon</span>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-pen-fancy fa-3x text-warning mb-3"></i>
                        <h5>General Writing</h5>
                        <p class="text-muted small">TrueScore® Assessment</p>
                        <span class="badge bg-secondary">Coming Soon</span>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-microphone fa-3x text-info mb-3"></i>
                        <h5>General Speaking</h5>
                        <p class="text-muted small">ClearScore® Assessment</p>
                        <span class="badge bg-secondary">Coming Soon</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    # Route handling
    if path == '/' or path == '/index.html':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': home_html
        }
    
    elif path == '/login':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': login_html
        }
    
    elif path == '/dashboard':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': dashboard_html
        }
    
    elif path == '/privacy-policy':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': privacy_html
        }
    
    elif path == '/terms-of-service':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': terms_html
        }
    
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy', 'service': 'IELTS GenAI Prep API'})
        }
    
    else:
        return {
            'statusCode': 302,
            'headers': {'Location': '/'},
            'body': ''
        }
'''
    
    # Create deployment package
    with zipfile.ZipFile('fixed-lambda.zip', 'w') as zip_file:
        zip_file.writestr('simple_lambda.py', lambda_code)
    
    print("Fixed Lambda package created successfully")
    return True

def deploy_fixed_lambda():
    """Deploy the fixed Lambda function"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        with open('fixed-lambda.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        
        return True
        
    except Exception as e:
        print(f"Error updating Lambda function: {e}")
        return False

if __name__ == "__main__":
    print("Fixing Lambda syntax error...")
    if create_fixed_lambda():
        print("Deploying fixed Lambda...")
        if deploy_fixed_lambda():
            print("Lambda fix deployed successfully!")
            print("Website should now be accessible at:")
            print("- https://www.ieltsaiprep.com/")
            print("- https://ieltsaiprep.com/")
        else:
            print("Deployment failed")
    else:
        print("Package creation failed")