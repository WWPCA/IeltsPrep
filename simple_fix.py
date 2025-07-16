#!/usr/bin/env python3
import boto3
import zipfile

def deploy_simple_fix():
    # Create Lambda code with correct pricing display
    lambda_code = """import json

def lambda_handler(event, context):
    path = event.get('path', '/')
    
    if path == '/':
        return home_page()
    elif path == '/login':
        return login_page()
    elif path == '/dashboard':
        return dashboard_page()
    else:
        return home_page()

def home_page():
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="/">IELTS GenAI Prep</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/login">Login</a>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <h1 class="text-center mb-5">GenAI Assessed IELTS Modules</h1>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header bg-success text-white text-center">
                        <h3>Academic Writing</h3>
                    </div>
                    <div class="card-body text-center">
                        <h1 class="text-success">$49.99<small class="text-muted"> for 4 assessments</small></h1>
                        <p>TrueScore GenAI Writing Assessment</p>
                        <ul class="list-unstyled">
                            <li>4 Unique Assessments Included</li>
                            <li>Task 1 & Task 2 Assessment</li>
                            <li>TrueScore GenAI Evaluation</li>
                        </ul>
                        <button class="btn btn-success">Purchase Now</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header bg-success text-white text-center">
                        <h3>General Writing</h3>
                    </div>
                    <div class="card-body text-center">
                        <h1 class="text-success">$49.99<small class="text-muted"> for 4 assessments</small></h1>
                        <p>TrueScore GenAI Writing Assessment</p>
                        <ul class="list-unstyled">
                            <li>4 Unique Assessments Included</li>
                            <li>Letters & Essays Assessment</li>
                            <li>TrueScore GenAI Evaluation</li>
                        </ul>
                        <button class="btn btn-success">Purchase Now</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header bg-primary text-white text-center">
                        <h3>Academic Speaking</h3>
                    </div>
                    <div class="card-body text-center">
                        <h1 class="text-primary">$49.99<small class="text-muted"> for 4 assessments</small></h1>
                        <p>ClearScore GenAI Speaking Assessment</p>
                        <ul class="list-unstyled">
                            <li>4 Unique Assessments Included</li>
                            <li>All 3 speaking parts covered</li>
                            <li>ClearScore GenAI Analysis</li>
                        </ul>
                        <button class="btn btn-primary">Purchase Now</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header bg-primary text-white text-center">
                        <h3>General Speaking</h3>
                    </div>
                    <div class="card-body text-center">
                        <h1 class="text-primary">$49.99<small class="text-muted"> for 4 assessments</small></h1>
                        <p>ClearScore GenAI Speaking Assessment</p>
                        <ul class="list-unstyled">
                            <li>4 Unique Assessments Included</li>
                            <li>General Training Topics</li>
                            <li>ClearScore GenAI Analysis</li>
                        </ul>
                        <button class="btn btn-primary">Purchase Now</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info mt-5">
            <h5>How to Get Started</h5>
            <p>Download our mobile app to purchase assessments for $49.99.00 each</p>
            <ol>
                <li>Download mobile app (iOS/Android)</li>
                <li>Create account and purchase assessments</li>
                <li>Access on mobile and desktop platforms</li>
            </ol>
        </div>
    </div>
</body>
</html>'''
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html
    }

def login_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title></head>
<body style="padding: 40px;">
<h2>Login</h2>
<p>Test credentials: test@ieltsgenaiprep.com / testpassword123</p>
<a href="/">Back to Home</a>
</body></html>'''
    }

def dashboard_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '''<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body style="padding: 40px;">
<h2>Dashboard</h2>
<p>Your assessments are ready!</p>
<a href="/">Back to Home</a>
</body></html>'''
    }
"""

    # Create deployment package
    with zipfile.ZipFile('pricing-fix.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)

    # Deploy to Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')

    with open('pricing-fix.zip', 'rb') as f:
        zip_content = f.read()

    print('Deploying pricing fix...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )

    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')

    print('Pricing fix deployed successfully!')

if __name__ == "__main__":
    deploy_simple_fix()