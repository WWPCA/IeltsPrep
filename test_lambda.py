#!/usr/bin/env python3
"""
Minimal test Lambda for debugging authentication
"""

import json
import boto3
import hashlib
import uuid
from datetime import datetime

def lambda_handler(event, context):
    """Debug Lambda handler"""
    try:
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        if path == '/test-register' and method == 'POST':
            # Simple registration test
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            users_table = dynamodb.Table('ielts-genai-prep-users')
            
            # Use simple string password for testing
            test_user = {
                'user_id': str(uuid.uuid4()),
                'email': 'debug@test.com',
                'name': 'Debug User',
                'password_hash': 'simple_password_123',  # Plain text for testing
                'created_at': datetime.utcnow().isoformat(),
                'assessment_counts': {
                    'academic_writing': {'remaining': 4, 'used': 0}
                }
            }
            
            users_table.put_item(Item=test_user)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Debug user created', 'user_id': test_user['user_id']})
            }
            
        elif path == '/test-login' and method == 'POST':
            # Simple login test
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            users_table = dynamodb.Table('ielts-genai-prep-users')
            
            response = users_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': 'debug@test.com'}
            )
            
            if response['Items']:
                user = response['Items'][0]
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'User found',
                        'email': user['email'],
                        'password_hash': user['password_hash'],
                        'user_data': str(user)
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'User not found'})
                }
        
        # Default response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Debug Lambda working',
                'path': path,
                'method': method
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }