"""
CORS Protection Module

This module provides Cross-Origin Resource Sharing (CORS) protection to ensure
only authorized domains can access API endpoints.
"""

import os
import logging
from flask import request, jsonify, abort
from functools import wraps

logger = logging.getLogger(__name__)

def get_allowed_origins():
    """
    Get list of allowed origins for CORS protection.
    
    Returns:
        list: List of allowed domain origins
    """
    allowed_origins = []
    
    # Add Replit domains if available
    replit_domains = os.environ.get('REPLIT_DOMAINS', '')
    if replit_domains:
        for domain in replit_domains.split(','):
            domain = domain.strip()
            if domain:
                allowed_origins.extend([
                    f'https://{domain}',
                    f'http://{domain}'  # For development only
                ])
    
    # Add custom domain if configured
    custom_domain = os.environ.get('CUSTOM_DOMAIN', '')
    if custom_domain:
        allowed_origins.append(f'https://{custom_domain}')
    
    # Add localhost for development
    if os.environ.get('FLASK_ENV') == 'development':
        allowed_origins.extend([
            'http://localhost:5000',
            'http://127.0.0.1:5000'
        ])
    
    return allowed_origins

def validate_origin(origin):
    """
    Validate if the origin is allowed to access API endpoints.
    
    Args:
        origin (str): The origin header from the request
        
    Returns:
        bool: True if origin is allowed, False otherwise
    """
    if not origin:
        return False
    
    allowed_origins = get_allowed_origins()
    
    # Check exact match
    if origin in allowed_origins:
        return True
    
    # Log unauthorized access attempt
    logger.warning(f"Unauthorized cross-origin request from: {origin}")
    return False

def cors_protected(f):
    """
    Decorator to protect API endpoints from unauthorized cross-origin requests.
    
    Args:
        f: The function to protect
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        
        # Allow same-origin requests (no Origin header)
        if not origin and not referer:
            return f(*args, **kwargs)
        
        # Check if origin is from same domain as request
        request_host = request.headers.get('Host')
        if origin:
            # Extract hostname from origin
            origin_host = origin.replace('https://', '').replace('http://', '')
            if origin_host == request_host:
                return f(*args, **kwargs)
        
        # Validate against allowed origins
        if origin and validate_origin(origin):
            return f(*args, **kwargs)
        
        # Block unauthorized cross-origin requests
        logger.warning(f"Blocked unauthorized cross-origin request from {origin or referer} to {request.endpoint}")
        return jsonify({
            'error': 'Cross-origin request not allowed',
            'message': 'This API endpoint can only be accessed from authorized domains'
        }), 403
    
    return decorated_function

def api_origin_protection(f):
    """
    Enhanced API endpoint protection that validates both origin and authentication.
    
    Args:
        f: The function to protect
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check CORS first
        origin = request.headers.get('Origin')
        
        # If this is a cross-origin request, validate it
        if origin:
            request_host = request.headers.get('Host')
            origin_host = origin.replace('https://', '').replace('http://', '')
            
            # If not same origin, check against allowed list
            if origin_host != request_host and not validate_origin(origin):
                return jsonify({
                    'error': 'Unauthorized domain',
                    'message': 'API access restricted to authorized domains only'
                }), 403
        
        # Check for API key or session authentication for additional security
        from flask_login import current_user
        
        # Allow authenticated users
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # For unauthenticated API calls, require specific headers
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'error': 'Authentication required',
                'message': 'API access requires authentication or valid API key'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def add_cors_headers(response, allowed_origin=None):
    """
    Add appropriate CORS headers to response.
    
    Args:
        response: Flask response object
        allowed_origin (str): Specific origin to allow, if validated
        
    Returns:
        Response: Modified response with CORS headers
    """
    if allowed_origin:
        response.headers['Access-Control-Allow-Origin'] = allowed_origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRF-Token'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
        # No CORS headers for unauthorized origins
        pass
    
    return response

def log_api_access(endpoint, origin=None, user_id=None):
    """
    Log API access for monitoring purposes.
    
    Args:
        endpoint (str): The API endpoint accessed
        origin (str): Origin of the request
        user_id (int): User ID if authenticated
    """
    logger.info(f"API access: endpoint={endpoint}, origin={origin}, user_id={user_id}")