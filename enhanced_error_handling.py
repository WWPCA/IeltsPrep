"""
Enhanced Error Handling System
Implements comprehensive error handling and recovery mechanisms identified in the code review.
"""

import logging
from functools import wraps
from flask import request, jsonify, flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import RequestEntityTooLarge
from api_issues import log_api_error

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedErrorHandler:
    """Comprehensive error handling for the application"""
    
    @staticmethod
    def handle_database_error(func):
        """Decorator for handling database-related errors"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                logger.error(f"Database integrity error in {func.__name__}: {e}")
                if 'email' in str(e).lower():
                    flash('Email address already exists. Please use a different email.', 'danger')
                else:
                    flash('A data integrity error occurred. Please check your input and try again.', 'danger')
                return redirect(request.url)
            except SQLAlchemyError as e:
                logger.error(f"Database error in {func.__name__}: {e}")
                flash('A database error occurred. Please try again later.', 'danger')
                return redirect(request.url)
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                flash('An unexpected error occurred. Please try again.', 'danger')
                return redirect(request.url)
        return wrapper
    
    @staticmethod
    def handle_api_error(api_name, endpoint):
        """Decorator for handling API-related errors"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                start_time = time.time()
                
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Log the API error for monitoring
                    log_api_error(
                        api_name=api_name,
                        endpoint=endpoint,
                        error=e,
                        request_obj=request,
                        request_duration=duration
                    )
                    
                    logger.error(f"API error in {func.__name__}: {e}")
                    
                    # Return appropriate error response based on request type
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'error': f'{api_name} service is temporarily unavailable. Please try again later.',
                            'error_code': 'SERVICE_UNAVAILABLE'
                        }), 503
                    else:
                        flash(f'Assessment service is temporarily unavailable. Please try again later.', 'warning')
                        return redirect(url_for('index'))
            return wrapper
        return decorator
    
    @staticmethod
    def handle_file_upload_error(func):
        """Decorator for handling file upload errors"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestEntityTooLarge:
                logger.warning(f"File too large in {func.__name__}")
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'File size too large. Please upload a smaller file.'
                    }), 413
                else:
                    flash('File size too large. Please upload a smaller file.', 'warning')
                    return redirect(request.url)
            except Exception as e:
                logger.error(f"File upload error in {func.__name__}: {e}")
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'File upload failed. Please try again.'
                    }), 400
                else:
                    flash('File upload failed. Please try again.', 'danger')
                    return redirect(request.url)
        return wrapper
    
    @staticmethod
    def handle_authentication_error(func):
        """Decorator for handling authentication-related errors"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Authentication error in {func.__name__}: {e}")
                flash('Authentication failed. Please check your credentials and try again.', 'danger')
                return redirect(url_for('login'))
        return wrapper
    
    @staticmethod
    def validate_request_size(max_size_mb=10):
        """Decorator to validate request content size"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                content_length = request.content_length
                if content_length and content_length > max_size_mb * 1024 * 1024:
                    logger.warning(f"Request too large in {func.__name__}: {content_length} bytes")
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'error': f'Request size too large. Maximum allowed: {max_size_mb}MB'
                        }), 413
                    else:
                        flash(f'Request size too large. Maximum allowed: {max_size_mb}MB', 'warning')
                        return redirect(request.url)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def handle_session_timeout(func):
        """Decorator for handling session timeout scenarios"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask_login import current_user
            
            if current_user.is_authenticated:
                # Check if session is still valid
                try:
                    # Attempt to access user data to verify session
                    _ = current_user.email
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Session validation failed in {func.__name__}: {e}")
                    flash('Your session has expired. Please log in again.', 'info')
                    return redirect(url_for('login'))
            else:
                return func(*args, **kwargs)
        return wrapper

def setup_global_error_handlers(app):
    """Set up global error handlers for the Flask application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request: {error}")
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Invalid request format'
            }), 400
        flash('Invalid request. Please check your input.', 'warning')
        return redirect(url_for('index'))
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized access: {error}")
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden access: {error}")
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"Page not found: {request.url}")
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Resource not found'
            }), 404
        flash('The page you requested was not found.', 'warning')
        return redirect(url_for('index'))
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Internal server error. Please try again later.'
            }), 500
        flash('An internal error occurred. Please try again later.', 'danger')
        return redirect(url_for('index'))
    
    @app.errorhandler(503)
    def service_unavailable(error):
        logger.error(f"Service unavailable: {error}")
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Service temporarily unavailable. Please try again later.'
            }), 503
        flash('Service temporarily unavailable. Please try again later.', 'warning')
        return redirect(url_for('index'))

# Export the decorators for easy use
handle_database_error = EnhancedErrorHandler.handle_database_error
handle_api_error = EnhancedErrorHandler.handle_api_error
handle_file_upload_error = EnhancedErrorHandler.handle_file_upload_error
handle_authentication_error = EnhancedErrorHandler.handle_authentication_error
validate_request_size = EnhancedErrorHandler.validate_request_size
handle_session_timeout = EnhancedErrorHandler.handle_session_timeout