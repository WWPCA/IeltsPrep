#!/usr/bin/env python3
"""
Production AWS Lambda Handler for IELTS GenAI Prep
Real AWS services integration without mock dependencies
"""

import json
import os
import uuid
import time
import base64
import boto3
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Main AWS Lambda handler for production environment"""
    try:
        logger.info(f"Lambda invoked: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', '/')}")
        
        # Initialize AWS services
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
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
                pass
        
        # Route requests
        if path == '/health' or path == '/':
            return handle_health_check()
        elif path == '/api/auth/register' and http_method == 'POST':
            return handle_user_registration(data, dynamodb)
        elif path == '/api/auth/login' and http_method == 'POST':
            return handle_user_login(data, dynamodb)
        elif path.startswith('/assessment/'):
            return handle_assessment_access(path, headers, dynamodb)
        else:
            return success_response({'message': 'IELTS GenAI Prep API - Production'})
            
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        return error_response(f"Internal server error: {str(e)}", 500)

def handle_health_check():
    """Health check endpoint"""
    return success_response({
        'status': 'healthy',
        'service': 'ielts-genai-prep-api',
        'version': '1.0',
        'timestamp': datetime.utcnow().isoformat()
    })

def handle_user_registration(data: Dict[str, Any], dynamodb):
    """Handle user registration"""
    try:
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not email or not password:
            return error_response('Email and password required', 400)
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Store user in DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        user_id = str(uuid.uuid4())
        
        users_table.put_item(
            Item={
                'user_id': user_id,
                'email': email,
                'name': name,
                'password_hash': password_hash,
                'created_at': datetime.utcnow().isoformat(),
                'assessment_counts': {
                    'academic_writing': {'remaining': 0, 'used': 0},
                    'general_writing': {'remaining': 0, 'used': 0},
                    'academic_speaking': {'remaining': 0, 'used': 0},
                    'general_speaking': {'remaining': 0, 'used': 0}
                }
            }
        )
        
        logger.info(f"User registered: {email}")
        return success_response({'message': 'User registered successfully', 'user_id': user_id})
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return error_response('Registration failed', 500)

def handle_user_login(data: Dict[str, Any], dynamodb):
    """Handle user login"""
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
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
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
        
        logger.info(f"User logged in: {email}")
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
    """Handle assessment access"""
    try:
        # Extract assessment type from path
        assessment_type = path.split('/')[-1]
        
        # Verify session
        session_id = headers.get('Authorization', '').replace('Bearer ', '')
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
        
        # Return assessment template or data
        return success_response({
            'assessment_type': assessment_type,
            'user_email': session['user_email'],
            'session_valid': True,
            'template': f'Assessment template for {assessment_type}'
        })
        
    except Exception as e:
        logger.error(f"Assessment access error: {str(e)}")
        return error_response('Assessment access failed', 500)

def success_response(data: Dict[str, Any], status_code: int = 200):
    """Format success response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(data)
    }

def error_response(message: str, status_code: int = 400):
    """Format error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }