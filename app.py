#!/usr/bin/env python3
"""
Pure AWS Lambda Handler for IELTS GenAI Prep QR Authentication
Compatible with SAM CLI local testing
"""

import json
import os
import uuid
import time
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
        
        # Generate QR code using simple API
        qr_img = qrcode.make(data)
        
        # Convert to base64
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    except ImportError:
        print("[WARNING] QRCode library not available, using placeholder")
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def lambda_handler(event, context):
    """Main AWS Lambda handler for QR authentication"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
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
        elif path == '/purchase/verify/apple' and method == 'POST':
            return handle_apple_purchase_verification(data)
        elif path == '/purchase/verify/google' and method == 'POST':
            return handle_google_purchase_verification(data)
        elif path.startswith('/assessment/') and method == 'GET':
            return handle_assessment_access(path, headers)
        elif path == '/api/website/request-qr' and method == 'POST':
            return handle_website_qr_request(data)
        elif path == '/api/website/check-auth' and method == 'POST':
            return handle_website_auth_check(data)
        elif path == '/api/mobile/scan-qr' and method == 'POST':
            return handle_mobile_qr_scan(data)
        elif path == '/api/register' and method == 'POST':
            return handle_user_registration(data)
        elif path == '/api/login' and method == 'POST':
            return handle_user_login(data)
        elif path == '/qr-auth' and method == 'GET':
            return handle_qr_auth_page()
        elif path == '/profile' and method == 'GET':
            return handle_profile_page(headers)
        elif path == '/test_mobile_home_screen.html' and method == 'GET':
            return handle_static_file('test_mobile_home_screen.html')
        elif path == '/nova-assessment.html' and method == 'GET':
            return handle_static_file('nova_assessment_demo.html')
        elif path == '/database-schema' and method == 'GET':
            return handle_database_schema_page()
        elif path == '/nova-assessment' and method == 'GET':
            return handle_nova_assessment_demo()
        elif path == '/' and method == 'GET':
            return handle_home_page()
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_static_file(filename: str) -> Dict[str, Any]:
    """Handle static file serving"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content_type = 'text/html' if filename.endswith('.html') else 'text/plain'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'File {filename} not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_home_page() -> Dict[str, Any]:
    """Handle home page - serve mobile app home screen"""
    return handle_static_file('test_mobile_home_screen.html')

def handle_qr_auth_page() -> Dict[str, Any]:
    """Serve QR authentication page"""
    try:
        with open('templates/qr_auth_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>QR Authentication page not found</h1>'
        }

def handle_profile_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve user profile page with session verification"""
    try:
        # Check for valid session cookie
        cookie_header = headers.get('cookie', '')
        session_id = None
        
        # Extract session ID from cookies
        if 'web_session_id=' in cookie_header:
            for cookie in cookie_header.split(';'):
                if 'web_session_id=' in cookie:
                    session_id = cookie.split('=')[1].strip()
                    break
        
        if not session_id:
            # No session found, redirect to QR auth
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Verify session exists and is valid
        session_data = aws_mock.get_session(session_id)
        if not session_data:
            # Invalid session, redirect to QR auth
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Check session expiry
        if session_data.get('expires_at', 0) < time.time():
            # Session expired
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Load profile page template
        with open('templates/profile.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Profile page not found</h1>'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Profile page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading profile: {str(e)}</h1>'
        }

def handle_database_schema_page() -> Dict[str, Any]:
    """Serve database schema documentation page"""
    try:
        with open('database_schema_demo.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Database schema page not found'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Database schema page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading database schema: {str(e)}</h1>'
        }

def handle_nova_assessment_demo() -> Dict[str, Any]:
    """Serve Nova AI assessment demonstration page"""
    try:
        with open('nova_assessment_demo.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Nova assessment demo not found'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Nova assessment demo error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading Nova demo: {str(e)}</h1>'
        }

def handle_apple_purchase_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Apple App Store in-app purchase verification"""
    try:
        receipt_data = data.get('receipt_data')
        product_id = data.get('product_id')
        
        if not receipt_data or not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing receipt_data or product_id'
                })
            }
        
        print(f"[CLOUDWATCH] Apple purchase verification: {product_id}")
        
        # In development environment, simulate successful verification
        # In production, this would verify with Apple's App Store servers
        verification_result = {
            'success': True,
            'product_id': product_id,
            'transaction_id': f"apple_txn_{int(time.time())}",
            'verified': True,
            'environment': 'development'
        }
        
        # Store purchase record in DynamoDB
        purchase_record = {
            'transaction_id': verification_result['transaction_id'],
            'product_id': product_id,
            'platform': 'apple',
            'verified_at': datetime.utcnow().isoformat(),
            'receipt_data': receipt_data[:50] + "..." if len(receipt_data) > 50 else receipt_data
        }
        
        # Store in mock DynamoDB purchase records table
        aws_mock.purchase_records_table.put_item(purchase_record)
        
        print(f"[CLOUDWATCH] Apple purchase verified: {verification_result['transaction_id']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(verification_result)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Apple purchase verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_google_purchase_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Google Play Store in-app purchase verification"""
    try:
        purchase_token = data.get('purchase_token')
        product_id = data.get('product_id')
        
        if not purchase_token or not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing purchase_token or product_id'
                })
            }
        
        print(f"[CLOUDWATCH] Google purchase verification: {product_id}")
        
        # In development environment, simulate successful verification
        # In production, this would verify with Google Play Developer API
        verification_result = {
            'success': True,
            'product_id': product_id,
            'transaction_id': f"google_txn_{int(time.time())}",
            'verified': True,
            'environment': 'development'
        }
        
        # Store purchase record in DynamoDB
        purchase_record = {
            'transaction_id': verification_result['transaction_id'],
            'product_id': product_id,
            'platform': 'google',
            'verified_at': datetime.utcnow().isoformat(),
            'purchase_token': purchase_token[:50] + "..." if len(purchase_token) > 50 else purchase_token
        }
        
        # Store in mock DynamoDB purchase records table
        aws_mock.purchase_records_table.put_item(purchase_record)
        
        print(f"[CLOUDWATCH] Google purchase verified: {verification_result['transaction_id']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(verification_result)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Google purchase verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_website_qr_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle website QR authentication request - generates unique QR for website login"""
    try:
        # Generate unique website authentication token
        website_token_id = str(uuid.uuid4())
        
        # Create QR data with unique identifier and domain verification
        qr_data = {
            'type': 'website_auth',
            'token_id': website_token_id,
            'domain': 'ieltsaiprep.com',
            'timestamp': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
        # Store authentication token in DynamoDB with pending status
        auth_token = {
            'token_id': website_token_id,
            'type': 'website_auth',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            'authenticated_user': None,
            'user_products': None
        }
        
        aws_mock.store_qr_token(auth_token)
        
        # Generate QR code image
        qr_code_image = generate_qr_code(json.dumps(qr_data))
        
        print(f"[CLOUDWATCH] Website QR token generated: {website_token_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token_id': website_token_id,
                'qr_code_image': qr_code_image,
                'expires_at': auth_token['expires_at'],
                'expires_in_minutes': 10
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Website QR request error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_website_auth_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if website QR token has been authenticated by mobile app"""
    try:
        token_id = data.get('token_id')
        
        if not token_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'error': 'Missing token_id'})
            }
        
        # Get token from DynamoDB
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'expired': True})
            }
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.utcnow() > expires_at:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'expired': True})
            }
        
        # Check authentication status
        if token_data.get('status') == 'authenticated':
            # Create website session for authenticated user
            session_id = f"web_session_{int(time.time())}_{token_id[:8]}"
            session_data = {
                'session_id': session_id,
                'user_email': token_data['authenticated_user'],
                'products': token_data['user_products'],
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': time.time() + 3600,  # 1 hour
                'auth_method': 'mobile_qr'
            }
            
            aws_mock.create_session(session_data)
            
            print(f"[CLOUDWATCH] Website session created: {session_id} for {token_data['authenticated_user']}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Set-Cookie': f'web_session_id={session_id}; Max-Age=3600; Path=/'
                },
                'body': json.dumps({
                    'authenticated': True,
                    'user_email': token_data['authenticated_user'],
                    'products': token_data['user_products'],
                    'session_id': session_id
                })
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'waiting': True})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Website auth check error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'authenticated': False, 'error': str(e)})
        }

def handle_mobile_qr_scan(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle mobile app scanning website QR code - authenticates specific user"""
    try:
        qr_data = data.get('qr_data')
        user_email = data.get('user_email')
        user_products = data.get('user_products', [])
        
        if not qr_data or not user_email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing qr_data or user_email'
                })
            }
        
        # Parse QR data
        try:
            qr_info = json.loads(qr_data)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid QR code format'
                })
            }
        
        # Validate QR code structure
        if (qr_info.get('type') != 'website_auth' or 
            qr_info.get('domain') != 'ieltsaiprep.com' or 
            not qr_info.get('token_id')):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid QR code - not an IELTS GenAI Prep authentication code'
                })
            }
        
        token_id = qr_info['token_id']
        
        # Get and validate token
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code expired or invalid'
                })
            }
        
        # Check if already used
        if token_data.get('status') == 'authenticated':
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code already used'
                })
            }
        
        # Update token with user authentication
        token_data['status'] = 'authenticated'
        token_data['authenticated_user'] = user_email
        token_data['user_products'] = user_products
        token_data['authenticated_at'] = datetime.utcnow().isoformat()
        
        aws_mock.store_qr_token(token_data)
        
        print(f"[CLOUDWATCH] Mobile QR scan successful: {user_email} authenticated token {token_id}")
        print(f"[CLOUDWATCH] User products: {user_products}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Authentication successful',
                'user_email': user_email,
                'products': user_products
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Mobile QR scan error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_generate_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token generation after purchase verification"""
    try:
        user_email = data.get('user_email')
        product_id = data.get('product_id')
        purchase_verified = data.get('purchase_verified', False)
        
        if not all([user_email, product_id, purchase_verified]):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
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
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_verify_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token verification and session creation"""
    try:
        token_id = data.get('token')
        
        if not token_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Token required'})
            }
        
        print(f"[CLOUDWATCH] QR Verification attempt: {token_id}")
        
        # Retrieve token from AuthTokens table
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            print(f"[CLOUDWATCH] QR Verification failed: Invalid token {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Invalid token'})
            }
        
        current_time = int(time.time())
        expires_at = token_data.get('expires_at', 0)
        
        # Check token expiry
        if current_time > expires_at:
            print(f"[CLOUDWATCH] QR Verification failed: Expired token {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
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
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
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
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_assessment_access(path: str, headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment access with session verification"""
    try:
        # Extract assessment type from path
        assessment_type = path.split('/')[-1]
        
        # Get session from cookie header
        cookie_header = headers.get('Cookie', headers.get('cookie', ''))
        session_id = None
        
        for cookie in cookie_header.split(';'):
            if 'qr_session_id=' in cookie:
                session_id = cookie.split('qr_session_id=')[1].strip()
                break
        
        if not session_id:
            print(f"[CLOUDWATCH] Assessment access denied: No session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {'Location': '/'},
                'body': ''
            }
        
        # Verify session in ElastiCache
        session_data = aws_mock.get_session(session_id)
        
        if not session_data:
            print(f"[CLOUDWATCH] Assessment access denied: Invalid session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {'Location': '/'},
                'body': ''
            }
        
        user_email = session_data['user_email']
        purchased_products = session_data.get('purchased_products', [])
        
        # Check if user has purchased this assessment type
        if assessment_type not in purchased_products:
            print(f"[CLOUDWATCH] Assessment access denied: {user_email} has not purchased {assessment_type}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': f"""
                <!DOCTYPE html>
                <html>
                <head><title>Access Restricted</title></head>
                <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                    <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                        <h2>🔒 Assessment Access Restricted</h2>
                        <p>You need to purchase the <strong>{assessment_type.replace('_', ' ').title()}</strong> assessment to access this content.</p>
                        <div style="margin-top: 20px;">
                            <a href="/test-mobile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Purchase on Mobile App</a>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        
        print(f"[CLOUDWATCH] Assessment access granted: {user_email} accessing {assessment_type}")
        
        # Return assessment access page with existing template integration
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
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
                        <h3>Assessment Module Ready</h3>
                        <p>This assessment module integrates with your existing templates from the templates/assessments directory.</p>
                        <p>Nova Sonic AI integration would be loaded here for speech assessment.</p>
                    </div>
                    <div style="margin-top: 20px;">
                        <button style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin-right: 10px;">Start Assessment</button>
                        <a href="/profile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Dashboard</a>
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
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        health_data = aws_mock.get_health_status()
        health_data['lambda'] = {
            'status': 'healthy',
            'memory_usage': '128MB',
            'cold_starts': 0,
            'architecture': 'serverless'
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
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'unhealthy', 'error': str(e)})
        }

def handle_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration with DynamoDB storage"""
    try:
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not name or not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'All fields are required'})
            }
        
        if len(password) < 6:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Password must be at least 6 characters'})
            }
        
        # Check if user already exists
        existing_user = aws_mock.users_table.get_item(email)
        if existing_user:
            return {
                'statusCode': 409,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'User already exists with this email'})
            }
        
        # Hash password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user record
        user_data = {
            'user_id': email,
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'products': [],
            'last_login': None
        }
        
        # Store in DynamoDB
        success = aws_mock.users_table.put_item(user_data)
        
        if success:
            aws_mock.log_event('UserAuth', f'User registered: {email}')
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True, 
                    'user': {
                        'name': name,
                        'email': email,
                        'products': []
                    }
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Failed to create user account'})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] User registration error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': 'Registration failed'})
        }

def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login with DynamoDB authentication"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Email and password are required'})
            }
        
        # Get user from DynamoDB
        user_data = aws_mock.users_table.get_item(email)
        if not user_data:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Invalid email or password'})
            }
        
        # Verify password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user_data['password_hash'] != password_hash:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Invalid email or password'})
            }
        
        # Update last login
        aws_mock.users_table.update_item(email, {
            'last_login': datetime.utcnow().isoformat()
        })
        
        # Create session
        session_id = f"mobile_session_{int(time.time())}_{email.replace('@', '_').replace('.', '_')}"
        session_data = {
            'user_email': email,
            'created_at': time.time(),
            'type': 'mobile_app'
        }
        aws_mock.create_session(session_data)
        
        aws_mock.log_event('UserAuth', f'User logged in: {email}')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': True,
                'user': {
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'products': user_data.get('products', [])
                },
                'session_id': session_id
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] User login error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': 'Login failed'})
        }