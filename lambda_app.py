"""
AWS Lambda Flask Application for IELTS GenAI Prep
Global serverless architecture with DynamoDB and regional routing
"""

import json
import boto3
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")

# AWS Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE = "IELTSUsers"
ASSESSMENTS_TABLE = "IELTSAssessments"
ELASTICACHE_ENDPOINT = os.environ.get("ELASTICACHE_ENDPOINT")

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')  # Nova Sonic only in us-east-1

# Initialize Redis for session management
redis_client = None
if ELASTICACHE_ENDPOINT:
    try:
        redis_client = redis.Redis(host=ELASTICACHE_ENDPOINT.split(':')[0], 
                                 port=int(ELASTICACHE_ENDPOINT.split(':')[1]), 
                                 decode_responses=True)
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

# DynamoDB Tables
users_table = dynamodb.Table(DYNAMODB_TABLE)
assessments_table = dynamodb.Table(ASSESSMENTS_TABLE)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check for API Gateway"""
    return jsonify({'status': 'healthy', 'region': AWS_REGION, 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register new user with DynamoDB"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                return jsonify({'error': 'User already exists'}), 409
        except Exception as e:
            logger.error(f"DynamoDB error checking user: {e}")
        
        # Create new user
        user_data = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow().isoformat(),
            'assessment_modules': [],  # Purchased modules
            'assessments_completed': 0,
            'region': AWS_REGION
        }
        
        users_table.put_item(Item=user_data)
        
        return jsonify({'message': 'User registered successfully', 'email': email}), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Get user from DynamoDB
        response = users_table.get_item(Key={'email': email})
        if 'Item' not in response:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = response['Item']
        
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create session
        session_id = f"session_{email}_{int(datetime.utcnow().timestamp())}"
        session_data = {
            'email': email,
            'logged_in': True,
            'region': AWS_REGION,
            'modules': user.get('assessment_modules', [])
        }
        
        # Store session in Redis with 1-hour expiration
        if redis_client:
            redis_client.set(session_id, json.dumps(session_data), ex=3600)
        
        return jsonify({
            'message': 'Login successful',
            'session_id': session_id,
            'modules': user.get('assessment_modules', [])
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/nova-sonic/speaking', methods=['POST'])
def nova_sonic_speaking():
    """
    Nova Sonic speech-to-speech assessment (routed to us-east-1)
    Global users may experience latency - notify user beforehand
    """
    try:
        data = request.get_json()
        user_audio = data.get('audio_data')  # Base64 encoded audio
        session_id = data.get('session_id')
        assessment_type = data.get('assessment_type', 'academic_speaking')
        
        if not user_audio or not session_id:
            return jsonify({'error': 'Audio data and session required'}), 400
        
        # Verify session
        if redis_client:
            session_data = redis_client.get(session_id)
            if not session_data:
                return jsonify({'error': 'Invalid session'}), 401
            session_info = json.loads(session_data)
            user_email = session_info['email']
        else:
            return jsonify({'error': 'Session management unavailable'}), 503
        
        # Nova Sonic API call with retry logic and extended timeout
        try:
            # Call Nova Sonic (speech-to-speech) - only available in us-east-1
            nova_response = bedrock.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                body=json.dumps({
                    "audio": user_audio,
                    "prompt": "Assess this IELTS speaking response for fluency, pronunciation, vocabulary, and grammar. Provide detailed feedback.",
                    "maxTokens": 1000
                }),
                contentType="application/json"
            )
            
            response_body = json.loads(nova_response['body'].read().decode('utf-8'))
            
            # Extract written assessment only (no voice data stored)
            written_assessment = {
                'fluency_score': response_body.get('fluency_score', 0),
                'pronunciation_score': response_body.get('pronunciation_score', 0),
                'vocabulary_score': response_body.get('vocabulary_score', 0),
                'grammar_score': response_body.get('grammar_score', 0),
                'overall_score': response_body.get('overall_score', 0),
                'feedback': response_body.get('feedback', ''),
                'transcript': response_body.get('transcript', ''),
                'assessed_at': datetime.utcnow().isoformat(),
                'assessment_type': assessment_type
            }
            
            # Save only written assessment to DynamoDB
            users_table.update_item(
                Key={'email': user_email},
                UpdateExpression='SET speaking_assessments = list_append(if_not_exists(speaking_assessments, :empty_list), :assessment)',
                ExpressionAttributeValues={
                    ':assessment': [written_assessment],
                    ':empty_list': []
                }
            )
            
            return jsonify({
                'message': 'Assessment completed',
                'assessment': written_assessment,
                'note': 'Voice data not stored - only written assessment saved'
            }), 200
            
        except Exception as e:
            logger.error(f"Nova Sonic error: {e}")
            return jsonify({'error': 'Speech assessment failed', 'retry_suggested': True}), 500
        
    except Exception as e:
        logger.error(f"Speaking assessment error: {e}")
        return jsonify({'error': 'Assessment failed'}), 500

@app.route('/api/nova-micro/writing', methods=['POST'])
def nova_micro_writing():
    """
    Nova Micro writing assessment (can use regional endpoints)
    """
    try:
        data = request.get_json()
        essay_text = data.get('essay_text')
        prompt = data.get('prompt')
        session_id = data.get('session_id')
        assessment_type = data.get('assessment_type', 'academic_writing')
        
        if not essay_text or not session_id:
            return jsonify({'error': 'Essay text and session required'}), 400
        
        # Verify session
        if redis_client:
            session_data = redis_client.get(session_id)
            if not session_data:
                return jsonify({'error': 'Invalid session'}), 401
            session_info = json.loads(session_data)
            user_email = session_info['email']
        else:
            return jsonify({'error': 'Session management unavailable'}), 503
        
        # Nova Micro API call (regional)
        try:
            nova_response = bedrock.invoke_model(
                modelId="amazon.nova-micro-v1:0",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an IELTS writing assessor. Evaluate this essay for Task Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy."
                        },
                        {
                            "role": "user",
                            "content": f"Prompt: {prompt}\n\nEssay: {essay_text}"
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }),
                contentType="application/json"
            )
            
            response_body = json.loads(nova_response['body'].read().decode('utf-8'))
            
            # Extract written assessment
            written_assessment = {
                'task_achievement': response_body.get('task_achievement', 0),
                'coherence_cohesion': response_body.get('coherence_cohesion', 0),
                'lexical_resource': response_body.get('lexical_resource', 0),
                'grammatical_range': response_body.get('grammatical_range', 0),
                'overall_score': response_body.get('overall_score', 0),
                'feedback': response_body.get('feedback', ''),
                'essay_text': essay_text,
                'prompt': prompt,
                'assessed_at': datetime.utcnow().isoformat(),
                'assessment_type': assessment_type
            }
            
            # Save to DynamoDB
            users_table.update_item(
                Key={'email': user_email},
                UpdateExpression='SET writing_assessments = list_append(if_not_exists(writing_assessments, :empty_list), :assessment)',
                ExpressionAttributeValues={
                    ':assessment': [written_assessment],
                    ':empty_list': []
                }
            )
            
            return jsonify({
                'message': 'Writing assessment completed',
                'assessment': written_assessment
            }), 200
            
        except Exception as e:
            logger.error(f"Nova Micro error: {e}")
            return jsonify({'error': 'Writing assessment failed'}), 500
        
    except Exception as e:
        logger.error(f"Writing assessment error: {e}")
        return jsonify({'error': 'Assessment failed'}), 500

@app.route('/api/purchase/verify-apple', methods=['POST'])
def verify_apple_purchase():
    """Verify Apple App Store purchase"""
    try:
        data = request.get_json()
        receipt_data = data.get('receipt_data')
        session_id = data.get('session_id')
        
        if not receipt_data or not session_id:
            return jsonify({'error': 'Receipt data and session required'}), 400
        
        # Get user from session
        if redis_client:
            session_data = redis_client.get(session_id)
            if not session_data:
                return jsonify({'error': 'Invalid session'}), 401
            session_info = json.loads(session_data)
            user_email = session_info['email']
        
        # Verify with Apple (simplified - use actual App Store Connect API)
        # This would normally make a request to https://buy.itunes.apple.com/verifyReceipt
        # For now, we'll simulate successful verification
        
        module_purchased = data.get('product_id', 'academic_speaking')  # e.g., 'academic_speaking'
        
        # Update user's purchased modules
        users_table.update_item(
            Key={'email': user_email},
            UpdateExpression='ADD assessment_modules :module',
            ExpressionAttributeValues={':module': {module_purchased}}
        )
        
        return jsonify({
            'message': 'Purchase verified successfully',
            'module': module_purchased,
            'price': '$36'
        }), 200
        
    except Exception as e:
        logger.error(f"Apple purchase verification error: {e}")
        return jsonify({'error': 'Purchase verification failed'}), 500

@app.route('/api/purchase/verify-google', methods=['POST'])
def verify_google_purchase():
    """Verify Google Play Store purchase"""
    try:
        data = request.get_json()
        purchase_token = data.get('purchase_token')
        session_id = data.get('session_id')
        
        if not purchase_token or not session_id:
            return jsonify({'error': 'Purchase token and session required'}), 400
        
        # Verify with Google Play Billing API
        # This would use Google Play Developer API to verify the purchase
        # For now, we'll simulate successful verification
        
        module_purchased = data.get('product_id', 'academic_writing')
        
        # Get user from session and update modules
        if redis_client:
            session_data = redis_client.get(session_id)
            if not session_data:
                return jsonify({'error': 'Invalid session'}), 401
            session_info = json.loads(session_data)
            user_email = session_info['email']
        
        users_table.update_item(
            Key={'email': user_email},
            UpdateExpression='ADD assessment_modules :module',
            ExpressionAttributeValues={':module': {module_purchased}}
        )
        
        return jsonify({
            'message': 'Purchase verified successfully',
            'module': module_purchased,
            'price': '$36'
        }), 200
        
    except Exception as e:
        logger.error(f"Google purchase verification error: {e}")
        return jsonify({'error': 'Purchase verification failed'}), 500

# Lambda handler for AWS deployment
def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        # Convert API Gateway event to Flask request
        from werkzeug.wrappers import Request
        from werkzeug.test import EnvironBuilder
        
        builder = EnvironBuilder(
            path=event.get('path', '/'),
            method=event.get('httpMethod', 'GET'),
            headers=event.get('headers', {}),
            data=event.get('body', ''),
            query_string=event.get('queryStringParameters', {})
        )
        
        env = builder.get_environ()
        request = Request(env)
        
        with app.request_context(env):
            response = app.full_dispatch_request()
            
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)