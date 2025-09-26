"""
Authentication utilities for the AI Learning Hub API
Provides JWT token generation and verification for mobile clients
"""
import os
import json
import time
import datetime
import jwt
from flask import current_app, request, jsonify

# Secret key for JWT tokens - should be stored securely in production
JWT_SECRET = os.environ.get("JWT_SECRET", "development_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 86400  # 24 hours

def generate_token(user_id):
    """
    Generate a JWT token for the given user ID
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return token

def verify_token(token):
    """
    Verify a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None

def token_required(f):
    """
    Decorator for endpoints that require a valid token
    Allows API authentication without sessions for mobile clients
    """
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user_id to request
        request.user_id = payload['user_id']
        
        return f(*args, **kwargs)
    
    # Rename the function to avoid decorator name conflicts
    decorated.__name__ = f.__name__
    return decorated