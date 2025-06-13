#!/usr/bin/env python3
"""
AWS Lambda Handler for IELTS GenAI Prep QR Authentication
Pure serverless implementation for .replit environment testing
"""

import json
import os
import uuid
import time
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Set environment for .replit testing
os.environ['REPLIT_ENVIRONMENT'] = 'true'

# Import AWS mock services
from aws_mock_config import aws_mock

def generate_qr_code(data: str) -> str:
    """Generate QR code image as base64 string"""
    try:
        import qrcode
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"[ERROR] QR code generation failed: {str(e)}")
        # Return a simple placeholder for testing
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def handle_generate_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token generation after purchase verification"""
    try:
        user_email = data.get('user_email')
        product_id = data.get('product_id')
        purchase_verified = data.get('purchase_verified', False)
        
        if not all([user_email, product_id, purchase_verified]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required fields: user_email, product_id, purchase_verified'
                })
            }
        
        # Generate unique token
        token_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Store in AuthTokens table (DynamoDB simulation)
        token_data = {
            'token_id': token_id,
            'user_email': user_email,
            'product_id': product_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': int(expires_at.timestamp()),
            'ttl': int(expires_at.timestamp()),
            'used': False,
            'purchase_verified': purchase_verified
        }
        
        # Store token using AWS mock service
        aws_mock.store_qr_token(token_data)
        
        # Add user to mock purchases if not exists
        if user_email not in aws_mock.get_health_status().get('mock_purchases', {}):
            current_purchases = aws_mock.get_health_status().get('mock_purchases', {})
            current_purchases[user_email] = [product_id]
        else:
            current_purchases = aws_mock.get_health_status().get('mock_purchases', {})
            if product_id not in current_purchases.get(user_email, []):
                current_purchases[user_email].append(product_id)
        
        # Generate QR code image
        qr_code_image = generate_qr_code(token_id)
        
        print(f"[CLOUDWATCH] QR Token Generated: {token_id} for {user_email} - Product: {product_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token_id': token_id,
                'user_email': user_email,
                'product_id': product_id,
                'expires_at': expires_at.isoformat(),
                'expires_in_minutes': 10,
                'qr_code_image': f'data:image/png;base64,{qr_code_image}'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Generation error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_verify_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token verification and session creation"""
    try:
        token_id = data.get('token')
        
        if not token_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Token required'
                })
            }
        
        print(f"[CLOUDWATCH] QR Verification attempt: {token_id}")
        
        # Retrieve token from AuthTokens table
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            print(f"[CLOUDWATCH] QR Verification failed: Invalid token {token_id}")
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid token'
                })
            }
        
        current_time = int(time.time())
        expires_at = token_data.get('expires_at', 0)
        
        # Check token expiry
        if current_time > expires_at:
            print(f"[CLOUDWATCH] QR Verification failed: Expired token {token_id}")
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code expired. Please generate a new one from your mobile app.'
                })
            }
        
        # Check if token already used
        if token_data.get('used'):
            print(f"[CLOUDWATCH] QR Verification failed: Token already used {token_id}")
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code already used. Please generate a new one.'
                })
            }
        
        # Mark token as used
        token_data['used'] = True
        token_data['used_at'] = datetime.utcnow().isoformat()
        
        # Create ElastiCache session (1-hour expiry)
        session_id = f"session_{int(time.time())}_{token_id[:8]}"
        session_data = {
            'session_id': session_id,
            'user_email': token_data['user_email'],
            'product_id': token_data.get('product_id'),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': time.time() + 3600,
            'authenticated_via': 'qr_token',
            'purchased_products': [token_data.get('product_id')]
        }
        
        # Store session using AWS mock service
        aws_mock.create_session(session_data)
        
        print(f"[CLOUDWATCH] QR Verification successful: {token_id} -> Session: {session_id}")
        print(f"[CLOUDWATCH] User {token_data['user_email']} authenticated with products: {session_data['purchased_products']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Set-Cookie': f'qr_session_id={session_id}; Max-Age=3600; Path=/'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Authentication successful',
                'session_id': session_id,
                'user_email': token_data['user_email'],
                'redirect_url': '/profile'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Verification error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_assessment_access(path: str, headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment access with session verification"""
    try:
        # Extract assessment type from path
        assessment_type = path.split('/')[-1]
        
        # Get session from cookie header
        cookie_header = headers.get('Cookie', '')
        session_id = None
        
        for cookie in cookie_header.split(';'):
            if 'qr_session_id=' in cookie:
                session_id = cookie.split('qr_session_id=')[1].strip()
                break
        
        if not session_id:
            print(f"[CLOUDWATCH] Assessment access denied: No session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/'
                },
                'body': ''
            }
        
        # Verify session in ElastiCache
        session_data = aws_mock.get_session(session_id)
        
        if not session_data:
            print(f"[CLOUDWATCH] Assessment access denied: Invalid session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/'
                },
                'body': ''
            }
        
        user_email = session_data['user_email']
        purchased_products = session_data.get('purchased_products', [])
        
        # Check if user has purchased this assessment type
        if assessment_type not in purchased_products:
            print(f"[CLOUDWATCH] Assessment access denied: {user_email} has not purchased {assessment_type}")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html'
                },
                'body': f"""
                <!DOCTYPE html>
                <html>
                <head><title>Access Restricted</title></head>
                <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                    <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                        <h2>🔒 Assessment Access Restricted</h2>
                        <p>You need to purchase the <strong>{assessment_type.replace('_', ' ').title()}</strong> assessment to access this content.</p>
                        <p>This assessment requires a purchase to access.</p>
                        <div style="margin-top: 20px;">
                            <a href="/test-mobile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Purchase on Mobile App</a>
                            <a href="/profile" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Back to Dashboard</a>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        
        print(f"[CLOUDWATCH] Assessment access granted: {user_email} accessing {assessment_type}")
        
        # Return assessment access page
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': f"""
            <!DOCTYPE html>
            <html>
            <head><title>{assessment_type.replace('_', ' ').title()} Assessment</title></head>
            <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <h2>✅ Assessment Access Granted</h2>
                    <p><strong>User:</strong> {user_email}</p>
                    <p><strong>Assessment:</strong> {assessment_type.replace('_', ' ').title()}</p>
                    <p><strong>Session:</strong> {session_id}</p>
                    <div style="margin: 20px 0; padding: 15px; background: #e8f5e8; border-radius: 5px;">
                        <h3>Assessment Module</h3>
                        <p>This is where the {assessment_type.replace('_', ' ').title()} assessment would load with Nova Sonic AI integration.</p>
                        <p>The assessment templates from the existing codebase would be rendered here.</p>
                    </div>
                    <div style="margin-top: 20px;">
                        <a href="/profile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Dashboard</a>
                        <a href="/test-mobile" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Test More Purchases</a>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Assessment access error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        health_data = aws_mock.get_health_status()
        health_data['lambda'] = {
            'status': 'healthy',
            'memory_usage': '128MB',
            'cold_starts': 0
        }
        
        print(f"[CLOUDWATCH] Health check: healthy")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(health_data)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Health check failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e)
            })
        }

def lambda_handler(event, context):
    """Main Lambda entry point"""
    try:
        path = event.get('path', '')
        method = event.get('httpMethod', 'GET')
        body = event.get('body', '{}')
        headers = event.get('headers', {})
        
        # Parse request body
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        
        print(f"[CLOUDWATCH] Lambda processing {method} {path}")
        
        # Route requests
        if path == '/api/health':
            return handle_health_check()
        elif path == '/api/auth/generate-qr' and method == 'POST':
            return handle_generate_qr(data)
        elif path == '/api/auth/verify-qr' and method == 'POST':
            return handle_verify_qr(data)
        elif path.startswith('/assessment/') and method == 'GET':
            return handle_assessment_access(path, headers)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Endpoint not found'
                })
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

if __name__ == "__main__":
    # Test the Lambda handler locally
    test_event = {
        'path': '/api/health',
        'httpMethod': 'GET',
        'headers': {},
        'body': '{}'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))