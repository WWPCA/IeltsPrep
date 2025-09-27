"""
Mobile API endpoints for IELTS GenAI Prep
Provides JWT-based authentication and user management for mobile clients
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
# Using DynamoDB UserDAL instead of SQLAlchemy models
# from dynamodb_dal import UserDAL  # Import when needed in specific functions
from auth_jwt import generate_jwt_token, jwt_required, create_api_response

# Create API blueprint
api_mobile = Blueprint('api_mobile', __name__, url_prefix='/api/v1')


@api_mobile.route('/auth/login', methods=['POST'])
def mobile_login():
    """
    Mobile login endpoint that returns JWT token
    """
    try:
        data = request.get_json()
        if not data:
            return create_api_response(False, 'Request body must be JSON', status_code=400)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return create_api_response(False, 'Email and password are required', status_code=400)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return create_api_response(False, 'Invalid email or password', status_code=401)
        
        if not user.is_active:
            return create_api_response(False, 'Account is deactivated', status_code=401)
        
        # Generate JWT token
        token = generate_jwt_token(user.id)
        
        # Update last login
        user.last_login = db.func.now()
        db.session.commit()
        
        # Return token and user info
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'join_date': user.join_date.isoformat() if user.join_date else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'has_active_assessment': user.has_active_assessment_package()
        }
        
        return create_api_response(True, 'Login successful', {
            'token': token,
            'user': user_data,
            'token_expires_in': current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()
        })
        
    except Exception as e:
        current_app.logger.error(f"Mobile login error: {e}")
        return create_api_response(False, 'Login failed', status_code=500)


@api_mobile.route('/auth/register', methods=['POST'])
def mobile_register():
    """
    Mobile registration endpoint
    """
    try:
        data = request.get_json()
        if not data:
            return create_api_response(False, 'Request body must be JSON', status_code=400)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not all([username, email, password]):
            return create_api_response(False, 'Username, email, and password are required', status_code=400)
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return create_api_response(False, 'Email already registered', status_code=409)
        
        if User.query.filter_by(username=username).first():
            return create_api_response(False, 'Username already taken', status_code=409)
        
        # Create new user
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.full_name = full_name
        new_user.is_active = True
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token for immediate login
        token = generate_jwt_token(new_user.id)
        
        user_data = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'full_name': new_user.full_name,
            'join_date': new_user.join_date.isoformat()
        }
        
        return create_api_response(True, 'Registration successful', {
            'token': token,
            'user': user_data,
            'token_expires_in': current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Mobile registration error: {e}")
        return create_api_response(False, 'Registration failed', status_code=500)


@api_mobile.route('/user/profile', methods=['GET'])
@jwt_required
def get_user_profile():
    """
    Get current user profile (requires JWT token)
    """
    try:
        from flask import g
        user = g.current_user
        
        # Get assessment entitlements
        entitlements = AssessmentEntitlement.query.filter_by(user_id=user.id).all()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'bio': user.bio,
            'join_date': user.join_date.isoformat() if user.join_date else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'preferred_language': user.preferred_language,
            'assessment_package_status': user.assessment_package_status,
            'assessment_package_expiry': user.assessment_package_expiry.isoformat() if user.assessment_package_expiry else None,
            'preferences': user.preferences,
            'assessment_entitlements': [
                {
                    'product_id': ent.product_id,
                    'remaining_uses': ent.remaining_uses,
                    'expires_at': ent.expires_at.isoformat() if ent.expires_at else None
                }
                for ent in entitlements
            ]
        }
        
        return create_api_response(True, 'Profile retrieved successfully', user_data)
        
    except Exception as e:
        current_app.logger.error(f"Get profile error: {e}")
        return create_api_response(False, 'Failed to retrieve profile', status_code=500)


@api_mobile.route('/user/profile', methods=['PUT'])
@jwt_required
def update_user_profile():
    """
    Update current user profile (requires JWT token)
    """
    try:
        from flask import g
        user = g.current_user
        data = request.get_json()
        
        if not data:
            return create_api_response(False, 'Request body must be JSON', status_code=400)
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'bio' in data:
            user.bio = data['bio'].strip()
        
        if 'preferred_language' in data:
            user.preferred_language = data['preferred_language']
        
        if 'preferences' in data and isinstance(data['preferences'], dict):
            user.preferences = data['preferences']
        
        db.session.commit()
        
        return create_api_response(True, 'Profile updated successfully')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update profile error: {e}")
        return create_api_response(False, 'Failed to update profile', status_code=500)


@api_mobile.route('/health', methods=['GET'])
def api_health():
    """
    API health check endpoint
    """
    return create_api_response(True, 'API is healthy', {
        'version': '1.0',
        'service': 'IELTS GenAI Prep Mobile API'
    })


# Error handlers for the API blueprint
@api_mobile.errorhandler(404)
def api_not_found(error):
    return create_api_response(False, 'Endpoint not found', status_code=404)


@api_mobile.errorhandler(405)
def api_method_not_allowed(error):
    return create_api_response(False, 'Method not allowed', status_code=405)


@api_mobile.errorhandler(500)
def api_internal_error(error):
    return create_api_response(False, 'Internal server error', status_code=500)