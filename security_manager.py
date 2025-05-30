"""
Enterprise Security Manager
Provides comprehensive security features including rate limiting, account lockout,
input validation, SQL injection protection, and session security.
"""

import os
import re
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session, flash, redirect, url_for, jsonify
from flask_login import current_user, logout_user
from email_validator import validate_email, EmailNotValidError
from redis import Redis
from redis.exceptions import RedisError

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
RATE_LIMIT_STORAGE = {}  # Memory fallback
SESSION_TIMEOUT = timedelta(minutes=30)
ACCOUNT_LOCKOUT_DURATION = timedelta(hours=1)
MAX_LOGIN_ATTEMPTS = 5

class SecurityManager:
    """Comprehensive security management with Redis backing and memory fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_storage = {}
        
        # Initialize Redis with fallback
        try:
            self.redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis security storage initialized successfully")
        except (RedisError, ConnectionError) as e:
            logger.warning(f"Redis unavailable, using memory storage: {e}")
    
    def _get_storage(self):
        """Get storage backend (Redis or memory fallback)"""
        return self.redis_client if self.redis_client else self.memory_storage
    
    def _set_value(self, key, value, expire=None):
        """Set value with expiration"""
        try:
            if self.redis_client:
                if expire:
                    self.redis_client.setex(key, expire, value)
                else:
                    self.redis_client.set(key, value)
            else:
                # Memory storage with expiration tracking
                expiry = datetime.utcnow() + timedelta(seconds=expire) if expire else None
                self.memory_storage[key] = {'value': value, 'expires': expiry}
        except RedisError:
            logger.warning("Redis write failed, falling back to memory")
            expiry = datetime.utcnow() + timedelta(seconds=expire) if expire else None
            self.memory_storage[key] = {'value': value, 'expires': expiry}
    
    def _get_value(self, key):
        """Get value with expiration check"""
        try:
            if self.redis_client:
                return self.redis_client.get(key)
            else:
                # Memory storage with expiration check
                entry = self.memory_storage.get(key)
                if entry and (not entry['expires'] or entry['expires'] > datetime.utcnow()):
                    return entry['value']
                elif entry:
                    del self.memory_storage[key]
                return None
        except RedisError:
            logger.warning("Redis read failed, checking memory")
            entry = self.memory_storage.get(key)
            if entry and (not entry['expires'] or entry['expires'] > datetime.utcnow()):
                return entry['value']
            return None
    
    def _increment_value(self, key, expire=None):
        """Increment value with expiration"""
        try:
            if self.redis_client:
                value = self.redis_client.incr(key)
                if expire and value == 1:  # First increment, set expiration
                    self.redis_client.expire(key, expire)
                return value
            else:
                # Memory storage increment
                entry = self.memory_storage.get(key, {'value': 0, 'expires': None})
                if entry['expires'] and entry['expires'] <= datetime.utcnow():
                    entry = {'value': 0, 'expires': None}
                
                entry['value'] += 1
                if expire and entry['value'] == 1:
                    entry['expires'] = datetime.utcnow() + timedelta(seconds=expire)
                
                self.memory_storage[key] = entry
                return entry['value']
        except RedisError:
            logger.warning("Redis increment failed, using memory")
            entry = self.memory_storage.get(key, {'value': 0, 'expires': None})
            entry['value'] += 1
            self.memory_storage[key] = entry
            return entry['value']
    
    def check_rate_limit(self, identifier, limit, window):
        """
        Check if rate limit is exceeded
        
        Args:
            identifier (str): Unique identifier (IP, user ID, etc.)
            limit (int): Maximum requests allowed
            window (int): Time window in seconds
            
        Returns:
            tuple: (is_allowed, remaining_attempts)
        """
        key = f"rate_limit:{identifier}"
        current_count = self._increment_value(key, window)
        
        remaining = max(0, limit - current_count)
        is_allowed = current_count <= limit
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {identifier}: {current_count}/{limit}")
        
        return is_allowed, remaining
    
    def check_account_lockout(self, user_identifier):
        """
        Check if account is locked due to failed login attempts
        
        Args:
            user_identifier (str): User email or ID
            
        Returns:
            tuple: (is_locked, lockout_expires, attempts)
        """
        attempts_key = f"login_attempts:{user_identifier}"
        lockout_key = f"account_lockout:{user_identifier}"
        
        # Check if account is currently locked
        lockout_time = self._get_value(lockout_key)
        if lockout_time:
            lockout_expires = datetime.fromisoformat(lockout_time)
            if lockout_expires > datetime.utcnow():
                return True, lockout_expires, MAX_LOGIN_ATTEMPTS
            else:
                # Lockout expired, clear attempts
                self._set_value(attempts_key, "0", 300)  # Reset for 5 minutes
        
        # Get current attempts
        attempts = int(self._get_value(attempts_key) or 0)
        return False, None, attempts
    
    def record_failed_login(self, user_identifier):
        """
        Record failed login attempt and potentially lock account
        
        Args:
            user_identifier (str): User email or ID
            
        Returns:
            tuple: (is_now_locked, attempts_count)
        """
        attempts_key = f"login_attempts:{user_identifier}"
        lockout_key = f"account_lockout:{user_identifier}"
        
        # Increment failed attempts
        attempts = self._increment_value(attempts_key, 3600)  # 1 hour window
        
        # Lock account if threshold exceeded
        if attempts >= MAX_LOGIN_ATTEMPTS:
            lockout_expires = datetime.utcnow() + ACCOUNT_LOCKOUT_DURATION
            self._set_value(lockout_key, lockout_expires.isoformat(), 
                          int(ACCOUNT_LOCKOUT_DURATION.total_seconds()))
            
            logger.warning(f"Account locked for {user_identifier}: {attempts} failed attempts")
            return True, attempts
        
        return False, attempts
    
    def clear_failed_attempts(self, user_identifier):
        """Clear failed login attempts after successful login"""
        attempts_key = f"login_attempts:{user_identifier}"
        self._set_value(attempts_key, "0", 300)
        logger.info(f"Failed attempts cleared for {user_identifier}")
    
    def validate_email_input(self, email):
        """
        Validate email address format
        
        Args:
            email (str): Email address to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            if not email or len(email) > 254:
                return False, "Email address required and must be under 254 characters"
            
            validated_email = validate_email(email)
            return True, None
            
        except EmailNotValidError as e:
            logger.warning(f"Invalid email format: {email[:50]}")
            return False, "Invalid email address format"
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return False, "Email validation failed"
    
    def validate_password_strength(self, password):
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid, error_message, strength_score)
        """
        if not password:
            return False, "Password is required", 0
        
        score = 0
        issues = []
        
        # Length check
        if len(password) < 8:
            issues.append("at least 8 characters")
        else:
            score += 1
        
        # Character variety checks
        if not re.search(r'[a-z]', password):
            issues.append("lowercase letters")
        else:
            score += 1
            
        if not re.search(r'[A-Z]', password):
            issues.append("uppercase letters")
        else:
            score += 1
            
        if not re.search(r'\d', password):
            issues.append("numbers")
        else:
            score += 1
            
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            issues.append("special characters")
        else:
            score += 1
        
        # Common password check
        common_passwords = ['password', '123456', 'qwerty', 'abc123', 'password123']
        if password.lower() in common_passwords:
            return False, "Password is too common", 0
        
        if score < 3:
            missing = ", ".join(issues)
            return False, f"Password must include: {missing}", score
        
        return True, None, score
    
    def check_sql_injection(self, input_string):
        """
        Check for SQL injection patterns
        
        Args:
            input_string (str): Input to check
            
        Returns:
            bool: True if malicious patterns detected
        """
        if not input_string:
            return False
        
        # Common SQL injection patterns
        suspicious_patterns = [
            r"';?\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER)\s+",
            r"UNION\s+SELECT",
            r"--\s*$",
            r"/\*.*\*/",
            r"'\s*OR\s+\w+\s*=\s*\w+",
            r"1\s*=\s*1",
            r"admin'\s*--",
            r"'\s*;\s*EXEC",
            r"CONCAT\s*\(",
            r"CHAR\s*\(",
            r"0x[0-9a-fA-F]+",
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, input_string.upper(), re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                return True
        
        return False
    
    def sanitize_input(self, input_string, max_length=10000):
        """
        Sanitize user input
        
        Args:
            input_string (str): Input to sanitize
            max_length (int): Maximum allowed length
            
        Returns:
            str: Sanitized input
        """
        if not input_string:
            return ""
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(input_string))
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")
        
        return sanitized.strip()
    
    def validate_session_integrity(self, user_id):
        """
        Validate session integrity against hijacking
        
        Args:
            user_id (int): Current user ID
            
        Returns:
            bool: True if session is valid
        """
        try:
            # Check user agent consistency
            current_ua = request.headers.get('User-Agent', '')
            stored_ua_hash = session.get('user_agent_hash')
            expected_hash = hashlib.md5(current_ua.encode()).hexdigest()
            
            if stored_ua_hash and stored_ua_hash != expected_hash:
                logger.warning(f"Session user agent mismatch for user {user_id}")
                return False
            
            # Store user agent hash if not present
            if not stored_ua_hash:
                session['user_agent_hash'] = expected_hash
            
            # Check session timeout
            last_activity = session.get('last_activity')
            if last_activity:
                last_time = datetime.fromisoformat(last_activity)
                if datetime.utcnow() - last_time > SESSION_TIMEOUT:
                    logger.info(f"Session expired for user {user_id}")
                    return False
            
            # Update last activity
            session['last_activity'] = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            logger.error(f"Session validation error for user {user_id}: {e}")
            return False
    
    def log_security_event(self, event_type, user_id=None, details=None):
        """
        Log security events with structured data
        
        Args:
            event_type (str): Type of security event
            user_id (int, optional): User ID if applicable
            details (dict, optional): Additional event details
        """
        log_data = {
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': self._hash_ip(request.remote_addr) if request else None,
            'user_agent': request.headers.get('User-Agent', '')[:100] if request else None,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        logger.info("Security event", extra=log_data)
    
    def _hash_ip(self, ip_address):
        """Hash IP address for privacy"""
        salt = os.environ.get("IP_HASH_SALT", "default_salt_change_in_production")
        return hashlib.sha256((ip_address + salt).encode()).hexdigest()[:16]

# Global instance
security_manager = SecurityManager()

def rate_limit(limit_type):
    """
    Rate limiting decorator
    
    Args:
        limit_type (str): Type of rate limit ('login', 'api', 'assessment')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Define rate limits
            limits = {
                'login': (5, 300),      # 5 attempts per 5 minutes
                'api': (100, 3600),     # 100 requests per hour
                'assessment': (10, 600), # 10 assessments per 10 minutes
            }
            
            if limit_type not in limits:
                logger.error(f"Unknown rate limit type: {limit_type}")
                return f(*args, **kwargs)
            
            limit, window = limits[limit_type]
            identifier = request.remote_addr
            
            # Use user ID if available for better tracking
            if hasattr(current_user, 'id') and current_user.is_authenticated:
                identifier = f"user_{current_user.id}"
            
            is_allowed, remaining = security_manager.check_rate_limit(
                f"{limit_type}_{identifier}", limit, window
            )
            
            if not is_allowed:
                security_manager.log_security_event(
                    'rate_limit_exceeded', 
                    getattr(current_user, 'id', None),
                    {'limit_type': limit_type, 'limit': limit, 'window': window}
                )
                
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'Rate limit exceeded. Please try again later.',
                        'retry_after': window
                    }), 429
                else:
                    flash('Too many requests. Please try again later.', 'warning')
                    return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_inputs(**field_types):
    """
    Input validation decorator
    
    Args:
        **field_types: Field names and their types ('email', 'password', 'text', 'audio')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() if request.is_json else request.form
            
            for field_name, field_type in field_types.items():
                value = data.get(field_name)
                
                if field_type == 'email':
                    is_valid, error = security_manager.validate_email_input(value)
                    if not is_valid:
                        return jsonify({'success': False, 'error': error}), 400
                
                elif field_type == 'password':
                    is_valid, error, _ = security_manager.validate_password_strength(value)
                    if not is_valid:
                        return jsonify({'success': False, 'error': error}), 400
                
                elif field_type == 'text':
                    if value and security_manager.check_sql_injection(value):
                        security_manager.log_security_event(
                            'sql_injection_attempt',
                            getattr(current_user, 'id', None),
                            {'field': field_name, 'value': value[:100]}
                        )
                        return jsonify({'success': False, 'error': 'Invalid input detected'}), 400
                    
                    # Sanitize the input
                    if value:
                        data[field_name] = security_manager.sanitize_input(value)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_protection():
    """Enhanced API protection decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate session integrity
            if current_user.is_authenticated:
                if not security_manager.validate_session_integrity(current_user.id):
                    logout_user()
                    security_manager.log_security_event(
                        'session_hijacking_detected',
                        current_user.id
                    )
                    return jsonify({
                        'success': False,
                        'error': 'Session invalid. Please log in again.',
                        'logout_required': True
                    }), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def secure_session():
    """Enhanced session security decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate session integrity if user is authenticated
            if current_user.is_authenticated:
                if not security_manager.validate_session_integrity(current_user.id):
                    logout_user()
                    security_manager.log_security_event(
                        'session_invalidated',
                        current_user.id
                    )
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'error': 'Session invalid. Please log in again.',
                            'logout_required': True
                        }), 401
                    else:
                        flash('Your session has been invalidated. Please log in again.', 'warning')
                        return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def account_lockout_protection():
    """Account lockout protection decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if account is locked for authenticated users
            if current_user.is_authenticated:
                user_identifier = current_user.email
                is_locked, lockout_expires, attempts = security_manager.check_account_lockout(user_identifier)
                
                if is_locked:
                    security_manager.log_security_event(
                        'account_locked_access_attempt',
                        current_user.id,
                        {'lockout_expires': lockout_expires.isoformat() if lockout_expires else None}
                    )
                    
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'error': 'Account locked due to failed login attempts.',
                            'lockout_expires': lockout_expires.isoformat() if lockout_expires else None
                        }), 423
                    else:
                        flash('Account locked for 1 hour due to failed login attempts.', 'warning')
                        return redirect(url_for('password_reset'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def setup_global_security(app):
    """Initialize global security settings for the Flask application"""
    try:
        # Initialize security manager
        if not hasattr(app, 'security_manager'):
            app.security_manager = SecurityManager()
        
        # Set up security headers
        @app.after_request
        def add_security_headers(response):
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            # Enable XSS protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            # Strict transport security for HTTPS
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            # Content security policy
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            
            return response
        
        # Set up session security
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            PERMANENT_SESSION_LIFETIME=SESSION_TIMEOUT
        )
        
        logger.info("Global security configuration applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup global security: {e}")
        return False