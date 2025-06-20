#!/usr/bin/env python3
"""
Fix Lambda deployment with correct handler configuration
"""
import boto3
import zipfile
import time

def create_fixed_lambda_package():
    """Create deployment package with correct handler name"""
    
    # Read the comprehensive home page template
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_page_content = f.read()
    
    # Create Lambda function with correct handler name
    lambda_code = f'''"""
IELTS GenAI Prep - Enhanced Lambda Handler
Serves comprehensive home page design matching preview template
"""
import json
import base64
import qrcode
import io
import os
import hashlib
import time
from typing import Dict, Any, Optional

def generate_qr_code(data: str) -> str:
    """Generate QR code image as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{{img_str}}"

def lambda_handler(event, context):
    """Enhanced Lambda handler with comprehensive home page"""
    
    try:
        # Extract request information
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {{}})
        
        print(f"[CLOUDWATCH] Processing {{http_method}} {{path}}")
        
        # Handle home page requests
        if path == '/' or path == '/index.html':
            print(f"[CLOUDWATCH] Serving comprehensive home page")
            return {{
                'statusCode': 200,
                'headers': {{
                    'Content-Type': 'text/html; charset=utf-8',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }},
                'body': """{home_page_content}"""
            }}
        
        # Handle static file requests
        elif path.startswith('/static/') or path.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
            print(f"[CLOUDWATCH] Static file request: {{path}}")
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'text/plain'}},
                'body': 'Static file placeholder'
            }}
        
        # Handle API requests
        elif path.startswith('/api/'):
            print(f"[CLOUDWATCH] API request: {{path}}")
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'message': 'API endpoint placeholder', 'path': path}})
            }}
        
        # Handle login page
        elif path == '/login':
            print(f"[CLOUDWATCH] Serving login page")
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'text/html'}},
                'body': """
                <!DOCTYPE html>
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
                                    <p>To access assessments, please:</p>
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
                </html>
                """
            }}
        
        # Handle QR auth page
        elif path == '/qr-auth':
            print(f"[CLOUDWATCH] Serving QR auth page")
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'text/html'}},
                'body': """
                <!DOCTYPE html>
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
                </html>
                """
            }}
        
        # Handle privacy policy
        elif path == '/privacy-policy':
            print(f"[CLOUDWATCH] Serving privacy policy")
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'text/html'}},
                'body': """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Privacy Policy - IELTS GenAI Prep</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <h1>Privacy Policy</h1>
                        <p>IELTS GenAI Prep Privacy Policy - Coming Soon</p>
                    </div>
                </body>
                </html>
                """
            }}
        
        # Handle terms of service
        elif path == '/terms-of-service':
            print(f"[CLOUDWATCH] Serving terms of service")
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'text/html'}},
                'body': """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Terms of Service - IELTS GenAI Prep</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <h1>Terms of Service</h1>
                        <p>IELTS GenAI Prep Terms of Service - Coming Soon</p>
                    </div>
                </body>
                </html>
                """
            }}
        
        # Default case - redirect to home
        else:
            print(f"[CLOUDWATCH] Unknown path {{path}}, redirecting to home")
            return {{
                'statusCode': 302,
                'headers': {{'Location': '/'}},
                'body': ''
            }}
            
    except Exception as e:
        print(f"[CLOUDWATCH] Error processing request: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Internal server error', 'details': str(e)}})
        }}
'''
    
    # Create the deployment package with correct file name
    with zipfile.ZipFile('fixed-lambda.zip', 'w') as zip_file:
        # Add the Lambda function with correct file name for handler
        zip_file.writestr('simple_lambda.py', lambda_code)
    
    print("Fixed Lambda package created: fixed-lambda.zip")
    return True

def deploy_fixed_lambda():
    """Deploy the fixed Lambda function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Read the deployment package
        with open('fixed-lambda.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        
        # Wait for update to complete
        print("Waiting for Lambda update to complete...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"Error updating Lambda function: {e}")
        return False

if __name__ == "__main__":
    print("Creating fixed Lambda deployment package...")
    if create_fixed_lambda_package():
        print("Deploying fixed Lambda function...")
        if deploy_fixed_lambda():
            print("Fixed Lambda deployment completed successfully!")
            print("Testing deployment...")
        else:
            print("Lambda deployment failed")
    else:
        print("Package creation failed")