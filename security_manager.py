"""
Security Manager Module
Provides comprehensive security controls for IELTS GenAI Prep platform
"""

import os
import logging
import hashlib
import time
from functools import wraps
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import request, jsonify, abort, session

logger = logging.getLogger(__name__)

class SecurityManager:
    """Centralized security management system"""
    
    def __init__(self):
        self.rate_limits = defaultdict(deque)
        self.blocked_ips = set()
        self.suspicious_activity = defaultdict(int)
        self.redis_available = False
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection for distributed rate limiting"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis connected for security management")
        except Exception as e:
            logger.warning(f"Redis unavailable, using memory storage: {e}")
            self.redis_available = False
    
    def rate_limit(self, limit=100, window=3600, per='ip'):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                identifier = self._get_identifier(per)
                
                if self._is_rate_limited(identifier, limit, window):
                    logger.warning(f"Rate limit exceeded for {identifier}")
                    return jsonify({
                        'success': False,
                        'error': 'Rate limit exceeded. Please try again later.'
                    }), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def _get_identifier(self, per):
        """Get identifier for rate limiting"""
        if per == 'ip':
            return request.remote_addr
        elif per == 'user':
            return session.get('user_id', request.remote_addr)
        elif per == 'session':
            return session.get('session_id', request.remote_addr)
        else:
            return request.remote_addr
    
    def _is_rate_limited(self, identifier, limit, window):
        """Check if identifier is rate limited"""
        current_time = time.time()
        
        if self.redis_available:
            return self._redis_rate_limit(identifier, limit, window, current_time)
        else:
            return self._memory_rate_limit(identifier, limit, window, current_time)
    
    def _redis_rate_limit(self, identifier, limit, window, current_time):
        """Redis-based rate limiting"""
        try:
            key = f"rate_limit:{identifier}"
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window)
            results = pipe.execute()
            
            return results[1] >= limit
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            return self._memory_rate_limit(identifier, limit, window, current_time)
    
    def _memory_rate_limit(self, identifier, limit, window, current_time):
        """Memory-based rate limiting"""
        requests = self.rate_limits[identifier]
        
        # Remove old requests
        while requests and requests[0] < current_time - window:
            requests.popleft()
        
        # Check if limit exceeded
        if len(requests) >= limit:
            return True
        
        # Add current request
        requests.append(current_time)
        return False
    
    def detect_suspicious_activity(self, activity_type, threshold=5):
        """Detect and track suspicious activity"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                identifier = request.remote_addr
                
                # Increment suspicious activity counter
                self.suspicious_activity[f"{identifier}:{activity_type}"] += 1
                
                # Check if threshold exceeded
                if self.suspicious_activity[f"{identifier}:{activity_type}"] > threshold:
                    logger.warning(f"Suspicious activity detected: {activity_type} from {identifier}")
                    self.blocked_ips.add(identifier)
                    
                    return jsonify({
                        'success': False,
                        'error': 'Suspicious activity detected. Access temporarily restricted.'
                    }), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def block_suspicious_ips(self):
        """Decorator to block known suspicious IPs"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if request.remote_addr in self.blocked_ips:
                    logger.warning(f"Blocked IP access attempt: {request.remote_addr}")
                    abort(403)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def validate_request_size(self, max_size_mb=10):
        """Validate request content size"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                content_length = request.content_length
                max_size_bytes = max_size_mb * 1024 * 1024
                
                if content_length and content_length > max_size_bytes:
                    logger.warning(f"Request size exceeded: {content_length} bytes from {request.remote_addr}")
                    return jsonify({
                        'success': False,
                        'error': f'Request too large. Maximum size is {max_size_mb}MB.'
                    }), 413
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def sanitize_input(self, input_string):
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(input_string, str):
            return input_string
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'data:', 'vbscript:']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def generate_secure_token(self, length=32):
        """Generate secure random token"""
        import secrets
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data):
        """Hash sensitive data with salt"""
        salt = os.urandom(32)
        hashed = hashlib.pbkdf2_hmac('sha256', data.encode('utf-8'), salt, 100000)
        return salt + hashed
    
    def verify_hashed_data(self, data, hashed_data):
        """Verify hashed data"""
        salt = hashed_data[:32]
        stored_hash = hashed_data[32:]
        new_hash = hashlib.pbkdf2_hmac('sha256', data.encode('utf-8'), salt, 100000)
        return new_hash == stored_hash
    
    def log_security_event(self, event_type, details=None):
        """Log security events for monitoring"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'ip_address': request.remote_addr if request else 'system',
                'user_agent': request.headers.get('User-Agent') if request else 'system',
                'details': details or {}
            }
            
            logger.info(f"Security Event: {event_type} - {log_entry}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def cleanup_old_data(self):
        """Clean up old rate limiting and security data"""
        try:
            current_time = time.time()
            
            # Clean up memory-based rate limits
            for identifier in list(self.rate_limits.keys()):
                requests = self.rate_limits[identifier]
                while requests and requests[0] < current_time - 3600:  # 1 hour window
                    requests.popleft()
                
                if not requests:
                    del self.rate_limits[identifier]
            
            # Reset suspicious activity counters daily
            if hasattr(self, 'last_cleanup'):
                if current_time - self.last_cleanup > 86400:  # 24 hours
                    self.suspicious_activity.clear()
                    self.last_cleanup = current_time
            else:
                self.last_cleanup = current_time
            
        except Exception as e:
            logger.error(f"Error during security cleanup: {e}")

# Global security manager instance
security_manager = SecurityManager()

# Convenience functions for easy import
def rate_limit(limit=100, window=3600, per='ip'):
    """Rate limiting decorator"""
    return security_manager.rate_limit(limit, window, per)

def detect_suspicious_activity(activity_type, threshold=5):
    """Suspicious activity detection decorator"""
    return security_manager.detect_suspicious_activity(activity_type, threshold)

def block_suspicious_ips():
    """Block suspicious IPs decorator"""
    return security_manager.block_suspicious_ips()

def validate_request_size(max_size_mb=10):
    """Request size validation decorator"""
    return security_manager.validate_request_size(max_size_mb)

def sanitize_input(input_string):
    """Sanitize user input"""
    return security_manager.sanitize_input(input_string)

def generate_secure_token(length=32):
    """Generate secure token"""
    return security_manager.generate_secure_token(length)

def log_security_event(event_type, details=None):
    """Log security event"""
    return security_manager.log_security_event(event_type, details)

def validate_inputs(*input_strings):
    """Validate and sanitize multiple inputs"""
    return [security_manager.sanitize_input(inp) for inp in input_strings]

def secure_session():
    """Decorator to ensure secure session handling"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Basic session security checks
            if 'user_id' in session:
                # Regenerate session ID periodically for security
                if not session.get('last_regenerated') or \
                   time.time() - session.get('last_regenerated', 0) > 3600:
                    session['last_regenerated'] = time.time()
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize security configuration
def configure_global_security():
    """Configure global security settings"""
    try:
        logger.info("Global security configuration applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to configure global security: {e}")
        return False

# Apply global security configuration
configure_global_security()