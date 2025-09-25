import json
import boto3
import hashlib
import jwt
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')
users_table = dynamodb.Table('ielts-genai-prep-users')
tokens_table = dynamodb.Table('ielts-genai-prep-auth-tokens')
reset_tokens_table = dynamodb.Table('ielts-genai-prep-reset-tokens')

# JWT Secret from environment variables
import os
JWT_SECRET = os.environ.get('JWT_SECRET', 'ielts-ai-prep-jwt-secret-2024-production')

def lambda_handler(event, context):
    """
    Main Lambda handler for authentication endpoints
    """
    try:
        # Parse the request
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}

        # Route to appropriate handler
        if http_method == 'POST' and path == '/api/register':
            return handle_register(body)
        elif http_method == 'POST' and path == '/api/login':
            return handle_login(body)
        elif http_method == 'POST' and path == '/api/mobile-login':
            return handle_mobile_login(body)
        elif http_method == 'POST' and path == '/api/validate-token':
            return handle_validate_token(event)
        elif http_method == 'POST' and path == '/api/forgot-password':
            return handle_forgot_password(body)
        elif http_method == 'POST' and path == '/api/reset-password':
            return handle_reset_password(body)
        elif http_method == 'POST' and path == '/api/account-deletion':
            return handle_account_deletion(event)
        elif http_method == 'GET' and path == '/api/health':
            return handle_health_check()
        else:
            return create_response(404, {'error': 'Endpoint not found'})

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_register(body):
    """
    Handle user registration
    """
    try:
        email = body.get('email', '').lower().strip()
        password = body.get('password', '')
        platform = body.get('platform', 'ios')

        if not email or not password:
            return create_response(400, {'error': 'Email and password required'})

        # Check if user already exists
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                return create_response(409, {'error': 'User already exists'})
        except ClientError as e:
            print(f"Error checking existing user: {str(e)}")

        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Create user record
        user_id = str(uuid.uuid4())
        user_data = {
            'email': email,
            'user_id': user_id,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'platform': platform,
            'subscription_status': 'inactive',
            'assessments_remaining': 0
        }

        users_table.put_item(Item=user_data)

        # Generate JWT token
        access_token = generate_jwt_token(user_id, email)
        refresh_token = str(uuid.uuid4())

        # Store token in DynamoDB
        store_auth_token(user_id, access_token, refresh_token)

        # Send welcome email for iOS users
        try:
            email_payload = {
                'type': 'welcome',
                'email': email,
                'name': email.split('@')[0],
                'platform': 'iOS'
            }

            lambda_client.invoke(
                FunctionName='ielts-email-service',
                InvocationType='Event',
                Payload=json.dumps(email_payload)
            )
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")

        return create_response(200, {
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'user_id': user_id,
                'email': email,
                'subscription_status': 'inactive',
                'platform': 'ios'
            },
            'accessToken': access_token,
            'refreshToken': refresh_token
        })

    except Exception as e:
        print(f"Error in handle_register: {str(e)}")
        return create_response(500, {'error': 'Registration failed'})

def handle_login(body):
    """
    Handle user login
    """
    try:
        email = body.get('email', '').lower().strip()
        password = body.get('password', '')
        platform = body.get('platform', 'ios')

        if not email or not password:
            return create_response(400, {'error': 'Email and password required'})

        # Get user from database
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' not in response:
                return create_response(401, {'error': 'Invalid credentials'})

            user = response['Item']
        except ClientError as e:
            print(f"Error getting user: {str(e)}")
            return create_response(500, {'error': 'Login failed'})

        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] != password_hash:
            return create_response(401, {'error': 'Invalid credentials'})

        # Update last login
        users_table.update_item(
            Key={'email': email},
            UpdateExpression='SET last_login = :timestamp',
            ExpressionAttributeValues={':timestamp': datetime.utcnow().isoformat()}
        )

        # Generate new tokens
        access_token = generate_jwt_token(user['user_id'], email)
        refresh_token = str(uuid.uuid4())

        # Store token
        store_auth_token(user['user_id'], access_token, refresh_token)

        return create_response(200, {
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user['user_id'],
                'email': email,
                'subscription_status': user.get('subscription_status', 'inactive'),
                'assessments_remaining': user.get('assessments_remaining', 0),
                'platform': 'ios'
            },
            'accessToken': access_token,
            'refreshToken': refresh_token
        })

    except Exception as e:
        print(f"Error in handle_login: {str(e)}")
        return create_response(500, {'error': 'Login failed'})

def handle_mobile_login(body):
    """
    Handle mobile-specific login with additional device info
    """
    try:
        result = handle_login(body)

        # If login successful, add mobile-specific data
        if result['statusCode'] == 200:
            response_body = json.loads(result['body'])
            response_body['platform'] = 'ios'
            response_body['mobile_features'] = {
                'qr_auth': True,
                'offline_mode': True,
                'push_notifications': True,
                'app_store_integration': True,
                'native_ui': True
            }
            result['body'] = json.dumps(response_body)

        return result

    except Exception as e:
        print(f"Error in handle_mobile_login: {str(e)}")
        return create_response(500, {'error': 'Mobile login failed'})

def handle_validate_token(event):
    """
    Validate JWT token
    """
    try:
        # Extract token from Authorization header
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')

        if not auth_header.startswith('Bearer '):
            return create_response(401, {'valid': False, 'error': 'Invalid authorization header'})

        token = auth_header.replace('Bearer ', '')

        # Validate JWT token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')

            # Check if token exists in database
            response = tokens_table.get_item(Key={'user_id': user_id})
            if 'Item' not in response:
                return create_response(401, {'valid': False, 'error': 'Token not found'})

            token_data = response['Item']
            if token_data['access_token'] != token:
                return create_response(401, {'valid': False, 'error': 'Token mismatch'})

            return create_response(200, {
                'valid': True,
                'user_id': user_id,
                'email': payload.get('email')
            })

        except jwt.ExpiredSignatureError:
            return create_response(401, {'valid': False, 'error': 'Token expired'})
        except jwt.InvalidTokenError:
            return create_response(401, {'valid': False, 'error': 'Invalid token'})

    except Exception as e:
        print(f"Error in handle_validate_token: {str(e)}")
        return create_response(500, {'valid': False, 'error': 'Token validation failed'})

def handle_forgot_password(body):
    """
    Handle forgot password request - NEW FUNCTIONALITY
    """
    try:
        email = body.get('email', '').lower().strip()

        if not email:
            return create_response(400, {'error': 'Email address is required'})

        # Check if user exists
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' not in response:
                # For security, don't reveal if email exists or not
                return create_response(200, {
                    'success': True,
                    'message': 'If an account with this email exists, a password reset link has been sent.'
                })

            user = response['Item']
        except ClientError as e:
            print(f"Error getting user for password reset: {str(e)}")
            return create_response(500, {'error': 'Password reset request failed'})

        # Generate reset token
        reset_token = str(uuid.uuid4())

        # Store reset token in DynamoDB with 1-hour expiration
        try:
            reset_token_data = {
                'reset_token': reset_token,
                'email': email,
                'user_id': user['user_id'],
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                'used': False
            }

            reset_tokens_table.put_item(Item=reset_token_data)

        except Exception as e:
            print(f"Error storing reset token: {str(e)}")
            return create_response(500, {'error': 'Password reset request failed'})

        # Send password reset email
        try:
            email_payload = {
                'type': 'password_reset',
                'email': email,
                'reset_token': reset_token,
                'name': user.get('name', email.split('@')[0]),
                'platform': 'iOS'
            }

            lambda_client.invoke(
                FunctionName='ielts-email-service',
                InvocationType='Event',
                Payload=json.dumps(email_payload)
            )

        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")

        return create_response(200, {
            'success': True,
            'message': 'If an account with this email exists, a password reset link has been sent.'
        })

    except Exception as e:
        print(f"Error in handle_forgot_password: {str(e)}")
        return create_response(500, {'error': 'Password reset request failed'})

def handle_reset_password(body):
    """
    Handle password reset with token - NEW FUNCTIONALITY
    """
    try:
        reset_token = body.get('token', '')
        new_password = body.get('password', '')

        if not reset_token or not new_password:
            return create_response(400, {'error': 'Reset token and new password are required'})

        # Validate reset token
        try:
            response = reset_tokens_table.get_item(Key={'reset_token': reset_token})
            if 'Item' not in response:
                return create_response(400, {'error': 'Invalid or expired reset token'})

            token_data = response['Item']
        except ClientError as e:
            print(f"Error getting reset token: {str(e)}")
            return create_response(400, {'error': 'Invalid or expired reset token'})

        # Check if token is expired or used
        expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
        if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
            return create_response(400, {'error': 'Reset token has expired'})

        if token_data.get('used', False):
            return create_response(400, {'error': 'Reset token has already been used'})

        # Update user password
        email = token_data['email']
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()

        try:
            users_table.update_item(
                Key={'email': email},
                UpdateExpression='SET password_hash = :password_hash, last_login = :timestamp',
                ExpressionAttributeValues={
                    ':password_hash': password_hash,
                    ':timestamp': datetime.utcnow().isoformat()
                }
            )
        except ClientError as e:
            print(f"Error updating user password: {str(e)}")
            return create_response(500, {'error': 'Password reset failed'})

        # Mark token as used
        try:
            reset_tokens_table.update_item(
                Key={'reset_token': reset_token},
                UpdateExpression='SET used = :used',
                ExpressionAttributeValues={':used': True}
            )
        except Exception as e:
            print(f"Error marking token as used: {str(e)}")

        # Invalidate all existing auth tokens for this user
        try:
            user_id = token_data['user_id']
            tokens_table.delete_item(Key={'user_id': user_id})
        except Exception as e:
            print(f"Error invalidating tokens: {str(e)}")

        return create_response(200, {
            'success': True,
            'message': 'Password reset successfully. Please log in with your new password.'
        })

    except Exception as e:
        print(f"Error in handle_reset_password: {str(e)}")
        return create_response(500, {'error': 'Password reset failed'})

def handle_account_deletion(event):
    """
    Handle GDPR-compliant account deletion
    """
    try:
        # Validate token first
        token_validation = handle_validate_token(event)
        if token_validation['statusCode'] != 200:
            return token_validation

        token_data = json.loads(token_validation['body'])
        user_id = token_data['user_id']
        email = token_data['email']

        # Delete user data
        users_table.delete_item(Key={'email': email})
        tokens_table.delete_item(Key={'user_id': user_id})

        # Delete reset tokens
        try:
            response = reset_tokens_table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            for item in response.get('Items', []):
                reset_tokens_table.delete_item(Key={'reset_token': item['reset_token']})
        except Exception as e:
            print(f"Error deleting reset tokens: {str(e)}")

        # Delete from assessments table
        try:
            assessments_table = dynamodb.Table('ielts-genai-prep-assessments')
            response = assessments_table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            for item in response.get('Items', []):
                assessments_table.delete_item(Key={'assessment_id': item['assessment_id']})
        except Exception as e:
            print(f"Error deleting user assessments: {str(e)}")

        # Send account deletion confirmation email
        try:
            email_payload = {
                'type': 'account_deletion',
                'email': email,
                'platform': 'iOS'
            }

            lambda_client.invoke(
                FunctionName='ielts-email-service',
                InvocationType='Event',
                Payload=json.dumps(email_payload)
            )
        except Exception as e:
            print(f"Error sending deletion confirmation email: {str(e)}")

        return create_response(200, {
            'success': True,
            'message': 'Account deleted successfully'
        })

    except Exception as e:
        print(f"Error in handle_account_deletion: {str(e)}")
        return create_response(500, {'error': 'Account deletion failed'})

def handle_health_check():
    """
    Health check endpoint
    """
    try:
        # Test DynamoDB connections
        users_table.scan(Limit=1)
        tokens_table.scan(Limit=1)
        reset_tokens_table.scan(Limit=1)

        return create_response(200, {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'platform': 'iOS',
            'services': {
                'dynamodb': 'active',
                'lambda': 'active',
                'email_service': 'active'
            },
            'features': {
                'user_registration': True,
                'user_login': True,
                'password_reset': True,
                'account_deletion': True,
                'token_validation': True
            }
        })

    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return create_response(500, {
            'status': 'unhealthy',
            'error': str(e),
            'platform': 'iOS'
        })

def generate_jwt_token(user_id, email):
    """
    Generate JWT access token
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'platform': 'ios',
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def store_auth_token(user_id, access_token, refresh_token):
    """
    Store authentication tokens in DynamoDB
    """
    token_data = {
        'user_id': user_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'platform': 'ios',
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }
    tokens_table.put_item(Item=token_data)

def create_response(status_code, body):
    """
    Create standardized API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }