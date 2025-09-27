"""
Pure AWS Lambda Handler - Maximum Performance Serverless Architecture
Replaces Flask + Gunicorn with direct Lambda routing for optimal cold start performance
"""

import json
import logging
import os
import time
import uuid
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from urllib.parse import parse_qs, unquote
from typing import Dict, Any, Optional, Tuple

# Import security module
from lambda_security import (
    security_middleware, 
    SecurityError,
    InputValidator,
    TokenManager,
    RecaptchaValidator,
    validate_request_data,
    SCHEMAS,
    token_manager
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services based on environment
try:
    from environment_utils import is_development
    IS_DEVELOPMENT = is_development()
    
    if not IS_DEVELOPMENT:
        # Production - use DynamoDB
        from dynamodb_dal import DynamoDBConnection, UserDAL
        region = os.environ.get('AWS_REGION', 'us-east-1')
        db_connection = DynamoDBConnection(region=region)
        user_dal = UserDAL(db_connection)
        DYNAMODB_AVAILABLE = True
        logger.info(f"[PRODUCTION] DynamoDB connected - region: {region}")
    else:
        # Development - use mock services
        from aws_mock_config import aws_mock
        db_connection = aws_mock
        user_dal = None
        DYNAMODB_AVAILABLE = False
        logger.info("[DEVELOPMENT] Using mock services")
        
except Exception as e:
    logger.warning(f"Service initialization warning: {e}")
    from aws_mock_config import aws_mock
    db_connection = aws_mock
    user_dal = None
    IS_DEVELOPMENT = True
    DYNAMODB_AVAILABLE = False

# Initialize additional services
try:
    from receipt_validation import ReceiptValidationService
    receipt_service = ReceiptValidationService()
    logger.info("[INFO] Receipt validation initialized")
except (ImportError, RuntimeError) as e:
    logger.info(f"[INFO] Receipt validation unavailable: {e}")
    receipt_service = None

try:
    import api_mobile
    MOBILE_API_AVAILABLE = True
    logger.info("[INFO] Mobile API handlers loaded")
except ImportError:
    MOBILE_API_AVAILABLE = False
    logger.info("[INFO] Mobile API handlers not available")

# Configuration
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_V2_SITE_KEY", "6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix")
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_V2_SECRET_KEY")
SESSION_SECRET = os.environ.get("SESSION_SECRET")

# CORS Origins
ALLOWED_ORIGINS = [
    'capacitor://localhost',  # Capacitor iOS
    'http://localhost',       # Capacitor Android
    'https://localhost',      # Capacitor Android (HTTPS)
    'ionic://localhost',      # Ionic specific
    'http://localhost:3000',  # Local web dev
    'http://localhost:8100',  # Ionic serve
    'https://ieltsgenaiprep.com',    # Production web
    'https://www.ieltsgenaiprep.com', # Production web (www)
]

# Secure storage (DynamoDB-backed in production, in-memory for development)
if not IS_DEVELOPMENT and DYNAMODB_AVAILABLE:
    # Use DynamoDB tables for production
    sessions_table = 'ielts-genai-prep-sessions'
    tokens_table = 'ielts-genai-prep-secure-tokens'
else:
    # Fallback to in-memory for development
    sessions = {}
    qr_tokens = {}
    mock_purchases = {}
    password_reset_tokens = {}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler - Pure serverless architecture
    Direct routing without web framework overhead for maximum performance
    """
    try:
        # Extract request details
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers') or {}
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '') or ''
        is_base64 = event.get('isBase64Encoded', False)
        
        # Decode base64 body if needed
        if is_base64 and body:
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse JSON body for API requests
        json_body = {}
        if body and headers.get('Content-Type', '').startswith('application/json'):
            try:
                json_body = json.loads(body)
            except json.JSONDecodeError:
                pass
        
        # Parse form data for POST requests
        form_data = {}
        if body and headers.get('Content-Type', '').startswith('application/x-www-form-urlencoded'):
            try:
                form_data = dict(parse_qs(body, keep_blank_values=True))
                # Convert lists to single values
                form_data = {k: v[0] if isinstance(v, list) and v else v for k, v in form_data.items()}
            except:
                pass
        
        # Combine data sources
        request_data = {**json_body, **form_data}
        
        logger.info(f"Request: {method} {path}")
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return create_cors_response(headers.get('Origin'))
        
        # Route request
        response = route_request(event, context, path, method, headers, query_params, request_data)
        
        # Add security headers and CORS
        response['request_path'] = path  # Add path for CORS logic
        response = add_security_headers(response, headers.get('Origin'))
        
        return response
        
    except Exception as e:
        logger.error(f"Lambda error: {e}", exc_info=True)
        
        return create_response(
            status_code=500,
            body=json.dumps({
                'error': 'Internal server error',
                'requestId': getattr(context, 'aws_request_id', 'unknown')
            }),
            content_type='application/json'
        )

def route_request(event: Dict[str, Any], context: Any, path: str, method: str, headers: Dict, query_params: Dict,
                  data: Dict) -> Dict[str, Any]:
    """Route requests to appropriate handlers"""
    
    # Normalize path
    path = path.rstrip('/')
    if not path:
        path = '/'
    
    # Static files
    if path.startswith('/static/'):
        return handle_static_file(path)
    
    # API Routes
    if path.startswith('/api/'):
        return handle_api_request(event, context, path, method, headers, query_params, data)
    
    # Web Pages
    return handle_web_request(event, context, path, method, headers, query_params, data)

def handle_api_request(event: Dict[str, Any], context: Any, path: str, method: str, headers: Dict, query_params: Dict,
                       data: Dict) -> Dict[str, Any]:
    """Handle API endpoints with maximum performance"""
    
    # Health check
    if path == '/api/health':
        return handle_health_check()
    
    # QR Authentication (security-wrapped functions)
    elif path == '/api/auth/generate-qr' and method == 'POST':
        return handle_generate_qr(event, context)
    
    elif path == '/api/auth/verify-qr' and method == 'POST':
        return handle_verify_qr(event, context)
    
    # Mobile Authentication
    elif path == '/api/mobile-authenticate' and method == 'POST':
        return handle_mobile_authenticate(data)
    
    # User Assessments
    elif path.startswith('/api/assessment/') and method == 'GET':
        user_email = path.split('/')[-1]
        return handle_get_assessments(user_email)
    
    # Password Reset (security-wrapped functions)
    elif path == '/api/forgot-password' and method == 'POST':
        return handle_forgot_password(event, context)
    
    elif path == '/api/reset-password' and method == 'POST':
        return handle_reset_password(data)
    
    # Mobile API delegation
    elif path.startswith('/api/v1/') and MOBILE_API_AVAILABLE:
        return delegate_to_mobile_api(path, method, headers, query_params, data)
    
    # 404 for unknown API endpoints
    else:
        return create_response(
            status_code=404,
            body=json.dumps({'error': 'API endpoint not found'}),
            content_type='application/json'
        )

def handle_web_request(event: Dict[str, Any], context: Any, path: str, method: str, headers: Dict, query_params: Dict,
                       data: Dict) -> Dict[str, Any]:
    """Handle web page requests"""
    
    # Home page
    if path == '/' or path == '/index':
        return render_html_page('home', 'IELTS GenAI Prep - AI-Powered IELTS Preparation')
    
    # Authentication pages
    elif path == '/login':
        if method == 'GET':
            return render_html_page('login', 'Login - IELTS GenAI Prep')
        elif method == 'POST':
            return handle_login(event, context)
    
    elif path == '/register':
        if method == 'GET':
            return render_html_page('register', 'Register - IELTS GenAI Prep')
        elif method == 'POST':
            return handle_register(data, headers)
    
    # Product pages
    elif path == '/assessment-products':
        return render_html_page('assessment_products', 'Assessment Products')
    
    elif path == '/about':
        return render_html_page('about', 'About - IELTS GenAI Prep')
    
    elif path == '/contact':
        return render_html_page('contact', 'Contact - IELTS GenAI Prep')
    
    # Legal pages
    elif path == '/terms_and_payment':
        return render_html_page('terms_and_payment', 'Terms and Payment')
    
    elif path == '/privacy_policy':
        return render_html_page('privacy_policy', 'Privacy Policy')
    
    # Password reset pages
    elif path == '/forgot_password':
        return render_html_page('forgot_password', 'Forgot Password')
    
    elif path == '/reset_password':
        return render_html_page('reset_password', 'Reset Password')
    
    # User pages (require authentication)
    elif path == '/profile':
        return handle_profile_page(headers)
    
    elif path.startswith('/assessment/'):
        return handle_assessment_page(path, headers)
    
    # QR login
    elif path in ['/qr-auth', '/qr-login']:
        return render_html_page('qr_login', 'QR Login')
    
    # Logout
    elif path == '/logout':
        return handle_logout(headers)
    
    # 404 for unknown pages
    else:
        return create_response(
            status_code=404,
            body=generate_404_html(),
            content_type='text/html'
        )

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint - optimized for API Gateway health checks"""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': 'development' if IS_DEVELOPMENT else 'production',
            'services': {
                'dynamodb': 'mock' if IS_DEVELOPMENT else 'connected',
                'lambda': 'running'
            }
        }
        
        return create_response(
            status_code=200,
            body=json.dumps(health_data),
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_response(
            status_code=503,
            body=json.dumps({
                'status': 'unhealthy',
                'error': str(e)
            }),
            content_type='application/json'
        )

@security_middleware(sensitive_endpoint=True)
def handle_generate_qr(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Generate secure QR code for authentication"""
    try:
        import qrcode
        import io
        
        # Generate cryptographically secure token with device binding
        headers = event.get('headers', {})
        device_info = {
            'user_agent': headers.get('User-Agent', '')[:100],
            'ip': headers.get('X-Forwarded-For', '').split(',')[0].strip(),
            'timestamp': time.time()
        }
        
        # Create secure token with HMAC signing
        secure_token = token_manager.generate_secure_token(device_info, expires_in=300)
        
        if not secure_token:
            raise SecurityError("Token generation failed")
        
        # Store token securely (DynamoDB in production, memory in development)
        if not IS_DEVELOPMENT and DYNAMODB_AVAILABLE:
            # TODO: Store in DynamoDB with TTL
            pass
        else:
            qr_tokens[secure_token] = {
                'created_at': time.time(),
                'expires_at': time.time() + 300,
                'used': False,
                'device_info': device_info
            }
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_url = f"https://ieltsgenaiprep.com/qr-auth?token={secure_token}"
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Convert to base64 image
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return create_response(
            status_code=200,
            body=json.dumps({
                'success': True,
                'token': secure_token,
                'qr_code': f"data:image/png;base64,{img_str}",
                'expires_in': 300
            }),
            content_type='application/json'
        )
        
    except SecurityError as e:
        return create_response(
            status_code=e.status_code,
            body=json.dumps({'error': e.message}),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"QR generation failed: {e}")
        return create_response(
            status_code=500,
            body=json.dumps({'error': 'QR generation failed'}),
            content_type='application/json'
        )

@security_middleware(sensitive_endpoint=True)
def handle_verify_qr(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Verify secure QR code token"""
    try:
        # Parse and validate request data
        body = event.get('body', '')
        if not body:
            raise SecurityError("Request body required")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise SecurityError("Invalid JSON format")
        
        # Validate request data
        validated_data = validate_request_data(data, SCHEMAS['qr_verify'])
        token = validated_data.get('token')
        
        # Validate token signature and expiration
        valid, token_data = token_manager.validate_token(token)
        if not valid:
            raise SecurityError("Invalid or expired token")
        
        # Additional security check for development fallback
        if IS_DEVELOPMENT and token in qr_tokens:
            stored_token = qr_tokens[token]
            if stored_token['used'] or time.time() > stored_token['expires_at']:
                raise SecurityError("Token expired or already used")
            
            # Mark as used
            stored_token['used'] = True
        
        # Generate secure session
        session_id = str(uuid.uuid4())
        session_data = {
            'user_email': 'qr_user@example.com',  # TODO: Get from token data
            'created_at': time.time(),
            'expires_at': time.time() + 3600,
            'device_info': token_data
        }
        
        # Store session securely
        if not IS_DEVELOPMENT and DYNAMODB_AVAILABLE:
            # TODO: Store in DynamoDB sessions table
            pass
        else:
            sessions[session_id] = session_data
        
        return create_response(
            status_code=200,
            body=json.dumps({
                'success': True,
                'session_id': session_id,
                'redirect_url': '/profile'
            }),
            content_type='application/json',
            cookies=[f'session_id={session_id}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600; Path=/']
        )
        
    except SecurityError as e:
        return create_response(
            status_code=e.status_code,
            body=json.dumps({'error': e.message}),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"QR verification failed: {e}")
        return create_response(
            status_code=500,
            body=json.dumps({'error': 'QR verification failed'}),
            content_type='application/json'
        )

def handle_mobile_authenticate(data: Dict) -> Dict[str, Any]:
    """Handle mobile authentication"""
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return create_response(
            status_code=400,
            body=json.dumps({'error': 'Email and password required'}),
            content_type='application/json'
        )
    
    # TODO: Implement real authentication
    session_id = str(uuid.uuid4())
    
    return create_response(
        status_code=200,
        body=json.dumps({
            'success': True,
            'session_id': session_id,
            'user_email': email
        }),
        content_type='application/json'
    )

def handle_get_assessments(user_email: str) -> Dict[str, Any]:
    """Get user assessments"""
    # Mock data for development
    assessments = {
        'academic_speaking': [],
        'academic_writing': [],
        'general_speaking': [],
        'general_writing': []
    }
    
    return create_response(
        status_code=200,
        body=json.dumps(assessments),
        content_type='application/json'
    )

@security_middleware(sensitive_endpoint=True, require_recaptcha=True)
def handle_forgot_password(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle forgot password request with security validation"""
    try:
        # Parse and validate request data
        body = event.get('body', '')
        if not body:
            raise SecurityError("Request body required")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise SecurityError("Invalid JSON format")
        
        # Validate request data including reCAPTCHA
        validated_data = validate_request_data(data, SCHEMAS['forgot_password'])
        email = validated_data.get('email').lower().strip()
        
        # Generate secure reset token
        reset_data = {
            'email': email,
            'timestamp': time.time(),
            'ip': event.get('headers', {}).get('X-Forwarded-For', '').split(',')[0].strip()
        }
        
        reset_token = token_manager.generate_secure_token(reset_data, expires_in=3600)
        
        if not reset_token:
            raise SecurityError("Token generation failed")
        
        # Store reset token securely
        if not IS_DEVELOPMENT and DYNAMODB_AVAILABLE:
            # TODO: Store in DynamoDB tokens table with TTL
            pass
        else:
            password_reset_tokens[reset_token] = {
                'email': email,
                'created_at': time.time(),
                'expires_at': time.time() + 3600,
                'ip': reset_data['ip']
            }
        
        # TODO: Send secure email with reset link
        logger.info(f"Password reset requested for email: {email}")
        
        # Always return success for security (don't reveal if email exists)
        return create_response(
            status_code=200,
            body=json.dumps({
                'success': True,
                'message': 'If this email is registered, you will receive password reset instructions.'
            }),
            content_type='application/json'
        )
        
    except SecurityError as e:
        return create_response(
            status_code=e.status_code,
            body=json.dumps({'error': e.message}),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        return create_response(
            status_code=500,
            body=json.dumps({'error': 'Password reset request failed'}),
            content_type='application/json'
        )

def handle_reset_password(data: Dict) -> Dict[str, Any]:
    """Handle password reset"""
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return create_response(
            status_code=400,
            body=json.dumps({'error': 'Token and password required'}),
            content_type='application/json'
        )
    
    if token not in password_reset_tokens:
        return create_response(
            status_code=400,
            body=json.dumps({'error': 'Invalid or expired token'}),
            content_type='application/json'
        )
    
    # TODO: Update password in database
    del password_reset_tokens[token]
    
    return create_response(
        status_code=200,
        body=json.dumps({
            'success': True,
            'message': 'Password reset successful'
        }),
        content_type='application/json'
    )

@security_middleware(sensitive_endpoint=True, require_recaptcha=True)
def handle_login(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user login with comprehensive security validation"""
    try:
        # Parse and validate request data
        body = event.get('body', '')
        if not body:
            raise SecurityError("Request body required")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise SecurityError("Invalid JSON format")
        
        # Validate request data
        validated_data = validate_request_data(data, SCHEMAS['login'])
        email = validated_data.get('email').lower().strip()
        password = validated_data.get('password')
        
        # Validate password strength
        valid_password, password_error = InputValidator.validate_password(password)
        if not valid_password:
            raise SecurityError(password_error)
        
        # TODO: Implement real authentication with user database lookup
        # For now, create secure session
        headers = event.get('headers', {})
        session_data = {
            'user_email': email,
            'created_at': time.time(),
            'expires_at': time.time() + 3600,
            'ip': headers.get('X-Forwarded-For', '').split(',')[0].strip(),
            'user_agent': headers.get('User-Agent', '')[:100]
        }
        
        session_id = str(uuid.uuid4())
        
        # Store session securely
        if not IS_DEVELOPMENT and DYNAMODB_AVAILABLE:
            # TODO: Store in DynamoDB sessions table with TTL
            pass
        else:
            sessions[session_id] = session_data
        
        return create_response(
            status_code=302,
            body='',
            headers={'Location': '/profile'},
            cookies=[f'session_id={session_id}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600; Path=/']
        )
        
    except SecurityError as e:
        return create_response(
            status_code=e.status_code,
            body=json.dumps({'error': e.message}),
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return create_response(
            status_code=500,
            body=json.dumps({'error': 'Login failed'}),
            content_type='application/json'
        )

def handle_register(data: Dict, headers: Dict) -> Dict[str, Any]:
    """Handle user registration"""
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return create_response(
            status_code=400,
            body=json.dumps({'error': 'Email and password required'}),
            content_type='application/json'
        )
    
    # TODO: Implement registration
    return create_response(
        status_code=200,
        body=json.dumps({
            'success': True,
            'message': 'Registration successful'
        }),
        content_type='application/json'
    )

def handle_profile_page(headers: Dict) -> Dict[str, Any]:
    """Handle profile page - requires authentication"""
    session_id = get_session_id_from_headers(headers)
    
    if not session_id or session_id not in sessions:
        return create_response(
            status_code=302,
            body='',
            headers={'Location': '/login'}
        )
    
    return render_html_page('profile', 'Profile - IELTS GenAI Prep')

def handle_assessment_page(path: str, headers: Dict) -> Dict[str, Any]:
    """Handle assessment pages"""
    session_id = get_session_id_from_headers(headers)
    
    if not session_id or session_id not in sessions:
        return create_response(
            status_code=302,
            body='',
            headers={'Location': '/login'}
        )
    
    path_parts = path.split('/')
    if len(path_parts) >= 3:
        assessment_type = path_parts[2]
        return render_html_page('assessment', f'{assessment_type.replace("_", " ").title()} Assessment')
    
    return create_response(
        status_code=404,
        body=generate_404_html(),
        content_type='text/html'
    )

def handle_logout(headers: Dict) -> Dict[str, Any]:
    """Handle logout"""
    session_id = get_session_id_from_headers(headers)
    
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    return create_response(
        status_code=302,
        body='',
        headers={'Location': '/'},
        cookies=['session_id=; HttpOnly; Secure; SameSite=Strict; Max-Age=0; Path=/']
    )

def handle_static_file(path: str) -> Dict[str, Any]:
    """Handle static file requests"""
    try:
        file_path = path[1:]  # Remove leading slash
        
        # Security check
        if '..' in file_path or file_path.startswith('/'):
            return create_response(status_code=403, body='Forbidden')
        
        # Read file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        content_type = get_content_type(file_path)
        is_binary = content_type.startswith(('image/', 'application/', 'font/'))
        
        if is_binary:
            body = base64.b64encode(content).decode('utf-8')
            is_base64_encoded = True
        else:
            body = content.decode('utf-8')
            is_base64_encoded = False
        
        return create_response(
            status_code=200,
            body=body,
            content_type=content_type,
            is_base64_encoded=is_base64_encoded
        )
        
    except FileNotFoundError:
        return create_response(status_code=404, body='File not found')
    except Exception as e:
        logger.error(f"Static file error: {e}")
        return create_response(status_code=500, body='Internal server error')

def delegate_to_mobile_api(path: str, method: str, headers: Dict,
                          query_params: Dict, data: Dict) -> Dict[str, Any]:
    """Delegate to mobile API handlers"""
    # This would integrate with existing mobile API
    return create_response(
        status_code=200,
        body=json.dumps({'message': 'Mobile API endpoint'}),
        content_type='application/json'
    )

def render_html_page(page_name: str, title: str) -> Dict[str, Any]:
    """Render HTML page - optimized for Lambda"""
    try:
        html_content = load_template(page_name, {'title': title})
        return create_response(
            status_code=200,
            body=html_content,
            content_type='text/html'
        )
    except Exception as e:
        logger.error(f"Page render error: {e}")
        return create_response(
            status_code=500,
            body=generate_500_html(),
            content_type='text/html'
        )

def load_template(template_name: str, context: Dict) -> str:
    """Load and render HTML template"""
    try:
        # Try loading from templates directory
        template_path = f"templates/{template_name}.html"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple template variable replacement
        for key, value in context.items():
            content = content.replace(f"{{{{{ key }}}}}", str(value))
        
        return content
        
    except FileNotFoundError:
        # Return basic HTML if template not found
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{context.get('title', 'IELTS GenAI Prep')}</title>
        </head>
        <body>
            <h1>Template Not Found: {template_name}</h1>
            <p>This page is under construction.</p>
        </body>
        </html>
        """

def create_cors_response(origin: Optional[str]) -> Dict[str, Any]:
    """Handle CORS preflight requests"""
    return create_response(
        status_code=200,
        body='',
        headers={
            'Access-Control-Allow-Origin': origin if origin in ALLOWED_ORIGINS else '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-API-Key,X-Session-ID,X-Device-ID,X-Platform',
            'Access-Control-Allow-Credentials': 'true' if origin in ALLOWED_ORIGINS else 'false',
            'Access-Control-Max-Age': '86400'
        }
    )

def add_security_headers(response: Dict[str, Any], origin: Optional[str]) -> Dict[str, Any]:
    """Add security headers and strict CORS enforcement"""
    headers = response.get('headers', {})
    
    # Security headers
    headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://api.ieltsgenaiprep.com",
        'Vary': 'Origin'
    })
    
    # Strict CORS enforcement - only allow specific origins for auth endpoints
    request_path = response.get('request_path', '')
    is_auth_endpoint = any(auth_path in request_path for auth_path in ['/api/auth/', '/api/mobile-authenticate', '/login', '/register'])
    
    if origin and origin in ALLOWED_ORIGINS:
        # For allowlisted origins
        headers['Access-Control-Allow-Origin'] = origin
        if not is_auth_endpoint:  # Only allow credentials for non-auth endpoints
            headers['Access-Control-Allow-Credentials'] = 'true'
    elif is_auth_endpoint:
        # For auth endpoints, deny unknown origins
        headers['Access-Control-Allow-Origin'] = 'null'
    elif origin is None:
        # For requests without origin (mobile apps on non-auth endpoints)
        headers['Access-Control-Allow-Origin'] = '*'
    else:
        # For non-allowlisted origins on non-auth endpoints
        headers['Access-Control-Allow-Origin'] = 'null'
    
    headers.update({
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-API-Key,X-Session-ID,X-Device-ID,X-Platform',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Expose-Headers': 'X-Session-ID,X-RateLimit-Remaining,X-RateLimit-Reset'
    })
    
    response['headers'] = headers
    return response

def create_response(status_code: int, body: str = '', content_type: str = 'text/plain',
                   headers: Optional[Dict] = None, cookies: Optional[list] = None,
                   is_base64_encoded: bool = False) -> Dict[str, Any]:
    """Create optimized API Gateway response"""
    response = {
        'statusCode': status_code,
        'body': body,
        'isBase64Encoded': is_base64_encoded,
        'headers': {
            'Content-Type': content_type,
            **(headers or {})
        }
    }
    
    # Handle cookies as multi-value headers
    if cookies:
        response['multiValueHeaders'] = {'Set-Cookie': cookies}
    
    return response

def get_session_id_from_headers(headers: Dict) -> Optional[str]:
    """Extract session ID from cookies"""
    cookie_header = headers.get('Cookie', '')
    
    for cookie in cookie_header.split(';'):
        cookie = cookie.strip()
        if cookie.startswith('session_id='):
            return cookie.split('=', 1)[1]
    
    return None

def get_content_type(file_path: str) -> str:
    """Get content type from file extension"""
    ext = file_path.split('.')[-1].lower()
    
    content_types = {
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'svg': 'image/svg+xml',
        'ico': 'image/x-icon',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'ttf': 'font/ttf',
        'pdf': 'application/pdf'
    }
    
    return content_types.get(ext, 'application/octet-stream')

def generate_404_html() -> str:
    """Generate 404 page HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Page Not Found</title>
    </head>
    <body>
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">Go home</a>
    </body>
    </html>
    """

def generate_500_html() -> str:
    """Generate 500 error page HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>500 - Internal Server Error</title>
    </head>
    <body>
        <h1>500 - Internal Server Error</h1>
        <p>Something went wrong on our end.</p>
        <a href="/">Go home</a>
    </body>
    </html>
    """

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'path': '/api/health',
        'httpMethod': 'GET',
        'headers': {},
        'queryStringParameters': {},
        'body': ''
    }
    
    class MockContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, MockContext())
    print("Test Result:")
    print(json.dumps(result, indent=2))