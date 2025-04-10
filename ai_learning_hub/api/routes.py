"""
API Routes for AI Learning Hub Mobile Applications
This module provides RESTful endpoints for the native iOS and Android apps.
"""
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
import json
import os
from datetime import datetime

from ai_learning_hub.api.utils import api_response, error_response, handle_api_exception, get_device_info
from ai_learning_hub.api.auth import token_required, generate_token

# Create a blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Global error handler
@api_bp.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions within the API"""
    return handle_api_exception(e)

# ------------------- Authentication endpoints -------------------
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """API endpoint for mobile login"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Invalid request format', 400)
        
        # Extract login credentials
        email = data.get('email')
        password = data.get('password')
        device_info = get_device_info(request)
        
        if not email or not password:
            return error_response('Missing email or password', 400)
        
        # TODO: Implement login logic with user authentication
        # For now, return a development message
        return api_response(
            message='Login endpoint active',
            data={
                'token': 'sample_token_for_development',
                'user': {
                    'id': 1,
                    'username': 'test_user',
                    'email': email
                },
                'device_info': device_info
            }
        )
    except Exception as e:
        return handle_api_exception(e)

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """API endpoint for mobile registration"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Invalid request format', 400)
        
        # Extract registration data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return error_response('Missing required registration fields', 400)
        
        # TODO: Implement registration logic
        # For now, return a development message
        return api_response(
            message='Registration endpoint active',
            data={
                'user_id': 1
            }
        )
    except Exception as e:
        return handle_api_exception(e)

# ------------------- Course endpoints -------------------
@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all available courses"""
    try:
        # TODO: Implement course retrieval logic
        return api_response(
            message='Courses endpoint active',
            data={
                'courses': []
            }
        )
    except Exception as e:
        return handle_api_exception(e)

@api_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get a specific course by ID"""
    try:
        # TODO: Implement specific course retrieval logic
        return api_response(
            message=f'Course {course_id} endpoint active',
            data={
                'course': {}
            }
        )
    except Exception as e:
        return handle_api_exception(e)

# ------------------- User data endpoints -------------------
@api_bp.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    """Get the current user's profile"""
    try:
        # Get user_id from the request (added by the token_required decorator)
        user_id = request.user_id
        
        # TODO: Implement user profile retrieval logic
        return api_response(
            message='User profile endpoint active',
            data={
                'user': {
                    'id': user_id,
                    'username': 'test_user',
                    'email': 'test@example.com'
                }
            }
        )
    except Exception as e:
        return handle_api_exception(e)

@api_bp.route('/user/progress', methods=['GET'])
@token_required
def get_user_progress():
    """Get the current user's learning progress"""
    try:
        # Get user_id from the request (added by the token_required decorator)
        user_id = request.user_id
        
        # TODO: Implement progress retrieval logic
        return api_response(
            message='User progress endpoint active',
            data={
                'progress': {
                    'courses_enrolled': 0,
                    'courses_completed': 0
                }
            }
        )
    except Exception as e:
        return handle_api_exception(e)

# ------------------- Mobile specific endpoints -------------------
@api_bp.route('/sync', methods=['POST'])
@token_required
def sync_data():
    """Synchronize offline data with the server"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Invalid request format', 400)
        
        # Get user_id from the request (added by the token_required decorator)
        user_id = request.user_id
        
        # Extract sync data
        device_id = data.get('device_id')
        sync_type = data.get('sync_type')
        content_type = data.get('content_type')
        
        if not device_id or not sync_type:
            return error_response('Missing required sync fields', 400)
        
        # TODO: Implement data synchronization logic
        return api_response(
            message='Sync endpoint active',
            data={
                'sync_id': 123,
                'last_sync': datetime.utcnow().isoformat(),
                'server_changes': []
            }
        )
    except Exception as e:
        return handle_api_exception(e)

@api_bp.route('/config', methods=['GET'])
def get_app_config():
    """Get mobile app configuration"""
    try:
        # Get device info
        device_info = get_device_info(request)
        platform = device_info.get('platform', 'unknown')
        
        # Return app-specific configuration for mobile clients
        return api_response(
            data={
                'api_version': '1.0',
                'min_app_version': {
                    'ios': '1.0.0',
                    'android': '1.0.0'
                },
                'features': {
                    'offline_mode': True,
                    'push_notifications': True
                },
                'media_cdn': request.url_root + 'static/',
                'support_email': 'support@ailearninghub.example.com'
            }
        )
    except Exception as e:
        return handle_api_exception(e)