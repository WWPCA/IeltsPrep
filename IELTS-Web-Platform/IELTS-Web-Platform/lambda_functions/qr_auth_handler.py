import json
import boto3
import uuid
import qrcode
import base64
from datetime import datetime, timedelta
from io import BytesIO
from botocore.exceptions import ClientError

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('ielts-genai-prep-users')
# Note: You may need to create a QR sessions table
# qr_sessions_table = dynamodb.Table('ielts-qr-sessions')

def lambda_handler(event, context):
    """
    Main Lambda handler for QR authentication endpoints
    """
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        if http_method == 'POST' and path == '/api/auth/generate-qr':
            return handle_generate_qr(body)
        elif http_method == 'POST' and path == '/api/auth/verify-qr':
            return handle_verify_qr(body)
        elif http_method == 'POST' and path == '/api/website/request-qr':
            return handle_website_request_qr(body)
        elif http_method == 'POST' and path == '/api/website/check-auth':
            return handle_website_check_auth(body)
        elif http_method == 'POST' and path == '/api/mobile/scan-qr':
            return handle_mobile_scan_qr(body)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error in qr_auth lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_generate_qr(body):
    """
    Generate QR code for website login
    """
    try:
        # Create unique session ID
        session_id = str(uuid.uuid4())
        
        # QR code data contains session ID and timestamp
        qr_data = {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'purpose': 'website_login',
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
        # Generate QR code
        qr_code_data = json.dumps(qr_data)
        qr_image = generate_qr_code_image(qr_code_data)
        
        # Store session in database (you may need to create this table)
        session_record = {
            'session_id': session_id,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': qr_data['expires_at'],
            'user_id': None,
            'auth_token': None
        }
        
        # For now, store in memory or use a temporary solution
        # In production, store in DynamoDB with TTL
        
        return create_response(200, {
            'success': True,
            'session_id': session_id,
            'qr_code': qr_image,
            'expires_at': qr_data['expires_at'],
            'message': 'QR code generated successfully'
        })
        
    except Exception as e:
        print(f"Error in handle_generate_qr: {str(e)}")
        return create_response(500, {'error': 'Failed to generate QR code'})

def handle_verify_qr(body):
    """
    Verify QR code scan from mobile app
    """
    try:
        session_id = body.get('session_id')
        user_token = body.get('user_token')
        
        if not all([session_id, user_token]):
            return create_response(400, {'error': 'Session ID and user token required'})
        
        # Validate user token (integrate with auth system)
        user_data = validate_user_token(user_token)
        if not user_data:
            return create_response(401, {'error': 'Invalid user token'})
        
        # Update session with user authentication
        # In production, update the QR sessions table
        session_update = {
            'session_id': session_id,
            'status': 'authenticated',
            'user_id': user_data['user_id'],
            'user_email': user_data['email'],
            'authenticated_at': datetime.utcnow().isoformat(),
            'auth_token': user_token
        }
        
        return create_response(200, {
            'success': True,
            'message': 'QR code verified successfully',
            'session_id': session_id,
            'user': {
                'user_id': user_data['user_id'],
                'email': user_data['email']
            }
        })
        
    except Exception as e:
        print(f"Error in handle_verify_qr: {str(e)}")
        return create_response(500, {'error': 'QR verification failed'})

def handle_website_request_qr(body):
    """
    Website requests QR code session
    """
    try:
        # Generate new QR session for website
        return handle_generate_qr(body)
        
    except Exception as e:
        print(f"Error in handle_website_request_qr: {str(e)}")
        return create_response(500, {'error': 'Failed to request QR session'})

def handle_website_check_auth(body):
    """
    Website checks QR authentication status
    """
    try:
        session_id = body.get('session_id')
        
        if not session_id:
            return create_response(400, {'error': 'Session ID required'})
        
        # Check session status in database
        # For now, return mock response
        # In production, query QR sessions table
        
        # Mock authenticated session
        session_status = {
            'session_id': session_id,
            'status': 'authenticated',  # or 'pending', 'expired'
            'user': {
                'user_id': 'mock_user_id',
                'email': 'user@example.com'
            },
            'auth_token': 'mock_auth_token'
        }
        
        if session_status['status'] == 'authenticated':
            return create_response(200, {
                'success': True,
                'authenticated': True,
                'user': session_status['user'],
                'auth_token': session_status['auth_token']
            })
        elif session_status['status'] == 'pending':
            return create_response(200, {
                'success': True,
                'authenticated': False,
                'status': 'pending',
                'message': 'Waiting for mobile app scan'
            })
        else:
            return create_response(200, {
                'success': True,
                'authenticated': False,
                'status': 'expired',
                'message': 'QR code has expired'
            })
        
    except Exception as e:
        print(f"Error in handle_website_check_auth: {str(e)}")
        return create_response(500, {'error': 'Failed to check authentication status'})

def handle_mobile_scan_qr(body):
    """
    Mobile app scans QR code
    """
    try:
        qr_data = body.get('qr_data')
        user_token = body.get('user_token')
        
        if not all([qr_data, user_token]):
            return create_response(400, {'error': 'QR data and user token required'})
        
        # Parse QR code data
        try:
            qr_info = json.loads(qr_data)
            session_id = qr_info.get('session_id')
            expires_at = qr_info.get('expires_at')
            
            # Check if QR code is expired
            if datetime.utcnow() > datetime.fromisoformat(expires_at.replace('Z', '+00:00')):
                return create_response(400, {
                    'error': 'QR code has expired',
                    'expired': True
                })
            
        except (json.JSONDecodeError, KeyError) as e:
            return create_response(400, {'error': 'Invalid QR code format'})
        
        # Validate user token
        user_data = validate_user_token(user_token)
        if not user_data:
            return create_response(401, {'error': 'Invalid user token'})
        
        # Process QR authentication
        auth_result = {
            'session_id': session_id,
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'authenticated_at': datetime.utcnow().isoformat()
        }
        
        # In production, update QR sessions table
        
        return create_response(200, {
            'success': True,
            'message': 'QR code scanned successfully',
            'authentication': auth_result
        })
        
    except Exception as e:
        print(f"Error in handle_mobile_scan_qr: {str(e)}")
        return create_response(500, {'error': 'QR scan failed'})

def generate_qr_code_image(data):
    """
    Generate QR code image as base64 string
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error generating QR code image: {str(e)}")
        return None

def validate_user_token(token):
    """
    Validate user authentication token
    """
    try:
        # For now, return mock user data
        # In production, integrate with auth_handler
        
        if token and token.startswith('mock_'):
            return {
                'user_id': 'mock_user_id',
                'email': 'user@example.com'
            }
        
        return None
        
    except Exception as e:
        print(f"Error validating user token: {str(e)}")
        return None

def create_response(status_code, body):
    """
    Create standardized API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }