#!/usr/bin/env python3
"""
Simplified AWS Lambda Handler for IELTS GenAI Prep
Production version without external dependencies
"""

import json
import os
import uuid
import boto3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Main AWS Lambda handler for production environment"""
    try:
        logger.info(f"Processing: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', '/')}")
        
        # Extract request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Parse JSON body if present
        data = {}
        if body:
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in request body")
                pass
        
        # Initialize AWS services
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Route requests
        if path == '/health' or path == '/':
            return handle_health_check()
        elif path == '/api/auth/register' and http_method == 'POST':
            return handle_user_registration(data, dynamodb)
        elif path == '/api/auth/login' and http_method == 'POST':
            return handle_user_login(data, dynamodb)
        elif path.startswith('/assessment/'):
            return handle_assessment_access(path, headers, dynamodb)
        elif path == '/api/health':
            return handle_health_check()
        else:
            return success_response({
                'message': 'IELTS GenAI Prep API - Production Ready',
                'version': '1.0',
                'environment': 'AWS Lambda',
                'path': path,
                'method': http_method
            })
            
    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}")
        return error_response(f"Service temporarily unavailable", 500)

def handle_health_check():
    """Health check endpoint"""
    return success_response({
        'status': 'healthy',
        'service': 'ielts-genai-prep-api',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'region': 'us-east-1',
        'environment': 'production'
    })

def handle_user_registration(data: Dict[str, Any], dynamodb):
    """Handle user registration with simple password hashing"""
    try:
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not email or not password:
            return error_response('Email and password required', 400)
        
        # Simple password hashing (SHA-256 with salt)
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        stored_password = salt + password_hash
        
        # Store user in DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        user_id = str(uuid.uuid4())
        
        # Check if user already exists
        response = users_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if response['Items']:
            return error_response('User already exists', 409)
        
        users_table.put_item(
            Item={
                'user_id': user_id,
                'email': email,
                'name': name,
                'password_hash': stored_password.hex(),
                'created_at': datetime.utcnow().isoformat(),
                'assessment_counts': {
                    'academic_writing': {'remaining': 0, 'used': 0},
                    'general_writing': {'remaining': 0, 'used': 0},
                    'academic_speaking': {'remaining': 0, 'used': 0},
                    'general_speaking': {'remaining': 0, 'used': 0}
                }
            }
        )
        
        logger.info(f"User registered successfully: {email}")
        return success_response({
            'message': 'Registration successful',
            'user_id': user_id,
            'email': email
        })
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return error_response('Registration failed', 500)

def handle_user_login(data: Dict[str, Any], dynamodb):
    """Handle user login with password verification"""
    try:
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return error_response('Email and password required', 400)
        
        # Query user from DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        response = users_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if not response['Items']:
            return error_response('Invalid credentials', 401)
        
        user = response['Items'][0]
        
        # Verify password
        stored_password = bytes.fromhex(user['password_hash'])
        salt = stored_password[:32]
        stored_hash = stored_password[32:]
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        
        if password_hash != stored_hash:
            return error_response('Invalid credentials', 401)
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_email': email,
            'user_id': user['user_id'],
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store session in DynamoDB
        auth_table = dynamodb.Table('ielts-genai-prep-auth-tokens')
        auth_table.put_item(Item=session_data)
        
        logger.info(f"User login successful: {email}")
        return success_response({
            'message': 'Login successful',
            'session_id': session_id,
            'user': {
                'email': email,
                'name': user.get('name', ''),
                'assessment_counts': user.get('assessment_counts', {})
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return error_response('Login failed', 500)

def handle_assessment_access(path: str, headers: Dict[str, Any], dynamodb):
    """Handle assessment access with session verification"""
    try:
        assessment_type = path.split('/')[-1]
        
        # Verify session from Authorization header
        auth_header = headers.get('Authorization', headers.get('authorization', ''))
        session_id = auth_header.replace('Bearer ', '') if auth_header else ''
        
        if not session_id:
            return error_response('Authentication required', 401)
        
        # Check session validity
        auth_table = dynamodb.Table('ielts-genai-prep-auth-tokens')
        response = auth_table.get_item(Key={'session_id': session_id})
        
        if 'Item' not in response:
            return error_response('Invalid session', 401)
        
        session = response['Item']
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.utcnow() > expires_at:
            return error_response('Session expired', 401)
        
        logger.info(f"Assessment access granted: {assessment_type} for {session['user_email']}")
        return success_response({
            'assessment_type': assessment_type,
            'user_email': session['user_email'],
            'session_valid': True,
            'access_granted': True,
            'message': f'Access granted to {assessment_type} assessment'
        })
        
    except Exception as e:
        logger.error(f"Assessment access error: {str(e)}")
        return error_response('Assessment access failed', 500)

def success_response(data: Dict[str, Any], status_code: int = 200):
    """Format success response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps(data, default=str)
    }

def error_response(message: str, status_code: int = 400):
    """Format error response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps({'error': message, 'status': status_code})
    }