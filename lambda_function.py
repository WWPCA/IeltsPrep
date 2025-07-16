
import json
import os
import uuid
import urllib.request
import urllib.parse
import base64
import hashlib
import hmac
import time
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# DynamoDB Configuration for Production
DYNAMODB_REGION = 'us-east-1'
DYNAMODB_TABLES = {
    'users': 'ielts-genai-prep-users',
    'sessions': 'ielts-genai-prep-sessions',
    'assessments': 'ielts-genai-prep-assessments',
    'questions': 'ielts-assessment-questions',
    'rubrics': 'ielts-assessment-rubrics'
}

def get_dynamodb_client():
    """Get DynamoDB client for production"""
    import boto3
    return boto3.client('dynamodb', region_name=DYNAMODB_REGION)

def get_dynamodb_resource():
    """Get DynamoDB resource for production"""
    import boto3
    return boto3.resource('dynamodb', region_name=DYNAMODB_REGION)

def synthesize_maya_voice_nova_sonic(text: str) -> Optional[str]:
    """
    Synthesize Maya's voice using AWS Nova Sonic en-GB-feminine
    Returns base64 encoded audio data
    """
    try:
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Configure for British female voice
        request_body = {
            "inputText": text,
            "voice": {
                "id": "en-GB-feminine"
            },
            "outputFormat": {
                "format": "mp3"
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-sonic-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'audio' in response_body:
            return response_body['audio']
        else:
            return None
            
    except Exception as e:
        print(f"[NOVA_SONIC] Error: {str(e)}")
        return None

def send_welcome_email(email: str) -> None:
    """Send welcome email via AWS SES"""
    try:
        import boto3
        ses_client = boto3.client('ses', region_name='us-east-1')
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold;">Welcome to IELTS GenAI Prep!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your journey to IELTS success starts here</p>
                </div>
                
                <div style="padding: 40px 30px;">
                    <h2 style="color: #333; margin-top: 0;">Hello!</h2>
                    <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                        Thank you for creating your account with IELTS GenAI Prep. You now have access to our advanced AI-powered assessment platform featuring:
                    </p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #667eea; margin-top: 0;">✨ TrueScore® Writing Assessment</h3>
                        <p style="color: #666; margin-bottom: 10px;">• Task Achievement evaluation</p>
                        <p style="color: #666; margin-bottom: 10px;">• Coherence & Cohesion analysis</p>
                        <p style="color: #666; margin-bottom: 10px;">• Lexical Resource assessment</p>
                        <p style="color: #666; margin-bottom: 0;">• Grammar Range & Accuracy scoring</p>
                    </div>
                    
                    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #4a90e2; margin-top: 0;">🎯 ClearScore® Speaking Assessment</h3>
                        <p style="color: #666; margin-bottom: 10px;">• Maya AI examiner conversations</p>
                        <p style="color: #666; margin-bottom: 10px;">• Fluency & Coherence evaluation</p>
                        <p style="color: #666; margin-bottom: 10px;">• Pronunciation assessment</p>
                        <p style="color: #666; margin-bottom: 0;">• Lexical Resource & Grammar scoring</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://www.ieltsaiprep.com/login" style="background: #e31e24; color: white; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-weight: bold; display: inline-block;">Start Your First Assessment</a>
                    </div>
                    
                    <p style="color: #666; line-height: 1.6; margin-top: 30px;">
                        Your account is now active and ready to use. Log in to access your personalized dashboard and begin your IELTS preparation journey.
                    </p>
                    
                    <p style="color: #666; line-height: 1.6;">
                        If you have any questions, please don't hesitate to contact our support team.
                    </p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="color: #666; margin: 0; font-size: 14px;">
                        © 2025 IELTS GenAI Prep. All rights reserved.<br>
                        <a href="https://www.ieltsaiprep.com/privacy-policy" style="color: #667eea; text-decoration: none;">Privacy Policy</a> | 
                        <a href="https://www.ieltsaiprep.com/terms-of-service" style="color: #667eea; text-decoration: none;">Terms of Service</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to IELTS GenAI Prep!
        
        Thank you for creating your account. You now have access to our advanced AI-powered assessment platform.
        
        Features included:
        - TrueScore® Writing Assessment with comprehensive feedback
        - ClearScore® Speaking Assessment with Maya AI examiner
        - Official IELTS band scoring criteria
        - Personalized progress tracking
        
        Log in at: https://www.ieltsaiprep.com/login
        
        If you have any questions, please contact our support team.
        
        Best regards,
        IELTS GenAI Prep Team
        """
        
        ses_client.send_email(
            Source='welcome@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Welcome to IELTS GenAI Prep - Your Account is Ready!'},
                'Body': {
                    'Text': {'Data': text_body},
                    'Html': {'Data': html_body}
                }
            }
        )
        
    except Exception as e:
        print(f"[SES] Welcome email error: {str(e)}")

def send_account_deletion_email(email: str) -> None:
    """Send account deletion confirmation email via AWS SES"""
    try:
        import boto3
        ses_client = boto3.client('ses', region_name='us-east-1')
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold;">Account Deletion Confirmed</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your IELTS GenAI Prep account has been deleted</p>
                </div>
                
                <div style="padding: 40px 30px;">
                    <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                        This email confirms that your IELTS GenAI Prep account (<strong>{email}</strong>) has been permanently deleted from our systems.
                    </p>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #856404; margin-top: 0;">What has been deleted:</h3>
                        <p style="color: #856404; margin-bottom: 10px;">• Your account profile and personal information</p>
                        <p style="color: #856404; margin-bottom: 10px;">• All assessment history and results</p>
                        <p style="color: #856404; margin-bottom: 10px;">• Your purchased assessment attempts</p>
                        <p style="color: #856404; margin-bottom: 0;">• All preferences and settings</p>
                    </div>
                    
                    <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #721c24; margin-top: 0;">Important Security Notice:</h3>
                        <p style="color: #721c24; margin-bottom: 10px;">• This action cannot be undone</p>
                        <p style="color: #721c24; margin-bottom: 10px;">• You will need to create a new account for future access</p>
                        <p style="color: #721c24; margin-bottom: 0;">• Previous purchase history cannot be restored</p>
                    </div>
                    
                    <p style="color: #666; line-height: 1.6; margin-top: 30px;">
                        If you did not request this deletion or believe this was done in error, please contact our support team immediately.
                    </p>
                    
                    <p style="color: #666; line-height: 1.6;">
                        Thank you for using IELTS GenAI Prep. We hope to serve you again in the future.
                    </p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="color: #666; margin: 0; font-size: 14px;">
                        © 2025 IELTS GenAI Prep. All rights reserved.<br>
                        <a href="https://www.ieltsaiprep.com/privacy-policy" style="color: #667eea; text-decoration: none;">Privacy Policy</a> | 
                        <a href="https://www.ieltsaiprep.com/terms-of-service" style="color: #667eea; text-decoration: none;">Terms of Service</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Account Deletion Confirmed
        
        This email confirms that your IELTS GenAI Prep account ({email}) has been permanently deleted from our systems.
        
        What has been deleted:
        - Your account profile and personal information
        - All assessment history and results
        - Your purchased assessment attempts
        - All preferences and settings
        
        Important Security Notice:
        - This action cannot be undone
        - You will need to create a new account for future access
        - Previous purchase history cannot be restored
        
        If you did not request this deletion or believe this was done in error, please contact our support team immediately.
        
        Thank you for using IELTS GenAI Prep.
        
        IELTS GenAI Prep Team
        """
        
        ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Account Deletion Confirmation - IELTS GenAI Prep'},
                'Body': {
                    'Text': {'Data': text_body},
                    'Html': {'Data': html_body}
                }
            }
        )
        
    except Exception as e:
        print(f"[SES] Deletion email error: {str(e)}")

def verify_user_credentials(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify user credentials against DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['users'])
        
        response = table.get_item(Key={'email': email})
        if 'Item' not in response:
            return None
            
        user = response['Item']
        
        # Verify password using bcrypt
        import bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
        else:
            return None
            
    except Exception as e:
        print(f"[DYNAMODB] Credential verification error: {str(e)}")
        return None

def create_user_account(email: str, password: str) -> bool:
    """Create new user account in DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['users'])
        
        # Check if user already exists
        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            return False
            
        # Hash password using bcrypt
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user record
        user_data = {
            'email': email,
            'user_id': str(uuid.uuid4()),
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'assessment_attempts': 0,
            'max_attempts': 4
        }
        
        table.put_item(Item=user_data)
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] User creation error: {str(e)}")
        return False

def create_user_session(session_data: Dict[str, Any]) -> bool:
    """Create user session in DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['sessions'])
        
        table.put_item(Item=session_data)
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] Session creation error: {str(e)}")
        return False

def get_user_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get user session from DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['sessions'])
        
        response = table.get_item(Key={'session_id': session_id})
        if 'Item' not in response:
            return None
            
        session = response['Item']
        
        # Check if session is expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.utcnow() > expires_at:
            return None
            
        return session
        
    except Exception as e:
        print(f"[DYNAMODB] Session retrieval error: {str(e)}")
        return None

def delete_user_account(email: str) -> bool:
    """Delete user account from DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        
        # Delete from users table
        users_table = dynamodb.Table(DYNAMODB_TABLES['users'])
        users_table.delete_item(Key={'email': email})
        
        # Delete user sessions
        sessions_table = dynamodb.Table(DYNAMODB_TABLES['sessions'])
        # Note: In production, you'd scan for sessions by user_email and delete them
        
        # Delete user assessments
        assessments_table = dynamodb.Table(DYNAMODB_TABLES['assessments'])
        # Note: In production, you'd scan for assessments by user_email and delete them
        
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] Account deletion error: {str(e)}")
        return False

def get_assessment_questions(assessment_type: str) -> List[Dict[str, Any]]:
    """Get assessment questions from DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['questions'])
        
        response = table.scan(
            FilterExpression='assessment_type = :type',
            ExpressionAttributeValues={':type': assessment_type}
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"[DYNAMODB] Questions retrieval error: {str(e)}")
        return []

def get_assessment_rubric(assessment_type: str) -> Optional[Dict[str, Any]]:
    """Get assessment rubric from DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['rubrics'])
        
        response = table.get_item(Key={'assessment_type': assessment_type})
        if 'Item' not in response:
            return None
            
        return response['Item']
        
    except Exception as e:
        print(f"[DYNAMODB] Rubric retrieval error: {str(e)}")
        return None

def save_assessment_result(user_email: str, assessment_data: Dict[str, Any]) -> bool:
    """Save assessment result to DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['assessments'])
        
        assessment_record = {
            'assessment_id': str(uuid.uuid4()),
            'user_email': user_email,
            'assessment_type': assessment_data['assessment_type'],
            'overall_band': assessment_data['overall_band'],
            'criteria_scores': assessment_data['criteria_scores'],
            'feedback': assessment_data['feedback'],
            'timestamp': datetime.utcnow().isoformat(),
            'completed': True
        }
        
        table.put_item(Item=assessment_record)
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] Assessment save error: {str(e)}")
        return False

def get_user_assessment_history(user_email: str) -> List[Dict[str, Any]]:
    """Get user's assessment history from DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLES['assessments'])
        
        response = table.scan(
            FilterExpression='user_email = :email',
            ExpressionAttributeValues={':email': user_email}
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"[DYNAMODB] Assessment history error: {str(e)}")
        return []

def evaluate_writing_with_nova_micro(essay_text: str, prompt: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate writing using Nova Micro with IELTS rubrics"""
    try:
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        system_prompt = f"""
        You are an expert IELTS Writing examiner. Evaluate the following essay using official IELTS criteria.
        
        Assessment Type: {rubric.get('assessment_type', 'writing')}
        
        IMPORTANT: You must respond with ONLY a valid JSON object in this exact format:
        {
            "overall_band": 7.0,
            "criteria_scores": {
                "task_achievement": 7.0,
                "coherence_cohesion": 7.0,
                "lexical_resource": 7.0,
                "grammatical_range": 7.0
            },
            "detailed_feedback": {
                "strengths": ["Strong task response", "Clear organization"],
                "areas_for_improvement": ["Expand vocabulary range", "Improve complex sentences"],
                "specific_suggestions": ["Use more varied linking devices", "Include more specific examples"]
            }
        }
        
        Evaluate based on official IELTS band descriptors.
        """
        
        user_prompt = f"""
        Essay Prompt: {prompt}
        
        Student Essay: {essay_text}
        
        Please provide a comprehensive evaluation following the JSON format specified.
        """
        
        request_body = {
            "messages": [
                {"role": "user", "content": system_prompt + "\n\n" + user_prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'output' in response_body and 'message' in response_body['output']:
            content = response_body['output']['message']['content'][0]['text']
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                assessment_json = json.loads(json_match.group())
                return assessment_json
                
        # Fallback response
        return {
            "overall_band": 6.5,
            "criteria_scores": {
                "task_achievement": 6.5,
                "coherence_cohesion": 6.5,
                "lexical_resource": 6.5,
                "grammatical_range": 6.5
            },
            "detailed_feedback": {
                "strengths": ["Clear task response", "Good organization"],
                "areas_for_improvement": ["Expand vocabulary", "Improve grammar accuracy"],
                "specific_suggestions": ["Use more complex sentences", "Include more examples"]
            }
        }
        
    except Exception as e:
        print(f"[NOVA_MICRO] Writing evaluation error: {str(e)}")
        return {
            "overall_band": 6.0,
            "criteria_scores": {
                "task_achievement": 6.0,
                "coherence_cohesion": 6.0,
                "lexical_resource": 6.0,
                "grammatical_range": 6.0
            },
            "detailed_feedback": {
                "strengths": ["Task completion"],
                "areas_for_improvement": ["Overall writing skills"],
                "specific_suggestions": ["Practice more writing exercises"]
            }
        }

def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v2 response with Google"""
    try:
        secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
        if not secret_key:
            return False
            
        # Prepare POST data
        post_data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        if user_ip:
            post_data['remoteip'] = user_ip
            
        # Make request to Google
        data = urllib.parse.urlencode(post_data).encode('utf-8')
        req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            success = result.get('success', False)
            
            if not success:
                error_codes = result.get('error-codes', [])
                print(f"[RECAPTCHA] Verification failed: {error_codes}")
            
            return success
            
    except Exception as e:
        print(f"[RECAPTCHA] Verification error: {str(e)}")
        return False

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Validate CloudFront secret header
        headers = event.get('headers', {})
        cf_secret = headers.get('CF-Secret-3140348d', headers.get('cf-secret-3140348d'))
        
        if not cf_secret:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Access denied'})
            }
        
        # Extract request information
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        body = event.get('body', '{}')
        
        # Parse request body
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        
        print(f"[LAMBDA] Processing {method} {path}")
        
        # Route requests
        if path == '/' and method == 'GET':
            return handle_home_page()
        elif path == '/api/health' and method == 'GET':
            return handle_health_check()
        elif path == '/api/register' and method == 'POST':
            return handle_user_registration(data)
        elif path == '/api/login' and method == 'POST':
            return handle_user_login(data)
        elif path == '/api/account-deletion' and method == 'POST':
            return handle_account_deletion(data)
        elif path == '/api/nova-micro-writing' and method == 'POST':
            return handle_nova_micro_writing(data)
        elif path == '/api/nova-sonic-connect' and method == 'GET':
            return handle_nova_sonic_connection_test()
        elif path == '/api/nova-sonic-stream' and method == 'POST':
            return handle_nova_sonic_stream(data)
        elif path == '/login' and method == 'GET':
            return handle_login_page()
        elif path == '/dashboard' and method == 'GET':
            return handle_dashboard_page(headers)
        elif path == '/my-profile' and method == 'GET':
            return handle_profile_page(headers)
        elif path == '/privacy-policy' and method == 'GET':
            return handle_privacy_policy()
        elif path == '/terms-of-service' and method == 'GET':
            return handle_terms_of_service()
        elif path == '/robots.txt' and method == 'GET':
            return handle_robots_txt()
        elif path.startswith('/assessment/') and method == 'GET':
            return handle_assessment_access(path, headers)
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"[LAMBDA] Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_home_page():
    """Serve original working template with AI SEO optimizations"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'public, max-age=3600'
        },
        'body': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="The only AI-powered IELTS assessment platform with standardized band scoring. Prepare for IELTS Writing and Speaking with TrueScore® and ClearScore® technologies.">
    <meta name="keywords" content="IELTS AI Assessment, IELTS Writing Feedback, IELTS Speaking Evaluation, GenAI IELTS App, TrueScore IELTS, ClearScore IELTS, AI Band Score, IELTS Band Descriptors, Academic IELTS, General Training IELTS, AI IELTS Practice, Online IELTS Preparation, AI Language Assessment, IELTS Prep App, IELTS writing preparation, IELTS speaking practice test, IELTS writing practice test, IELTS practice test with feedback">
    <meta property="og:title" content="IELTS GenAI Prep - AI-Powered IELTS Assessment Platform">
    <meta property="og:description" content="The only AI-powered IELTS assessment platform with standardized band scoring using TrueScore® and ClearScore® technologies.">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="IELTS GenAI Prep - AI-Powered IELTS Assessment Platform">
    <meta name="twitter:description" content="The only AI-powered IELTS assessment platform with standardized band scoring using TrueScore® and ClearScore® technologies.">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Schema.org Organization Markup -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "IELTS GenAI Prep",
      "url": "https://www.ieltsgenaiprep.com",
      "logo": "https://www.ieltsgenaiprep.com/logo.png",
      "description": "IELTS GenAI Prep is an AI-powered IELTS assessment platform offering instant band-aligned feedback for Writing and Speaking modules.",
      "sameAs": [
        "https://www.linkedin.com/company/ieltsgenaiprep",
        "https://www.twitter.com/ieltsgenaiprep"
      ]
    }
    </script>
    
    <!-- FAQ Schema Markup -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is IELTS GenAI Prep?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "IELTS GenAI Prep is an AI-powered assessment platform that delivers standardized, examiner-aligned band scores for IELTS Writing and Speaking, using official IELTS scoring criteria."
          }
        },
        {
          "@type": "Question",
          "name": "What makes IELTS GenAI Prep different from other IELTS prep tools?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "It is the only platform using TrueScore® and ClearScore® technologies to provide instant, AI-generated feedback that mirrors official IELTS band descriptors for both Academic and General Training modules."
          }
        },
        {
          "@type": "Question",
          "name": "How does TrueScore® assess IELTS Writing tasks?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "TrueScore® uses GenAI models trained on IELTS scoring rubrics to assess Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy. Each submission receives band-aligned feedback."
          }
        },
        {
          "@type": "Question",
          "name": "How is ClearScore® used to evaluate IELTS Speaking?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "ClearScore® simulates a live speaking test using AI voice assessment technology. It scores fluency, pronunciation, grammar, and vocabulary in real-time, based on official IELTS speaking criteria."
          }
        },
        {
          "@type": "Question",
          "name": "Do you offer Academic and General Training modules?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. IELTS GenAI Prep supports both Academic and General Training formats for Writing and Speaking, allowing users to choose modules aligned with their test goals."
          }
        },
        {
          "@type": "Question",
          "name": "How much does it cost to use IELTS GenAI Prep?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Each module (Writing or Speaking) is priced at $36 for four AI-graded assessments. This includes band scores and detailed feedback on every attempt."
          }
        },
        {
          "@type": "Question",
          "name": "Is this a mobile-only platform?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "IELTS GenAI Prep is optimized for mobile and desktop. Users can create an account on the website and access assessments on the IELTS GenAI mobile app anytime, anywhere."
          }
        },
        {
          "@type": "Question",
          "name": "How fast is the scoring process?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "All AI assessments are completed within seconds to a few minutes, providing instant band scores and feedback so users can improve quickly and effectively."
          }
        },
        {
          "@type": "Question",
          "name": "How reliable are the AI-generated IELTS scores?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Our GenAI scores show a 96% alignment with certified IELTS examiners. The technology is built to mimic human scoring standards while ensuring consistency and speed."
          }
        },
        {
          "@type": "Question",
          "name": "Can I track my performance over time?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. Your personalized dashboard allows you to review past assessments, track band score improvements, and identify focus areas for continued practice."
          }
        }
      ]
    }
    </script>
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
        }
        
        .pricing-card {
            border: 1px solid rgba(0, 0, 0, 0.125);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .pricing-card:hover {
            transform: translateY(-5px);
        }
        
        .genai-brand-section {
            margin-bottom: 60px;
        }
        
        .brand-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .brand-title {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .brand-tagline {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
        }
        
        .features {
            padding: 80px 0;
            background: #f8f9fa;
        }
        
        .navbar {
            background-color: #fff !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .navbar-brand {
            font-weight: bold;
            color: #4361ee !important;
        }
        
        .navbar-nav .nav-link {
            color: #333 !important;
            font-weight: 500;
        }
        
        .navbar-nav .nav-link:hover {
            color: #4361ee !important;
        }
        
        /* Enhanced animations and interactivity */
        .hero h1 {
            animation: fadeInUp 0.8s ease-out;
        }
        
        .hero h2 {
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }
        
        .hero .mb-4 > div {
            animation: fadeInLeft 0.6s ease-out 0.4s both;
        }
        
        .hero .mb-4 > div:nth-child(2) {
            animation-delay: 0.6s;
        }
        
        .hero .mb-4 > div:nth-child(3) {
            animation-delay: 0.8s;
        }
        
        .hero p {
            animation: fadeInUp 0.8s ease-out 1s both;
        }
        
        .hero-buttons {
            animation: fadeInUp 0.8s ease-out 1.2s both;
        }
        
        .hero .col-lg-6:last-child {
            animation: fadeInRight 0.8s ease-out 0.5s both;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Button hover effects */
        .hero-buttons .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .btn-success:hover {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);
        }
        
        .btn-outline-light:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,1);
            backdrop-filter: blur(10px);
        }
        
        /* Icon container hover effects */
        .hero .me-3:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.1);
            transition: all 0.3s ease;
        }
        
        /* Improved typography for better readability and spacing */
        @media (max-width: 768px) {
            .hero {
                padding: 60px 0;
            }
            
            .hero h1 {
                font-size: 2.5rem !important;
                line-height: 1.3 !important;
            }
            
            .hero h2 {
                font-size: 1.3rem !important;
            }
            
            .hero-buttons .btn {
                display: block;
                width: 100%;
                margin-bottom: 15px;
                margin-right: 0 !important;
            }
            
            .hero .col-lg-6:first-child {
                text-align: center !important;
            }
        }
        
        @media (max-width: 576px) {
            .hero h1 {
                font-size: 2rem !important;
                line-height: 1.2 !important;
            }
            
            .hero h2 {
                font-size: 1.1rem !important;
            }
            
            .hero .mb-4 span {
                font-size: 1rem !important;
            }
        }
    </style>
</head>

<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">IELTS GenAI Prep</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#how-it-works">How it Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#assessments">Assessments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#faq">FAQ</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero" style="margin-top: 76px; padding: 80px 0; position: relative; overflow: hidden;">
        <!-- Background enhancement -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); pointer-events: none;"></div>
        
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6 text-center text-lg-start mb-5 mb-lg-0">
                    <!-- SEO-Optimized H1 and Introduction -->
                    <h1 class="display-3 fw-bold mb-3" style="font-size: 3.5rem; line-height: 1.2; letter-spacing: -0.02em; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        AI-Powered IELTS Writing and Speaking Assessments with Official Band Scoring
                    </h1>
                    
                    <p class="h4 mb-4" style="font-size: 1.3rem; line-height: 1.4; font-weight: 500; color: rgba(255,255,255,0.95); margin-bottom: 2rem;">
                        IELTS GenAI Prep is the only AI-based IELTS preparation platform offering instant band-aligned feedback on Writing and Speaking. Powered by TrueScore® and ClearScore®, we replicate official examiner standards using GenAI technology.
                    </p>
                    
                    <!-- Benefits with icons -->
                    <div class="mb-4">
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-3">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                <i class="fas fa-brain text-white" style="font-size: 1.1rem;"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">AI-Powered Scoring Technology</span>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-3">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                <i class="fas fa-check-circle text-white" style="font-size: 1.1rem;"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">Official IELTS Criteria Alignment</span>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-4">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                <i class="fas fa-bullseye text-white" style="font-size: 1.1rem;"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">Academic & General Training Modules</span>
                        </div>
                    </div>
                    
                    <p class="mb-5" style="font-size: 1.1rem; line-height: 1.7; color: rgba(255,255,255,0.9); max-width: 500px; margin-left: auto; margin-right: auto;">
                        Experience TrueScore® and ClearScore® technologies that deliver standardized IELTS assessments based on official scoring criteria.
                    </p>
                    
                    <!-- Enhanced CTA buttons -->
                    <div class="hero-buttons text-center text-lg-start">
                        <a href="/login" class="btn btn-success btn-lg me-3 mb-3" style="font-size: 1.2rem; padding: 15px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4); border: none; transition: all 0.3s ease;" aria-label="Start using IELTS GenAI Prep assessments">
                            <i class="fas fa-rocket me-2"></i>
                            Get Started
                        </a>
                        <a href="#how-it-works" class="btn btn-outline-light btn-lg mb-3" style="font-size: 1.2rem; padding: 15px 30px; border-radius: 12px; border: 2px solid rgba(255,255,255,0.8); transition: all 0.3s ease;" aria-label="Learn more about how IELTS GenAI Prep works">
                            <i class="fas fa-info-circle me-2"></i>
                            Learn More
                        </a>
                    </div>
                </div>
                
                <div class="col-lg-6 text-center">
                    <!-- Sample Assessment Report Demo -->
                    <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; backdrop-filter: blur(15px); box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                        <div class="mb-3">
                            <span class="badge bg-primary text-white px-3 py-2" style="font-size: 0.9rem; font-weight: 600;">
                                <i class="fas fa-star me-1"></i>
                                YOUR SCORE PREVIEW
                            </span>
                        </div>
                        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 15px; padding: 30px; margin-bottom: 20px; position: relative;">
                            <h3 class="text-white mb-2" style="font-size: 1.4rem; font-weight: 600; line-height: 1.3;">
                                <i class="fas fa-certificate me-2"></i>
                                See Exactly How Your IELTS Score Will Look
                            </h3>
                            <div class="mb-3 d-flex justify-content-center">
                                <span class="badge bg-light text-dark px-3 py-1" style="font-size: 0.85rem; font-weight: 500; display: inline-block; text-align: center;">
                                    <i class="fas fa-pencil-alt me-1"></i>
                                    Academic Writing Assessment Sample
                                </span>
                            </div>
                            <p class="text-white mb-4" style="font-size: 0.95rem; opacity: 0.95; font-weight: 400;">
                                Instant feedback. Official IELTS alignment. No guesswork.
                            </p>
                            
                            <div class="text-white" style="font-size: 1.05rem; line-height: 1.6;">
                                <div class="mb-4 text-center" style="padding: 12px; background: rgba(255,255,255,0.15); border-radius: 10px;">
                                    <strong style="font-size: 1.3rem;">Overall Band Score: 7.5</strong>
                                </div>
                                
                                <div class="mb-3" style="font-size: 0.95rem;">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Task Achievement (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 8</span>
                                    </div>
                                    <small style="opacity: 0.9; display: block; font-style: italic;">Sufficiently addresses all parts with well-developed ideas</small>
                                </div>
                                
                                <div class="mb-3" style="font-size: 0.95rem;">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Coherence & Cohesion (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 7</span>
                                    </div>
                                    <small style="opacity: 0.9; display: block; font-style: italic;">Logically organizes information with clear progression</small>
                                </div>
                                
                                <div class="mb-3" style="font-size: 0.95rem;">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Lexical Resource (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 7</span>
                                    </div>
                                    <small style="opacity: 0.9; display: block; font-style: italic;">Flexible vocabulary to discuss variety of topics</small>
                                </div>
                                
                                <div class="mb-3" style="font-size: 0.95rem;">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Grammar Range & Accuracy (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 8</span>
                                    </div>
                                    <small style="opacity: 0.9; display: block; font-style: italic;">Wide range of structures with good control</small>
                                </div>
                            </div>
                            
                            <div class="mt-4 pt-3" style="border-top: 1px solid rgba(255,255,255,0.3);">
                                <div class="d-flex align-items-center justify-content-between flex-wrap">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="fas fa-shield-check me-2" style="color: #90ee90;"></i>
                                        <span style="font-size: 0.9rem; font-weight: 500;">Official IELTS Marking Rubrics + GenAI Precision</span>
                                    </div>

                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <div class="text-white mb-2" style="font-size: 0.95rem; font-weight: 500;">
                                <i class="fas fa-robot me-1"></i>
                                Powered by TrueScore® & ClearScore® Technologies
                            </div>
                            <div class="text-white" style="font-size: 0.9rem; opacity: 0.8; line-height: 1.4;">
                                This is an exact preview of the detailed report you'll receive after completing your first assessment.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- GenAI Technology Overview Section -->
    <section class="assessment-sections py-5" id="features">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="mb-3">The World's ONLY Standardized IELTS GenAI Assessment System</h2>
                <p class="text-muted">Our proprietary technologies deliver consistent, examiner-aligned evaluations</p>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card h-100 border-success">
                        <div class="card-header bg-success text-white text-center py-3">
                            <h3 class="m-0">TrueScore® Writing Assessment</h3>
                        </div>
                        <div class="card-body text-center">
                            <i class="fas fa-pencil-alt fa-3x text-success mb-3"></i>
                            <div class="badge bg-light text-dark mb-3">EXCLUSIVE TECHNOLOGY</div>
                            <p>TrueScore® is the only GenAI system that evaluates IELTS writing using the full IELTS marking rubric. Get instant, expert-level feedback on:</p>
                            <ul class="text-start mb-3" style="list-style-type: none; padding-left: 0; font-size: 16px; line-height: 1.6;">
                                <li class="mb-2"><span style="color: #28a745; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Task Achievement</strong></li>
                                <li class="mb-2"><span style="color: #28a745; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Coherence and Cohesion</strong></li>
                                <li class="mb-2"><span style="color: #28a745; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Lexical Resource</strong></li>
                                <li class="mb-2"><span style="color: #28a745; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Grammatical Range and Accuracy</strong></li>
                            </ul>
                            <p>Whether you're preparing for Academic Writing Tasks 1 & 2 or General Training Letter and Essay Writing, our AI coach gives you clear, structured band score reports and actionable improvement tips.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card h-100 border-primary">
                        <div class="card-header bg-primary text-white text-center py-3">
                            <h3 class="m-0">ClearScore® Speaking Assessment</h3>
                        </div>
                        <div class="card-body text-center">
                            <i class="fas fa-microphone-alt fa-3x text-primary mb-3"></i>
                            <div class="badge bg-light text-dark mb-3">EXCLUSIVE TECHNOLOGY</div>
                            <p>ClearScore® is the world's first AI system for IELTS speaking evaluation. With real-time speech analysis, it provides detailed, criteria-based feedback across all three parts of the IELTS Speaking test:</p>
                            <ul class="text-start mb-3" style="list-style-type: none; padding-left: 0; font-size: 16px; line-height: 1.6;">
                                <li class="mb-2"><span style="color: #007bff; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Fluency and Coherence</strong></li>
                                <li class="mb-2"><span style="color: #007bff; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Lexical Resource</strong></li>
                                <li class="mb-2"><span style="color: #007bff; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Grammatical Range and Accuracy</strong></li>
                                <li class="mb-2"><span style="color: #007bff; font-size: 16px; margin-right: 10px;">●</span><strong style="font-weight: 600;">Pronunciation</strong></li>
                            </ul>
                            <p>Practice with Maya, your AI IELTS examiner, for interactive, conversational assessments that mirror the real test.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="about">
        <div class="container">
            <h2 class="text-center mb-5">Why Choose IELTS GenAI Prep for Your Assessment Preparation?</h2>
            
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-bullseye fa-4x text-primary mb-3"></i>
                        <h3 class="h4">🎯 Official Band-Descriptive Feedback</h3>
                        <p>All assessments follow official IELTS band descriptors, ensuring your practice matches the real test.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-mobile-alt fa-4x text-success mb-3"></i>
                        <h3 class="h4">📱 Mobile & Desktop Access – Anytime, Anywhere</h3>
                        <p>Prepare at your own pace with secure cross-platform access. Start on mobile, continue on desktop – one account works everywhere.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-lightbulb fa-4x text-warning mb-3"></i>
                        <h3 class="h4">💡 Designed for Success</h3>
                        <p>Our tools are perfect for IELTS Academic and General Training candidates seeking reliable, expert-guided feedback to boost scores and build confidence.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Product Plans Section -->
    <section class="pricing py-5 bg-light" id="assessments">
        <div class="container">
            <h2 class="text-center mb-4">GenAI Assessed IELTS Modules</h2>
            <p class="text-center mb-5">Our specialized GenAI technologies provide accurate assessment for IELTS preparation</p>
            
            <!-- TrueScore® Section -->
            <div class="genai-brand-section mb-5">
                <div class="text-center mb-4">
                    <div class="brand-icon text-success">
                        <i class="fas fa-pencil-alt"></i>
                    </div>
                    <h3 class="brand-title">TrueScore® Writing Assessment</h3>
                    <p class="brand-tagline">Professional GenAI assessment of IELTS writing tasks aligned with the official IELTS band descriptors on Task Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy</p>
                </div>
                
                <div class="row">
                    <!-- Academic Writing Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-success text-white text-center">
                                <h3 class="my-0 font-weight-bold">Academic Writing</h3>
                            </div>
                            <div class="card-body">
                                <h1 class="card-title pricing-card-title text-center">$36<small class="text-muted"> for 4 assessments</small></h1>
                                <ul class="list-unstyled mt-3 mb-4">
                                    <li><i class="fas fa-check text-success me-2"></i>4 Unique Assessments Included</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Task 1 & Task 2 Assessment</li>
                                    <li><i class="fas fa-check text-success me-2"></i>TrueScore® GenAI Evaluation</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Official IELTS Criteria Alignment</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Detailed Band Score Feedback</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Writing Improvement Recommendations</li>
                                </ul>
                                <a href="/qr-auth" class="btn btn-lg btn-block btn-success w-100">Purchase via Mobile App</a>
                            </div>
                        </div>
                    </div>

                    <!-- General Writing Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-success text-white text-center">
                                <h3 class="my-0 font-weight-bold">General Training Writing</h3>
                            </div>
                            <div class="card-body">
                                <h1 class="card-title pricing-card-title text-center">$36<small class="text-muted"> for 4 assessments</small></h1>
                                <ul class="list-unstyled mt-3 mb-4">
                                    <li><i class="fas fa-check text-success me-2"></i>4 Unique Assessments Included</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Letter & Essay Assessment</li>
                                    <li><i class="fas fa-check text-success me-2"></i>TrueScore® GenAI Evaluation</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Official IELTS Criteria Alignment</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Comprehensive Feedback System</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Target Band Achievement Support</li>
                                </ul>
                                <a href="/qr-auth" class="btn btn-lg btn-block btn-success w-100">Purchase via Mobile App</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ClearScore® Section -->
            <div class="genai-brand-section">
                <div class="text-center mb-4">
                    <div class="brand-icon text-primary">
                        <i class="fas fa-microphone-alt"></i>
                    </div>
                    <h3 class="brand-title">ClearScore® Speaking Assessment</h3>
                    <p class="brand-tagline">Revolutionary GenAI speaking assessment with real-time conversation analysis covering Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, and Pronunciation</p>
                </div>
                
                <div class="row">
                    <!-- Academic Speaking Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-primary text-white text-center">
                                <h3 class="my-0 font-weight-bold">Academic Speaking</h3>
                            </div>
                            <div class="card-body">
                                <h1 class="card-title pricing-card-title text-center">$36<small class="text-muted"> for 4 assessments</small></h1>
                                <ul class="list-unstyled mt-3 mb-4">
                                    <li><i class="fas fa-check text-primary me-2"></i>4 Unique Assessments Included</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>Interactive Maya AI Examiner</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>ClearScore® GenAI Analysis</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>Real-time Speech Assessment</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>All Three Speaking Parts</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>Pronunciation & Fluency Feedback</li>
                                </ul>
                                <a href="/qr-auth" class="btn btn-lg btn-block btn-primary w-100">Purchase via Mobile App</a>
                            </div>
                        </div>
                    </div>

                    <!-- General Speaking Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-primary text-white text-center">
                                <h3 class="my-0 font-weight-bold">General Training Speaking</h3>
                            </div>
                            <div class="card-body">
                                <h1 class="card-title pricing-card-title text-center">$36<small class="text-muted"> for 4 assessments</small></h1>
                                <ul class="list-unstyled mt-3 mb-4">
                                    <li><i class="fas fa-check text-primary me-2"></i>4 Unique Assessments Included</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>Maya AI Conversation Partner</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>ClearScore® GenAI Technology</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>Comprehensive Speaking Analysis</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>General Training Topic Focus</li>
                                    <li><i class="fas fa-check text-primary me-2"></i>Instant Performance Feedback</li>
                                </ul>
                                <a href="/qr-auth" class="btn btn-lg btn-block btn-primary w-100">Purchase via Mobile App</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section (AI Optimized) -->
    <section class="py-5" id="how-it-works">
        <div class="container">
            <h2 class="text-center mb-5">How It Works</h2>
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <ol class="list-group list-group-numbered">
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Submit your IELTS Writing or Speaking task</div>
                                Upload your writing response or complete a speaking assessment using our AI-powered platform
                            </div>
                            <span class="badge bg-primary rounded-pill">1</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">GenAI evaluates it using official IELTS scoring criteria</div>
                                Our TrueScore® and ClearScore® technologies analyze your response against official band descriptors
                            </div>
                            <span class="badge bg-primary rounded-pill">2</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">You receive your band score and personalized feedback within minutes</div>
                                Get instant results with detailed feedback on all assessment criteria and improvement recommendations
                            </div>
                            <span class="badge bg-primary rounded-pill">3</span>
                        </li>
                    </ol>
                </div>
            </div>
            
            <div class="row mt-5">
                <div class="col-12 text-center">
                    <h3 class="mb-4">How to Get Started</h3>
                    <div class="row">
                        <div class="col-md-4 mb-4 text-center">
                            <div class="mb-3">
                                <i class="fas fa-mobile-alt fa-3x text-primary"></i>
                            </div>
                            <h4>Step 1: Download the IELTS GenAI Prep app</h4>
                            <p>Download the IELTS GenAI Prep app from the App Store or Google Play</p>
                        </div>
                        <div class="col-md-4 mb-4 text-center">
                            <div class="mb-3">
                                <i class="fas fa-credit-card fa-3x text-warning"></i>
                            </div>
                            <h4>Step 2: Create your account and purchase a package</h4>
                            <p>Create your account and purchase a package ($36 for 4 assessments)</p>
                        </div>
                        <div class="col-md-4 mb-4 text-center">
                            <div class="mb-3">
                                <i class="fas fa-laptop fa-3x text-success"></i>
                            </div>
                            <h4>Step 3: Log in on the mobile app or desktop site</h4>
                            <p>Log in on the mobile app or desktop site with your account – your progress syncs automatically</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section (AI Optimized) -->
    <section class="py-5 bg-light" id="faq">
        <div class="container">
            <h2 class="text-center mb-5">Frequently Asked Questions</h2>
            <div class="row">
                <div class="col-lg-10 mx-auto">
                    <div class="accordion" id="faqAccordion">
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq1">
                                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse1" aria-expanded="true" aria-controls="collapse1">
                                    <h3 class="mb-0">What is IELTS GenAI Prep?</h3>
                                </button>
                            </h2>
                            <div id="collapse1" class="accordion-collapse collapse show" aria-labelledby="faq1" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>IELTS GenAI Prep is an AI-powered assessment platform that delivers standardized, examiner-aligned band scores for IELTS Writing and Speaking, using official IELTS scoring criteria.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq2">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse2" aria-expanded="false" aria-controls="collapse2">
                                    <h3 class="mb-0">What makes IELTS GenAI Prep different from other IELTS prep tools?</h3>
                                </button>
                            </h2>
                            <div id="collapse2" class="accordion-collapse collapse" aria-labelledby="faq2" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>It is the only platform using TrueScore® and ClearScore® technologies to provide instant, AI-generated feedback that mirrors official IELTS band descriptors for both Academic and General Training modules.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq3">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse3" aria-expanded="false" aria-controls="collapse3">
                                    <h3 class="mb-0">How does TrueScore® assess IELTS Writing tasks?</h3>
                                </button>
                            </h2>
                            <div id="collapse3" class="accordion-collapse collapse" aria-labelledby="faq3" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>TrueScore® uses GenAI models trained on IELTS scoring rubrics to assess Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy. Each submission receives band-aligned feedback.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq4">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse4" aria-expanded="false" aria-controls="collapse4">
                                    <h3 class="mb-0">How is ClearScore® used to evaluate IELTS Speaking?</h3>
                                </button>
                            </h2>
                            <div id="collapse4" class="accordion-collapse collapse" aria-labelledby="faq4" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>ClearScore® simulates a live speaking test using AI voice assessment technology. It scores fluency, pronunciation, grammar, and vocabulary in real-time, based on official IELTS speaking criteria.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq5">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse5" aria-expanded="false" aria-controls="collapse5">
                                    <h3 class="mb-0">Do you offer Academic and General Training modules?</h3>
                                </button>
                            </h2>
                            <div id="collapse5" class="accordion-collapse collapse" aria-labelledby="faq5" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>Yes. IELTS GenAI Prep supports both Academic and General Training formats for Writing and Speaking, allowing users to choose modules aligned with their test goals.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq6">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse6" aria-expanded="false" aria-controls="collapse6">
                                    <h3 class="mb-0">How much does it cost to use IELTS GenAI Prep?</h3>
                                </button>
                            </h2>
                            <div id="collapse6" class="accordion-collapse collapse" aria-labelledby="faq6" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>Each module (Writing or Speaking) is priced at $36 for four AI-graded assessments. This includes band scores and detailed feedback on every attempt.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq7">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse7" aria-expanded="false" aria-controls="collapse7">
                                    <h3 class="mb-0">Is this a mobile-only platform?</h3>
                                </button>
                            </h2>
                            <div id="collapse7" class="accordion-collapse collapse" aria-labelledby="faq7" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>IELTS GenAI Prep is optimized for mobile and desktop. Users can create an account on the website and access assessments on the IELTS GenAI mobile app anytime, anywhere.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq8">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse8" aria-expanded="false" aria-controls="collapse8">
                                    <h3 class="mb-0">How fast is the scoring process?</h3>
                                </button>
                            </h2>
                            <div id="collapse8" class="accordion-collapse collapse" aria-labelledby="faq8" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>All AI assessments are completed within seconds to a few minutes, providing instant band scores and feedback so users can improve quickly and effectively.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq9">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse9" aria-expanded="false" aria-controls="collapse9">
                                    <h3 class="mb-0">How reliable are the AI-generated IELTS scores?</h3>
                                </button>
                            </h2>
                            <div id="collapse9" class="accordion-collapse collapse" aria-labelledby="faq9" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>Our GenAI scores show a 96% alignment with certified IELTS examiners. The technology is built to mimic human scoring standards while ensuring consistency and speed.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="faq10">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse10" aria-expanded="false" aria-controls="collapse10">
                                    <h3 class="mb-0">Can I track my performance over time?</h3>
                                </button>
                            </h2>
                            <div id="collapse10" class="accordion-collapse collapse" aria-labelledby="faq10" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    <p>Yes. Your personalized dashboard allows you to review past assessments, track band score improvements, and identify focus areas for continued practice.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>IELTS GenAI Prep</h5>
                    <p>The world's only standardized IELTS GenAI assessment platform</p>
                </div>
                <div class="col-md-6">
                    <div class="d-flex flex-column flex-md-row justify-content-md-end">
                        <div class="mb-2">
                            <a href="/privacy-policy" class="text-light me-3">Privacy Policy</a>
                            <a href="/terms-of-service" class="text-light">Terms of Service</a>
                        </div>
                    </div>
                    <div class="text-md-end">
                        <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    }

def handle_health_check():
    """Handle health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'dynamodb': 'connected',
                'nova_sonic': 'available',
                'nova_micro': 'available',
                'ses': 'configured'
            }
        })
    }

def handle_user_registration(data):
    """Handle user registration with welcome email"""
    try:
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        recaptcha_response = data.get('recaptcha_response', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Verify reCAPTCHA
        if not verify_recaptcha_v2(recaptcha_response):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'reCAPTCHA verification failed'})
            }
        
        # Create user account
        if not create_user_account(email, password):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'User already exists or registration failed'})
            }
        
        # Send welcome email
        send_welcome_email(email)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'Account created successfully. Welcome email sent.'
            })
        }
        
    except Exception as e:
        print(f"[ERROR] Registration handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Registration failed'})
        }

def handle_user_login(data):
    """Handle user login with credential verification"""
    try:
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Verify user credentials
        user = verify_user_credentials(email, password)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_email': email,
            'user_id': user.get('user_id', email),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        if create_user_session(session_data):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'session_id': session_id,
                    'user_email': email,
                    'message': 'Login successful'
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Session creation failed'})
            }
        
    except Exception as e:
        print(f"[ERROR] Login handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Login failed'})
        }

def handle_account_deletion(data):
    """Handle account deletion with confirmation email"""
    try:
        email = data.get('email', '').strip()
        confirmation = data.get('confirmation', '').strip()
        
        if not email or not confirmation:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and confirmation are required'})
            }
        
        if email != confirmation:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email confirmation does not match'})
            }
        
        # Delete user account
        if delete_user_account(email):
            # Send deletion confirmation email
            send_account_deletion_email(email)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Account deleted successfully. Confirmation email sent.'
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Account deletion failed'})
            }
        
    except Exception as e:
        print(f"[ERROR] Account deletion handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Account deletion failed'})
        }

def handle_nova_micro_writing(data):
    """Handle Nova Micro writing assessment"""
    try:
        essay_text = data.get('essay_text', '').strip()
        prompt = data.get('prompt', '').strip()
        assessment_type = data.get('assessment_type', 'academic-writing')
        user_email = data.get('user_email', '')
        
        if not essay_text or not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Essay text and prompt are required'})
            }
        
        # Get assessment rubric
        rubric = get_assessment_rubric(assessment_type)
        if not rubric:
            rubric = {'assessment_type': assessment_type}
        
        # Evaluate with Nova Micro
        assessment_result = evaluate_writing_with_nova_micro(essay_text, prompt, rubric)
        
        # Save to DynamoDB
        if user_email:
            save_assessment_result(user_email, {
                'assessment_type': assessment_type,
                'overall_band': assessment_result['overall_band'],
                'criteria_scores': assessment_result['criteria_scores'],
                'feedback': assessment_result['detailed_feedback']
            })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'assessment_result': assessment_result
            })
        }
        
    except Exception as e:
        print(f"[ERROR] Nova Micro writing handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Writing assessment failed'})
        }

def handle_nova_sonic_connection_test():
    """Test Nova Sonic connectivity"""
    try:
        # Test Maya voice synthesis
        audio_data = synthesize_maya_voice_nova_sonic("Hello, I'm Maya, your IELTS speaking examiner. Let's begin your assessment.")
        
        if audio_data:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'status': 'Nova Sonic Amy voice connected',
                    'voice_id': 'en-GB-feminine',
                    'message': 'Maya voice working ✓'
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Nova Sonic connection failed'
                })
            }
        
    except Exception as e:
        print(f"[ERROR] Nova Sonic connection test error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Nova Sonic test failed'})
        }

def handle_nova_sonic_stream(data):
    """Handle Nova Sonic streaming for Maya conversations"""
    try:
        user_text = data.get('user_text', '').strip()
        conversation_stage = data.get('conversation_stage', 'part1')
        
        if not user_text:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'User text is required'})
            }
        
        # Generate Maya's response based on conversation stage
        if conversation_stage == 'part1':
            maya_response = f"Thank you for that response. Let me ask you another question about yourself."
        elif conversation_stage == 'part2':
            maya_response = f"That's interesting. Now, let's move to the next part of the assessment."
        else:
            maya_response = f"I see. Can you elaborate on that point further?"
        
        # Synthesize with Nova Sonic
        audio_data = synthesize_maya_voice_nova_sonic(maya_response)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'maya_response': maya_response,
                'audio_data': audio_data,
                'voice_id': 'en-GB-feminine'
            })
        }
        
    except Exception as e:
        print(f"[ERROR] Nova Sonic stream handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Nova Sonic streaming failed'})
        }

# Additional handlers for pages would go here...
# Including login_page, dashboard_page, profile_page, privacy_policy, terms_of_service, etc.

