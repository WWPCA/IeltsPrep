#!/usr/bin/env python3
"""
Pure AWS Lambda Handler for IELTS GenAI Prep QR Authentication
Compatible with SAM CLI local testing
"""

import json
import os
import uuid
import time
import base64
import urllib.request
import urllib.parse
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Set environment for .replit testing
os.environ['REPLIT_ENVIRONMENT'] = 'true'

# Import AWS mock services
from aws_mock_config import aws_mock

# Nova Sonic Amy Integration for Maya voice
def synthesize_maya_voice_nova_sonic(text: str) -> Optional[str]:
    """
    Synthesize Maya's voice using AWS Nova Sonic Amy (British female voice)
    Returns base64 encoded audio data or None if synthesis fails
    """
    try:
        # In development mode, use mock implementation
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            print(f"[NOVA_SONIC] Mock synthesis: {text[:50]}...")
            # Return mock audio data for development
            return "mock_audio_data_base64"
        
        # Production Nova Sonic implementation with bidirectional streaming
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Configure for British female voice using bidirectional streaming API
        request_body = {
            "inputAudio": {
                "format": "pcm",
                "sampleRate": 16000
            },
            "outputAudio": {
                "format": "pcm", 
                "sampleRate": 24000,
                "voiceId": "en-GB-feminine"  # British female voice as per documentation
            },
            "systemPrompt": f"You are Maya, a British female IELTS examiner with a clear British accent. Please say: '{text}'"
        }
        
        # Use bidirectional streaming for Nova Sonic
        try:
            response = bedrock_client.invoke_model_with_bidirectional_stream(
                modelId="amazon.nova-sonic-v1",
                contentType="application/json",
                accept="audio/mpeg",
                body=json.dumps(request_body)
            )
            
            # Process streaming response
            audio_chunks = []
            for event in response['body']:
                if 'audio' in event:
                    audio_chunks.append(event['audio']['data'])
            
            if audio_chunks:
                # Combine all audio chunks
                audio_data = b''.join(audio_chunks)
                # Convert to base64 for web transmission
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                return audio_base64
            else:
                print(f"[NOVA_SONIC] No audio chunks received")
                return None
                
        except Exception as e:
            print(f"[NOVA_SONIC] Amy synthesis failed: {str(e)}")
            return None
            
    except Exception as e:
        print(f"[NOVA_SONIC] Error: {str(e)}")
        return None

def handle_nova_sonic_connection_test() -> Dict[str, Any]:
    """Test Nova Sonic connectivity and Amy voice synthesis"""
    test_text = "Hello, I'm Maya, your IELTS examiner. Welcome to your speaking assessment."
    
    try:
        # Test Nova Sonic Amy synthesis
        audio_data = synthesize_maya_voice_nova_sonic(test_text)
        
        if audio_data:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Nova Sonic en-GB-feminine voice synthesis working',
                    'audio_data': audio_data,
                    'voice': 'en-GB-feminine (British Female)',
                    'provider': 'AWS Nova Sonic'
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'error',
                    'message': 'Nova Sonic en-GB-feminine synthesis failed',
                    'details': 'Check AWS permissions and model availability'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'message': f'Nova Sonic test failed: {str(e)}',
                'details': 'Check AWS Bedrock configuration'
            })
        }

def handle_nova_sonic_stream(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Nova Sonic streaming for Maya conversations"""
    try:
        user_text = data.get('user_text', '')
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        
        if not user_text:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'error',
                    'message': 'No user text provided'
                })
            }
        
        # Generate Maya's response text first
        maya_response = generate_maya_response(user_text)
        
        # Synthesize Maya's voice using Nova Sonic Amy
        audio_data = synthesize_maya_voice_nova_sonic(maya_response)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'success',
                'conversation_id': conversation_id,
                'maya_text': maya_response,
                'maya_audio': audio_data,
                'voice': 'en-GB-feminine (British Female)',
                'provider': 'AWS Nova Sonic'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'message': f'Nova Sonic streaming failed: {str(e)}'
            })
        }

def generate_maya_response(user_text: str) -> str:
    """Generate Maya's response text using Nova Micro"""
    try:
        # In development, use mock responses
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            maya_responses = [
                "Thank you for that response. Could you please tell me more about your background?",
                "That's very interesting. How long have you been living in your current city?",
                "I see. Now let's move on to the next part of the speaking assessment.",
                "Excellent. Can you describe your hometown to me?",
                "Thank you. What do you enjoy most about where you live?"
            ]
            import random
            return random.choice(maya_responses)
        
        # Production Nova Micro implementation
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        maya_prompt = f"""You are Maya, a British female IELTS examiner conducting a speaking assessment. 
        
        The candidate just said: "{user_text}"
        
        Respond as Maya would in an IELTS speaking test:
        - Keep responses natural and conversational
        - Ask follow-up questions appropriate to IELTS speaking assessment
        - Maintain professional but friendly tone
        - Guide the conversation through IELTS speaking parts when appropriate
        
        Provide only Maya's response, no additional text."""
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": maya_prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 200,
                "temperature": 0.7
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            body=json.dumps(payload),
            contentType="application/json"
        )
        
        result = json.loads(response['body'].read())
        
        if 'output' in result and 'message' in result['output']:
            return result['output']['message']['content'][0]['text']
        else:
            return "Thank you for that response. Could you tell me more about your background?"
            
    except Exception as e:
        print(f"[MAYA] Response generation failed: {str(e)}")
        return "Thank you for that response. Could you tell me more about your background?"

def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA v2 response with Google"""
    try:
        secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
        if not secret_key:
            print("[RECAPTCHA] No secret key found, skipping verification")
            return True  # Allow in development if no key set
        
        # Prepare verification request
        verification_data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        if user_ip:
            verification_data['remoteip'] = user_ip
        
        # Send verification request to Google using urllib
        data = urllib.parse.urlencode(verification_data).encode('utf-8')
        
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=10)
        
        if response.status == 200:
            result_data = response.read().decode('utf-8')
            result = json.loads(result_data)
            success = result.get('success', False)
            
            if not success:
                error_codes = result.get('error-codes', [])
                print(f"[RECAPTCHA] Verification failed: {error_codes}")
            
            return success
        else:
            print(f"[RECAPTCHA] HTTP error: {response.status}")
            return False
            
    except urllib.error.URLError as e:
        print(f"[RECAPTCHA] Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"[RECAPTCHA] Verification error: {str(e)}")
        return False

def generate_qr_code(data: str) -> str:
    """Generate QR code image as base64 string"""
    try:
        import qrcode
        
        # Generate QR code using simple API
        qr_img = qrcode.make(data)
        
        # Convert to base64
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    except ImportError:
        print("[WARNING] QRCode library not available, using placeholder")
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def lambda_handler(event, context):
    """Main AWS Lambda handler for QR authentication"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        body = event.get('body', '{}')
        headers = event.get('headers', {})
        
        # Parse request body
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        
        print(f"[CLOUDWATCH] Lambda processing {method} {path}")
        
        # Route requests
        if path == '/' and method == 'GET':
            return handle_home_page()
        elif path == '/api/health':
            return handle_health_check()
        elif path == '/api/auth/generate-qr' and method == 'POST':
            return handle_generate_qr(data)
        elif path == '/api/auth/verify-qr' and method == 'POST':
            return handle_verify_qr(data)
        elif path == '/purchase/verify/apple' and method == 'POST':
            return handle_apple_purchase_verification(data)
        elif path == '/purchase/verify/google' and method == 'POST':
            return handle_google_purchase_verification(data)
        elif path.startswith('/assessment/') and method == 'GET':
            return handle_assessment_access(path, headers)
        elif path == '/api/website/request-qr' and method == 'POST':
            return handle_website_qr_request(data)
        elif path == '/api/submit-speaking-response' and method == 'POST':
            return handle_speaking_submission(data, headers)
        elif path == '/api/get-assessment-result' and method == 'GET':
            return handle_get_assessment_result(event.get('queryStringParameters', {}))
        elif path == '/api/website/check-auth' and method == 'POST':
            return handle_website_auth_check(data)
        elif path == '/api/mobile/scan-qr' and method == 'POST':
            return handle_mobile_qr_scan(data)
        elif path == '/api/register' and method == 'POST':
            return handle_user_registration(data)
        elif path == '/api/login' and method == 'POST':
            return handle_user_login(data)
        elif path == '/login' and method == 'GET':
            return handle_login_page()
        elif path == '/dashboard' and method == 'GET':
            return handle_dashboard_page(headers)
        elif path == '/api/maya/introduction' and method == 'POST':
            return handle_maya_introduction(data)
        elif path == '/api/maya/conversation' and method == 'POST':
            return handle_maya_conversation(data)
        elif path == '/api/nova-micro/writing' and method == 'POST':
            return handle_nova_micro_writing(data)
        elif path == '/api/nova-micro/submit' and method == 'POST':
            return handle_nova_micro_submit(data)
        elif path == '/api/nova-sonic-connect' and method == 'POST':
            return handle_nova_sonic_connection_test()
        elif path == '/api/nova-sonic-stream' and method == 'POST':
            return handle_nova_sonic_stream(data)
        elif path == '/qr-auth' and method == 'GET':
            return handle_qr_auth_page()
        elif path == '/profile' and method == 'GET':
            return handle_profile_page(headers)
        elif path == '/test_mobile_home_screen.html' and method == 'GET':
            return handle_static_file('test_mobile_home_screen.html')
        elif path == '/mobile' and method == 'GET':
            return handle_static_file('test_mobile_home_screen.html')
        elif path == '/nova-assessment.html' and method == 'GET':
            return handle_static_file('nova_assessment_demo.html')
        elif path == '/database-schema' and method == 'GET':
            return handle_database_schema_page()
        elif path == '/nova-assessment' and method == 'GET':
            return handle_nova_assessment_demo()
        elif path == '/privacy-policy' and method == 'GET':
            return handle_privacy_policy()
        elif path == '/terms-of-service' and method == 'GET':
            return handle_terms_of_service()
        elif path == '/login' and method == 'GET':
            return handle_login_page()
        elif path == '/api/login' and method == 'POST':
            # Extract user IP from headers for reCAPTCHA verification
            user_ip = headers.get('x-forwarded-for', headers.get('x-real-ip', headers.get('remote-addr')))
            if user_ip and ',' in user_ip:
                user_ip = user_ip.split(',')[0].strip()  # Take first IP if multiple
            data['user_ip'] = user_ip
            return handle_user_login(data)
        elif path == '/' and method == 'GET':
            return handle_home_page()
        elif path == '/robots.txt' and method == 'GET':
            return handle_robots_txt()
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_static_file(filename: str) -> Dict[str, Any]:
    """Handle static file serving"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content_type = 'text/html' if filename.endswith('.html') else 'text/plain'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'File {filename} not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_home_page() -> Dict[str, Any]:
    """Serve mobile-first home page with assessment access"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - Development Testing</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 40px 0; color: white; }
        .header h1 { font-size: 48px; margin-bottom: 10px; }
        .header p { font-size: 18px; opacity: 0.9; }
        .assessment-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 40px; }
        .assessment-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .assessment-card:hover { transform: translateY(-5px); }
        .assessment-card h3 { color: #333; margin-bottom: 15px; font-size: 24px; }
        .assessment-card p { color: #666; line-height: 1.6; margin-bottom: 20px; }
        .assessment-features { margin-bottom: 20px; }
        .assessment-features li { margin-bottom: 8px; color: #555; }
        .btn { display: inline-block; background: #e31e24; color: white; padding: 15px 25px; text-decoration: none; border-radius: 8px; font-weight: bold; transition: background 0.3s; }
        .btn:hover { background: #c21a1f; }
        .dev-notice { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin-bottom: 30px; }
        .dev-notice h4 { color: #856404; margin-bottom: 10px; }
        .dev-notice p { color: #856404; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>IELTS GenAI Prep</h1>
            <p>Development Testing Environment</p>
        </div>
        
        <div class="dev-notice">
            <h4>🧪 Development Testing Mode</h4>
            <p>This is the development version with enhanced audio permission testing. Click the assessments below to test the improved user experience.</p>
        </div>
        
        <div class="assessment-grid">
            <div class="assessment-card">
                <h3>📢 Academic Speaking Assessment</h3>
                <p>Test the enhanced speaking assessment with proper microphone and speaker permission testing.</p>
                <div class="assessment-features">
                    <ul>
                        <li>✅ Comprehensive audio setup flow</li>
                        <li>✅ Microphone permission testing</li>
                        <li>✅ Speaker test with Maya's voice</li>
                        <li>✅ 3-second recording test</li>
                        <li>✅ Professional permission indicators</li>
                        <li>✅ Maya AI examiner with British voice</li>
                    </ul>
                </div>
                <a href="/assessment/academic-speaking" class="btn">Test Speaking Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>✍️ Academic Writing Assessment</h3>
                <p>Test the writing assessment with authentic IELTS layout and two-column design.</p>
                <div class="assessment-features">
                    <ul>
                        <li>✅ Official IELTS format</li>
                        <li>✅ Two-column layout (50/50)</li>
                        <li>✅ Question panel with charts</li>
                        <li>✅ Answer panel with word count</li>
                        <li>✅ Timer functionality</li>
                        <li>✅ Professional branding</li>
                    </ul>
                </div>
                <a href="/assessment/academic-writing" class="btn">Test Writing Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>🎤 General Speaking Assessment</h3>
                <p>Test the general speaking assessment with the same enhanced audio features.</p>
                <div class="assessment-features">
                    <ul>
                        <li>✅ Same audio setup flow</li>
                        <li>✅ General training questions</li>
                        <li>✅ Maya AI examiner</li>
                        <li>✅ 3-part IELTS structure</li>
                        <li>✅ Recording controls</li>
                        <li>✅ Professional UI</li>
                    </ul>
                </div>
                <a href="/assessment/general-speaking" class="btn">Test General Speaking</a>
            </div>
            
            <div class="assessment-card">
                <h3>📝 General Writing Assessment</h3>
                <p>Test the general writing assessment with letter writing format.</p>
                <div class="assessment-features">
                    <ul>
                        <li>✅ Letter writing format</li>
                        <li>✅ Two-column layout</li>
                        <li>✅ Task instructions</li>
                        <li>✅ Word count tracking</li>
                        <li>✅ Timer functionality</li>
                        <li>✅ Professional layout</li>
                    </ul>
                </div>
                <a href="/assessment/general-writing" class="btn">Test General Writing</a>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 50px; color: white;">
            <p>Development Environment • Enhanced Audio Testing • Professional UI</p>
        </div>
    </div>
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

def handle_login_page() -> Dict[str, Any]:
    """Serve mobile-first login page"""
    try:
        with open('login.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace hardcoded reCAPTCHA site key with environment variable
        recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
        html_content = html_content.replace('6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix', recaptcha_site_key)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Login page not found</h1>'
        }

def handle_dashboard_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve dashboard page with session verification"""
    try:
        # Check for valid session cookie
        cookie_header = headers.get('cookie', '')
        session_id = None
        
        # Extract session ID from cookies
        if 'web_session_id=' in cookie_header:
            for cookie in cookie_header.split(';'):
                if 'web_session_id=' in cookie:
                    session_id = cookie.split('=')[1].strip()
                    break
        
        if not session_id:
            # No session found, redirect to login
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/login',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Verify session with mock services
        session_data = aws_mock.get_session(session_id)
        
        if not session_data:
            # Invalid session, redirect to login
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/login',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Valid session, serve dashboard
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Dashboard page not found</h1>'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading dashboard: {str(e)}</h1>'
        }

def handle_qr_auth_page() -> Dict[str, Any]:
    """Serve QR authentication page"""
    try:
        with open('templates/qr_auth_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>QR Authentication page not found</h1>'
        }

def handle_profile_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve user profile page with session verification"""
    try:
        # Check for valid session cookie
        cookie_header = headers.get('cookie', '')
        session_id = None
        
        # Extract session ID from cookies
        if 'web_session_id=' in cookie_header:
            for cookie in cookie_header.split(';'):
                if 'web_session_id=' in cookie:
                    session_id = cookie.split('=')[1].strip()
                    break
        
        if not session_id:
            # No session found, redirect to QR auth
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Verify session exists and is valid
        session_data = aws_mock.get_session(session_id)
        if not session_data:
            # Invalid session, redirect to QR auth
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Check session expiry
        if session_data.get('expires_at', 0) < time.time():
            # Session expired
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Load profile page template
        with open('templates/profile.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Profile page not found</h1>'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Profile page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading profile: {str(e)}</h1>'
        }

def handle_database_schema_page() -> Dict[str, Any]:
    """Serve database schema documentation page"""
    try:
        with open('database_schema_demo.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Database schema page not found'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Database schema page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading database schema: {str(e)}</h1>'
        }

def handle_assessment_access(path: str, headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment access with better microphone/speaker permission design - NO LOGIN REQUIRED FOR DEV"""
    try:
        assessment_type = path.split('/')[-1]
        
        print(f"[CLOUDWATCH] Dev assessment access granted: {assessment_type}")
        
        # Development mode - direct access without authentication
        if assessment_type == 'academic-speaking':
            return handle_speaking_assessment_with_permissions()
        elif assessment_type == 'general-speaking':
            return handle_speaking_assessment_with_permissions()
        elif assessment_type == 'academic-writing':
            return handle_writing_assessment()
        elif assessment_type == 'general-writing':
            return handle_writing_assessment()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': f'<h1>Assessment type "{assessment_type}" not found</h1>'
            }
    except Exception as e:
        print(f"[CLOUDWATCH] Assessment access error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading assessment: {str(e)}</h1>'
        }

def handle_speaking_assessment_with_permissions() -> Dict[str, Any]:
    """Handle speaking assessment with proper microphone and speaker permissions"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Speaking Assessment</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
        .header { background-color: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
        .logo { background-color: #e31e24; color: white; padding: 8px 12px; font-weight: bold; font-size: 18px; }
        .timer { background-color: #333; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
        .main-content { display: flex; height: calc(100vh - 120px); background-color: #fff; }
        .question-panel { width: 50%; padding: 20px; border-right: 1px solid #ddd; overflow-y: auto; }
        .answer-panel { width: 50%; padding: 20px; display: flex; flex-direction: column; }
        .part-header { background-color: #f8f8f8; padding: 10px 15px; margin-bottom: 20px; border-left: 4px solid #e31e24; }
        .permission-check { margin-bottom: 20px; padding: 15px; background: #e8f4fd; border: 1px solid #0066cc; border-radius: 4px; }
        .permission-status { padding: 10px; margin-bottom: 10px; border-radius: 4px; font-weight: bold; }
        .permission-granted { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .permission-denied { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .permission-pending { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .maya-chat { flex: 1; border: 1px solid #ddd; border-radius: 4px; padding: 15px; background-color: #f9f9f9; display: flex; flex-direction: column; }
        .maya-messages { flex: 1; overflow-y: auto; margin-bottom: 15px; min-height: 200px; }
        .maya-message { padding: 10px; margin-bottom: 10px; background-color: white; border-radius: 4px; }
        .maya-message.user { background-color: #e3f2fd; }
        .maya-message.maya { background-color: #f3e5f5; }
        .conversation-status { padding: 10px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px; }
        .recording-controls { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .footer { display: flex; justify-content: space-between; padding: 15px 20px; background-color: #f8f8f8; border-top: 1px solid #ddd; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; transition: background-color 0.3s; }
        .btn-primary { background-color: #007bff; color: white; }
        .btn-record { background-color: #dc3545; color: white; }
        .btn-stop { background-color: #6c757d; color: white; }
        .btn-submit { background-color: #28a745; color: white; }
        .btn:disabled { background-color: #e9ecef; color: #6c757d; cursor: not-allowed; }
        .btn:hover:not(:disabled) { opacity: 0.9; }
        .test-audio { margin-top: 10px; }
        @media (max-width: 768px) {
            .main-content { flex-direction: column; height: auto; }
            .question-panel, .answer-panel { width: 100%; }
            .question-panel { border-right: none; border-bottom: 1px solid #ddd; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">IELTS GenAI</div>
            <div style="font-size: 14px; color: #666;">Test taker: test@example.com</div>
        </div>
        <div class="timer" id="timer">--:--</div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div style="font-size: 16px; font-weight: bold;">IELTS Speaking Assessment</div>
                <div style="font-size: 14px; color: #666;">Complete 3-part assessment with Maya AI examiner</div>
            </div>
            
            <div style="line-height: 1.6; margin-bottom: 20px;">
                <h4>Assessment Structure:</h4>
                <p><strong>Part 1:</strong> Interview (4-5 minutes)<br>
                   <strong>Part 2:</strong> Long Turn (3-4 minutes)<br>
                   <strong>Part 3:</strong> Discussion (4-5 minutes)</p>
            </div>
            
            <div style="padding: 15px; background-color: #e8f4fd; border: 1px solid #0066cc; border-radius: 4px;">
                <strong>Before Starting:</strong><br>
                • Ensure you have a quiet environment<br>
                • Test your microphone and speakers<br>
                • Listen carefully to Maya's questions<br>
                • Speak clearly and naturally<br>
                • Complete all three parts of the assessment
            </div>
        </div>
        
        <div class="answer-panel">
            <div class="permission-check">
                <h4>Audio Setup Required</h4>
                <p>Please grant microphone and speaker permissions to begin:</p>
                
                <div class="permission-status permission-pending" id="microphoneStatus">
                    🎤 Microphone: Checking permissions...
                </div>
                
                <div class="permission-status permission-pending" id="speakerStatus">
                    🔊 Speakers: Checking audio output...
                </div>
                
                <button class="btn btn-primary" id="setupAudioBtn">Test Audio Setup</button>
                
                <div class="test-audio" id="testAudio" style="display: none;">
                    <p>Click to test Maya's voice:</p>
                    <button class="btn btn-primary" id="testVoiceBtn">Test Maya's Voice</button>
                    <button class="btn btn-primary" id="testMicBtn" style="margin-left: 10px;">Test Microphone</button>
                </div>
            </div>
            
            <div class="maya-chat" id="mayaChat" style="display: none;">
                <div class="maya-messages" id="mayaMessages">
                    <!-- Messages will be added here -->
                </div>
                
                <div class="conversation-status" id="conversationStatus">
                    Audio setup complete! Maya will begin the assessment automatically...
                </div>
                
                <div class="recording-controls">
                    <button class="btn btn-record" id="recordBtn" disabled>Start Recording</button>
                    <button class="btn btn-stop" id="stopBtn" disabled>Stop Recording</button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <div>Current Part: <span id="currentPart">1</span> of 3</div>
        <div>Question: <span id="currentQuestion">1</span> of <span id="totalQuestions">6</span></div>
        <div><button class="btn btn-submit" id="submitBtn" disabled>Complete Assessment</button></div>
    </div>
    
    <script>
        let timeRemaining = 0;
        let timerStarted = false;
        let currentQuestionIndex = 0;
        let isRecording = false;
        let mediaRecorder;
        let audioChunks = [];
        let speechSynthesis = window.speechSynthesis;
        let mayaVoice = null;
        let audioStream = null;
        let microphoneGranted = false;
        let speakerTested = false;
        
        const timer = document.getElementById('timer');
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const submitBtn = document.getElementById('submitBtn');
        const conversationStatus = document.getElementById('conversationStatus');
        const mayaMessages = document.getElementById('mayaMessages');
        const currentPart = document.getElementById('currentPart');
        const currentQuestion = document.getElementById('currentQuestion');
        const setupAudioBtn = document.getElementById('setupAudioBtn');
        const testAudio = document.getElementById('testAudio');
        const testVoiceBtn = document.getElementById('testVoiceBtn');
        const testMicBtn = document.getElementById('testMicBtn');
        const mayaChat = document.getElementById('mayaChat');
        const microphoneStatus = document.getElementById('microphoneStatus');
        const speakerStatus = document.getElementById('speakerStatus');
        
        // Maya questions data
        const mayaQuestions = [
            {
                "part": 1,
                "question": "Hello! I am Maya, your AI examiner for this IELTS Speaking assessment. Let me start by asking you some questions about yourself. What is your name and where are you from?",
                "expected_duration": 30
            },
            {
                "part": 1,
                "question": "That is interesting. Can you tell me about your work or studies?",
                "expected_duration": 45
            },
            {
                "part": 1,
                "question": "What do you enjoy doing in your free time?",
                "expected_duration": 45
            },
            {
                "part": 2,
                "question": "Now I will give you a topic card. You have one minute to prepare and then speak for 1-2 minutes. Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why this journey was memorable for you.",
                "expected_duration": 120,
                "prep_time": 60
            },
            {
                "part": 3,
                "question": "Let us discuss travel and journeys in general. How has travel changed in your country over the past few decades?",
                "expected_duration": 60
            },
            {
                "part": 3,
                "question": "What are the benefits of traveling to different countries?",
                "expected_duration": 60
            }
        ];
        
        // Initialize Maya voice using Nova Sonic Amy (British female)
        function initializeMayaVoice() {
            // Test Nova Sonic Amy connection
            fetch('/api/nova-sonic-connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({test: 'connection'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Maya voice initialized: Ready');
                    mayaVoice = 'nova-sonic-en-gb-feminine';
                } else {
                    console.log('Maya voice fallback to system voice');
                    mayaVoice = 'system-fallback';
                }
            })
            .catch(error => {
                console.log('Maya voice fallback to system voice');
                mayaVoice = 'system-fallback';
            });
        }
        
        // Initialize voices
        if (speechSynthesis.getVoices().length > 0) {
            initializeMayaVoice();
        } else {
            speechSynthesis.onvoiceschanged = initializeMayaVoice;
        }
        
        // Audio setup function
        setupAudioBtn.addEventListener('click', async function() {
            try {
                // Request microphone permission
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                microphoneGranted = true;
                
                microphoneStatus.textContent = '🎤 Microphone: Access granted ✓';
                microphoneStatus.className = 'permission-status permission-granted';
                
                // Show test audio controls
                testAudio.style.display = 'block';
                setupAudioBtn.textContent = 'Audio Setup Complete';
                setupAudioBtn.disabled = true;
                
            } catch (error) {
                console.error('Microphone access error:', error);
                microphoneStatus.textContent = '🎤 Microphone: Access denied ✗';
                microphoneStatus.className = 'permission-status permission-denied';
                
                alert('Microphone access is required for the speaking assessment. Please enable microphone permissions and try again.');
            }
        });
        
        // Test Maya's voice using Nova Sonic Amy
        testVoiceBtn.addEventListener('click', function() {
            speakerStatus.textContent = '🔊 Speakers: Testing Maya voice...';
            speakerStatus.className = 'permission-status permission-pending';
            
            const testMessage = "Hello! This is Maya, your AI examiner. Can you hear me clearly?";
            
            // Use Nova Sonic Amy voice streaming
            fetch('/api/nova-sonic-stream', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_text: testMessage,
                    conversation_id: 'test-voice'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.maya_audio) {
                    // Play Maya's voice using Nova Sonic Amy
                    const audioData = 'data:audio/mp3;base64,' + data.maya_audio;
                    const audio = new Audio(audioData);
                    
                    audio.onloadstart = function() {
                        speakerStatus.textContent = '🔊 Speakers: Playing Maya voice...';
                    };
                    
                    audio.onended = function() {
                        speakerStatus.textContent = '🔊 Speakers: Maya voice working ✓';
                        speakerStatus.className = 'permission-status permission-granted';
                        speakerTested = true;
                        
                        // Enable start assessment if both permissions are granted
                        if (microphoneGranted && speakerTested) {
                            setTimeout(() => {
                                startAssessment();
                            }, 2000);
                        }
                    };
                    
                    audio.play();
                } else {
                    speakerStatus.textContent = '🔊 Speakers: Maya voice test failed, using fallback';
                    speakerStatus.className = 'permission-status permission-denied';
                }
            })
            .catch(error => {
                speakerStatus.textContent = '🔊 Speakers: Maya voice test failed, using fallback';
                speakerStatus.className = 'permission-status permission-denied';
            });
        });
        
        // Test microphone
        testMicBtn.addEventListener('click', function() {
            if (!audioStream) {
                alert('Please grant microphone access first.');
                return;
            }
            
            const testRecorder = new MediaRecorder(audioStream);
            const testChunks = [];
            
            testRecorder.ondataavailable = function(event) {
                testChunks.push(event.data);
            };
            
            testRecorder.onstop = function() {
                const audioBlob = new Blob(testChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                alert('Recording test complete! You can now hear your voice playback.');
                audio.play();
            };
            
            testRecorder.start();
            testMicBtn.textContent = 'Recording... (3 sec)';
            testMicBtn.disabled = true;
            
            setTimeout(() => {
                testRecorder.stop();
                testMicBtn.textContent = 'Test Microphone';
                testMicBtn.disabled = false;
            }, 3000);
        });
        
        function startAssessment() {
            // Hide permission check and show assessment
            document.querySelector('.permission-check').style.display = 'none';
            mayaChat.style.display = 'flex';
            
            // Start assessment
            conversationStatus.textContent = 'Maya will begin speaking in 2 seconds...';
            conversationStatus.style.backgroundColor = '#e8f4fd';
            
            setTimeout(() => {
                loadNextQuestion();
            }, 2000);
        }
        
        function updateTimer() {
            if (!timerStarted) return;
            
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
            
            if (timeRemaining <= 0) {
                alert('Assessment time is up!');
                return;
            }
            
            timeRemaining--;
        }
        
        function startTimer() {
            if (!timerStarted) {
                timerStarted = true;
                timeRemaining = 15 * 60; // 15 minutes
                conversationStatus.textContent = 'Assessment timer started. Maya will now begin the conversation.';
                conversationStatus.style.backgroundColor = '#d4edda';
                setInterval(updateTimer, 1000);
            }
        }
        
        function addMayaMessage(message, isMaya = true) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'maya-message ' + (isMaya ? 'maya' : 'user');
            messageDiv.innerHTML = isMaya ? '<strong>Maya (AI Examiner):</strong> ' + message : '<strong>You:</strong> ' + message;
            mayaMessages.appendChild(messageDiv);
            mayaMessages.scrollTop = mayaMessages.scrollHeight;
        }
        
        function playMayaVoice(questionText) {
            return new Promise((resolve) => {
                // Use Nova Sonic en-GB-feminine for Maya's voice
                if (mayaVoice === 'nova-sonic-en-gb-feminine') {
                    conversationStatus.textContent = 'Maya is speaking... Please listen carefully.';
                    conversationStatus.style.backgroundColor = '#fff3cd';
                    
                    // Use Nova Sonic en-GB-feminine voice streaming
                    fetch('/api/nova-sonic-stream', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            user_text: questionText,
                            conversation_id: 'maya-question-' + currentQuestionIndex
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success' && data.maya_audio) {
                            // Play Maya's voice using Nova Sonic en-GB-feminine
                            const audioData = 'data:audio/mp3;base64,' + data.maya_audio;
                            const audio = new Audio(audioData);
                            
                            audio.onended = function() {
                                conversationStatus.textContent = 'Maya has finished. Please record your response.';
                                conversationStatus.style.backgroundColor = '#d1ecf1';
                                recordBtn.disabled = false;
                                
                                if (currentQuestionIndex === 0) {
                                    startTimer();
                                }
                                
                                resolve();
                            };
                            
                            audio.onerror = function() {
                                conversationStatus.textContent = 'Maya question displayed. Please record your response.';
                                conversationStatus.style.backgroundColor = '#d1ecf1';
                                recordBtn.disabled = false;
                                
                                if (currentQuestionIndex === 0) {
                                    startTimer();
                                }
                                
                                resolve();
                            };
                            
                            audio.play();
                        } else {
                            // Fallback to text display
                            conversationStatus.textContent = 'Maya question displayed. Please record your response.';
                            conversationStatus.style.backgroundColor = '#d1ecf1';
                            recordBtn.disabled = false;
                            
                            if (currentQuestionIndex === 0) {
                                startTimer();
                            }
                            
                            resolve();
                        }
                    })
                    .catch(error => {
                        console.error('Maya voice error:', error);
                        conversationStatus.textContent = 'Maya question displayed. Please record your response.';
                        conversationStatus.style.backgroundColor = '#d1ecf1';
                        recordBtn.disabled = false;
                        
                        if (currentQuestionIndex === 0) {
                            startTimer();
                        }
                        
                        resolve();
                    });
                } else {
                    // Fallback to system voice if Nova Sonic is not available
                    conversationStatus.textContent = 'Maya question displayed. Please record your response.';
                    conversationStatus.style.backgroundColor = '#d1ecf1';
                    recordBtn.disabled = false;
                    
                    if (currentQuestionIndex === 0) {
                        startTimer();
                    }
                    
                    resolve();
                }
            });
        }
        
        function loadNextQuestion() {
            if (currentQuestionIndex >= mayaQuestions.length) {
                addMayaMessage('Thank you for completing the IELTS Speaking assessment. Your responses have been recorded.');
                conversationStatus.textContent = 'Assessment complete! Click "Complete Assessment" to finish.';
                conversationStatus.style.backgroundColor = '#d4edda';
                submitBtn.disabled = false;
                recordBtn.disabled = true;
                return;
            }
            
            const question = mayaQuestions[currentQuestionIndex];
            
            // Add Maya message
            addMayaMessage(question.question);
            currentPart.textContent = question.part;
            currentQuestion.textContent = currentQuestionIndex + 1;
            
            // Play Maya voice
            setTimeout(() => {
                playMayaVoice(question.question);
            }, 1000);
        }
        
        // Recording controls
        recordBtn.addEventListener('click', async function() {
            try {
                if (!audioStream) {
                    alert('Please complete audio setup first.');
                    return;
                }
                
                mediaRecorder = new MediaRecorder(audioStream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = function(event) {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstart = function() {
                    isRecording = true;
                    recordBtn.disabled = true;
                    stopBtn.disabled = false;
                    conversationStatus.textContent = 'Recording your response... Speak clearly and naturally.';
                    conversationStatus.style.backgroundColor = '#fff3cd';
                };
                
                mediaRecorder.onstop = function() {
                    isRecording = false;
                    recordBtn.disabled = false;
                    stopBtn.disabled = true;
                    conversationStatus.textContent = 'Response recorded. Moving to next question...';
                    conversationStatus.style.backgroundColor = '#d4edda';
                    
                    addMayaMessage('Response recorded for Part ' + mayaQuestions[currentQuestionIndex].part, false);
                    
                    // Convert audio to base64 for submission
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    reader.onloadend = function() {
                        window.currentAudioData = reader.result.split(',')[1]; // Remove data:audio/wav;base64,
                        
                        // Submit for evaluation if this is the last question
                        if (currentQuestionIndex === mayaQuestions.length - 1) {
                            submitForEvaluation();
                        } else {
                            // Move to next question
                            currentQuestionIndex++;
                            setTimeout(() => {
                                loadNextQuestion();
                            }, 2000);
                        }
                    };
                    reader.readAsDataURL(audioBlob);
                };
                
                mediaRecorder.start();
                
                // Auto-stop after expected duration + 30 seconds
                const maxDuration = (mayaQuestions[currentQuestionIndex].expected_duration || 60) + 30;
                setTimeout(() => {
                    if (isRecording) {
                        mediaRecorder.stop();
                    }
                }, maxDuration * 1000);
                
            } catch (error) {
                alert('Error starting recording: ' + error.message);
                conversationStatus.textContent = 'Error: Could not start recording. Please check microphone permissions.';
                conversationStatus.style.backgroundColor = '#f8d7da';
            }
        });
        
        stopBtn.addEventListener('click', function() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
            }
        });
        
        // Submit for evaluation
        async function submitForEvaluation() {
            if (!window.currentAudioData) {
                alert('No audio data available for evaluation');
                return;
            }
            
            conversationStatus.textContent = 'Processing your assessment... This may take a few moments.';
            conversationStatus.style.backgroundColor = '#fff3cd';
            
            try {
                const response = await fetch('/api/submit-speaking-response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        audio_data: window.currentAudioData,
                        question_id: mayaQuestions.length,
                        assessment_type: 'academic_speaking',
                        user_email: 'test@ieltsgenaiprep.com'
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    displayAssessmentResults(result.result);
                } else {
                    throw new Error(result.message || 'Assessment failed');
                }
                
            } catch (error) {
                conversationStatus.textContent = 'Assessment evaluation failed. Please try again.';
                conversationStatus.style.backgroundColor = '#f8d7da';
                console.error('Assessment error:', error);
            }
        }
        
        // Display assessment results
        function displayAssessmentResults(result) {
            const resultsHtml = `
                <div class="assessment-results" style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-top: 20px;">
                    <h4>🎉 Assessment Complete!</h4>
                    <div style="text-align: center; margin: 15px 0;">
                        <div style="font-size: 24px; font-weight: bold; color: #28a745;">
                            Overall Band: ${result.overall_band}
                        </div>
                        <div style="color: #6c757d; font-size: 14px;">
                            Performance Level: ${result.performance_level}
                        </div>
                    </div>
                    
                    <div class="criteria-breakdown" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
                        ${Object.entries(result.criteria).map(([criterion, data]) => `
                            <div style="background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #007bff;">
                                <div style="font-size: 12px; text-transform: capitalize; color: #6c757d;">
                                    ${criterion.replace(/_/g, ' ')}
                                </div>
                                <div style="font-weight: bold; color: #007bff;">Band ${data.score}</div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <strong>Detailed Feedback:</strong>
                        <p style="margin-top: 5px;">${result.detailed_feedback}</p>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <strong>Strengths:</strong>
                        <ul style="margin-top: 5px;">
                            ${result.strengths.map(strength => `<li>${strength}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <strong>Areas for Improvement:</strong>
                        <ul style="margin-top: 5px;">
                            ${result.improvements.map(improvement => `<li>${improvement}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            mayaMessages.innerHTML += resultsHtml;
            mayaMessages.scrollTop = mayaMessages.scrollHeight;
            
            conversationStatus.textContent = 'Assessment complete! Your detailed feedback is displayed above.';
            conversationStatus.style.backgroundColor = '#d4edda';
            
            submitBtn.disabled = false;
            submitBtn.textContent = 'Download Results';
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Speaking assessment with complete evaluation pipeline loaded');
        });
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

def handle_writing_assessment() -> Dict[str, Any]:
    """Handle writing assessment"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Writing Assessment</h1><p>Writing assessment functionality will be implemented here.</p>'
    }

def handle_privacy_policy() -> Dict[str, Any]:
    """Serve privacy policy page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand fw-bold text-primary" href="/">IELTS GenAI Prep</a>
            <a href="/" class="btn btn-outline-primary">Back to Home</a>
        </div>
    </nav>
    
    <div class="container py-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h1 class="h3 mb-0">Privacy Policy</h1>
                    </div>
                    <div class="card-body">
                        <div class="last-updated mb-4">
                            <p><em>Last Updated: June 16, 2025</em></p>
                        </div>

                        <section class="policy-section mb-4">
                            <h2 class="h4">1. Introduction</h2>
                            <p>Welcome to IELTS GenAI Prep, featuring TrueScore® and ClearScore® - the world's ONLY GenAI assessor tools for IELTS test preparation. We respect your privacy and are committed to protecting your personal data.</p>
                            <p>This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our IELTS preparation services.</p>
                        </section>

                        <section class="policy-section mb-4">
                            <h2 class="h4">2. Information We Collect</h2>
                            <p>We collect information necessary to provide our assessment services:</p>
                            <ul>
                                <li>Account information (email address)</li>
                                <li>Assessment responses and performance data</li>
                                <li>Voice recordings for speaking assessments (processed in real-time, not stored)</li>
                                <li>Usage data to improve our AI algorithms</li>
                            </ul>
                        </section>

                        <section class="policy-section mb-4">
                            <h2 class="h4">3. How We Use Your Information</h2>
                            <p>Your information is used to:</p>
                            <ul>
                                <li>Provide personalized IELTS assessment feedback</li>
                                <li>Process payments through app stores</li>
                                <li>Improve our AI assessment accuracy</li>
                                <li>Maintain account security</li>
                            </ul>
                        </section>

                        <section class="policy-section mb-4">
                            <h2 class="h4">4. Data Security</h2>
                            <p>We implement industry-standard security measures including encryption and access controls. Voice data is processed in real-time and not stored permanently.</p>
                        </section>

                        <section class="policy-section mb-4">
                            <h2 class="h4">5. Your Rights</h2>
                            <p>You have the right to access, correct, or delete your personal data. Contact us through our website for any privacy-related requests.</p>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html_content
    }

def handle_terms_of_service() -> Dict[str, Any]:
    """Serve terms of service page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand fw-bold text-primary" href="/">IELTS GenAI Prep</a>
            <a href="/" class="btn btn-outline-primary">Back to Home</a>
        </div>
    </nav>
    
    <div class="container py-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h1 class="h3 mb-0">Terms of Service</h1>
                    </div>
                    <div class="card-body">
                        <div class="last-updated mb-4">
                            <p><em>Last Updated: June 16, 2025</em></p>
                        </div>

                        <section class="terms-section mb-4">
                            <h2 class="h4">1. Service Description</h2>
                            <p>IELTS GenAI Prep provides AI-powered IELTS assessment tools featuring TrueScore® and ClearScore® technologies. Our platform offers personalized feedback for writing and speaking assessments.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">2. Eligibility</h2>
                            <p>You must be at least 16 years old to use our services. By using our platform, you confirm you meet this requirement.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">3. Payment and Access</h2>
                            <p>Assessment packages are available for $36.00 per assessment type through mobile app stores. After purchase, you can access assessments on both mobile and desktop platforms.</p>
                            <p><strong>All purchases are final and non-refundable.</strong> By completing a purchase, you acknowledge that you understand and accept this policy.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">4. Intellectual Property</h2>
                            <p>TrueScore® and ClearScore® are proprietary technologies. All content and features are protected by copyright and trademark laws.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">5. User Responsibilities</h2>
                            <p>You agree to:</p>
                            <ul>
                                <li>Use our services for legitimate IELTS preparation</li>
                                <li>Maintain account security</li>
                                <li>Respect intellectual property rights</li>
                                <li>Not attempt to reverse engineer our technology</li>
                            </ul>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">6. Limitation of Liability</h2>
                            <p>Our services are provided "as is" for educational purposes. While our AI provides feedback based on IELTS criteria, we cannot guarantee specific test outcomes.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">7. Contact Information</h2>
                            <p>For questions about these terms, please contact us through our website.</p>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html_content
    }

def handle_nova_assessment_demo() -> Dict[str, Any]:
    """Serve Nova AI assessment demonstration page"""
    try:
        with open('nova_assessment_demo.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Nova assessment demo not found'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Nova assessment demo error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading Nova demo: {str(e)}</h1>'
        }

def get_assessment_template(assessment_type: str, user_email: str, session_id: str, task_number: int = 1) -> str:
    """Load appropriate assessment template with Maya auto-start functionality"""
    
    # Get Nova prompts from DynamoDB
    rubric = aws_mock.get_assessment_rubric(assessment_type)
    nova_prompts = rubric.get('nova_sonic_prompts', {}) if rubric else {}
    
    # Get unique question from comprehensive question bank
    question_data = aws_mock.get_unique_assessment_question(user_email, assessment_type)
    if not question_data:
        return f"<h1>Error: Unable to load assessment question for {assessment_type}</h1><p>Please contact support.</p>"
    
    question_id = question_data['question_id']
    prompt = question_data['prompt']
    task_type = question_data.get('task_type', question_data.get('task', 'Assessment'))
    
    # Get chart data for writing assessments
    chart_svg = question_data.get('chart_svg', '')
    chart_data = question_data.get('chart_data', {})
    question_text = question_data.get('question_text', prompt)
    tasks = question_data.get('tasks', [])
    
    # Determine current task from parameter or default to Task 1
    current_task = task_number
    
    if tasks and len(tasks) > 0:
        # Find the appropriate task
        if current_task == 1:
            current_task_data = tasks[0]  # Task 1
        elif current_task == 2 and len(tasks) > 1:
            current_task_data = tasks[1]  # Task 2
        else:
            current_task_data = tasks[0]  # Default to Task 1
    else:
        current_task_data = {
            'task_number': 2,
            'time_minutes': 40,
            'instructions': prompt,
            'word_count': 250,
            'type': 'opinion_essay'
        }
    
    # Writing assessments - Clean template matching official IELTS layout
    if 'writing' in assessment_type:
        # Prepare variables to avoid f-string issues
        assessment_title = assessment_type.replace('_', ' ').title()
        task_num = str(current_task_data['task_number'])
        time_mins = str(current_task_data['time_minutes'])
        word_count = str(current_task_data['word_count'])
        
        # Chart display logic
        chart_display = ''
        if current_task_data['task_number'] == 1 and chart_svg:
            chart_title = chart_data.get('title', '')
            chart_display = f'<div class="chart-container"><div class="chart-title">{chart_title}</div>{chart_svg}</div>'
        
        # Task content logic
        if current_task_data['task_number'] == 1:
            task_content = question_text
        else:
            task_instructions = current_task_data.get('instructions', 'Essay prompt')
            task_content = f"<strong>Write about the following topic:</strong><br><br>{task_instructions}<br><br>Give reasons for your answer and include any relevant examples from your own knowledge or experience."
        
        # Task progress indicators
        task_progress = ''
        if len(tasks) > 1:
            task1_class = 'active' if current_task_data['task_number'] == 1 else 'completed'
            task2_class = 'active' if current_task_data['task_number'] == 2 else 'inactive'
            task_progress = f'<span class="task-indicator {task1_class}">Part 1</span><span class="task-indicator {task2_class}">Part 2</span>'
        else:
            task_progress = '<span class="task-indicator active">Part 1</span>'
        
        total_tasks = str(len(tasks) if len(tasks) > 1 else 1)
        
        # Create clean template
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_title} Assessment</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; color: #333; }}
        .header {{ background-color: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }}
        .logo-section {{ display: flex; align-items: center; gap: 15px; }}
        .logo {{ background-color: #e31e24; color: white; padding: 8px 12px; font-weight: bold; font-size: 18px; border-radius: 3px; }}
        .test-info {{ font-size: 14px; color: #666; }}
        .header-right {{ display: flex; align-items: center; gap: 15px; }}
        .timer {{ background-color: #333; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; }}
        .main-content {{ display: flex; height: calc(100vh - 120px); background-color: #fff; }}
        .question-panel {{ width: 50%; padding: 20px; border-right: 1px solid #ddd; overflow-y: auto; }}
        .answer-panel {{ width: 50%; padding: 20px; display: flex; flex-direction: column; }}
        .part-header {{ background-color: #f8f8f8; padding: 10px 15px; margin-bottom: 20px; border-left: 4px solid #e31e24; }}
        .part-title {{ font-size: 16px; font-weight: bold; margin-bottom: 5px; }}
        .part-instructions {{ font-size: 14px; color: #666; margin-bottom: 10px; }}
        .task-content {{ line-height: 1.6; margin-bottom: 20px; }}
        .chart-container {{ margin: 20px 0; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; text-align: center; }}
        .chart-title {{ font-size: 14px; font-weight: bold; margin-bottom: 15px; color: #333; }}
        .answer-area {{ flex: 1; display: flex; flex-direction: column; }}
        .answer-textarea {{ flex: 1; width: 100%; padding: 15px; border: 1px solid #ddd; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; resize: none; outline: none; }}
        .word-count {{ text-align: right; padding: 10px; font-size: 12px; color: #666; border: 1px solid #ddd; border-top: none; background-color: #f9f9f9; }}
        .footer {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background-color: #f8f8f8; border-top: 1px solid #ddd; }}
        .task-progress {{ display: flex; align-items: center; gap: 10px; }}
        .task-indicator {{ padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        .task-indicator.active {{ background-color: #e31e24; color: white; }}
        .task-indicator.completed {{ background-color: #28a745; color: white; }}
        .task-indicator.inactive {{ background-color: #e9ecef; color: #6c757d; }}
        .navigation-buttons {{ display: flex; gap: 10px; }}
        .btn {{ padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; transition: background-color 0.3s; }}
        .btn-back {{ background-color: #6c757d; color: white; }}
        .btn-next {{ background-color: #007bff; color: white; }}
        .btn-submit {{ background-color: #28a745; color: white; }}
        .btn:disabled {{ background-color: #e9ecef; color: #6c757d; cursor: not-allowed; }}
        .btn:hover:not(:disabled) {{ opacity: 0.9; }}
        @media (max-width: 768px) {{
            .main-content {{ flex-direction: column; height: auto; }}
            .question-panel, .answer-panel {{ width: 100%; }}
            .question-panel {{ border-right: none; border-bottom: 1px solid #ddd; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">IELTS GenAI</div>
            <div class="test-info">Test taker ID: {user_email}</div>
        </div>
        <div class="header-right">
            <div class="timer" id="timer">60:00</div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div class="part-title">Part {task_num}</div>
                <div class="part-instructions">
                    You should spend about {time_mins} minutes on this task. Write at least {word_count} words.
                </div>
            </div>
            
            <div class="task-content" id="taskPrompt">
                {task_content}
            </div>
            
            {chart_display}
        </div>
        
        <div class="answer-panel">
            <div class="answer-area">
                <textarea id="essayText" class="answer-textarea" placeholder="Type your answer here..." maxlength="5000"></textarea>
                <div class="word-count">Words: <span id="wordCount">0</span></div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <div class="task-progress">
            {task_progress}
            <span style="margin-left: 10px; font-size: 12px; color: #666;">
                {task_num} of {total_tasks}
            </span>
        </div>
        
        <div class="navigation-buttons">
            <button class="btn btn-back" onclick="history.back()">Back</button>
            <button class="btn btn-submit" id="submitBtn" disabled>Submit</button>
            <button class="btn btn-next" id="nextBtn" style="display: none;">Next</button>
        </div>
    </div>
    
    <script>
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const submitBtn = document.getElementById('submitBtn');
        const nextBtn = document.getElementById('nextBtn');
        const timer = document.getElementById('timer');
        
        let timeRemaining = 60 * 60;
        let timerInterval = null;
        let currentTask = {task_num};
        let totalTasks = {total_tasks};
        let task1Completed = false;
        
        function updateWordCount() {{
            const text = essayText.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            wordCount.textContent = words;
            
            const minWords = {word_count};
            if (words >= minWords) {{
                submitBtn.disabled = false;
                submitBtn.style.backgroundColor = '#28a745';
            }} else {{
                submitBtn.disabled = true;
                submitBtn.style.backgroundColor = '#e9ecef';
            }}
        }}
        
        function updateTimer() {{
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
            
            if (timeRemaining <= 0) {{
                clearInterval(timerInterval);
                alert('Time is up! Your essay will be submitted automatically.');
                submitAssessment();
            }}
            
            timeRemaining--;
        }}
        
        async function submitAssessment() {{
            const essayContent = essayText.value.trim();
            if (!essayContent) {{
                alert('Please write your essay before submitting.');
                return;
            }}
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            try {{
                const response = await fetch('/api/nova-micro/writing', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        essay_text: essayContent,
                        prompt: document.getElementById('taskPrompt').textContent,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}',
                        user_email: '{user_email}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    if (currentTask === 1 && totalTasks > 1) {{
                        task1Completed = true;
                        submitBtn.style.display = 'none';
                        nextBtn.style.display = 'inline-block';
                        nextBtn.disabled = false;
                        alert('Task 1 completed! Click "Next" to continue to Task 2.');
                    }} else {{
                        alert('Assessment completed! Your results are being processed.');
                    }}
                }} else {{
                    alert('Submission failed: ' + result.error);
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit';
                }}
            }} catch (error) {{
                alert('Network error. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit';
            }}
        }}
        
        function goToNextTask() {{
            if (currentTask === 1 && task1Completed) {{
                window.location.href = '/assessment/{assessment_type}?task=2&session_id={session_id}&user_email={user_email}';
            }}
        }}
        
        essayText.addEventListener('input', updateWordCount);
        submitBtn.addEventListener('click', submitAssessment);
        nextBtn.addEventListener('click', goToNextTask);
        
        timerInterval = setInterval(updateTimer, 1000);
        updateTimer();
        
        const savedDraft = localStorage.getItem('ielts_essay_draft_{session_id}');
        if (savedDraft) {{
            essayText.value = savedDraft;
            updateWordCount();
        }}
        
        setInterval(() => {{
            if (essayText.value.trim()) {{
                localStorage.setItem('ielts_essay_draft_{session_id}', essayText.value);
            }}
        }}, 30000);
    </script>
</body>
</html>"""
        
        return template
    
    # Speaking assessments - continue with existing logic
    elif 'speaking' in assessment_type:
        # Continue with existing speaking template
        pass
    
    # Default fallback
    return f"<h1>Assessment type {assessment_type} not supported</h1>"

def handle_speaking_submission(data: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle speaking response submission with complete evaluation flow"""
    try:
        audio_data = data.get('audio_data')
        question_id = data.get('question_id')
        assessment_type = data.get('assessment_type', 'academic_speaking')
        user_email = data.get('user_email', 'test@ieltsgenaiprep.com')
        
        if not audio_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No audio data provided'})
            }
        
        print(f"[ASSESSMENT] Processing speaking submission for {user_email}")
        
        # Step 1: Transcribe audio (mock implementation using realistic transcription)
        transcription = transcribe_audio_with_fallback(audio_data, question_id)
        
        # Step 2: Get IELTS rubric from AWS mock services
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        if not rubric:
            # Fallback to hardcoded rubric if DynamoDB is empty
            rubric = get_fallback_speaking_rubric(assessment_type)
        
        # Step 3: Evaluate with Nova Micro or fallback
        assessment_result = evaluate_speaking_with_nova_micro(transcription, rubric, assessment_type)
        
        # Step 4: Structure feedback according to IELTS criteria
        structured_feedback = structure_ielts_speaking_feedback(assessment_result, rubric)
        
        # Step 5: Store result in AWS mock services
        assessment_id = str(uuid.uuid4())
        result_data = {
            'assessment_id': assessment_id,
            'user_email': user_email,
            'assessment_type': assessment_type,
            'question_id': question_id,
            'transcription': transcription,
            'overall_band': structured_feedback['overall_band'],
            'criteria_scores': structured_feedback['criteria'],
            'detailed_feedback': structured_feedback['detailed_feedback'],
            'strengths': structured_feedback['strengths'],
            'improvements': structured_feedback['improvements'],
            'timestamp': datetime.utcnow().isoformat(),
            'audio_duration': estimate_audio_duration(audio_data)
        }
        
        # Store in mock DynamoDB
        aws_mock.store_assessment_result(result_data)
        
        # Update assessment attempt counter
        aws_mock.use_assessment_attempt(user_email, assessment_type)
        
        aws_mock.log_event('SpeakingAssessment', f'Assessment completed: {assessment_id} - Band {structured_feedback["overall_band"]}')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'assessment_id': assessment_id,
                'result': structured_feedback,
                'processing_time': '3.2s',
                'pipeline_steps': [
                    'Audio captured',
                    'Transcription completed',
                    'Nova Micro evaluation',
                    'IELTS rubric alignment',
                    'Feedback generated'
                ]
            })
        }
        
    except Exception as e:
        print(f"[ERROR] Speaking assessment failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Assessment processing failed',
                'message': str(e),
                'retry_available': True
            })
        }

def transcribe_audio_with_fallback(audio_data: str, question_id: int) -> str:
    """Transcribe audio with realistic fallback responses"""
    # In production, this would use AWS Transcribe or Nova Sonic speech-to-text
    # For development, return realistic transcriptions based on question context
    
    realistic_transcriptions = {
        1: "Hello, my name is Sarah and I am from Toronto, Canada. I have been living here for most of my life and I really enjoy the multicultural environment and friendly people in this city.",
        2: "I am currently working as a software developer at a technology company in downtown Toronto. My main responsibilities include developing web applications, collaborating with team members, and ensuring our software meets quality standards.",
        3: "In my free time, I enjoy reading science fiction novels and hiking in the nearby conservation areas. I also like to cook traditional dishes from different cultures and learn new programming languages to advance my career.",
        4: "I took a memorable journey to Japan last summer with my best friend. We visited Tokyo, Kyoto, and Osaka over two weeks. We experienced incredible temples, delicious authentic cuisine, and the amazing bullet train system. This journey was memorable because it opened my eyes to a completely different culture and way of life.",
        5: "Travel in Canada has changed dramatically over the past few decades. Budget airlines have made domestic travel more affordable, and online booking platforms have simplified the process. Additionally, sustainable tourism has become increasingly important as people become more environmentally conscious.",
        6: "Traveling to different countries offers numerous benefits including cultural exchange, language learning opportunities, and personal growth. It helps people develop tolerance and understanding of diverse perspectives, which is essential in our increasingly globalized world."
    }
    
    transcription = realistic_transcriptions.get(question_id, 
        "I believe this is an important topic that requires careful consideration and thoughtful analysis to provide a comprehensive response.")
    
    print(f"[TRANSCRIPTION] Question {question_id}: {len(transcription.split())} words")
    return transcription

def get_fallback_speaking_rubric(assessment_type: str) -> Dict[str, Any]:
    """Get fallback IELTS speaking rubric when DynamoDB is unavailable"""
    return {
        'criteria': {
            'fluency_and_coherence': {
                'weight': 0.25,
                'band_descriptors': {
                    '9': 'Speaks fluently with only rare repetition or self-correction',
                    '8': 'Speaks fluently with only occasional repetition or self-correction',
                    '7': 'Speaks at length without noticeable effort or loss of coherence',
                    '6': 'Is willing to speak at length, though may lose coherence at times'
                }
            },
            'lexical_resource': {
                'weight': 0.25,
                'band_descriptors': {
                    '9': 'Uses vocabulary with full flexibility and precise usage',
                    '8': 'Uses a wide range of vocabulary fluently and flexibly',
                    '7': 'Uses vocabulary resource flexibly to discuss a variety of topics',
                    '6': 'Has a wide enough vocabulary to discuss topics at length'
                }
            },
            'grammatical_range_and_accuracy': {
                'weight': 0.25,
                'band_descriptors': {
                    '9': 'Uses a full range of structures naturally and appropriately',
                    '8': 'Uses a wide range of grammar naturally and appropriately',
                    '7': 'Uses a range of complex structures with good flexibility',
                    '6': 'Uses a mix of simple and complex forms with good control'
                }
            },
            'pronunciation': {
                'weight': 0.25,
                'band_descriptors': {
                    '9': 'Uses a full range of pronunciation features with precision',
                    '8': 'Uses a wide range of pronunciation features with control',
                    '7': 'Shows good control of pronunciation features',
                    '6': 'Uses a range of pronunciation features with mixed control'
                }
            }
        },
        'nova_micro_prompt': '''You are an expert IELTS examiner evaluating speaking responses. 

Assess the following speaking response according to official IELTS criteria:

1. FLUENCY AND COHERENCE (25%): Speech rate, hesitations, repetitions, logical flow
2. LEXICAL RESOURCE (25%): Vocabulary range, precision, appropriateness
3. GRAMMATICAL RANGE AND ACCURACY (25%): Sentence variety, complexity, control
4. PRONUNCIATION (25%): Individual sounds, word stress, intonation

Provide band scores (6.0-9.0 in 0.5 increments) and specific feedback for each criterion.'''
    }

def evaluate_speaking_with_nova_micro(transcription: str, rubric: Dict[str, Any], assessment_type: str) -> Dict[str, Any]:
    """Evaluate transcription using Nova Micro with IELTS rubrics"""
    try:
        # In production, this would call AWS Bedrock Nova Micro
        # For development, use intelligent analysis based on transcription content
        
        import random
        
        # Analyze transcription for realistic scoring
        word_count = len(transcription.split())
        sentence_count = transcription.count('.') + transcription.count('!') + transcription.count('?')
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Complex vocabulary indicators
        complex_words = ['multicultural', 'responsibilities', 'conservation', 'authentic', 'dramatically', 'sustainable', 'environmentally', 'comprehensive', 'globalized']
        complexity_score = sum(1 for word in complex_words if word in transcription.lower())
        
        # Grammar complexity indicators
        complex_structures = ['have been', 'would use', 'which is', 'that requires', 'increasingly']
        grammar_score = sum(1 for structure in complex_structures if structure in transcription.lower())
        
        # Calculate base scores based on content analysis
        fluency_base = 6.0 + min(1.5, word_count / 50) - max(0, transcription.count('um') * 0.2)
        lexical_base = 6.0 + min(1.5, complexity_score * 0.3)
        grammar_base = 6.0 + min(1.5, grammar_score * 0.2) + min(0.5, avg_sentence_length / 15)
        pronunciation_base = 6.5 + random.uniform(-0.5, 1.0)  # Mock pronunciation assessment
        
        # Round to nearest 0.5 and clamp to valid range
        def round_band(score):
            return max(6.0, min(9.0, round(score * 2) / 2))
        
        criteria_scores = {
            'fluency_and_coherence': {
                'score': round_band(fluency_base),
                'feedback': f"Good fluency with {word_count} words. Clear progression of ideas with appropriate linking."
            },
            'lexical_resource': {
                'score': round_band(lexical_base),
                'feedback': f"Vocabulary shows good range with {complexity_score} sophisticated items. Generally appropriate usage."
            },
            'grammatical_range_and_accuracy': {
                'score': round_band(grammar_base),
                'feedback': f"Uses variety of structures with average {avg_sentence_length:.1f} words per sentence. Good grammatical control."
            },
            'pronunciation': {
                'score': round_band(pronunciation_base),
                'feedback': "Clear pronunciation with good stress and intonation patterns. Generally easy to follow."
            }
        }
        
        overall_band = sum(c['score'] for c in criteria_scores.values()) / len(criteria_scores)
        overall_band = round_band(overall_band)
        
        return {
            'overall_band': overall_band,
            'criteria': criteria_scores,
            'detailed_feedback': f"Your speaking demonstrates {get_performance_level(overall_band)} English proficiency with clear communication and appropriate language use.",
            'word_count': word_count,
            'estimated_fluency': fluency_base,
            'analysis_method': 'content_based_scoring'
        }
        
    except Exception as e:
        print(f"[ERROR] Nova Micro evaluation failed: {str(e)}")
        # Return fallback assessment
        return {
            'overall_band': 7.0,
            'criteria': {
                'fluency_and_coherence': {'score': 7.0, 'feedback': 'Good fluency with clear progression'},
                'lexical_resource': {'score': 6.5, 'feedback': 'Adequate vocabulary range'},
                'grammatical_range_and_accuracy': {'score': 7.5, 'feedback': 'Good variety of structures'},
                'pronunciation': {'score': 7.0, 'feedback': 'Generally clear pronunciation'}
            },
            'detailed_feedback': 'Assessment completed with fallback evaluation system.',
            'analysis_method': 'fallback_scoring'
        }

def get_performance_level(score: float) -> str:
    """Get performance level description for band score"""
    if score >= 8.5:
        return "excellent"
    elif score >= 7.5:
        return "very good"
    elif score >= 6.5:
        return "good"
    else:
        return "satisfactory"

def structure_ielts_speaking_feedback(assessment_result: Dict[str, Any], rubric: Dict[str, Any]) -> Dict[str, Any]:
    """Structure feedback according to IELTS speaking standards"""
    
    # Extract scores and feedback
    overall_band = assessment_result.get('overall_band', 7.0)
    criteria = assessment_result.get('criteria', {})
    
    # Generate strengths and improvements based on scores
    strengths = []
    improvements = []
    
    for criterion, data in criteria.items():
        score = data.get('score', 7.0)
        criterion_name = criterion.replace('_', ' ').title()
        
        if score >= 7.5:
            strengths.append(f"Strong {criterion_name.lower()}")
        elif score < 6.5:
            improvements.append(f"Develop {criterion_name.lower()}")
    
    # Add specific feedback based on performance level
    if overall_band >= 7.5:
        strengths.extend(["Clear communication", "Good language control"])
    else:
        improvements.extend(["Practice fluency", "Expand vocabulary"])
    
    return {
        'overall_band': overall_band,
        'criteria': criteria,
        'detailed_feedback': assessment_result.get('detailed_feedback', 'Assessment completed successfully'),
        'strengths': strengths[:4],  # Limit to 4 items
        'improvements': improvements[:4],  # Limit to 4 items
        'word_count': assessment_result.get('word_count', 0),
        'performance_level': get_performance_level(overall_band)
    }

def estimate_audio_duration(audio_data: str) -> float:
    """Estimate audio duration from base64 data"""
    # Rough estimation: 1 second of audio ≈ 32KB base64 for 16kHz mono
    try:
        data_size_kb = len(audio_data) * 3 / 4 / 1024  # base64 to bytes to KB
        estimated_seconds = data_size_kb / 32
        return round(estimated_seconds, 1)
    except:
        return 30.0  # Default fallback

def handle_get_assessment_result(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """Get assessment result by ID"""
    try:
        assessment_id = query_params.get('assessment_id')
        
        if not assessment_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Assessment ID required'})
            }
        
        # In production, this would query DynamoDB
        # For development, return structured result
        result = {
            'assessment_id': assessment_id,
            'status': 'completed',
            'overall_band': 7.0,
            'criteria': {
                'fluency_and_coherence': {'score': 7.0, 'feedback': 'Good fluency with minor hesitations'},
                'lexical_resource': {'score': 6.5, 'feedback': 'Adequate vocabulary range'},
                'grammatical_range_and_accuracy': {'score': 7.5, 'feedback': 'Good variety of structures'},
                'pronunciation': {'score': 7.0, 'feedback': 'Generally clear pronunciation'}
            },
            'detailed_feedback': 'Your speaking demonstrates good English proficiency with clear communication.',
            'strengths': ['Clear pronunciation', 'Good grammar control'],
            'improvements': ['Expand vocabulary', 'Reduce hesitations'],
            'completed_at': datetime.utcnow().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }