"""
AWS Lambda Security Module - Production-grade API security
Implements rate limiting, input validation, authentication, and security middleware
"""

import json
import os
import time
import hashlib
import hmac
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import logging
import urllib.request
import urllib.parse
import urllib.error
from functools import wraps

logger = logging.getLogger(__name__)

# Environment imports
try:
    from environment_utils import is_development
    IS_DEVELOPMENT = is_development()
except ImportError:
    IS_DEVELOPMENT = True

# Database connection
try:
    if not IS_DEVELOPMENT:
        from dynamodb_dal import DynamoDBConnection, UserDAL
        import boto3
        region = os.environ.get('AWS_REGION', 'us-east-1')
        dynamodb = boto3.resource('dynamodb', region_name=region)
        DYNAMODB_AVAILABLE = True
    else:
        from aws_mock_config import aws_mock
        dynamodb = aws_mock
        DYNAMODB_AVAILABLE = False
except ImportError:
    dynamodb = None
    DYNAMODB_AVAILABLE = False

# Security Configuration
RATE_LIMIT_TABLE = 'ielts-genai-prep-rate-limits'
SESSION_TABLE = 'ielts-genai-prep-sessions'
TOKEN_TABLE = 'ielts-genai-prep-secure-tokens'

# Rate limiting rules (requests per window)
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 60},  # 100 req/min
    'auth_sensitive': {'requests': 5, 'window': 300},  # 5 req/5min
    'qr_generation': {'requests': 3, 'window': 300},  # 3 req/5min
    'password_reset': {'requests': 3, 'window': 1800},  # 3 req/30min
    'login_attempts': {'requests': 5, 'window': 900},  # 5 req/15min
}

# Sensitive endpoints requiring strict rate limiting
SENSITIVE_ENDPOINTS = {
    '/api/auth/generate-qr': 'qr_generation',
    '/api/auth/verify-qr': 'auth_sensitive', 
    '/api/mobile-authenticate': 'login_attempts',
    '/api/forgot-password': 'password_reset',
    '/api/reset-password': 'auth_sensitive',
}

class SecurityError(Exception):
    """Custom exception for security violations"""
    def __init__(self, message: str, status_code: int = 403):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class RateLimiter:
    """DynamoDB-based rate limiter with sliding windows"""
    
    def __init__(self):
        self.table_name = RATE_LIMIT_TABLE
        
    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key for identifier + endpoint"""
        return f"{identifier}#{endpoint}"
    
    def _get_identifier(self, headers: Dict, path: str) -> str:
        """Get unique identifier for rate limiting (IP + User-Agent + Path hash)"""
        ip = headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not ip:
            ip = headers.get('X-Real-IP', 'unknown')
        
        user_agent = headers.get('User-Agent', '')[:50]  # Truncate UA
        path_hash = hashlib.md5(path.encode()).hexdigest()[:8]
        
        return f"{ip}:{path_hash}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
    
    def check_rate_limit(self, headers: Dict, path: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        try:
            # Determine rate limit category
            limit_category = SENSITIVE_ENDPOINTS.get(path, 'default')
            limits = RATE_LIMITS[limit_category]
            
            identifier = self._get_identifier(headers, path)
            key = self._get_rate_limit_key(identifier, path)
            
            current_time = int(time.time())
            window_start = current_time - limits['window']
            
            if not DYNAMODB_AVAILABLE:
                # Mock rate limiting for development
                return True, {
                    'allowed': True,
                    'limit': limits['requests'],
                    'remaining': limits['requests'] - 1,
                    'reset_time': current_time + limits['window']
                }
            
            # Get current request count from DynamoDB
            table = dynamodb.Table(self.table_name)
            
            try:
                response = table.get_item(Key={'rate_limit_key': key})
                
                if 'Item' in response:
                    item = response['Item']
                    request_times = item.get('request_times', [])
                    
                    # Filter out old requests outside the window
                    valid_requests = [t for t in request_times if t > window_start]
                    
                    if len(valid_requests) >= limits['requests']:
                        return False, {
                            'allowed': False,
                            'limit': limits['requests'],
                            'remaining': 0,
                            'reset_time': min(valid_requests) + limits['window']
                        }
                    
                    # Add current request
                    valid_requests.append(current_time)
                    
                    # Update DynamoDB with new request times
                    table.put_item(
                        Item={
                            'rate_limit_key': key,
                            'request_times': valid_requests,
                            'ttl': current_time + (limits['window'] * 2)  # Auto-cleanup
                        }
                    )
                    
                    return True, {
                        'allowed': True,
                        'limit': limits['requests'],
                        'remaining': limits['requests'] - len(valid_requests),
                        'reset_time': current_time + limits['window']
                    }
                
                else:
                    # First request for this key
                    table.put_item(
                        Item={
                            'rate_limit_key': key,
                            'request_times': [current_time],
                            'ttl': current_time + (limits['window'] * 2)
                        }
                    )
                    
                    return True, {
                        'allowed': True,
                        'limit': limits['requests'],
                        'remaining': limits['requests'] - 1,
                        'reset_time': current_time + limits['window']
                    }
                    
            except Exception as e:
                logger.error(f"Rate limit DynamoDB error: {e}")
                # Fail open - allow request if DynamoDB is unavailable
                return True, {
                    'allowed': True,
                    'limit': limits['requests'],
                    'remaining': limits['requests'],
                    'reset_time': current_time + limits['window']
                }
                
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True, {'allowed': True, 'limit': 100, 'remaining': 99, 'reset_time': int(time.time()) + 60}

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Content type allowlist
    ALLOWED_CONTENT_TYPES = {
        'application/json',
        'application/x-www-form-urlencoded',
        'text/plain'
    }
    
    # Maximum payload sizes by content type
    MAX_PAYLOAD_SIZES = {
        'application/json': 1024 * 1024,  # 1MB
        'application/x-www-form-urlencoded': 10 * 1024,  # 10KB
        'text/plain': 10 * 1024,  # 10KB
    }
    
    @classmethod
    def validate_content_type(cls, headers: Dict) -> bool:
        """Validate request content type"""
        content_type = headers.get('Content-Type', '').split(';')[0].strip().lower()
        
        if not content_type:
            return True  # Allow requests without content type (GET requests)
        
        return content_type in cls.ALLOWED_CONTENT_TYPES
    
    @classmethod
    def validate_payload_size(cls, body: str, content_type: str) -> bool:
        """Validate payload size based on content type"""
        if not body:
            return True
            
        body_size = len(body.encode('utf-8'))
        max_size = cls.MAX_PAYLOAD_SIZES.get(content_type, 1024)  # 1KB default
        
        return body_size <= max_size
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:  # RFC 5321 limit
            return False
        return cls.EMAIL_PATTERN.match(email.lower()) is not None
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        # Check for at least one letter and one number
        has_letter = re.search(r'[a-zA-Z]', password)
        has_number = re.search(r'\d', password)
        
        if not (has_letter and has_number):
            return False, "Password must contain at least one letter and one number"
        
        return True, ""
    
    @classmethod
    def sanitize_input(cls, data: Any) -> Any:
        """Sanitize input data to prevent injection attacks"""
        if isinstance(data, str):
            # Remove null bytes and control characters except newline/tab
            cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', data)
            return cleaned.strip()[:1000]  # Limit string length
        
        elif isinstance(data, dict):
            return {k: cls.sanitize_input(v) for k, v in data.items() if isinstance(k, str) and k.strip()}
        
        elif isinstance(data, list):
            return [cls.sanitize_input(item) for item in data[:100]]  # Limit array size
        
        else:
            return data
    
    @classmethod
    def validate_json_schema(cls, data: Dict, schema: Dict) -> Tuple[bool, str]:
        """Basic JSON schema validation"""
        try:
            for field, rules in schema.items():
                if rules.get('required', False) and field not in data:
                    return False, f"Required field '{field}' is missing"
                
                if field in data:
                    value = data[field]
                    field_type = rules.get('type')
                    
                    if field_type == 'email' and not cls.validate_email(value):
                        return False, f"Invalid email format for field '{field}'"
                    
                    if field_type == 'string':
                        if not isinstance(value, str):
                            return False, f"Field '{field}' must be a string"
                        
                        min_len = rules.get('min_length', 0)
                        max_len = rules.get('max_length', 1000)
                        
                        if not (min_len <= len(value) <= max_len):
                            return False, f"Field '{field}' must be {min_len}-{max_len} characters"
            
            return True, ""
            
        except Exception as e:
            return False, f"Schema validation error: {str(e)}"

class TokenManager:
    """Secure token generation and validation with HMAC signing"""
    
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET') or os.environ.get('SESSION_SECRET')
        if not self.secret_key:
            logger.warning("No secret key found for token signing")
            self.secret_key = 'dev-secret-key-not-for-production'
    
    def generate_secure_token(self, data: Dict, expires_in: int = 300) -> str:
        """Generate HMAC-signed token with expiration"""
        try:
            payload = {
                'data': data,
                'expires_at': int(time.time()) + expires_in,
                'issued_at': int(time.time()),
                'token_id': secrets.token_urlsafe(16)
            }
            
            # Create HMAC signature
            payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine payload and signature
            token_data = {
                'payload': payload,
                'signature': signature
            }
            
            return secrets.token_urlsafe(16) + '.' + json.dumps(token_data, separators=(',', ':'))
            
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return None
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate HMAC-signed token"""
        try:
            if not token or '.' not in token:
                return False, None
            
            prefix, token_data_str = token.split('.', 1)
            token_data = json.loads(token_data_str)
            
            payload = token_data.get('payload')
            provided_signature = token_data.get('signature')
            
            if not payload or not provided_signature:
                return False, None
            
            # Verify signature
            payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(provided_signature, expected_signature):
                return False, None
            
            # Check expiration
            if int(time.time()) > payload.get('expires_at', 0):
                return False, None
            
            return True, payload.get('data')
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return False, None

class RecaptchaValidator:
    """Server-side reCAPTCHA v2 validation"""
    
    @classmethod
    def verify_recaptcha(cls, recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
        """Verify reCAPTCHA v2 response with Google"""
        try:
            secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
            if not secret_key:
                logger.warning("No reCAPTCHA secret key found")
                return True  # Allow in development if no key set
            
            if not recaptcha_response:
                return False
            
            # Prepare verification data
            verification_data = {
                'secret': secret_key,
                'response': recaptcha_response
            }
            
            if user_ip:
                verification_data['remoteip'] = user_ip
            
            # Send verification request
            data = urllib.parse.urlencode(verification_data).encode('utf-8')
            
            req = urllib.request.Request(
                'https://www.google.com/recaptcha/api/siteverify',
                data=data,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    result_data = response.read().decode('utf-8')
                    result = json.loads(result_data)
                    success = result.get('success', False)
                    
                    if not success:
                        error_codes = result.get('error-codes', [])
                        logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                    
                    return success
                else:
                    logger.error(f"reCAPTCHA HTTP error: {response.status}")
                    return False
                    
        except urllib.error.URLError as e:
            logger.error(f"reCAPTCHA network error: {e}")
            return False
        except Exception as e:
            logger.error(f"reCAPTCHA verification error: {e}")
            return False

def security_middleware(sensitive_endpoint: bool = False, require_recaptcha: bool = False):
    """Security middleware decorator for Lambda handlers"""
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                headers = event.get('headers') or {}
                body = event.get('body', '') or ''
                path = event.get('path', '/')
                method = event.get('httpMethod', 'GET')
                
                # 1. Content-Type validation
                if body and not InputValidator.validate_content_type(headers):
                    raise SecurityError("Invalid content type", 415)
                
                # 2. Payload size validation
                content_type = headers.get('Content-Type', '').split(';')[0].strip().lower()
                if body and not InputValidator.validate_payload_size(body, content_type):
                    raise SecurityError("Payload too large", 413)
                
                # 3. Rate limiting for sensitive endpoints
                if sensitive_endpoint or path in SENSITIVE_ENDPOINTS:
                    rate_limiter = RateLimiter()
                    allowed, rate_info = rate_limiter.check_rate_limit(headers, path)
                    
                    if not allowed:
                        return {
                            'statusCode': 429,
                            'headers': {
                                'Content-Type': 'application/json',
                                'X-RateLimit-Limit': str(rate_info['limit']),
                                'X-RateLimit-Remaining': '0',
                                'X-RateLimit-Reset': str(rate_info['reset_time']),
                                'Retry-After': str(rate_info['reset_time'] - int(time.time()))
                            },
                            'body': json.dumps({
                                'error': 'Rate limit exceeded',
                                'message': 'Too many requests. Please try again later.'
                            })
                        }
                
                # 4. reCAPTCHA validation if required
                if require_recaptcha and method == 'POST':
                    try:
                        request_data = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        request_data = {}
                    
                    recaptcha_response = request_data.get('recaptcha_response')
                    user_ip = headers.get('X-Forwarded-For', '').split(',')[0].strip()
                    
                    if not RecaptchaValidator.verify_recaptcha(recaptcha_response, user_ip):
                        raise SecurityError("reCAPTCHA verification failed", 400)
                
                # 5. Input sanitization
                if body:
                    try:
                        if content_type == 'application/json':
                            parsed_data = json.loads(body)
                            sanitized_data = InputValidator.sanitize_input(parsed_data)
                            event['body'] = json.dumps(sanitized_data)
                    except json.JSONDecodeError:
                        pass  # Let the handler deal with invalid JSON
                
                # Call the actual handler
                response = handler_func(event, context)
                
                # Add rate limiting headers to successful responses
                if 'headers' not in response:
                    response['headers'] = {}
                
                # Add security headers
                response['headers'].update({
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'DENY',
                    'X-XSS-Protection': '1; mode=block',
                    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://api.ieltsgenaiprep.com"
                })
                
                return response
                
            except SecurityError as e:
                logger.warning(f"Security violation: {e.message}")
                return {
                    'statusCode': e.status_code,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'error': 'Security violation',
                        'message': e.message
                    })
                }
            except Exception as e:
                logger.error(f"Security middleware error: {e}", exc_info=True)
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'error': 'Internal security error',
                        'message': 'Request could not be processed securely'
                    })
                }
        
        return wrapper
    return decorator

def validate_request_data(data: Dict, schema: Dict) -> Dict[str, Any]:
    """Validate and sanitize request data against schema"""
    # Sanitize input
    sanitized_data = InputValidator.sanitize_input(data)
    
    # Validate against schema
    valid, error_msg = InputValidator.validate_json_schema(sanitized_data, schema)
    if not valid:
        raise SecurityError(error_msg, 400)
    
    return sanitized_data

# Common validation schemas
SCHEMAS = {
    'login': {
        'email': {'type': 'email', 'required': True},
        'password': {'type': 'string', 'required': True, 'min_length': 8, 'max_length': 128},
        'recaptcha_response': {'type': 'string', 'required': False}
    },
    'register': {
        'email': {'type': 'email', 'required': True},
        'password': {'type': 'string', 'required': True, 'min_length': 8, 'max_length': 128},
        'username': {'type': 'string', 'required': False, 'min_length': 3, 'max_length': 50},
        'recaptcha_response': {'type': 'string', 'required': True}
    },
    'forgot_password': {
        'email': {'type': 'email', 'required': True},
        'recaptcha_response': {'type': 'string', 'required': True}
    },
    'reset_password': {
        'token': {'type': 'string', 'required': True, 'min_length': 20, 'max_length': 500},
        'password': {'type': 'string', 'required': True, 'min_length': 8, 'max_length': 128}
    },
    'qr_verify': {
        'token': {'type': 'string', 'required': True, 'min_length': 20, 'max_length': 200}
    }
}

# Initialize global instances
rate_limiter = RateLimiter()
token_manager = TokenManager()

# Export key components
__all__ = [
    'security_middleware',
    'SecurityError', 
    'RateLimiter',
    'InputValidator',
    'TokenManager',
    'RecaptchaValidator',
    'validate_request_data',
    'SCHEMAS',
    'rate_limiter',
    'token_manager'
]