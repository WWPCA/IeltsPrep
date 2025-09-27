"""
JWT Authentication utilities for IELTS GenAI Prep
Provides JWT token generation and verification for mobile API clients
Integrates with unified User model and Flask app configuration
"""
import json
import datetime
import jwt
from functools import wraps
from flask import current_app, request, jsonify
from models import User


def generate_jwt_token(user_id):
    """
    Generate a JWT token for the given user ID using app configuration
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        'iss': 'ielts-genai-prep',  # Issuer
        'aud': 'mobile-app'  # Audience
    }
    
    token = jwt.encode(
        payload, 
        current_app.config["JWT_SECRET_KEY"], 
        current_app.config["JWT_ALGORITHM"]
    )
    return token


def verify_jwt_token(token):
    """
    Verify a JWT token using app configuration
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            current_app.config["JWT_SECRET_KEY"], 
            algorithms=[current_app.config["JWT_ALGORITHM"]],
            audience='mobile-app',
            issuer='ielts-genai-prep'
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token (including audience/issuer mismatch)
        return None


def jwt_required(f):
    """
    Decorator for API endpoints that require a valid JWT token
    Provides mobile authentication without sessions
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info to request context (using g for proper Flask request context)
        from flask import g
        g.user_id = payload['user_id']
        
        # Load user object for convenience
        try:
            g.current_user = User.query.get(payload['user_id'])
            if not g.current_user or not g.current_user.is_active:
                return jsonify({'error': 'User account is inactive'}), 401
        except Exception:
            return jsonify({'error': 'User not found'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def create_api_response(success=True, message=None, data=None, status_code=200):
    """
    Standardized API response format for mobile clients
    
    Args:
        success: Boolean indicating if request was successful
        message: Optional message
        data: Response data
        status_code: HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': success,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code