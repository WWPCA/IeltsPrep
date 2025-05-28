"""
Comprehensive Security Manager for IELTS GenAI Prep

This module provides advanced security features including:
- Rate limiting with Redis backend
- Account lockout protection
- Enhanced input validation
- Session security management
- API endpoint protection
- Security monitoring and logging
"""

import os
import re
import time
import json
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, current_app, g
from flask_login import current_user
from sqlalchemy import text
import redis
from werkzeug.security import check_password_hash

# Configure logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Redis connection for rate limiting (fallback to in-memory if Redis unavailable)
try:
    redis_client = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None

# Fallback to in-memory storage when Redis unavailable
memory_store = {}

class SecurityManager:
    """Advanced security management for the IELTS platform"""
    
    def __init__(self):
        self.max_login_attempts = 5
        self.lockout_duration = 3600  # 1 hour in seconds
        self.rate_limits = {
            'login': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
            'api': {'requests': 100, 'window': 3600},  # 100 API calls per hour
            'assessment': {'requests': 10, 'window': 3600},  # 10 assessments per hour
            'contact': {'requests': 3, 'window': 3600},  # 3 contact forms per hour
        }
    
    def get_client_identifier(self):
        """Get unique identifier for client (IP + User-Agent hash)"""
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        user_agent = request.headers.get('User-Agent', '')
        identifier = f"{ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        return identifier
    
    def increment_counter(self, key, window_seconds):
        """Increment rate limiting counter"""
        if REDIS_AVAILABLE and redis_client:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            result = pipe.execute()
            return result[0]
        else:
            # Fallback to memory store
            now = time.time()
            if key not in memory_store:
                memory_store[key] = {'count': 1, 'expires': now + window_seconds}
                return 1
            
            if now > memory_store[key]['expires']:
                memory_store[key] = {'count': 1, 'expires': now + window_seconds}
                return 1
            
            memory_store[key]['count'] += 1
            return memory_store[key]['count']
    
    def check_rate_limit(self, limit_type, custom_identifier=None):
        """Check if request exceeds rate limit"""
        if limit_type not in self.rate_limits:
            return True, 0
        
        config = self.rate_limits[limit_type]
        identifier = custom_identifier or self.get_client_identifier()
        key = f"rate_limit:{limit_type}:{identifier}"
        
        current_count = self.increment_counter(key, config['window'])
        
        if current_count > config['requests']:
            security_logger.warning(
                f"Rate limit exceeded for {limit_type} from {identifier}. "
                f"Count: {current_count}/{config['requests']}"
            )
            return False, current_count
        
        return True, current_count
    
    def record_failed_login(self, identifier):
        """Record failed login attempt"""
        key = f"failed_login:{identifier}"
        count = self.increment_counter(key, self.lockout_duration)
        
        if count >= self.max_login_attempts:
            lockout_key = f"lockout:{identifier}"
            if REDIS_AVAILABLE and redis_client:
                redis_client.setex(lockout_key, self.lockout_duration, "locked")
            else:
                memory_store[lockout_key] = {
                    'locked': True,
                    'expires': time.time() + self.lockout_duration
                }
            
            security_logger.warning(
                f"Account locked due to {count} failed attempts from {identifier}"
            )
        
        return count
    
    def is_account_locked(self, identifier):
        """Check if account is locked due to failed attempts"""
        lockout_key = f"lockout:{identifier}"
        
        if REDIS_AVAILABLE and redis_client:
            return redis_client.exists(lockout_key)
        else:
            if lockout_key in memory_store:
                if time.time() < memory_store[lockout_key]['expires']:
                    return True
                else:
                    del memory_store[lockout_key]
            return False
    
    def clear_failed_attempts(self, identifier):
        """Clear failed login attempts after successful login"""
        if REDIS_AVAILABLE and redis_client:
            redis_client.delete(f"failed_login:{identifier}")
        else:
            key = f"failed_login:{identifier}"
            if key in memory_store:
                del memory_store[key]
    
    def validate_input(self, data, validation_type):
        """Enhanced input validation"""
        if validation_type == 'email':
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, data)) and len(data) <= 254
        
        elif validation_type == 'password':
            # Password complexity requirements
            if len(data) < 8 or len(data) > 128:
                return False
            has_upper = bool(re.search(r'[A-Z]', data))
            has_lower = bool(re.search(r'[a-z]', data))
            has_digit = bool(re.search(r'\d', data))
            has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', data))
            return has_upper and has_lower and has_digit and has_special
        
        elif validation_type == 'name':
            # Allow letters, spaces, hyphens, apostrophes
            pattern = r"^[a-zA-Z\s\-']{1,100}$"
            return bool(re.match(pattern, data))
        
        elif validation_type == 'text':
            # General text validation (no malicious patterns)
            malicious_patterns = [
                r'<script',
                r'javascript:',
                r'on\w+\s*=',
                r'data:text/html',
                r'vbscript:',
            ]
            data_lower = data.lower()
            return not any(re.search(pattern, data_lower) for pattern in malicious_patterns)
        
        return True
    
    def sanitize_input(self, data):
        """Sanitize user input"""
        if isinstance(data, str):
            # Remove null bytes and control characters
            data = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', data)
            # Limit length
            data = data[:10000] if len(data) > 10000 else data
        return data
    
    def check_sql_injection(self, query_string):
        """Check for potential SQL injection patterns"""
        suspicious_patterns = [
            r'(\bunion\b.*\bselect\b)',
            r'(\bselect\b.*\bfrom\b)',
            r'(\binsert\b.*\binto\b)',
            r'(\bdelete\b.*\bfrom\b)',
            r'(\bdrop\b.*\btable\b)',
            r'(\bupdate\b.*\bset\b)',
            r'(;.*--)',
            r'(\bor\b.*1.*=.*1)',
            r'(\band\b.*1.*=.*1)',
        ]
        
        query_lower = query_string.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, query_lower):
                return True
        return False
    
    def monitor_session_security(self):
        """Monitor session for security issues"""
        # Check session timeout (30 minutes)
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(minutes=30):
                session.clear()
                return False
        
        session['last_activity'] = datetime.now().isoformat()
        
        # Check for session hijacking indicators
        if 'user_agent_hash' in session:
            current_ua_hash = hashlib.md5(
                request.headers.get('User-Agent', '').encode()
            ).hexdigest()
            if session['user_agent_hash'] != current_ua_hash:
                security_logger.warning("Potential session hijacking detected")
                session.clear()
                return False
        else:
            session['user_agent_hash'] = hashlib.md5(
                request.headers.get('User-Agent', '').encode()
            ).hexdigest()
        
        return True
    
    def log_security_event(self, event_type, details):
        """Log security events"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'ip': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            'user_agent': request.headers.get('User-Agent', ''),
            'user_id': current_user.id if current_user.is_authenticated else None,
            'details': details
        }
        
        security_logger.info(f"Security Event: {json.dumps(log_data)}")

# Global security manager instance
security_manager = SecurityManager()

# Decorators for security protection
def rate_limit(limit_type, custom_key=None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = custom_key or security_manager.get_client_identifier()
            allowed, count = security_manager.check_rate_limit(limit_type, identifier)
            
            if not allowed:
                security_manager.log_security_event(
                    'rate_limit_exceeded',
                    {'limit_type': limit_type, 'count': count}
                )
                # Return appropriate response based on request type
                if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                    return jsonify({
                        'error': 'Rate limit exceeded. Please try again later.',
                        'retry_after': security_manager.rate_limits[limit_type]['window']
                    }), 429
                else:
                    # For web forms, show flash message and render template
                    from flask import flash, render_template
                    flash('Too many attempts. Please try again later.', 'danger')
                    if 'login' in request.endpoint:
                        return render_template('login.html', title='Login'), 429
                    return render_template('error.html', message='Rate limit exceeded'), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_inputs(**validations):
    """Input validation decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field, validation_type in validations.items():
                if request.method == 'POST':
                    data = request.form.get(field) or request.json.get(field) if request.json else None
                else:
                    data = request.args.get(field)
                
                if data is not None:
                    # Sanitize input
                    data = security_manager.sanitize_input(data)
                    
                    # Validate input
                    if not security_manager.validate_input(data, validation_type):
                        security_manager.log_security_event(
                            'invalid_input',
                            {'field': field, 'validation_type': validation_type}
                        )
                        return jsonify({'error': f'Invalid {field} format'}), 400
                    
                    # Check for SQL injection
                    if security_manager.check_sql_injection(str(data)):
                        security_manager.log_security_event(
                            'sql_injection_attempt',
                            {'field': field, 'data': data[:100]}
                        )
                        return jsonify({'error': 'Invalid input detected'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def secure_session():
    """Session security decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not security_manager.monitor_session_security():
                return jsonify({'error': 'Session expired'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_protection():
    """Comprehensive API protection decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check content length
            if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({'error': 'Request too large'}), 413
            
            # Check for suspicious headers
            suspicious_headers = ['x-forwarded-host', 'x-originating-ip']
            for header in suspicious_headers:
                if header in request.headers:
                    security_manager.log_security_event(
                        'suspicious_header',
                        {'header': header, 'value': request.headers[header]}
                    )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def account_lockout_protection():
    """Account lockout protection decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = security_manager.get_client_identifier()
            
            if security_manager.is_account_locked(identifier):
                security_manager.log_security_event(
                    'locked_account_attempt',
                    {'identifier': identifier}
                )
                # Return appropriate response based on request type
                if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                    return jsonify({
                        'error': 'Account temporarily locked due to multiple failed attempts. Please try again later.'
                    }), 423
                else:
                    # For web forms, show flash message and render template
                    from flask import flash, render_template
                    flash('Account temporarily locked due to multiple failed attempts. Please try again later.', 'danger')
                    if 'login' in request.endpoint:
                        return render_template('login.html', title='Login'), 423
                    return render_template('error.html', message='Account locked'), 423
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def setup_global_security(app):
    """Setup global security middleware for the Flask app"""
    
    @app.before_request
    def global_security_check():
        """Global security middleware"""
        # Skip security checks for static files
        if request.endpoint and request.endpoint.startswith('static'):
            return
        
        # Check for common attack patterns in URL
        suspicious_url_patterns = [
            r'\.\./',
            r'<script',
            r'javascript:',
            r'data:text/html',
        ]
        
        for pattern in suspicious_url_patterns:
            if re.search(pattern, request.url.lower()):
                security_manager.log_security_event(
                    'suspicious_url',
                    {'url': request.url}
                )
                return jsonify({'error': 'Invalid request'}), 400
        
        # Monitor session security for authenticated routes
        if current_user.is_authenticated:
            security_manager.monitor_session_security()