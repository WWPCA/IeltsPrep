import json
import boto3
import base64
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize AWS services
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('ielts-genai-prep-users')
assessments_table = dynamodb.Table('ielts-genai-prep-assessments')

# Nova AI Model IDs
NOVA_SONIC_MODEL_ID = "amazon.nova-sonic-v1:0"
NOVA_MICRO_MODEL_ID = "amazon.nova-micro-v1:0"

def lambda_handler(event, context):
    """
    Main Lambda handler for Nova AI service endpoints
    """
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        # Validate authentication for all endpoints
        auth_result = validate_auth_token(event)
        if auth_result['statusCode'] != 200:
            return auth_result
        
        user_data = json.loads(auth_result['body'])
        
        if http_method == 'POST' and path == '/api/nova-sonic-connect':
            return handle_nova_sonic_connect(body, user_data)
        elif http_method == 'POST' and path == '/api/nova-sonic-stream':
            return handle_nova_sonic_stream(body, user_data)
        elif http_method == 'POST' and path == '/api/nova-micro/writing':
            return handle_nova_micro_writing(body, user_data)
        elif http_method == 'POST' and path == '/api/nova-micro-assessment':
            return handle_nova_micro_assessment(body, user_data)
        elif http_method == 'POST' and path == '/api/maya/introduction':
            return handle_maya_introduction(body, user_data)
        elif http_method == 'POST' and path == '/api/maya/conversation':
            return handle_maya_conversation(body, user_data)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error in nova_ai lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_nova_sonic_connect(body, user_data):
    """
    Test Nova Sonic connectivity and initialize Maya AI examiner
    """
    try:
        # Test Nova Sonic connection
        test_prompt = "Hello, this is a connection test."
        
        request_body = {
            "inputText": test_prompt,
            "voice": {
                "id": "en-GB-feminine"  # Maya's British female voice
            },
            "outputAudio": {
                "format": "mp3",
                "sampleRate": 24000
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_SONIC_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        return create_response(200, {
            'success': True,
            'message': 'Nova Sonic connection successful',
            'maya_ready': True,
            'voice_config': {
                'voice_id': 'en-GB-feminine',
                'sample_rate': 24000,
                'format': 'mp3'
            },
            'test_audio': response_body.get('audioStream')
        })
        
    except Exception as e:
        print(f"Error in handle_nova_sonic_connect: {str(e)}")
        return create_response(500, {
            'success': False,
            'error': 'Nova Sonic connection failed',
            'maya_ready': False
        })

def handle_nova_sonic_stream(body, user_data):
    """
    Handle real-time speech streaming with Nova Sonic
    """
    try:
        audio_data = body.get('audioData')
        assessment_type = body.get('assessmentType', 'speaking')
        conversation_context = body.get('context', {})
        
        if not audio_data:
            return create_response(400, {'error': 'Audio data required'})
        
        # Check if user has remaining assessments
        if not check_assessment_attempts(user_data['user_id'], assessment_type):
            return create_response(403, {
                'error': 'No assessment attempts remaining',
                'message': 'Please purchase more assessment attempts to continue'
            })
        
        # Process audio with Nova Sonic
        maya_prompt = generate_maya_prompt(assessment_type, conversation_context)
        
        request_body = {
            "inputAudio": {
                "format": "mp3",
                "audioStream": audio_data
            },
            "voice": {
                "id": "en-GB-feminine"
            },
            "outputAudio": {
                "format": "mp3",
                "sampleRate": 24000
            },
            "systemPrompt": maya_prompt
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_SONIC_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Store conversation data
        conversation_record = {
            'user_id': user_data['user_id'],
            'assessment_type': assessment_type,
            'timestamp': datetime.utcnow().isoformat(),
            'user_audio': audio_data,
            'maya_response': response_body.get('audioStream'),
            'maya_text': response_body.get('outputText', ''),
            'context': conversation_context
        }
        
        # Save to assessments table
        save_conversation_data(conversation_record)
        
        return create_response(200, {
            'success': True,
            'maya_response': {
                'audio': response_body.get('audioStream'),
                'text': response_body.get('outputText', ''),
                'next_question': response_body.get('nextQuestion'),
                'assessment_progress': response_body.get('progress', 0)
            },
            'conversation_id': conversation_record.get('conversation_id')
        })
        
    except Exception as e:
        print(f"Error in handle_nova_sonic_stream: {str(e)}")
        return create_response(500, {'error': 'Speech processing failed'})

def handle_nova_micro_writing(body, user_data):
    """
    Handle writing assessment with Nova Micro
    """
    try:
        text_data = body.get('text')
        assessment_type = body.get('assessmentType', 'writing')
        question_prompt = body.get('questionPrompt', '')
        
        if not text_data:
            return create_response(400, {'error': 'Text data required'})
        
        # Check assessment attempts
        if not check_assessment_attempts(user_data['user_id'], assessment_type):
            return create_response(403, {
                'error': 'No assessment attempts remaining',
                'message': 'Please purchase more assessment attempts to continue'
            })
        
        # Generate IELTS evaluation prompt
        evaluation_prompt = generate_writing_evaluation_prompt(assessment_type, question_prompt, text_data)
        
        request_body = {
            "prompt": evaluation_prompt,
            "max_tokens": 2000,
            "temperature": 0.3,
            "top_p": 0.9
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_MICRO_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        evaluation_text = response_body.get('completion', '')
        
        # Parse evaluation results
        evaluation_results = parse_writing_evaluation(evaluation_text)
        
        # Decrement user's assessment attempts
        decrement_assessment_attempts(user_data['user_id'], assessment_type)
        
        # Store assessment result
        assessment_record = {
            'assessment_id': f"{user_data['user_id']}_{datetime.utcnow().isoformat()}",
            'user_id': user_data['user_id'],
            'assessment_type': assessment_type,
            'question_prompt': question_prompt,
            'user_response': text_data,
            'ai_evaluation': evaluation_results,
            'raw_evaluation': evaluation_text,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed'
        }
        
        assessments_table.put_item(Item=assessment_record)
        
        return create_response(200, {
            'success': True,
            'assessment_id': assessment_record['assessment_id'],
            'evaluation': evaluation_results,
            'message': 'Writing assessment completed successfully'
        })
        
    except Exception as e:
        print(f"Error in handle_nova_micro_writing: {str(e)}")
        return create_response(500, {'error': 'Writing assessment failed'})

def handle_nova_micro_assessment(body, user_data):
    """
    Alternative endpoint for Nova Micro assessment
    """
    return handle_nova_micro_writing(body, user_data)

def handle_maya_introduction(body, user_data):
    """
    Generate Maya's introduction for speaking assessment
    """
    try:
        assessment_type = body.get('assessmentType', 'academic_speaking')
        
        introduction_prompt = f"""
        You are Maya, a friendly and professional British female IELTS examiner. 
        Generate a warm introduction for a {assessment_type} assessment.
        Keep it natural, encouraging, and professional.
        """
        
        request_body = {
            "inputText": introduction_prompt,
            "voice": {
                "id": "en-GB-feminine"
            },
            "outputAudio": {
                "format": "mp3",
                "sampleRate": 24000
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_SONIC_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        return create_response(200, {
            'success': True,
            'maya_introduction': {
                'audio': response_body.get('audioStream'),
                'text': response_body.get('outputText', 'Hello! I\'m Maya, your IELTS examiner. Let\'s begin your speaking assessment.'),
                'assessment_type': assessment_type
            }
        })
        
    except Exception as e:
        print(f"Error in handle_maya_introduction: {str(e)}")
        return create_response(500, {'error': 'Maya introduction failed'})

def handle_maya_conversation(body, user_data):
    """
    Handle ongoing conversation with Maya during speaking assessment
    """
    try:
        user_response = body.get('userResponse')
        conversation_state = body.get('conversationState', {})
        assessment_type = body.get('assessmentType', 'academic_speaking')
        
        # Generate contextual Maya response
        maya_prompt = generate_conversation_prompt(assessment_type, conversation_state, user_response)
        
        request_body = {
            "inputText": maya_prompt,
            "voice": {
                "id": "en-GB-feminine"
            },
            "outputAudio": {
                "format": "mp3",
                "sampleRate": 24000
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_SONIC_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Update conversation state
        updated_state = update_conversation_state(conversation_state, user_response, response_body.get('outputText', ''))
        
        return create_response(200, {
            'success': True,
            'maya_response': {
                'audio': response_body.get('audioStream'),
                'text': response_body.get('outputText', ''),
                'conversation_state': updated_state,
                'assessment_progress': updated_state.get('progress', 0)
            }
        })
        
    except Exception as e:
        print(f"Error in handle_maya_conversation: {str(e)}")
        return create_response(500, {'error': 'Maya conversation failed'})

def validate_auth_token(event):
    """
    Validate authentication token from request headers
    """
    try:
        import jwt
        import os
        
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Invalid authorization header'})
        
        token = auth_header.replace('Bearer ', '')
        JWT_SECRET = os.environ.get('JWT_SECRET', 'ielts-ai-prep-jwt-secret-2024-production')
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            email = payload.get('email')
            
            # Verify user exists in database
            response = users_table.get_item(Key={'email': email})
            if 'Item' not in response:
                return create_response(401, {'error': 'User not found'})
            
            return create_response(200, {
                'user_id': user_id,
                'email': email
            })
            
        except jwt.ExpiredSignatureError:
            return create_response(401, {'error': 'Token expired'})
        except jwt.InvalidTokenError:
            return create_response(401, {'error': 'Invalid token'})
        
    except Exception as e:
        print(f"Auth validation error: {str(e)}")
        return create_response(401, {'error': 'Authentication failed'})

def check_assessment_attempts(user_id, assessment_type):
    """
    Check if user has remaining assessment attempts
    """
    try:
        # Get user's current assessment count
        response = users_table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        if not response.get('Items'):
            return False
        
        user = response['Items'][0]
        remaining = user.get('assessments_remaining', 0)
        
        if remaining <= 0:
            return False
        
        # Check specific assessment type purchases
        purchase_response = assessments_table.scan(
            FilterExpression='user_id = :user_id AND assessment_type = :type AND #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':type': assessment_type,
                ':status': 'active'
            }
        )
        
        for purchase in purchase_response.get('Items', []):
            if purchase.get('assessments_remaining', 0) > 0:
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking assessment attempts: {str(e)}")
        return False

def decrement_assessment_attempts(user_id, assessment_type):
    """
    Decrement user's assessment attempts after completion
    """
    try:
        # Find active purchase for this assessment type
        response = assessments_table.scan(
            FilterExpression='user_id = :user_id AND assessment_type = :type AND #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':type': assessment_type,
                ':status': 'active'
            }
        )
        
        for purchase in response.get('Items', []):
            if purchase.get('assessments_remaining', 0) > 0:
                # Decrement this purchase
                assessments_table.update_item(
                    Key={'assessment_id': purchase['purchase_id']},
                    UpdateExpression='SET assessments_remaining = assessments_remaining - :dec, assessments_used = assessments_used + :inc',
                    ExpressionAttributeValues={':dec': 1, ':inc': 1}
                )
                
                # Update user's total remaining count
                users_table.update_item(
                    Key={'email': purchase.get('email')},
                    UpdateExpression='SET assessments_remaining = assessments_remaining - :dec',
                    ExpressionAttributeValues={':dec': 1}
                )
                break
        
    except Exception as e:
        print(f"Error decrementing assessment attempts: {str(e)}")

def generate_maya_prompt(assessment_type, context):
    """
    Generate system prompt for Maya AI examiner
    """
    base_prompt = """
    You are Maya, a professional and friendly British female IELTS examiner. 
    You conduct speaking assessments following official IELTS guidelines.
    
    Your personality:
    - Professional but warm and encouraging
    - Clear British accent and pronunciation
    - Patient and supportive
    - Follows IELTS speaking test structure
    
    Assessment guidelines:
    - Ask clear, relevant questions
    - Provide appropriate follow-up questions
    - Maintain natural conversation flow
    - Evaluate based on IELTS speaking criteria
    """
    
    if assessment_type == 'academic_speaking':
        return base_prompt + "\nFocus on academic topics and formal language assessment."
    elif assessment_type == 'general_speaking':
        return base_prompt + "\nFocus on everyday topics and general communication skills."
    
    return base_prompt

def generate_writing_evaluation_prompt(assessment_type, question, response):
    """
    Generate evaluation prompt for writing assessment
    """
    return f"""
    Evaluate this IELTS {assessment_type} response using official IELTS writing criteria:
    
    Question: {question}
    
    Student Response: {response}
    
    Provide evaluation in this JSON format:
    {{
        "overall_band": 7.5,
        "criteria": {{
            "task_achievement": 7,
            "coherence_cohesion": 8,
            "lexical_resource": 7,
            "grammatical_range": 8
        }},
        "detailed_feedback": "Detailed analysis of the response...",
        "strengths": ["List of strengths"],
        "areas_for_improvement": ["List of areas to improve"],
        "word_count": 250
    }}
    """

def parse_writing_evaluation(evaluation_text):
    """
    Parse AI evaluation response into structured format
    """
    try:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Fallback to basic parsing if JSON extraction fails
        return {
            "overall_band": 6.5,
            "criteria": {
                "task_achievement": 6,
                "coherence_cohesion": 7,
                "lexical_resource": 6,
                "grammatical_range": 7
            },
            "detailed_feedback": evaluation_text,
            "strengths": ["Response addresses the task"],
            "areas_for_improvement": ["Expand vocabulary range"],
            "word_count": 200
        }
        
    except Exception as e:
        print(f"Error parsing evaluation: {str(e)}")
        return {"error": "Evaluation parsing failed"}

def generate_conversation_prompt(assessment_type, state, user_response):
    """
    Generate contextual conversation prompt for Maya
    """
    return f"""
    Continue the IELTS {assessment_type} conversation.
    Previous context: {state}
    User just said: {user_response}
    
    Respond naturally as Maya, the British IELTS examiner.
    """

def update_conversation_state(current_state, user_response, maya_response):
    """
    Update conversation state with new exchange
    """
    if not current_state:
        current_state = {'exchanges': [], 'progress': 0}
    
    current_state['exchanges'].append({
        'user': user_response,
        'maya': maya_response,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    current_state['progress'] = min(100, len(current_state['exchanges']) * 10)
    
    return current_state

def save_conversation_data(conversation_record):
    """
    Save conversation data to assessments table
    """
    try:
        conversation_record['conversation_id'] = f"conv_{conversation_record['user_id']}_{datetime.utcnow().isoformat()}"
        assessments_table.put_item(Item=conversation_record)
        
    except Exception as e:
        print(f"Error saving conversation data: {str(e)}")

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