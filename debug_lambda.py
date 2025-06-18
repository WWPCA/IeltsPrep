#!/usr/bin/env python3
"""
Debug AWS Lambda Handler for IELTS GenAI Prep
Enhanced logging for production debugging
"""

import json
import os
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def lambda_handler(event, context):
    """Debug Lambda handler with comprehensive logging"""
    try:
        logger.info(f"Lambda invoked with event: {json.dumps(event, default=str)}")
        logger.info(f"Context: {context}")
        
        # Check environment variables
        logger.info(f"Environment variables: {dict(os.environ)}")
        
        # Parse the request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        
        logger.info(f"Processing {http_method} {path}")
        logger.info(f"Headers: {headers}")
        
        # Test DynamoDB access
        try:
            import boto3
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('ielts-genai-prep-users')
            logger.info("DynamoDB connection successful")
        except Exception as e:
            logger.error(f"DynamoDB connection failed: {str(e)}")
        
        # Return successful response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'message': 'IELTS GenAI Prep API - Debug Mode',
                'status': 'success',
                'method': http_method,
                'path': path,
                'timestamp': context.aws_request_id if context else 'local',
                'environment': os.environ.get('ENVIRONMENT', 'unknown'),
                'region': os.environ.get('AWS_REGION', 'us-east-1')
            })
        }
        
        logger.info(f"Returning response: {json.dumps(response, default=str)}")
        return response
        
    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'event': event,
                'environment': dict(os.environ)
            })
        }
        
        logger.info(f"Returning error response: {json.dumps(error_response, default=str)}")
        return error_response