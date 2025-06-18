#!/usr/bin/env python3
"""
Debug AWS Lambda Handler for IELTS GenAI Prep
Enhanced logging for production debugging
"""

import json
import boto3
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Debug Lambda handler with comprehensive logging"""
    try:
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        body = event.get('body', '')
        
        logger.info(f"Request: {method} {path}")
        logger.info(f"Body: {body}")
        
        if path == '/debug-login' and method == 'POST':
            data = json.loads(body) if body else {}
            email = data.get('email', 'production@test.com')
            password = data.get('password', 'SecurePass123')
            
            # Initialize DynamoDB
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            users_table = dynamodb.Table('ielts-genai-prep-users')
            
            # Find user
            response = users_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if not response['Items']:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'User not found'})
                }
            
            user = response['Items'][0]
            stored_password_hash = user['password_hash']
            
            # Test password creation process
            salt = b'test_salt_32_bytes_long_exactly12'  # 32 bytes
            test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            combined = salt + test_hash
            hex_result = combined.hex()
            
            # Test verification process
            try:
                stored_combined = bytes.fromhex(stored_password_hash)
                stored_salt = stored_combined[:32]
                stored_hash = stored_combined[32:]
                verify_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), stored_salt, 100000)
                password_matches = verify_hash == stored_hash
            except Exception as verify_error:
                password_matches = False
                verify_error_msg = str(verify_error)
            else:
                verify_error_msg = "No error"
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'email': email,
                    'password_provided': password,
                    'stored_hash_length': len(stored_password_hash),
                    'stored_hash_sample': stored_password_hash[:20] + '...',
                    'test_hash_length': len(hex_result),
                    'test_hash_sample': hex_result[:20] + '...',
                    'password_matches': password_matches,
                    'verify_error': verify_error_msg,
                    'user_data_keys': list(user.keys())
                })
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Debug Lambda active',
                'path': path,
                'method': method
            })
        }
        
    except Exception as e:
        logger.error(f"Debug Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }