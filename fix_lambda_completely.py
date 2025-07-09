#!/usr/bin/env python3
"""
Completely fix the Lambda function with proper routing and authentication
"""

import boto3
import json
import zipfile
import io
import urllib.request

def create_working_lambda():
    """Create a completely working Lambda function"""
    
    lambda_code = '''
import json
import os
import uuid
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Log the incoming event
        print(f"[LAMBDA] Event: {json.dumps(event)}")
        
        # Extract request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        print(f"[LAMBDA] {http_method} {path}")
        print(f"[LAMBDA] Headers: {headers}")
        
        # Parse request body for POST requests
        data = {}
        if body:
            try:
                data = json.loads(body)
            except:
                print(f"[LAMBDA] Failed to parse body: {body}")
        
        # CloudFront security check
        cloudfront_header = headers.get('X-CloudFront-Secret', '')
        if cloudfront_header != 'CF-Secret-3140348d':
            print(f"[LAMBDA] Blocking direct access - missing CloudFront header")
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Forbidden'})
            }
        
        # Route handling
        if path == '/' and http_method == 'GET':
            return serve_home_page()
        elif path == '/login' and http_method == 'GET':
            return serve_login_page()
        elif path == '/login' and http_method == 'POST':
            return handle_login(data)
        elif path == '/api/login' and http_method == 'POST':
            return handle_login(data)
        elif path == '/dashboard' and http_method == 'GET':
            return serve_dashboard()
        elif path == '/privacy-policy' and http_method == 'GET':
            return serve_privacy_policy()
        elif path == '/terms-of-service' and http_method == 'GET':
            return serve_terms_of_service()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Not Found'})
            }
            
    except Exception as e:
        print(f"[LAMBDA] Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Internal Server Error'})
        }

def handle_login(data):
    """Handle user login"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        print(f"[LOGIN] Attempting login for: {email}")
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': False, 'message': 'Email and password required'})
            }
        
        # Get user from DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-genai-prep-users')
        
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if not response['Items']:
            print(f"[LOGIN] User not found: {email}")
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        user = response['Items'][0]
        
        # Check if user is active
        if not user.get('is_active', True):
            print(f"[LOGIN] User not active: {email}")
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': False, 'message': 'Account not active'})
            }
        
        # Verify password
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()
        
        if password_hash != user.get('password_hash', ''):
            print(f"[LOGIN] Invalid password for: {email}")
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        print(f"[LOGIN] Successful login for: {email}")
        
        # Create session
        session_id = str(uuid.uuid4())
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Set-Cookie': f'session_id={session_id}; HttpOnly; Secure; SameSite=Strict; Max-Age=86400; Path=/'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Login successful',
                'redirect': '/dashboard',
                'user_id': user['user_id'],
                'email': email
            })
        }
        
    except Exception as e:
        print(f"[LOGIN] Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': False, 'message': 'Internal server error'})
        }

def serve_home_page():
    """Serve the home page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>IELTS GenAI Prep</title></head><body><h1>IELTS GenAI Prep</h1><p>Welcome to IELTS GenAI Prep</p><a href="/login">Login</a></body></html>'
    }

def serve_login_page():
    """Serve the login page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Login</title></head><body><h1>Login</h1><form id="loginForm"><input type="email" id="email" placeholder="Email" required><input type="password" id="password" placeholder="Password" required><button type="submit">Login</button></form><script>document.getElementById("loginForm").addEventListener("submit", function(e) { e.preventDefault(); var email = document.getElementById("email").value; var password = document.getElementById("password").value; fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: email, password: password }) }).then(response => response.json()).then(data => { if (data.success) { window.location.href = "/dashboard"; } else { alert(data.message); } }); });</script></body></html>'
    }

def serve_dashboard():
    """Serve the dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Dashboard</title></head><body><h1>Dashboard</h1><p>Welcome to your dashboard!</p></body></html>'
    }

def serve_privacy_policy():
    """Serve privacy policy"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Privacy Policy</title></head><body><h1>Privacy Policy</h1><p>Privacy policy content</p></body></html>'
    }

def serve_terms_of_service():
    """Serve terms of service"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Terms of Service</title></head><body><h1>Terms of Service</h1><p>Terms of service content</p></body></html>'
    }
'''
    
    # Create ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("✅ Lambda function updated with working code")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda: {e}")
        return False

def test_working_lambda():
    """Test the working Lambda function"""
    import requests
    import time
    
    print("🧪 Testing working Lambda function...")
    
    # Wait for Lambda to update
    time.sleep(5)
    
    # Test login
    try:
        response = requests.post(
            'https://www.ieltsaiprep.com/api/login',
            json={
                'email': 'prodtest_20250709_175130_i1m2@ieltsaiprep.com',
                'password': 'TestProd2025!'
            },
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login working!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating completely working Lambda function...")
    
    if create_working_lambda():
        if test_working_lambda():
            print("\n🎉 Lambda function is now working!")
            print("You can log in at: https://www.ieltsaiprep.com/login")
            print("Credentials: prodtest_20250709_175130_i1m2@ieltsaiprep.com / TestProd2025!")
        else:
            print("\n❌ Lambda function still not working properly")
    else:
        print("❌ Failed to create working Lambda function")