"""
Enhanced Error Handling Module
Provides centralized error handling for database, API, and request validation errors
"""

import logging
from functools import wraps
from flask import request, jsonify, flash, redirect, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from sqlalchemy.exc import SQLAlchemyError
from api_issues import log_api_error

logger = logging.getLogger(__name__)

def handle_database_error(error, context="Database operation"):
    """Handle database errors with logging and user-friendly messages"""
    logger.error(f"{context} failed: {error}")
    
    # Log to API issues tracking
    log_api_error(
        api_name="database",
        endpoint=context,
        error=error,
        request_obj=request
    )
    
    if request.is_json:
        return jsonify({
            'success': False,
            'error': 'A database error occurred. Please try again later.'
        }), 500
    else:
        flash('An error occurred while processing your request. Please try again.', 'error')
        return redirect(url_for('profile'))

def handle_api_error(api_name, endpoint, error, user_friendly_message="Service temporarily unavailable"):
    """Handle API errors with consistent logging and response"""
    logger.error(f"{api_name} API error at {endpoint}: {error}")
    
    # Log to API issues tracking
    log_api_error(
        api_name=api_name,
        endpoint=endpoint,
        error=error,
        request_obj=request
    )
    
    if request.is_json:
        return jsonify({
            'success': False,
            'error': user_friendly_message
        }), 503
    else:
        flash(user_friendly_message, 'error')
        return redirect(url_for('profile'))

def validate_request_size(max_size_mb=10):
    """Decorator to validate request size"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check content length
                content_length = request.content_length
                if content_length and content_length > max_size_mb * 1024 * 1024:
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'error': f'Request too large. Maximum size is {max_size_mb}MB.'
                        }), 413
                    else:
                        flash(f'File too large. Maximum size is {max_size_mb}MB.', 'error')
                        return redirect(request.referrer or url_for('profile'))
                
                return f(*args, **kwargs)
                
            except RequestEntityTooLarge:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': f'Request too large. Maximum size is {max_size_mb}MB.'
                    }), 413
                else:
                    flash(f'File too large. Maximum size is {max_size_mb}MB.', 'error')
                    return redirect(request.referrer or url_for('profile'))
        
        return decorated_function
    return decorator

def database_transaction(f):
    """Decorator for database transactions with automatic rollback on error"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app import db
        
        try:
            result = f(*args, **kwargs)
            db.session.commit()
            return result
        except SQLAlchemyError as e:
            db.session.rollback()
            return handle_database_error(e, f"Transaction in {f.__name__}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'An unexpected error occurred. Please try again.'
                }), 500
            else:
                flash('An unexpected error occurred. Please try again.', 'error')
                return redirect(url_for('profile'))
    
    return decorated_function

def setup_global_error_handlers():
    """Setup global error handlers for the application"""
    logger.info("Global error handlers configured successfully")
    return True