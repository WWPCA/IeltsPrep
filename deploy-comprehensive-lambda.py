#!/usr/bin/env python3
"""
Deploy Lambda function with comprehensive home page template
"""
import boto3
import zipfile
import json

def create_comprehensive_lambda():
    """Create Lambda function with embedded comprehensive template"""
    
    # Read the comprehensive home page
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # Create Lambda function code
    lambda_code = '''import json

def lambda_handler(event, context):
    """Lambda handler with comprehensive home page"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    print(f"Processing {method} {path}")
    
    # Comprehensive home page HTML content
    home_html = """''' + home_content.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
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
        login_html = """<!DOCTYPE html>
<html>
<head>
    <title>Login - IELTS GenAI Prep</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h1 class="text-center mb-4">IELTS GenAI Prep Login</h1>
                <div class="alert alert-info">
                    <h5>Mobile-First Access Required</h5>
                    <p>To access assessments:</p>
                    <ol>
                        <li>Download our mobile app from App Store or Google Play</li>
                        <li>Create account and purchase assessment packages ($36 each)</li>
                        <li>Return here and login with your mobile app credentials</li>
                    </ol>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': login_html
        }
    
    elif path == '/qr-auth':
        qr_html = """<!DOCTYPE html>
<html>
<head>
    <title>Mobile App Access - IELTS GenAI Prep</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <h1 class="text-center mb-4">Access IELTS GenAI Prep</h1>
                <div class="alert alert-primary">
                    <h5>Download Mobile App First</h5>
                    <p>To access our GenAI assessment platform:</p>
                    <ol>
                        <li><strong>Download</strong> IELTS GenAI Prep from App Store or Google Play</li>
                        <li><strong>Register</strong> and purchase assessment packages ($36.00 each)</li>
                        <li><strong>Login</strong> on this website using your mobile app credentials</li>
                    </ol>
                    <p class="mb-0">One account works on both mobile and web platforms!</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': qr_html
        }
    
    elif path == '/privacy-policy':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '<!DOCTYPE html><html><head><title>Privacy Policy - IELTS GenAI Prep</title></head><body><div class="container mt-5"><h1>Privacy Policy</h1><p>IELTS GenAI Prep Privacy Policy - Coming Soon</p></div></body></html>'
        }
    
    elif path == '/terms-of-service':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '<!DOCTYPE html><html><head><title>Terms of Service - IELTS GenAI Prep</title></head><body><div class="container mt-5"><h1>Terms of Service</h1><p>IELTS GenAI Prep Terms of Service - Coming Soon</p></div></body></html>'
        }
    
    else:
        return {
            'statusCode': 302,
            'headers': {'Location': '/'},
            'body': ''
        }
'''
    
    # Create deployment package
    with zipfile.ZipFile('comprehensive-lambda.zip', 'w') as zip_file:
        zip_file.writestr('simple_lambda.py', lambda_code)
    
    print("Comprehensive Lambda package created successfully")
    return True

def deploy_to_aws():
    """Deploy the comprehensive Lambda function to AWS"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        with open('comprehensive-lambda.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"Error updating Lambda function: {e}")
        return False

if __name__ == "__main__":
    print("Creating comprehensive Lambda deployment package...")
    if create_comprehensive_lambda():
        print("Deploying to AWS Lambda...")
        if deploy_to_aws():
            print("Comprehensive home page deployment completed successfully!")
            print("Your detailed preview design is now live at ieltsaiprep.com")
        else:
            print("Deployment failed")
    else:
        print("Package creation failed")