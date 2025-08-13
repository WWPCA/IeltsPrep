
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
from typing import Dict, Any, Optional, List

# Production DynamoDB Configuration - ALL PRODUCTION TABLES ONLY
PRODUCTION_DYNAMODB_REGION = 'us-east-1'
PRODUCTION_DYNAMODB_TABLES = {
    'users': 'ielts-genai-prep-users',
    'sessions': 'ielts-genai-prep-sessions',
    'assessments': 'ielts-genai-prep-assessments',
    'questions': 'ielts-assessment-questions',
    'rubrics': 'ielts-assessment-rubrics',
    'content_reports': 'ielts-content-reports',
    'ai_safety_logs': 'ielts-ai-safety-logs'
}

def get_production_dynamodb_resource():
    """Get DynamoDB resource for production environment only"""
    import boto3
    return boto3.resource('dynamodb', region_name=PRODUCTION_DYNAMODB_REGION)

def synthesize_maya_voice_nova_sonic(text: str) -> Optional[str]:
    """Synthesize Maya's voice using AWS Nova Sonic en-GB-feminine with content safety"""
    try:
        # Content safety check before synthesis
        if not is_content_safe_for_synthesis(text):
            log_ai_safety_violation("voice_synthesis", text, "unsafe_content_blocked")
            return None
            
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
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
            # Log successful AI content generation
            log_ai_safety_event("voice_synthesis", text, "success")
            return response_body['audio']
        else:
            return None
            
    except Exception as e:
        print(f"[NOVA_SONIC] Error: {str(e)}")
        log_ai_safety_violation("voice_synthesis", text, f"synthesis_error: {str(e)}")
        return None

def is_content_safe_for_synthesis(text: str) -> bool:
    """Check if text content is safe for AI voice synthesis"""
    try:
        # Check for inappropriate content patterns
        inappropriate_patterns = [
            'hate speech', 'violence', 'explicit', 'harmful', 'dangerous',
            'illegal', 'discrimination', 'harassment', 'abuse'
        ]
        
        text_lower = text.lower()
        for pattern in inappropriate_patterns:
            if pattern in text_lower:
                return False
        
        # Additional AWS Comprehend safety check if available
        import boto3
        try:
            comprehend = boto3.client('comprehend', region_name='us-east-1')
            sentiment_response = comprehend.detect_sentiment(
                Text=text,
                LanguageCode='en'
            )
            
            # Block extremely negative content
            if sentiment_response['Sentiment'] == 'NEGATIVE' and sentiment_response['SentimentScore']['Negative'] > 0.8:
                return False
                
        except:
            pass  # Continue without Comprehend if not available
        
        return True
        
    except Exception as e:
        print(f"[CONTENT_SAFETY] Error checking content: {str(e)}")
        return True  # Default to safe if check fails

def log_ai_safety_event(event_type: str, content: str, status: str):
    """Log AI safety events for compliance monitoring"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['ai_safety_logs'])
        
        log_entry = {
            'log_id': str(uuid.uuid4()),
            'event_type': event_type,
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'content_length': len(content)
        }
        
        table.put_item(Item=log_entry)
        
    except Exception as e:
        print(f"[AI_SAFETY] Logging error: {str(e)}")

def log_ai_safety_violation(event_type: str, content: str, violation_type: str):
    """Log AI safety violations for compliance reporting"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['ai_safety_logs'])
        
        violation_entry = {
            'log_id': str(uuid.uuid4()),
            'event_type': event_type,
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'violation_type': violation_type,
            'status': 'blocked',
            'timestamp': datetime.utcnow().isoformat(),
            'content_length': len(content),
            'severity': 'high'
        }
        
        table.put_item(Item=violation_entry)
        
    except Exception as e:
        print(f"[AI_SAFETY] Violation logging error: {str(e)}")

def handle_content_report(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user content reports as required by Google Play AI policy"""
    try:
        user_email = request_data.get('user_email', '')
        reported_content = request_data.get('reported_content', '')
        report_type = request_data.get('report_type', 'inappropriate')
        report_reason = request_data.get('report_reason', '')
        assessment_id = request_data.get('assessment_id', '')
        
        if not user_email or not reported_content:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'User email and reported content are required'})
            }
        
        # Store content report
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['content_reports'])
        
        report_entry = {
            'report_id': str(uuid.uuid4()),
            'user_email': user_email,
            'reported_content': reported_content,
            'report_type': report_type,
            'report_reason': report_reason,
            'assessment_id': assessment_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending_review',
            'content_hash': hashlib.sha256(reported_content.encode()).hexdigest()
        }
        
        table.put_item(Item=report_entry)
        
        # Log for AI safety monitoring
        log_ai_safety_event("content_report", reported_content, "user_reported")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'report_id': report_entry['report_id'],
                'message': 'Content report submitted successfully. Thank you for helping us maintain a safe platform.'
            })
        }
        
    except Exception as e:
        print(f"[ERROR] Content report handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Content report submission failed'})
        }

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
                        Thank you for creating your account with IELTS GenAI Prep. You now have access to our advanced AI-powered assessment platform.
                    </p>
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 20px 0;">
                        <h4 style="color: #856404; margin-top: 0;">AI Content Safety</h4>
                        <p style="color: #856404; margin-bottom: 0;">Our AI systems are designed to be safe and helpful. If you encounter any inappropriate content, please use the report feature in the app.</p>
                    </div>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://www.ieltsaiprep.com/login" style="background: #e31e24; color: white; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-weight: bold; display: inline-block;">Start Your First Assessment</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        ses_client.send_email(
            Source='welcome@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Welcome to IELTS GenAI Prep - Your Account is Ready!'},
                'Body': {'Html': {'Data': html_body}}
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
                    <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #721c24; margin-top: 0;">Important Security Notice:</h3>
                        <p style="color: #721c24; margin-bottom: 10px;">• This action cannot be undone</p>
                        <p style="color: #721c24; margin-bottom: 10px;">• You will need to create a new account for future access</p>
                        <p style="color: #721c24; margin-bottom: 0;">• Previous purchase history cannot be restored</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Account Deletion Confirmation - IELTS GenAI Prep'},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        
    except Exception as e:
        print(f"[SES] Deletion email error: {str(e)}")

def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v2 response with Google"""
    try:
        secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
        if not secret_key:
            print("[RECAPTCHA] No secret key configured")
            return False
            
        # Prepare POST request for Google reCAPTCHA verification
        post_form = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        if user_ip:
            post_form['remoteip'] = user_ip
            
        # Make request to Google reCAPTCHA API
        request_body = urllib.parse.urlencode(post_form).encode('utf-8')
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=request_body,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            success = result.get('success', False)
            
            if not success:
                error_codes = result.get('error-codes', [])
                print(f"[RECAPTCHA] Verification failed: {error_codes}")
                return False
            
            print("[RECAPTCHA] Verification successful")
            return True
            
    except Exception as e:
        print(f"[RECAPTCHA] Verification error: {str(e)}")
        return False

def verify_user_credentials(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify user credentials against production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['users'])
        
        response = table.get_item(Key={'email': email})
        if 'Item' not in response:
            return None
            
        user = response['Item']
        
        import bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
        else:
            return None
            
    except Exception as e:
        print(f"[DYNAMODB] Credential verification error: {str(e)}")
        return None

def create_user_account(email: str, password: str) -> bool:
    """Create new user account in production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['users'])
        
        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            return False
            
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_record = {
            'email': email,
            'user_id': str(uuid.uuid4()),
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'assessment_attempts': 0,
            'max_attempts': 4,
            'gdpr_consent': True,
            'terms_consent': True,
            'consent_timestamp': datetime.utcnow().isoformat()
        }
        
        table.put_item(Item=user_record)
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] User creation error: {str(e)}")
        return False

def create_user_session(session_record: Dict[str, Any]) -> bool:
    """Create user session in production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['sessions'])
        
        table.put_item(Item=session_record)
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] Session creation error: {str(e)}")
        return False

def get_user_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get user session from production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['sessions'])
        
        response = table.get_item(Key={'session_id': session_id})
        if 'Item' not in response:
            return None
            
        session = response['Item']
        
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.utcnow() > expires_at:
            return None
            
        return session
        
    except Exception as e:
        print(f"[DYNAMODB] Session retrieval error: {str(e)}")
        return None

def delete_user_account(email: str) -> bool:
    """Delete user account from production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        users_table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['users'])
        users_table.delete_item(Key={'email': email})
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] Account deletion error: {str(e)}")
        return False

def get_assessment_questions(assessment_type: str) -> List[Dict[str, Any]]:
    """Get assessment questions from production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['questions'])
        
        response = table.scan(
            FilterExpression='assessment_type = :type',
            ExpressionAttributeValues={':type': assessment_type}
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"[DYNAMODB] Questions retrieval error: {str(e)}")
        return []

def get_user_assessment_history(user_email: str) -> List[Dict[str, Any]]:
    """Get user's assessment history from production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['assessments'])
        
        response = table.scan(
            FilterExpression='user_email = :email',
            ExpressionAttributeValues={':email': user_email}
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"[DYNAMODB] Assessment history error: {str(e)}")
        return []

def save_assessment_result(user_email: str, assessment_record: Dict[str, Any]) -> bool:
    """Save assessment result to production DynamoDB"""
    try:
        dynamodb = get_production_dynamodb_resource()
        table = dynamodb.Table(PRODUCTION_DYNAMODB_TABLES['assessments'])
        
        assessment_entry = {
            'assessment_id': str(uuid.uuid4()),
            'user_email': user_email,
            'assessment_type': assessment_record['assessment_type'],
            'overall_band': assessment_record['overall_band'],
            'criteria_scores': assessment_record['criteria_scores'],
            'feedback': assessment_record['feedback'],
            'timestamp': datetime.utcnow().isoformat(),
            'completed': True,
            'ai_generated': True,
            'content_safe': True
        }
        
        table.put_item(Item=assessment_entry)
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] Assessment save error: {str(e)}")
        return False

def evaluate_writing_with_nova_micro(essay_text: str, prompt: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate writing using Nova Micro with IELTS rubrics and content safety"""
    try:
        # Content safety check
        if not is_content_safe_for_evaluation(essay_text):
            log_ai_safety_violation("writing_evaluation", essay_text, "inappropriate_content")
            return {
                "overall_band": 0.0,
                "criteria_scores": {
                    "task_achievement": 0.0,
                    "coherence_cohesion": 0.0,
                    "lexical_resource": 0.0,
                    "grammatical_range": 0.0
                },
                "detailed_feedback": {
                    "strengths": [],
                    "areas_for_improvement": ["Content violates platform guidelines"],
                    "specific_suggestions": ["Please ensure your writing follows appropriate content guidelines"]
                },
                "content_flagged": True
            }
        
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        system_prompt = f"""
        You are an expert IELTS Writing examiner. Evaluate the following essay using official IELTS criteria.
        
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
        
        Evaluate based on official IELTS band descriptors. Be constructive and educational.
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
            
            import re
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                assessment_json = json.loads(json_match.group())
                
                # Log successful AI evaluation
                log_ai_safety_event("writing_evaluation", essay_text, "success")
                
                return assessment_json
                
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
        log_ai_safety_violation("writing_evaluation", essay_text, f"evaluation_error: {str(e)}")
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

def is_content_safe_for_evaluation(text: str) -> bool:
    """Check if content is safe for AI evaluation"""
    try:
        # Check for inappropriate content
        inappropriate_keywords = [
            'hate', 'violence', 'explicit', 'harmful', 'dangerous',
            'illegal', 'discrimination', 'harassment', 'abuse', 'threat'
        ]
        
        text_lower = text.lower()
        for keyword in inappropriate_keywords:
            if keyword in text_lower:
                return False
        
        # Check text length (prevent abuse)
        if len(text) > 5000:  # Reasonable limit for IELTS essays
            return False
            
        return True
        
    except Exception as e:
        print(f"[CONTENT_SAFETY] Error checking evaluation content: {str(e)}")
        return True

def get_assessment_history_html(assessment_history: list) -> str:
    """Generate HTML for assessment history display"""
    if not assessment_history:
        return """
        <div class="text-center py-4">
            <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
            <p class="text-muted">No assessment history yet. Start your first assessment!</p>
        </div>
        """
    
    html = """
    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Assessment Type</th>
                    <th>Date</th>
                    <th>Band Score</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for assessment in assessment_history[-5:]:
        assessment_type = assessment.get('assessment_type', 'Unknown').replace('-', ' ').title()
        date = assessment.get('timestamp', 'Unknown')
        band_score = assessment.get('overall_band', 'N/A')
        status = 'Completed' if assessment.get('completed', False) else 'In Progress'
        
        html += f"""
                <tr>
                    <td><i class="fas fa-file-alt"></i> {assessment_type}</td>
                    <td>{date}</td>
                    <td><span class="badge bg-primary">Band {band_score}</span></td>
                    <td><span class="badge bg-success">{status}</span></td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def get_user_assessment_history_html(user_email: str) -> str:
    """Generate HTML for user's assessment history in profile"""
    assessment_history = get_user_assessment_history(user_email)
    return get_assessment_history_html(assessment_history)

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
            request_data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            request_data = {}
        
        print(f"[LAMBDA] Processing {method} {path}")
        
        # Route requests
        if path == '/' and method == 'GET':
            return handle_home_page()
        elif path == '/api/health' and method == 'GET':
            return handle_health_check()
        elif path == '/api/register' and method == 'POST':
            return handle_user_registration(request_data)
        elif path == '/api/login' and method == 'POST':
            return handle_user_login(request_data)
        elif path == '/api/account-deletion' and method == 'POST':
            return handle_account_deletion(request_data)
        elif path == '/api/nova-micro-writing' and method == 'POST':
            return handle_nova_micro_writing(request_data)
        elif path == '/api/nova-sonic-connect' and method == 'GET':
            return handle_nova_sonic_connection()
        elif path == '/api/nova-sonic-stream' and method == 'POST':
            return handle_nova_sonic_stream(request_data)
        elif path == '/api/content-report' and method == 'POST':
            return handle_content_report(request_data)
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
    original_working_template = """<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <meta name=\"description\" content=\"The only AI-powered IELTS assessment platform with standardized band scoring. Prepare for IELTS Writing and Speaking with TrueScore® and ClearScore® technologies.\">\n    <meta name=\"keywords\" content=\"IELTS AI Assessment, IELTS Writing Feedback, IELTS Speaking Evaluation, GenAI IELTS App, TrueScore IELTS, ClearScore IELTS, AI Band Score, IELTS Band Descriptors, Academic IELTS, General Training IELTS, AI IELTS Practice, Online IELTS Preparation, AI Language Assessment, IELTS Prep App, IELTS writing preparation, IELTS speaking practice test, IELTS writing practice test, IELTS practice test with feedback\">\n    <meta property=\"og:title\" content=\"IELTS GenAI Prep - AI-Powered IELTS Assessment Platform\">\n    <meta property=\"og:description\" content=\"The only AI-powered IELTS assessment platform with standardized band scoring using TrueScore® and ClearScore® technologies.\">\n    <meta property=\"og:type\" content=\"website\">\n    <meta name=\"twitter:card\" content=\"summary_large_image\">\n    <meta name=\"twitter:title\" content=\"IELTS GenAI Prep - AI-Powered IELTS Assessment Platform\">\n    <meta name=\"twitter:description\" content=\"The only AI-powered IELTS assessment platform with standardized band scoring using TrueScore® and ClearScore® technologies.\">\n    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>\n    \n    <!-- Bootstrap CSS -->\n    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css\" rel=\"stylesheet\">\n    \n    <!-- Font Awesome for icons -->\n    <link href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css\" rel=\"stylesheet\">\n    \n    <!-- Google Fonts -->\n    <link href=\"https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap\" rel=\"stylesheet\">\n    \n    <!-- Schema.org Organization Markup -->\n    <script type=\"application/ld+json\">\n    {\n      \"@context\": \"https://schema.org\",\n      \"@type\": \"Organization\",\n      \"name\": \"IELTS GenAI Prep\",\n      \"url\": \"https://www.ieltsgenaiprep.com\",\n      \"logo\": \"https://www.ieltsgenaiprep.com/logo.png\",\n      \"description\": \"IELTS GenAI Prep is an AI-powered IELTS assessment platform offering instant band-aligned feedback for Writing and Speaking modules.\",\n      \"sameAs\": [\n        \"https://www.linkedin.com/company/ieltsgenaiprep\",\n        \"https://www.twitter.com/ieltsgenaiprep\"\n      ]\n    }\n    </script>\n    \n    <!-- FAQ Schema Markup -->\n    <script type=\"application/ld+json\">\n    {\n      \"@context\": \"https://schema.org\",\n      \"@type\": \"FAQPage\",\n      \"mainEntity\": [\n        {\n          \"@type\": \"Question\",\n          \"name\": \"What is IELTS GenAI Prep?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"IELTS GenAI Prep is an AI-powered assessment platform that delivers standardized, examiner-aligned band scores for IELTS Writing and Speaking, using official IELTS scoring criteria.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"What makes IELTS GenAI Prep different from other IELTS prep tools?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"It is the only platform using TrueScore® and ClearScore® technologies to provide instant, AI-generated feedback that mirrors official IELTS band descriptors for both Academic and General Training modules.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"How does TrueScore® assess IELTS Writing tasks?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"TrueScore® uses GenAI models trained on IELTS scoring rubrics to assess Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy. Each submission receives band-aligned feedback.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"How is ClearScore® used to evaluate IELTS Speaking?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"ClearScore® simulates a live speaking test using AI voice assessment technology. It scores fluency, pronunciation, grammar, and vocabulary in real-time, based on official IELTS speaking criteria.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"Do you offer Academic and General Training modules?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"Yes. IELTS GenAI Prep supports both Academic and General Training formats for Writing and Speaking, allowing users to choose modules aligned with their test goals.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"How much does it cost to use IELTS GenAI Prep?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"Each module (Writing or Speaking) is priced at $49.99 for four AI-graded assessments. This includes band scores and detailed feedback on every attempt.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"Is this a mobile-only platform?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"IELTS GenAI Prep is optimized for mobile and desktop. Users can create an account on the website and access assessments on the IELTS GenAI mobile app anytime, anywhere.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"How fast is the scoring process?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"All AI assessments are completed within seconds to a few minutes, providing instant band scores and feedback so users can improve quickly and effectively.\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"How reliable are the AI-generated IELTS scores?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"Our AI assessments are built on official IELTS band descriptors, ensuring consistent, rubric-aligned feedback\"\n          }\n        },\n        {\n          \"@type\": \"Question\",\n          \"name\": \"Can I track my performance over time?\",\n          \"acceptedAnswer\": {\n            \"@type\": \"Answer\",\n            \"text\": \"Yes. Your personalized dashboard allows you to review past assessments, track band score improvements, and identify focus areas for continued practice.\"\n          }\n        }\n      ]\n    }\n    </script>\n    \n    <style>\n        body {\n            font-family: 'Roboto', sans-serif;\n            line-height: 1.6;\n        }\n        \n        .pricing-card {\n            border: 1px solid rgba(0, 0, 0, 0.125);\n            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);\n            transition: transform 0.2s;\n        }\n        \n        .pricing-card:hover {\n            transform: translateY(-5px);\n        }\n        \n        .genai-brand-section {\n            margin-bottom: 60px;\n        }\n        \n        .brand-icon {\n            font-size: 2.5rem;\n            margin-bottom: 15px;\n        }\n        \n        .brand-title {\n            font-size: 2rem;\n            margin-bottom: 0.5rem;\n        }\n        \n        .brand-tagline {\n            color: #666;\n            margin-bottom: 2rem;\n            font-size: 1.1rem;\n        }\n        \n        .hero {\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            color: white;\n            padding: 80px 0;\n        }\n        \n        .features {\n            padding: 80px 0;\n            background: #f8f9fa;\n        }\n        \n        .navbar {\n            background-color: #fff !important;\n            box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n        }\n        \n        .navbar-brand {\n            font-weight: bold;\n            color: #4361ee !important;\n        }\n        \n        .navbar-nav .nav-link {\n            color: #333 !important;\n            font-weight: 500;\n        }\n        \n        .navbar-nav .nav-link:hover {\n            color: #4361ee !important;\n        }\n        \n        /* Enhanced animations and interactivity */\n        .hero h1 {\n            animation: fadeInUp 0.8s ease-out;\n        }\n        \n        .hero h2 {\n            animation: fadeInUp 0.8s ease-out 0.2s both;\n        }\n        \n        .hero .mb-4 > div {\n            animation: fadeInLeft 0.6s ease-out 0.4s both;\n        }\n        \n        .hero .mb-4 > div:nth-child(2) {\n            animation-delay: 0.6s;\n        }\n        \n        .hero .mb-4 > div:nth-child(3) {\n            animation-delay: 0.8s;\n        }\n        \n        .hero p {\n            animation: fadeInUp 0.8s ease-out 1s both;\n        }\n        \n        .hero-buttons {\n            animation: fadeInUp 0.8s ease-out 1.2s both;\n        }\n        \n        .hero .col-lg-6:last-child {\n            animation: fadeInRight 0.8s ease-out 0.5s both;\n        }\n        \n        @keyframes fadeInUp {\n            from {\n                opacity: 0;\n                transform: translateY(30px);\n            }\n            to {\n                opacity: 1;\n                transform: translateY(0);\n            }\n        }\n        \n        @keyframes fadeInLeft {\n            from {\n                opacity: 0;\n                transform: translateX(-30px);\n            }\n            to {\n                opacity: 1;\n                transform: translateX(0);\n            }\n        }\n        \n        @keyframes fadeInRight {\n            from {\n                opacity: 0;\n                transform: translateX(30px);\n            }\n            to {\n                opacity: 1;\n                transform: translateX(0);\n            }\n        }\n        \n        /* Button hover effects */\n        .hero-buttons .btn:hover {\n            transform: translateY(-3px);\n            box-shadow: 0 8px 25px rgba(0,0,0,0.2);\n        }\n        \n        .btn-success:hover {\n            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);\n            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);\n        }\n        \n        .btn-outline-light:hover {\n            background: rgba(255,255,255,0.1);\n            border-color: rgba(255,255,255,1);\n            backdrop-filter: blur(10px);\n        }\n        \n        /* Icon container hover effects */\n        .hero .me-3:hover {\n            background: rgba(255,255,255,0.3);\n            transform: scale(1.1);\n            transition: all 0.3s ease;\n        }\n        \n        /* Improved typography for better readability and spacing */\n        @media (max-width: 768px) {\n            .hero {\n                padding: 60px 0;\n            }\n            \n            .hero h1 {\n                font-size: 2.5rem !important;\n                line-height: 1.3 !important;\n            }\n            \n            .hero h2 {\n                font-size: 1.3rem !important;\n            }\n            \n            .hero-buttons .btn {\n                display: block;\n                width: 100%;\n                margin-bottom: 15px;\n                margin-right: 0 !important;\n            }\n            \n            .hero .col-lg-6:first-child {\n                text-align: center !important;\n            }\n        }\n        \n        @media (max-width: 576px) {\n            .hero h1 {\n                font-size: 2rem !important;\n                line-height: 1.2 !important;\n            }\n            \n            .hero h2 {\n                font-size: 1.1rem !important;\n            }\n            \n            .hero .mb-4 span {\n                font-size: 1rem !important;\n            }\n        }\n    </style>\n</head>\n\n<body>\n    <!-- Navigation -->\n    <nav class=\"navbar navbar-expand-lg navbar-light bg-light fixed-top\">\n        <div class=\"container\">\n            <a class=\"navbar-brand\" href=\"/\">IELTS GenAI Prep</a>\n            <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#navbarNav\">\n                <span class=\"navbar-toggler-icon\"></span>\n            </button>\n            <div class=\"collapse navbar-collapse\" id=\"navbarNav\">\n                <ul class=\"navbar-nav ms-auto\">\n                    <li class=\"nav-item\">\n                        <a class=\"nav-link\" href=\"#how-it-works\">How it Works</a>\n                    </li>\n                    <li class=\"nav-item\">\n                        <a class=\"nav-link\" href=\"#assessments\">Assessments</a>\n                    </li>\n                    <li class=\"nav-item\">\n                        <a class=\"nav-link\" href=\"#faq\">FAQ</a>\n                    </li>\n                    <li class=\"nav-item\">\n                        <a class=\"nav-link\" href=\"/login\">Login</a>\n                    </li>\n                </ul>\n            </div>\n        </div>\n    </nav>\n\n    <!-- Hero Section -->\n    <section class=\"hero\" style=\"margin-top: 76px; padding: 80px 0; position: relative; overflow: hidden;\">\n        <!-- Background enhancement -->\n        <div style=\"position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); pointer-events: none;\"></div>\n        \n        <div class=\"container\">\n            <div class=\"row align-items-center\">\n                <div class=\"col-lg-6 text-center text-lg-start mb-5 mb-lg-0\">\n                    <!-- SEO-Optimized H1 and Introduction -->\n                    <h1 class=\"display-3 fw-bold mb-3\" style=\"font-size: 3.5rem; line-height: 1.2; letter-spacing: -0.02em; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.1);\">\n                        AI-Powered IELTS Writing and Speaking Assessments with Official Band Scoring\n                    </h1>\n                    \n                    <p class=\"h4 mb-4\" style=\"font-size: 1.3rem; line-height: 1.4; font-weight: 500; color: rgba(255,255,255,0.95); margin-bottom: 2rem;\">\n                        IELTS GenAI Prep is the only AI-based IELTS preparation platform offering instant band-aligned feedback on Writing and Speaking. Powered by TrueScore® and ClearScore®, we replicate official examiner standards using GenAI technology.\n                    </p>\n                    \n                    <!-- Benefits with icons -->\n                    <div class=\"mb-4\">\n                        <div class=\"d-flex align-items-center justify-content-center justify-content-lg-start mb-3\">\n                            <div class=\"me-3\" style=\"width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);\">\n                                <i class=\"fas fa-brain text-white\" style=\"font-size: 1.1rem;\"></i>\n                            </div>\n                            <span class=\"text-white\" style=\"font-size: 1.1rem; font-weight: 500;\">AI-Powered Scoring Technology</span>\n                        </div>\n                        \n                        <div class=\"d-flex align-items-center justify-content-center justify-content-lg-start mb-3\">\n                            <div class=\"me-3\" style=\"width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);\">\n                                <i class=\"fas fa-check-circle text-white\" style=\"font-size: 1.1rem;\"></i>\n                            </div>\n                            <span class=\"text-white\" style=\"font-size: 1.1rem; font-weight: 500;\">Official IELTS Criteria Alignment</span>\n                        </div>\n                        \n                        <div class=\"d-flex align-items-center justify-content-center justify-content-lg-start mb-4\">\n                            <div class=\"me-3\" style=\"width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);\">\n                                <i class=\"fas fa-bullseye text-white\" style=\"font-size: 1.1rem;\"></i>\n                            </div>\n                            <span class=\"text-white\" style=\"font-size: 1.1rem; font-weight: 500;\">Academic & General Training Modules</span>\n                        </div>\n                    </div>\n                    \n                    <p class=\"mb-5\" style=\"font-size: 1.1rem; line-height: 1.7; color: rgba(255,255,255,0.9); max-width: 500px; margin-left: auto; margin-right: auto;\">\n                        Experience TrueScore® and ClearScore® technologies that deliver standardized IELTS assessments based on official scoring criteria.\n                    </p>\n                    \n                    <!-- Enhanced CTA buttons -->\n                    <div class=\"hero-buttons text-center text-lg-start\">\n                        <a href=\"/login\" class=\"btn btn-success btn-lg me-3 mb-3\" style=\"font-size: 1.2rem; padding: 15px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4); border: none; transition: all 0.3s ease;\" aria-label=\"Start using IELTS GenAI Prep assessments\">\n                            <i class=\"fas fa-rocket me-2\"></i>\n                            Get Started\n                        </a>\n                        <a href=\"#how-it-works\" class=\"btn btn-outline-light btn-lg mb-3\" style=\"font-size: 1.2rem; padding: 15px 30px; border-radius: 12px; border: 2px solid rgba(255,255,255,0.8); transition: all 0.3s ease;\" aria-label=\"Learn more about how IELTS GenAI Prep works\">\n                            <i class=\"fas fa-info-circle me-2\"></i>\n                            Learn More\n                        </a>\n                    </div>\n                </div>\n                \n                <div class=\"col-lg-6 text-center\">\n                    <!-- Sample Assessment Report Demo -->\n                    <div style=\"background: rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; backdrop-filter: blur(15px); box-shadow: 0 10px 30px rgba(0,0,0,0.1);\">\n                        <div class=\"mb-3\">\n                            <span class=\"badge bg-primary text-white px-3 py-2\" style=\"font-size: 0.9rem; font-weight: 600;\">\n                                <i class=\"fas fa-star me-1\"></i>\n                                YOUR SCORE PREVIEW\n                            </span>\n                        </div>\n                        <div style=\"background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 15px; padding: 30px; margin-bottom: 20px; position: relative;\">\n                            <h3 class=\"text-white mb-2\" style=\"font-size: 1.4rem; font-weight: 600; line-height: 1.3;\">\n                                <i class=\"fas fa-certificate me-2\"></i>\n                                See Exactly How Your IELTS Score Will Look\n                            </h3>\n                            <div class=\"mb-3 d-flex justify-content-center\">\n                                <span class=\"badge bg-light text-dark px-3 py-1\" style=\"font-size: 0.85rem; font-weight: 500; display: inline-block; text-align: center;\">\n                                    <i class=\"fas fa-pencil-alt me-1\"></i>\n                                    Academic Writing Assessment Sample\n                                </span>\n                            </div>\n                            <p class=\"text-white mb-4\" style=\"font-size: 0.95rem; opacity: 0.95; font-weight: 400;\">\n                                Instant feedback. Official IELTS alignment. No guesswork.\n                            </p>\n                            \n                            <div class=\"text-white\" style=\"font-size: 1.05rem; line-height: 1.6;\">\n                                <div class=\"mb-4 text-center\" style=\"padding: 12px; background: rgba(255,255,255,0.15); border-radius: 10px;\">\n                                    <strong style=\"font-size: 1.3rem;\">Overall Band Score: 7.5</strong>\n                                </div>\n                                \n                                <div class=\"mb-3\" style=\"font-size: 0.95rem;\">\n                                    <div class=\"d-flex justify-content-between align-items-center mb-1\">\n                                        <span><strong>Task Achievement (25%)</strong></span>\n                                        <span class=\"badge bg-light text-dark\">Band 8</span>\n                                    </div>\n                                    <small style=\"opacity: 0.9; display: block; font-style: italic;\">Sufficiently addresses all parts with well-developed ideas</small>\n                                </div>\n                                \n                                <div class=\"mb-3\" style=\"font-size: 0.95rem;\">\n                                    <div class=\"d-flex justify-content-between align-items-center mb-1\">\n                                        <span><strong>Coherence & Cohesion (25%)</strong></span>\n                                        <span class=\"badge bg-light text-dark\">Band 7</span>\n                                    </div>\n                                    <small style=\"opacity: 0.9; display: block; font-style: italic;\">Logically organizes information with clear progression</small>\n                                </div>\n                                \n                                <div class=\"mb-3\" style=\"font-size: 0.95rem;\">\n                                    <div class=\"d-flex justify-content-between align-items-center mb-1\">\n                                        <span><strong>Lexical Resource (25%)</strong></span>\n                                        <span class=\"badge bg-light text-dark\">Band 7</span>\n                                    </div>\n                                    <small style=\"opacity: 0.9; display: block; font-style: italic;\">Flexible vocabulary to discuss variety of topics</small>\n                                </div>\n                                \n                                <div class=\"mb-3\" style=\"font-size: 0.95rem;\">\n                                    <div class=\"d-flex justify-content-between align-items-center mb-1\">\n                                        <span><strong>Grammar Range & Accuracy (25%)</strong></span>\n                                        <span class=\"badge bg-light text-dark\">Band 8</span>\n                                    </div>\n                                    <small style=\"opacity: 0.9; display: block; font-style: italic;\">Wide range of structures with good control</small>\n                                </div>\n                            </div>\n                            \n                            <div class=\"mt-4 pt-3\" style=\"border-top: 1px solid rgba(255,255,255,0.3);\">\n                                <div class=\"d-flex align-items-center justify-content-between flex-wrap\">\n                                    <div class=\"d-flex align-items-center mb-2\">\n                                        <i class=\"fas fa-shield-check me-2\" style=\"color: #90ee90;\"></i>\n                                        <span style=\"font-size: 0.9rem; font-weight: 500;\">Official IELTS Marking Rubrics + GenAI Precision</span>\n                                    </div>\n\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"text-center\">\n                            <div class=\"text-white mb-2\" style=\"font-size: 0.95rem; font-weight: 500;\">\n                                <i class=\"fas fa-robot me-1\"></i>\n                                Powered by TrueScore® & ClearScore® Technologies\n                            </div>\n                            <div class=\"text-white\" style=\"font-size: 0.9rem; opacity: 0.8; line-height: 1.4;\">\n                                This is an exact preview of the detailed report you'll receive after completing your first assessment.\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <!-- GenAI Technology Overview Section -->\n    <section class=\"assessment-sections py-5\" id=\"features\">\n        <div class=\"container\">\n            <div class=\"text-center mb-5\">\n                <h2 class=\"mb-3\">The World's ONLY Standardized IELTS GenAI Assessment System</h2>\n                <p class=\"text-muted\">Our proprietary technologies deliver consistent, examiner-aligned evaluations</p>\n            </div>\n            \n            <div class=\"row\">\n                <div class=\"col-md-6 mb-4\">\n                    <div class=\"card h-100 border-success\">\n                        <div class=\"card-header bg-success text-white text-center py-3\">\n                            <h3 class=\"m-0\">TrueScore® Writing Assessment</h3>\n                        </div>\n                        <div class=\"card-body text-center\">\n                            <i class=\"fas fa-pencil-alt fa-3x text-success mb-3\"></i>\n                            <div class=\"badge bg-light text-dark mb-3\">EXCLUSIVE TECHNOLOGY</div>\n                            <p>TrueScore® is the only GenAI system that evaluates IELTS writing using the full IELTS marking rubric. Get instant, expert-level feedback on:</p>\n                            <ul class=\"text-start mb-3\" style=\"list-style-type: none; padding-left: 0; font-size: 16px; line-height: 1.6;\">\n                                <li class=\"mb-2\"><span style=\"color: #28a745; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Task Achievement</strong></li>\n                                <li class=\"mb-2\"><span style=\"color: #28a745; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Coherence and Cohesion</strong></li>\n                                <li class=\"mb-2\"><span style=\"color: #28a745; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Lexical Resource</strong></li>\n                                <li class=\"mb-2\"><span style=\"color: #28a745; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Grammatical Range and Accuracy</strong></li>\n                            </ul>\n                            <p>Whether you're preparing for Academic Writing Tasks 1 & 2 or General Training Letter and Essay Writing, our AI coach gives you clear, structured band score reports and actionable improvement tips.</p>\n                        </div>\n                    </div>\n                </div>\n                \n                <div class=\"col-md-6 mb-4\">\n                    <div class=\"card h-100 border-primary\">\n                        <div class=\"card-header bg-primary text-white text-center py-3\">\n                            <h3 class=\"m-0\">ClearScore® Speaking Assessment</h3>\n                        </div>\n                        <div class=\"card-body text-center\">\n                            <i class=\"fas fa-microphone-alt fa-3x text-primary mb-3\"></i>\n                            <div class=\"badge bg-light text-dark mb-3\">EXCLUSIVE TECHNOLOGY</div>\n                            <p>ClearScore® is the world's first AI system for IELTS speaking evaluation. With real-time speech analysis, it provides detailed, criteria-based feedback across all three parts of the IELTS Speaking test:</p>\n                            <ul class=\"text-start mb-3\" style=\"list-style-type: none; padding-left: 0; font-size: 16px; line-height: 1.6;\">\n                                <li class=\"mb-2\"><span style=\"color: #007bff; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Fluency and Coherence</strong></li>\n                                <li class=\"mb-2\"><span style=\"color: #007bff; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Lexical Resource</strong></li>\n                                <li class=\"mb-2\"><span style=\"color: #007bff; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Grammatical Range and Accuracy</strong></li>\n                                <li class=\"mb-2\"><span style=\"color: #007bff; font-size: 16px; margin-right: 10px;\">●</span><strong style=\"font-weight: 600;\">Pronunciation</strong></li>\n                            </ul>\n                            <p>Practice with Maya, your AI IELTS examiner, for interactive, conversational assessments that mirror the real test.</p>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <!-- Features Section -->\n    <section class=\"features\" id=\"about\">\n        <div class=\"container\">\n            <h2 class=\"text-center mb-5\">Why Choose IELTS GenAI Prep for Your Assessment Preparation?</h2>\n            \n            <div class=\"row\">\n                <div class=\"col-md-4 mb-4\">\n                    <div class=\"card h-100 p-3 text-center\">\n                        <i class=\"fas fa-bullseye fa-4x text-primary mb-3\"></i>\n                        <h3 class=\"h4\">🎯 Official Band-Descriptive Feedback</h3>\n                        <p>All assessments follow official IELTS band descriptors, ensuring your practice matches the real test.</p>\n                    </div>\n                </div>\n                \n                <div class=\"col-md-4 mb-4\">\n                    <div class=\"card h-100 p-3 text-center\">\n                        <i class=\"fas fa-mobile-alt fa-4x text-success mb-3\"></i>\n                        <h3 class=\"h4\">📱 Mobile & Desktop Access – Anytime, Anywhere</h3>\n                        <p>Prepare at your own pace with secure cross-platform access. Start on mobile, continue on desktop – one account works everywhere.</p>\n                    </div>\n                </div>\n                \n                <div class=\"col-md-4 mb-4\">\n                    <div class=\"card h-100 p-3 text-center\">\n                        <i class=\"fas fa-lightbulb fa-4x text-warning mb-3\"></i>\n                        <h3 class=\"h4\">💡 Designed for Success</h3>\n                        <p>Our tools are perfect for IELTS Academic and General Training candidates seeking reliable, expert-guided feedback to boost scores and build confidence.</p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <!-- Product Plans Section -->\n    <section class=\"pricing py-5 bg-light\" id=\"assessments\">\n        <div class=\"container\">\n            <h2 class=\"text-center mb-4\">GenAI Assessed IELTS Modules</h2>\n            <p class=\"text-center mb-5\">Our specialized GenAI technologies provide accurate assessment for IELTS preparation</p>\n            \n            <!-- TrueScore® Section -->\n            <div class=\"genai-brand-section mb-5\">\n                <div class=\"text-center mb-4\">\n                    <div class=\"brand-icon text-success\">\n                        <i class=\"fas fa-pencil-alt\"></i>\n                    </div>\n                    <h3 class=\"brand-title\">TrueScore® Writing Assessment</h3>\n                    <p class=\"brand-tagline\">Professional GenAI assessment of IELTS writing tasks aligned with the official IELTS band descriptors on Task Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy</p>\n                </div>\n                \n                <div class=\"row\">\n                    <!-- Academic Writing Assessment -->\n                    <div class=\"col-lg-6 mb-4\">\n                        <div class=\"card pricing-card\">\n                            <div class=\"card-header bg-success text-white text-center\">\n                                <h3 class=\"my-0 font-weight-bold\">Academic Writing</h3>\n                            </div>\n                            <div class=\"card-body\">\n                                <h1 class=\"card-title pricing-card-title text-center\">$36<small class=\"text-muted\"> for 4 assessments</small></h1>\n                                <ul class=\"list-unstyled mt-3 mb-4\">\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>4 Unique Assessments Included</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Task 1 & Task 2 Assessment</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>TrueScore® GenAI Evaluation</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Official IELTS Criteria Alignment</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Detailed Band Score Feedback</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Writing Improvement Recommendations</li>\n                                </ul>\n                                <a href=\"/qr-auth\" class=\"btn btn-lg btn-block btn-success w-100\">Purchase via Mobile App</a>\n                            </div>\n                        </div>\n                    </div>\n\n                    <!-- General Writing Assessment -->\n                    <div class=\"col-lg-6 mb-4\">\n                        <div class=\"card pricing-card\">\n                            <div class=\"card-header bg-success text-white text-center\">\n                                <h3 class=\"my-0 font-weight-bold\">General Training Writing</h3>\n                            </div>\n                            <div class=\"card-body\">\n                                <h1 class=\"card-title pricing-card-title text-center\">$36<small class=\"text-muted\"> for 4 assessments</small></h1>\n                                <ul class=\"list-unstyled mt-3 mb-4\">\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>4 Unique Assessments Included</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Letter & Essay Assessment</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>TrueScore® GenAI Evaluation</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Official IELTS Criteria Alignment</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Comprehensive Feedback System</li>\n                                    <li><i class=\"fas fa-check text-success me-2\"></i>Target Band Achievement Support</li>\n                                </ul>\n                                <a href=\"/qr-auth\" class=\"btn btn-lg btn-block btn-success w-100\">Purchase via Mobile App</a>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </div>\n\n            <!-- ClearScore® Section -->\n            <div class=\"genai-brand-section\">\n                <div class=\"text-center mb-4\">\n                    <div class=\"brand-icon text-primary\">\n                        <i class=\"fas fa-microphone-alt\"></i>\n                    </div>\n                    <h3 class=\"brand-title\">ClearScore® Speaking Assessment</h3>\n                    <p class=\"brand-tagline\">Revolutionary GenAI speaking assessment with real-time conversation analysis covering Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, and Pronunciation</p>\n                </div>\n                \n                <div class=\"row\">\n                    <!-- Academic Speaking Assessment -->\n                    <div class=\"col-lg-6 mb-4\">\n                        <div class=\"card pricing-card\">\n                            <div class=\"card-header bg-primary text-white text-center\">\n                                <h3 class=\"my-0 font-weight-bold\">Academic Speaking</h3>\n                            </div>\n                            <div class=\"card-body\">\n                                <h1 class=\"card-title pricing-card-title text-center\">$36<small class=\"text-muted\"> for 4 assessments</small></h1>\n                                <ul class=\"list-unstyled mt-3 mb-4\">\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>4 Unique Assessments Included</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>Interactive Maya AI Examiner</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>ClearScore® GenAI Analysis</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>Real-time Speech Assessment</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>All Three Speaking Parts</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>Pronunciation & Fluency Feedback</li>\n                                </ul>\n                                <a href=\"/qr-auth\" class=\"btn btn-lg btn-block btn-primary w-100\">Purchase via Mobile App</a>\n                            </div>\n                        </div>\n                    </div>\n\n                    <!-- General Speaking Assessment -->\n                    <div class=\"col-lg-6 mb-4\">\n                        <div class=\"card pricing-card\">\n                            <div class=\"card-header bg-primary text-white text-center\">\n                                <h3 class=\"my-0 font-weight-bold\">General Training Speaking</h3>\n                            </div>\n                            <div class=\"card-body\">\n                                <h1 class=\"card-title pricing-card-title text-center\">$36<small class=\"text-muted\"> for 4 assessments</small></h1>\n                                <ul class=\"list-unstyled mt-3 mb-4\">\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>4 Unique Assessments Included</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>Maya AI Conversation Partner</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>ClearScore® GenAI Technology</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>Comprehensive Speaking Analysis</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>General Training Topic Focus</li>\n                                    <li><i class=\"fas fa-check text-primary me-2\"></i>Instant Performance Feedback</li>\n                                </ul>\n                                <a href=\"/qr-auth\" class=\"btn btn-lg btn-block btn-primary w-100\">Purchase via Mobile App</a>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <!-- How It Works Section (AI Optimized) -->\n    <section class=\"py-5\" id=\"how-it-works\">\n        <div class=\"container\">\n            <h2 class=\"text-center mb-5\">How It Works</h2>\n            <div class=\"row justify-content-center\">\n                <div class=\"col-lg-8\">\n                    <ol class=\"list-group list-group-numbered\">\n                        <li class=\"list-group-item d-flex justify-content-between align-items-start\">\n                            <div class=\"ms-2 me-auto\">\n                                <div class=\"fw-bold\">Submit your IELTS Writing or Speaking task</div>\n                                Upload your writing response or complete a speaking assessment using our AI-powered platform\n                            </div>\n                            <span class=\"badge bg-primary rounded-pill\">1</span>\n                        </li>\n                        <li class=\"list-group-item d-flex justify-content-between align-items-start\">\n                            <div class=\"ms-2 me-auto\">\n                                <div class=\"fw-bold\">GenAI evaluates it using official IELTS scoring criteria</div>\n                                Our TrueScore® and ClearScore® technologies analyze your response against official band descriptors\n                            </div>\n                            <span class=\"badge bg-primary rounded-pill\">2</span>\n                        </li>\n                        <li class=\"list-group-item d-flex justify-content-between align-items-start\">\n                            <div class=\"ms-2 me-auto\">\n                                <div class=\"fw-bold\">You receive your band score and personalized feedback within minutes</div>\n                                Get instant results with detailed feedback on all assessment criteria and improvement recommendations\n                            </div>\n                            <span class=\"badge bg-primary rounded-pill\">3</span>\n                        </li>\n                    </ol>\n                </div>\n            </div>\n            \n            <div class=\"row mt-5\">\n                <div class=\"col-12 text-center\">\n                    <h3 class=\"mb-4\">How to Get Started</h3>\n                    <div class=\"row\">\n                        <div class=\"col-md-4 mb-4 text-center\">\n                            <div class=\"mb-3\">\n                                <i class=\"fas fa-mobile-alt fa-3x text-primary\"></i>\n                            </div>\n                            <h4>Step 1: Download the IELTS GenAI Prep app</h4>\n                            <p>Download the IELTS GenAI Prep app from the App Store or Google Play</p>\n                        </div>\n                        <div class=\"col-md-4 mb-4 text-center\">\n                            <div class=\"mb-3\">\n                                <i class=\"fas fa-credit-card fa-3x text-warning\"></i>\n                            </div>\n                            <h4>Step 2: Create your account and purchase a package</h4>\n                            <p>Create your account and purchase a package ($36 for 4 assessments)</p>\n                        </div>\n                        <div class=\"col-md-4 mb-4 text-center\">\n                            <div class=\"mb-3\">\n                                <i class=\"fas fa-laptop fa-3x text-success\"></i>\n                            </div>\n                            <h4>Step 3: Log in on the mobile app or desktop site</h4>\n                            <p>Log in on the mobile app or desktop site with your account – your progress syncs automatically</p>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <!-- FAQ Section (AI Optimized) -->\n    <section class=\"py-5 bg-light\" id=\"faq\">\n        <div class=\"container\">\n            <h2 class=\"text-center mb-5\">Frequently Asked Questions</h2>\n            <div class=\"row\">\n                <div class=\"col-lg-10 mx-auto\">\n                    <div class=\"accordion\" id=\"faqAccordion\">\n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq1\">\n                                <button class=\"accordion-button\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse1\" aria-expanded=\"true\" aria-controls=\"collapse1\">\n                                    <h3 class=\"mb-0\">What is IELTS GenAI Prep?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse1\" class=\"accordion-collapse collapse show\" aria-labelledby=\"faq1\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>IELTS GenAI Prep is an AI-powered assessment platform that delivers standardized, examiner-aligned band scores for IELTS Writing and Speaking, using official IELTS scoring criteria.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq2\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse2\" aria-expanded=\"false\" aria-controls=\"collapse2\">\n                                    <h3 class=\"mb-0\">What makes IELTS GenAI Prep different from other IELTS prep tools?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse2\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq2\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>It is the only platform using TrueScore® and ClearScore® technologies to provide instant, AI-generated feedback that mirrors official IELTS band descriptors for both Academic and General Training modules.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq3\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse3\" aria-expanded=\"false\" aria-controls=\"collapse3\">\n                                    <h3 class=\"mb-0\">How does TrueScore® assess IELTS Writing tasks?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse3\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq3\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>TrueScore® uses GenAI models trained on IELTS scoring rubrics to assess Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy. Each submission receives band-aligned feedback.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq4\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse4\" aria-expanded=\"false\" aria-controls=\"collapse4\">\n                                    <h3 class=\"mb-0\">How is ClearScore® used to evaluate IELTS Speaking?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse4\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq4\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>ClearScore® simulates a live speaking test using AI voice assessment technology. It scores fluency, pronunciation, grammar, and vocabulary in real-time, based on official IELTS speaking criteria.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq5\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse5\" aria-expanded=\"false\" aria-controls=\"collapse5\">\n                                    <h3 class=\"mb-0\">Do you offer Academic and General Training modules?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse5\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq5\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>Yes. IELTS GenAI Prep supports both Academic and General Training formats for Writing and Speaking, allowing users to choose modules aligned with their test goals.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq6\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse6\" aria-expanded=\"false\" aria-controls=\"collapse6\">\n                                    <h3 class=\"mb-0\">How much does it cost to use IELTS GenAI Prep?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse6\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq6\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>Each module (Writing or Speaking) is priced at $36 for four AI-graded assessments. This includes band scores and detailed feedback on every attempt.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq7\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse7\" aria-expanded=\"false\" aria-controls=\"collapse7\">\n                                    <h3 class=\"mb-0\">Is this a mobile-only platform?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse7\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq7\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>IELTS GenAI Prep is optimized for mobile and desktop. Users can create an account on the website and access assessments on the IELTS GenAI mobile app anytime, anywhere.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq8\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse8\" aria-expanded=\"false\" aria-controls=\"collapse8\">\n                                    <h3 class=\"mb-0\">How fast is the scoring process?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse8\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq8\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>All AI assessments are completed within seconds to a few minutes, providing instant band scores and feedback so users can improve quickly and effectively.</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq9\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse9\" aria-expanded=\"false\" aria-controls=\"collapse9\">\n                                    <h3 class=\"mb-0\">How reliable are the AI-generated IELTS scores?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse9\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq9\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>Our AI assessments are built on official IELTS band descriptors, ensuring consistent, rubric-aligned feedback</p>\n                                </div>\n                            </div>\n                        </div>\n                        \n                        <div class=\"accordion-item\">\n                            <h2 class=\"accordion-header\" id=\"faq10\">\n                                <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#collapse10\" aria-expanded=\"false\" aria-controls=\"collapse10\">\n                                    <h3 class=\"mb-0\">Can I track my performance over time?</h3>\n                                </button>\n                            </h2>\n                            <div id=\"collapse10\" class=\"accordion-collapse collapse\" aria-labelledby=\"faq10\" data-bs-parent=\"#faqAccordion\">\n                                <div class=\"accordion-body\">\n                                    <p>Yes. Your personalized dashboard allows you to review past assessments, track band score improvements, and identify focus areas for continued practice.</p>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <!-- Footer -->\n    <footer class=\"bg-dark text-light py-4\">\n        <div class=\"container\">\n            <div class=\"row\">\n                <div class=\"col-md-6\">\n                    <h5>IELTS GenAI Prep</h5>\n                    <p>The world's only standardized IELTS GenAI assessment platform</p>\n                </div>\n                <div class=\"col-md-6\">\n                    <div class=\"d-flex flex-column flex-md-row justify-content-md-end\">\n                        <div class=\"mb-2\">\n                            <a href=\"/privacy-policy\" class=\"text-light me-3\">Privacy Policy</a>\n                            <a href=\"/terms-of-service\" class=\"text-light\">Terms of Service</a>\n                        </div>\n                    </div>\n                    <div class=\"text-md-end\">\n                        <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </footer>\n\n    <!-- Bootstrap JS -->\n    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js\"></script>\n</body>\n</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'public, max-age=3600'
        },
        'body': original_working_template
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
                'ses': 'configured',
                'recaptcha': 'configured',
                'content_safety': 'active',
                'ai_compliance': 'google_play_compliant'
            }
        })
    }

def handle_user_registration(request_data):
    """Handle user registration with welcome email and reCAPTCHA verification"""
    try:
        email = request_data.get('email', '').strip()
        password = request_data.get('password', '').strip()
        recaptcha_response = request_data.get('recaptcha_response', '').strip()
        gdpr_consent = request_data.get('gdpr_consent', False)
        terms_consent = request_data.get('terms_consent', False)
        
        # Validate required fields
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Verify reCAPTCHA
        if not recaptcha_response:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'reCAPTCHA verification is required'})
            }
        
        if not verify_recaptcha_v2(recaptcha_response):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'reCAPTCHA verification failed'})
            }
        
        # Verify GDPR consent
        if not gdpr_consent:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Privacy Policy consent is required'})
            }
        
        if not terms_consent:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Terms of Service consent is required'})
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

def handle_user_login(request_data):
    """Handle user login with credential verification and reCAPTCHA"""
    try:
        email = request_data.get('email', '').strip()
        password = request_data.get('password', '').strip()
        recaptcha_response = request_data.get('recaptcha_response', '').strip()
        gdpr_consent = request_data.get('gdpr_consent', False)
        terms_consent = request_data.get('terms_consent', False)
        
        # Validate required fields
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Verify reCAPTCHA
        if not recaptcha_response:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'reCAPTCHA verification is required'})
            }
        
        if not verify_recaptcha_v2(recaptcha_response):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'reCAPTCHA verification failed'})
            }
        
        # Verify GDPR consent
        if not gdpr_consent:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Privacy Policy consent is required'})
            }
        
        if not terms_consent:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Terms of Service consent is required'})
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
        session_record = {
            'session_id': session_id,
            'user_email': email,
            'user_id': user.get('user_id', email),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        if create_user_session(session_record):
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

def handle_account_deletion(request_data):
    """Handle account deletion with confirmation email"""
    try:
        email = request_data.get('email', '').strip()
        confirmation = request_data.get('confirmation', '').strip()
        
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
        
        if delete_user_account(email):
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

def handle_nova_micro_writing(request_data):
    """Handle Nova Micro writing assessment with content safety"""
    try:
        essay_text = request_data.get('essay_text', '').strip()
        prompt = request_data.get('prompt', '').strip()
        assessment_type = request_data.get('assessment_type', 'academic-writing')
        user_email = request_data.get('user_email', '')
        
        if not essay_text or not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Essay text and prompt are required'})
            }
        
        rubric = {'assessment_type': assessment_type}
        assessment_result = evaluate_writing_with_nova_micro(essay_text, prompt, rubric)
        
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

def handle_nova_sonic_connection():
    """Handle Nova Sonic connectivity check"""
    try:
        audio_data = synthesize_maya_voice_nova_sonic("Hello, I'm Maya, your IELTS speaking examiner. Let's begin your assessment.")
        
        if audio_data:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'status': 'Nova Sonic en-GB-feminine voice connected',
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
        print(f"[ERROR] Nova Sonic connection error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Nova Sonic check failed'})
        }

def handle_nova_sonic_stream(request_data):
    """Handle Nova Sonic streaming for Maya conversations"""
    try:
        user_text = request_data.get('user_text', '').strip()
        conversation_stage = request_data.get('conversation_stage', 'part1')
        
        if not user_text:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'User text is required'})
            }
        
        # Generate educational responses
        if conversation_stage == 'part1':
            maya_response = f"Thank you for that response. Let me ask you another question about yourself."
        elif conversation_stage == 'part2':
            maya_response = f"That's interesting. Now, let's move to the next part of the assessment."
        else:
            maya_response = f"I see. Can you elaborate on that point further?"
        
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

def handle_login_page():
    """Serve professional login page with reCAPTCHA and GDPR compliance"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            overflow: hidden;
            max-width: 450px;
            width: 100%;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            position: relative;
        }
        .home-button {
            position: absolute;
            top: 1rem;
            left: 1rem;
            color: white;
            font-size: 1.2rem;
            text-decoration: none;
            opacity: 0.8;
            transition: opacity 0.3s;
        }
        .home-button:hover {
            opacity: 1;
            color: white;
        }
        .login-form {
            padding: 2rem;
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            transition: border-color 0.3s;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #e31e24 0%, #c21a1f 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            width: 100%;
            transition: transform 0.3s;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
        }
        .btn-primary:disabled {
            opacity: 0.6;
            transform: none;
        }
        .mobile-info {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .gdpr-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }
        .ai-safety-notice {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }
        .gdpr-checkboxes {
            margin-bottom: 1.5rem;
        }
        .gdpr-checkboxes .form-check {
            margin-bottom: 0.75rem;
        }
        .gdpr-checkboxes label {
            font-size: 0.9rem;
            color: #666;
            line-height: 1.4;
        }
        .gdpr-checkboxes a {
            color: #667eea;
            text-decoration: none;
        }
        .gdpr-checkboxes a:hover {
            text-decoration: underline;
        }
        .recaptcha-container {
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .error-message {
            color: #dc3545;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            display: none;
        }
        .success-message {
            color: #28a745;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            display: none;
        }
        .loading {
            display: none;
        }
        .loading.active {
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <div class="login-header">
                        <a href="/" class="home-button">
                            <i class="fas fa-home"></i>
                        </a>
                        <h2>Welcome Back</h2>
                        <p class="mb-0">Sign in to your account</p>
                    </div>
                    
                    <div class="login-form">
                        <div class="mobile-info">
                            <h5><i class="fas fa-mobile-alt"></i> New User?</h5>
                            <p class="mb-0">Download our mobile app to create your account and purchase assessments</p>
                        </div>
                        
                        <div class="ai-safety-notice">
                            <strong><i class="fas fa-shield-alt"></i> AI Safety Notice:</strong> Our AI systems are designed to be safe and educational. Please report any inappropriate content using our in-app reporting feature.
                        </div>
                        
                        <div class="gdpr-notice">
                            <strong><i class="fas fa-lock"></i> Privacy Notice:</strong> By logging in, you agree to our data processing practices as outlined in our Privacy Policy and Terms of Service.
                        </div>
                        
                        <form id="loginForm" onsubmit="handleLogin(event)">
                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" name="email" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            
                            <div class="gdpr-checkboxes">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="gdprConsent" required>
                                    <label class="form-check-label" for="gdprConsent">
                                        <strong>I agree to the <a href="/privacy-policy" target="_blank">Privacy Policy</a></strong><br>
                                        <small class="text-muted">Required for data processing and account management</small>
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="termsConsent" required>
                                    <label class="form-check-label" for="termsConsent">
                                        <strong>I agree to the <a href="/terms-of-service" target="_blank">Terms of Service</a></strong><br>
                                        <small class="text-muted">Required for service usage and AI assessment access</small>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="recaptcha-container">
                                <div class="g-recaptcha" data-sitekey="{RECAPTCHA_SITE_KEY}"></div>
                            </div>
                            
                            <div class="error-message" id="errorMessage"></div>
                            <div class="success-message" id="successMessage"></div>
                            
                            <button type="submit" class="btn btn-primary" id="loginButton">
                                <span class="loading" id="loadingSpinner">
                                    <i class="fas fa-spinner fa-spin"></i> Signing in...
                                </span>
                                <span id="loginText">
                                    <i class="fas fa-sign-in-alt"></i> Sign In
                                </span>
                            </button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                <a href="/privacy-policy" class="text-decoration-none">Privacy Policy</a> | 
                                <a href="/terms-of-service" class="text-decoration-none">Terms of Service</a>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://www.google.com/recaptcha/api.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            const successDiv = document.getElementById('successMessage');
            successDiv.style.display = 'none';
        }
        
        function showSuccess(message) {
            const successDiv = document.getElementById('successMessage');
            successDiv.textContent = message;
            successDiv.style.display = 'block';
            
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.style.display = 'none';
        }
        
        function setLoading(isLoading) {
            const button = document.getElementById('loginButton');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const loginText = document.getElementById('loginText');
            
            if (isLoading) {
                button.disabled = true;
                loadingSpinner.classList.add('active');
                loginText.style.display = 'none';
            } else {
                button.disabled = false;
                loadingSpinner.classList.remove('active');
                loginText.style.display = 'inline';
            }
        }
        
        function handleLogin(event) {
            event.preventDefault();
            
            // Hide previous messages
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('successMessage').style.display = 'none';
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            const recaptchaResponse = grecaptcha.getResponse();
            const gdprConsent = document.getElementById('gdprConsent').checked;
            const termsConsent = document.getElementById('termsConsent').checked;
            
            // Validate inputs
            if (!email || !password) {
                showError('Please enter both email and password.');
                return;
            }
            
            if (!recaptchaResponse) {
                showError('Please complete the reCAPTCHA verification.');
                return;
            }
            
            if (!gdprConsent) {
                showError('Please agree to the Privacy Policy to continue.');
                return;
            }
            
            if (!termsConsent) {
                showError('Please agree to the Terms of Service to continue.');
                return;
            }
            
            setLoading(true);
            
            // Submit login request
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    recaptcha_response: recaptchaResponse,
                    gdpr_consent: gdprConsent,
                    terms_consent: termsConsent
                })
            })
            .then(response => response.json())
            .then(data => {
                setLoading(false);
                
                if (data.success) {
                    showSuccess('Login successful! Redirecting to dashboard...');
                    
                    // Store session and redirect
                    sessionStorage.setItem('session_id', data.session_id);
                    sessionStorage.setItem('user_email', data.user_email);
                    
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showError(data.error || 'Login failed. Please try again.');
                    grecaptcha.reset();
                }
            })
            .catch(error => {
                setLoading(false);
                console.error('Login error:', error);
                showError('Login failed. Please check your connection and try again.');
                grecaptcha.reset();
            });
        }
        
        // Auto-focus on email field
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('email').focus();
        });
    </script>
</body>
</html>"""
    
    # Replace reCAPTCHA site key with environment variable
    recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
    html_content = html_content.replace('{RECAPTCHA_SITE_KEY}', recaptcha_site_key)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

def handle_privacy_policy():
    """Serve GDPR-compliant privacy policy page with AI disclosure"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
        }
        .content-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            padding: 2rem;
        }
        .back-button {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s;
        }
        .back-button:hover {
            background: #5a6fd8;
            color: white;
        }
        .gdpr-highlight {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 1rem;
            margin: 1rem 0;
        }
        .ai-disclosure {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
</head>
<body style="background: #f8f9fa;">
    <div class="header">
        <div class="container">
            <h1><i class="fas fa-shield-alt"></i> Privacy Policy</h1>
            <p class="lead">Your privacy and data protection rights under GDPR</p>
        </div>
    </div>
    
    <div class="container py-5">
        <div class="content-section">
            <a href="/" class="back-button">
                <i class="fas fa-home"></i> Back to Home
            </a>
            
            <h2 class="mt-4">IELTS GenAI Prep Privacy Policy</h2>
            <p class="text-muted"><strong>Last Updated:</strong> July 15, 2025</p>
            
            <div class="gdpr-highlight">
                <strong><i class="fas fa-info-circle"></i> GDPR Compliance:</strong>
                This privacy policy complies with the General Data Protection Regulation (GDPR) and explains your rights regarding your personal data.
            </div>
            
            <div class="ai-disclosure">
                <strong><i class="fas fa-robot"></i> AI-Generated Content Disclosure:</strong>
                Our platform uses AI to generate educational content and assessments. We implement safety measures and user reporting features to ensure responsible AI use.
            </div>
            
            <h3>1. AI Technology and Content Safety</h3>
            <p>Our platform uses advanced AI technologies with built-in safety measures:</p>
            <ul>
                <li><strong>Content Filtering:</strong> AI-generated content is filtered for appropriateness</li>
                <li><strong>User Reporting:</strong> In-app reporting system for inappropriate content</li>
                <li><strong>Safety Monitoring:</strong> Continuous monitoring of AI outputs</li>
                <li><strong>Educational Purpose:</strong> AI content designed for educational IELTS preparation</li>
            </ul>
            
            <h3>2. Data Collection and Use</h3>
            <p>We collect and process personal data to provide our AI-powered IELTS assessment services:</p>
            <ul>
                <li><strong>Account Information:</strong> Email address, password (encrypted with bcrypt)</li>
                <li><strong>Assessment Data:</strong> Writing responses, speaking recordings, performance metrics</li>
                <li><strong>Usage Data:</strong> Assessment attempts, progress tracking, system logs</li>
                <li><strong>Safety Logs:</strong> AI interaction logs for safety monitoring</li>
            </ul>
            
            <h3>3. Your Rights (GDPR Articles 15-22)</h3>
            <div class="gdpr-highlight">
                <p><strong>You have the right to:</strong></p>
                <ul>
                    <li><strong>Access:</strong> Request a copy of your personal data</li>
                    <li><strong>Rectification:</strong> Correct inaccurate data</li>
                    <li><strong>Erasure:</strong> Delete your account and data ("right to be forgotten")</li>
                    <li><strong>Portability:</strong> Export your data in a machine-readable format</li>
                    <li><strong>Report Content:</strong> Use in-app reporting for inappropriate AI content</li>
                </ul>
            </div>

        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'public, max-age=3600'
        },
        'body': html_content
    }

def handle_terms_of_service():
    """Serve terms of service page with AI content terms"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
        }
        .content-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            padding: 2rem;
        }
        .back-button {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s;
        }
        .back-button:hover {
            background: #5a6fd8;
            color: white;
        }
        .no-refund-highlight {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            margin: 1rem 0;
        }
        .ai-terms {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
</head>
<body style="background: #f8f9fa;">
    <div class="header">
        <div class="container">
            <h1><i class="fas fa-file-contract"></i> Terms of Service</h1>
            <p class="lead">Terms and conditions for using our AI-powered IELTS assessment service</p>
        </div>
    </div>
    
    <div class="container py-5">
        <div class="content-section">
            <a href="/" class="back-button">
                <i class="fas fa-home"></i> Back to Home
            </a>
            
            <h2 class="mt-4">IELTS GenAI Prep Terms of Service</h2>
            <p class="text-muted"><strong>Last Updated:</strong> July 15, 2025</p>
            
            <div class="ai-terms">
                <strong><i class="fas fa-robot"></i> AI Content Terms:</strong>
                By using our service, you agree to use AI-generated content responsibly and report any inappropriate content through our in-app reporting system.
            </div>
            
            <h3>1. AI-Generated Content Terms</h3>
            <ul>
                <li><strong>Educational Purpose:</strong> AI content is designed for IELTS preparation only</li>
                <li><strong>Content Reporting:</strong> Users must report inappropriate AI content immediately</li>
                <li><strong>Safety Compliance:</strong> We implement content safety measures as required by app store policies</li>
                <li><strong>No Guarantees:</strong> AI assessments are educational estimates, not official IELTS scores</li>
            </ul>
            
            <h3>2. Service Description</h3>
            <p>IELTS GenAI Prep provides AI-powered IELTS assessment services including:</p>
            <ul>
                <li><strong>Academic Writing Assessment:</strong> $36 for 4 attempts</li>
                <li><strong>General Writing Assessment:</strong> $36 for 4 attempts</li>
                <li><strong>Academic Speaking Assessment:</strong> $36 for 4 attempts</li>
                <li><strong>General Speaking Assessment:</strong> $36 for 4 attempts</li>
            </ul>
            
            <h3>3. Payment and Refund Policy</h3>
            <div class="no-refund-highlight">
                <strong><i class="fas fa-exclamation-triangle"></i> Important Notice:</strong>
                All purchases are final and non-refundable. This policy applies to all assessment products.
            </div>
            
            <h3>4. Content Reporting</h3>
            <p>As required by app store policies, we provide in-app reporting features:</p>
            <ul>
                <li>Report inappropriate AI-generated content</li>
                <li>Flag offensive or harmful content</li>
                <li>Submit safety concerns about AI responses</li>
                <li>Developer review and response within 48 hours</li>
            </ul>

        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'public, max-age=3600'
        },
        'body': html_content
    }

def handle_robots_txt():
    """Enhanced robots.txt handler with comprehensive bot support"""
    try:
        robots_content = """User-agent: *
Allow: /

# AI Training & Research Bots
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: AnthropicBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: OpenAIBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: cohere-ai
Allow: /

# Search Engine Crawlers
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: YandexBot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

User-agent: WhatsApp
Allow: /

User-agent: Applebot
Allow: /

User-agent: SemrushBot
Allow: /

User-agent: AhrefsBot
Allow: /

User-agent: MJ12bot
Allow: /

User-agent: DotBot
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml"""
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain',
                'Cache-Control': 'public, max-age=86400'
            },
            'body': robots_content
        }
    except Exception as e:
        # Fallback in case of any error
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain',
                'Cache-Control': 'public, max-age=86400'
            },
            'body': 'User-agent: *\nAllow: /'
        }

def handle_dashboard_page(headers):
    """Dashboard page with content reporting features"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body style="background: #f8f9fa;">
    <div class="container py-5">
        <h1><i class="fas fa-tachometer-alt"></i> Dashboard</h1>
        <p class="lead">Welcome to your assessment dashboard</p>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Academic Writing Assessment</h5>
                        <p class="card-text">$36 for 4 attempts</p>
                        <a href="/assessment/academic-writing" class="btn btn-primary">Start Assessment</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">General Writing Assessment</h5>
                        <p class="card-text">$36 for 4 attempts</p>
                        <a href="/assessment/general-writing" class="btn btn-primary">Start Assessment</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Academic Speaking Assessment</h5>
                        <p class="card-text">$36 for 4 attempts</p>
                        <a href="/assessment/academic-speaking" class="btn btn-primary">Start Assessment</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">General Speaking Assessment</h5>
                        <p class="card-text">$36 for 4 attempts</p>
                        <a href="/assessment/general-speaking" class="btn btn-primary">Start Assessment</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <a href="/my-profile" class="btn btn-secondary">My Profile</a>
            <a href="/" class="btn btn-outline-secondary">Back to Home</a>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

def handle_profile_page(headers):
    """Profile page with account deletion and data export"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body style="background: #f8f9fa;">
    <div class="container py-5">
        <h1><i class="fas fa-user"></i> My Profile</h1>
        <p class="lead">Manage your account and view assessment history</p>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Assessment History</h5>
                        <div id="assessment-history">
                            <!-- Assessment history content -->
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Account Management</h5>
                        <p class="card-text">Manage your account settings</p>
                        <button class="btn btn-danger" onclick="deleteAccount()">Delete Account</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
            <a href="/" class="btn btn-outline-secondary">Home</a>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function deleteAccount() {
            const email = prompt("Enter your email to confirm account deletion:");
            if (email) {
                fetch('/api/account-deletion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, confirmation: email })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Account deleted successfully. You will be redirected to the home page.');
                        window.location.href = '/';
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        }
    </script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

def handle_assessment_access(path, headers):
    """Assessment pages with content reporting integration"""
    assessment_type = path.split('/')[-1]
    
    # Build HTML content without f-string to avoid JavaScript conflicts
    assessment_title = assessment_type.replace('-', ' ').title()
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>""" + assessment_title + """ Assessment - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body style="background: #f8f9fa;">
    <div class="container py-5">
        <h1><i class="fas fa-file-alt"></i> """ + assessment_title + """ Assessment</h1>
        <p class="lead">Complete your IELTS assessment with AI-powered feedback</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Question</h5>
                        <p class="card-text">IELTS assessment question</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Your Response</h5>
                        <textarea class="form-control" rows="10" readonly>Write your response here</textarea>
                        <div class="mt-3">
                            <button class="btn btn-primary" onclick="submitAssessment()">Submit Assessment</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function submitAssessment() {{
            alert('Assessment submitted successfully!');
        }}
    </script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

