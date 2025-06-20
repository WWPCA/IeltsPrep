#!/usr/bin/env python3
"""
Deploy updated Lambda function with comprehensive home page design
"""
import boto3
import zipfile
import os
import time

def create_lambda_package():
    """Create deployment package with updated home page"""
    
    # Read the comprehensive home page template
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_page_content = f.read()
    
    # Read the current Lambda function
    with open('app.py', 'r', encoding='utf-8') as f:
        lambda_content = f.read()
    
    # Create simple Lambda function with embedded comprehensive HTML
    simple_lambda_code = f'''"""
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
                <html>
                <head><title>Login - IELTS GenAI Prep</title></head>
                <body>
                    <h1>IELTS GenAI Prep Login</h1>
                    <p>Please download our mobile app first to create an account and purchase assessments.</p>
                    <p>After purchasing in the mobile app, return here to login with the same credentials.</p>
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
                <html>
                <head><title>Mobile App Access - IELTS GenAI Prep</title></head>
                <body>
                    <h1>Access IELTS GenAI Prep</h1>
                    <p>To access assessments, please:</p>
                    <ol>
                        <li>Download our mobile app from the App Store or Google Play</li>
                        <li>Create account and purchase assessment packages ($36 each)</li>
                        <li>Return to this website and login with your mobile app credentials</li>
                    </ol>
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
                <html>
                <head><title>Privacy Policy - IELTS GenAI Prep</title></head>
                <body>
                    <h1>Privacy Policy</h1>
                    <p>IELTS GenAI Prep Privacy Policy - Coming Soon</p>
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
                <html>
                <head><title>Terms of Service - IELTS GenAI Prep</title></head>
                <body>
                    <h1>Terms of Service</h1>
                    <p>IELTS GenAI Prep Terms of Service - Coming Soon</p>
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
    
    # Create the deployment package
    with zipfile.ZipFile('enhanced-lambda.zip', 'w') as zip_file:
        # Add the Lambda function
        zip_file.writestr('lambda_function.py', simple_lambda_code)
    
    print("Enhanced Lambda package created: enhanced-lambda.zip")
    return True

def deploy_lambda():
    """Deploy the enhanced Lambda function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Read the deployment package
        with open('enhanced-lambda.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        
        # Wait for update to complete
        print("Waiting for Lambda update to complete...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"Error updating Lambda function: {e}")
        return False

if __name__ == "__main__":
    print("Creating enhanced Lambda deployment package...")
    if create_lambda_package():
        print("Deploying enhanced Lambda function...")
        if deploy_lambda():
            print("Enhanced Lambda deployment completed successfully!")
            print("Your comprehensive home page design is now live!")
        else:
            print("Lambda deployment failed")
    else:
        print("Package creation failed")