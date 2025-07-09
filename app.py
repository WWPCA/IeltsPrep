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
import requests
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Set environment for .replit testing
os.environ['REPLIT_ENVIRONMENT'] = 'true'

# Import AWS mock services
from aws_mock_config import aws_mock

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
        
        # Send verification request to Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=verification_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            
            if not success:
                error_codes = result.get('error-codes', [])
                print(f"[RECAPTCHA] Verification failed: {error_codes}")
            
            return success
        else:
            print(f"[RECAPTCHA] HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
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
    """Handle home page - serve updated working template for preview"""
    try:
        with open('working_template.html', 'r', encoding='utf-8') as f:
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
            'body': '<h1>Working template not found</h1>'
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

def get_assessment_template(assessment_type: str, user_email: str, session_id: str) -> str:
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
    
    if 'speaking' in assessment_type:
        # Format the speaking question properly based on IELTS structure
        speaking_content = ""
        if question_data.get('parts'):
            # Multi-part structure (proper IELTS format)
            for part in question_data['parts']:
                part_num = part.get('part', 1)
                topic = part.get('topic', 'Speaking Task')
                if part_num == 1:
                    questions = part.get('questions', [])
                    speaking_content += f"<h4>Part {part_num}: {topic}</h4><ul>"
                    for q in questions:
                        speaking_content += f"<li>{q}</li>"
                    speaking_content += "</ul>"
                elif part_num == 2:
                    prep_time = part.get('prep_time', 60)
                    talk_time = part.get('talk_time', 120)
                    speaking_content += f"<h4>Part {part_num}: {topic}</h4><p><strong>Preparation time:</strong> {prep_time} seconds</p><p><strong>Speaking time:</strong> {talk_time} seconds</p><div class='cue-card'>{prompt}</div>"
                elif part_num == 3:
                    questions = part.get('questions', [])
                    speaking_content += f"<h4>Part {part_num}: {topic}</h4><ul>"
                    for q in questions:
                        speaking_content += f"<li>{q}</li>"
                    speaking_content += "</ul>"
        else:
            # Single part question (current format)
            speaking_content = f"<h4>{task_type}</h4><div class='cue-card'>{prompt}</div>"
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maya - {assessment_type.replace('_', ' ').title()} Assessment</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .ielts-header {{ background: #0066cc; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .assessment-info {{ background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .speaking-structure {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .cue-card {{ background: #fffacd; padding: 20px; border: 2px solid #ffd700; border-radius: 8px; margin: 15px 0; }}
        .part-section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #0066cc; }}
        .maya-controls {{ text-align: center; margin: 20px 0; padding: 20px; background: #f0f8ff; border-radius: 8px; }}
        .btn {{ padding: 12px 24px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .status {{ text-align: center; margin: 15px 0; font-weight: bold; }}
        .conversation-area {{ background: #f8f9fa; padding: 20px; border-radius: 8px; min-height: 200px; margin: 20px 0; }}
        .maya-message {{ background: #d4edda; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .user-message {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .error-message {{ background: #f8d7da; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #f5c6cb; color: #721c24; }}
        .timer {{ font-size: 24px; font-weight: bold; color: #dc3545; }}
        .current-part {{ background: #28a745; color: white; padding: 10px; border-radius: 5px; display: inline-block; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="ielts-header">
            <h1>IELTS Speaking Assessment</h1>
            <p>Conducted by Maya - AI Examiner</p>
        </div>
        
        <div class="assessment-info">
            <h4>Assessment Details</h4>
            <p><strong>Test Type:</strong> {assessment_type.replace('_', ' ').title()}</p>
            <p><strong>User:</strong> {user_email}</p>
            <p><strong>Session:</strong> {session_id}</p>
            <p><strong>Question ID:</strong> {question_id} (from DynamoDB)</p>
            <p><strong>Total Duration:</strong> 11-14 minutes</p>
        </div>

        <div class="speaking-structure">
            <h3>IELTS Speaking Test Structure</h3>
            {speaking_content}
        </div>

        <div class="current-part" id="currentPart">Part 1: Introduction & Interview (4-5 minutes)</div>
        <div class="timer" id="timer">14:00</div>

        <div class="maya-controls">
            <div class="status" id="status">Maya will guide you through each part of the assessment</div>
            <button class="btn btn-success" id="startBtn">Start Assessment with Maya</button>
            <button class="btn btn-primary" id="speakBtn" disabled>🎤 Speak to Maya</button>
            <button class="btn btn-danger" id="stopBtn" disabled>⏹️ Stop</button>
        </div>
        
        <div class="conversation-area" id="conversation">
            <div class="maya-message">
                <strong>Maya:</strong> <span id="maya-text">Welcome! I'm Maya, your IELTS speaking examiner. Click 'Start Assessment' when you're ready to begin.</span>
            </div>
        </div>

        <audio id="mayaAudio" style="display: none;"></audio>
    </div>

    <script>
        let isListening = false;
        let recognition = null;
        let conversationActive = false;
        let timeRemaining = 14 * 60; // 14 minutes total for speaking assessment
        let currentPart = 1;
        let partTimeRemaining = 5 * 60; // Part 1: 5 minutes max
        let timerInterval = null;
        let twoMinuteWarningShown = false;
        let assessmentStarted = false;
        
        // IELTS Speaking timing structure
        const partTimings = {{
            1: {{ min: 4, max: 5, name: "Introduction & Interview" }},
            2: {{ min: 3, max: 4, name: "Long Turn" }},
            3: {{ min: 4, max: 5, name: "Discussion" }}
        }};
        
        // Create modal for warnings and time expiry
        function createSpeakingModal() {{
            const modal = document.createElement('div');
            modal.id = 'speakingModal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            `;
            
            const modalContent = document.createElement('div');
            modalContent.style.cssText = `
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                max-width: 500px;
                margin: 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            `;
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            return {{ modal, modalContent }};
        }}
        
        // Show 2-minute warning for overall assessment
        function showTwoMinuteWarning() {{
            if (twoMinuteWarningShown) return;
            twoMinuteWarningShown = true;
            
            const {{ modal, modalContent }} = createSpeakingModal();
            modalContent.innerHTML = `
                <h3 style="color: #dc3545; margin-bottom: 20px;">⚠️ Speaking Assessment Warning</h3>
                <p style="font-size: 18px; margin-bottom: 20px;">You have <strong>2 minutes</strong> remaining!</p>
                <p style="margin-bottom: 20px;">Maya will conclude the assessment shortly.</p>
                <button id="continueSpeakingBtn" style="
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                ">Continue Assessment</button>
            `;
            
            modal.style.display = 'flex';
            
            document.getElementById('continueSpeakingBtn').onclick = function() {{
                modal.style.display = 'none';
                modal.remove();
            }};
        }}
        
        // Handle assessment completion
        function completeAssessment() {{
            const {{ modal, modalContent }} = createSpeakingModal();
            modalContent.innerHTML = `
                <h3 style="color: #28a745; margin-bottom: 20px;">✅ Assessment Complete</h3>
                <p style="font-size: 18px; margin-bottom: 20px;">Your 14-minute speaking assessment has ended.</p>
                <p style="margin-bottom: 20px;">Maya will now provide your assessment results.</p>
                <div style="margin: 20px 0;">
                    <div style="
                        display: inline-block;
                        width: 40px;
                        height: 40px;
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #28a745;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    <p style="margin-top: 15px; font-style: italic;">Processing your results...</p>
                </div>
                <style>
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            `;
            
            modal.style.display = 'flex';
            
            // Disable controls
            document.getElementById('speakBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            
            // Auto-submit assessment after 3 seconds
            setTimeout(() => {{
                window.location.href = '/dashboard';
            }}, 5000);
        }}
        
        // Update current part display
        function updateCurrentPart() {{
            const part = partTimings[currentPart];
            const partElement = document.getElementById('currentPart');
            partElement.textContent = `Part ${{currentPart}}: ${{part.name}} (${{part.min}}-${{part.max}} minutes)`;
            
            // Update Maya's context for the new part
            addMessage('Maya', `Now moving to Part ${{currentPart}}: ${{part.name}}`, 'maya-message');
        }}
        
        // Start comprehensive timer
        function startSpeakingTimer() {{
            if (timerInterval) return; // Already started
            
            timerInterval = setInterval(() => {{
                timeRemaining--;
                partTimeRemaining--;
                
                // Update main timer display
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
                document.getElementById('timer').textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
                
                // 2-minute warning (120 seconds)
                if (timeRemaining === 120 && !twoMinuteWarningShown) {{
                    showTwoMinuteWarning();
                    document.getElementById('timer').style.color = '#dc3545';
                    document.getElementById('timer').style.fontSize = '28px';
                }}
                
                // Last 5 minutes - red warning
                if (timeRemaining <= 300) {{
                    document.getElementById('timer').style.color = '#dc3545';
                    document.getElementById('timer').style.fontSize = '28px';
                }}
                
                // Part transitions based on time
                if (currentPart === 1 && partTimeRemaining <= 0) {{
                    currentPart = 2;
                    partTimeRemaining = 4 * 60; // Part 2: 4 minutes max
                    updateCurrentPart();
                }} else if (currentPart === 2 && partTimeRemaining <= 0) {{
                    currentPart = 3;
                    partTimeRemaining = 5 * 60; // Part 3: 5 minutes max
                    updateCurrentPart();
                }}
                
                // Assessment completion
                if (timeRemaining <= 0) {{
                    clearInterval(timerInterval);
                    document.getElementById('timer').textContent = "COMPLETED";
                    document.getElementById('timer').style.color = '#28a745';
                    document.getElementById('timer').style.fontSize = '32px';
                    completeAssessment();
                }}
            }}, 1000);
        }}
        
        // Initialize speech recognition
        function initializeSpeechRecognition() {{
            if ('webkitSpeechRecognition' in window) {{
                recognition = new webkitSpeechRecognition();
            }} else if ('SpeechRecognition' in window) {{
                recognition = new SpeechRecognition();
            }} else {{
                document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Please use Chrome, Edge, or Safari.';
                return false;
            }}
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                addMessage('You', transcript, 'user-message');
                sendToMaya(transcript);
            }};
            
            recognition.onerror = function(event) {{
                console.error('Speech recognition error:', event.error);
                document.getElementById('status').textContent = 'Speech recognition error. Please try again.';
                isListening = false;
                updateButtons();
            }};
            
            recognition.onend = function() {{
                isListening = false;
                updateButtons();
            }};
            
            return true;
        }}
        
        // Auto-start Maya introduction
        async function startMayaIntroduction() {{
            try {{
                document.getElementById('status').textContent = '🤖 Maya is introducing herself...';
                
                const response = await fetch('/api/maya/introduction', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        assessment_type: '{assessment_type}',
                        user_email: '{user_email}',
                        session_id: '{session_id}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    document.getElementById('intro-text').textContent = result.introduction;
                    document.getElementById('status').textContent = '🔊 Maya is speaking...';
                    
                    // Auto-play Maya's introduction
                    if (result.audio_url) {{
                        const audio = document.getElementById('mayaAudio');
                        audio.src = result.audio_url;
                        
                        audio.onplay = () => {{
                            document.getElementById('status').textContent = '🔊 Maya is speaking - Listen carefully';
                        }};
                        
                        audio.onended = () => {{
                            document.getElementById('status').textContent = '✅ Maya has finished - Click "Speak to Maya" to respond';
                            conversationActive = true;
                            updateButtons();
                        }};
                        
                        audio.play();
                    }} else {{
                        document.getElementById('status').textContent = '✅ Maya is ready - Click "Speak to Maya" to start';
                        conversationActive = true;
                        updateButtons();
                    }}
                }} else {{
                    document.getElementById('status').textContent = '❌ Error starting assessment: ' + (result.error || 'Unknown error');
                }}
            }} catch (error) {{
                console.error('Error starting Maya:', error);
                document.getElementById('status').textContent = '❌ Connection error. Please refresh the page.';
            }}
        }}
        
        function addMessage(sender, message, className) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = className;
            messageDiv.innerHTML = `<strong>${{sender}}:</strong> ${{message}}`;
            document.getElementById('conversation').appendChild(messageDiv);
        }}
        
        // Enhanced Maya conversation with connectivity safeguards
        let mayaRetryAttempts = 0;
        const maxMayaRetries = 3;
        
        // Save conversation state regularly
        function saveConversationState() {{
            const conversationData = {{
                currentPart: currentPart,
                timeRemaining: timeRemaining,
                partTimeRemaining: partTimeRemaining,
                assessmentStarted: assessmentStarted,
                conversation: document.getElementById('conversation').innerHTML,
                timestamp: Date.now()
            }};
            localStorage.setItem('ielts_speaking_state_{session_id}', JSON.stringify(conversationData));
        }}
        
        // Auto-save conversation state every 15 seconds
        setInterval(saveConversationState, 15000);
        
        async function sendToMaya(userMessage) {{
            if (!navigator.onLine) {{
                document.getElementById('status').textContent = '📡 No internet connection. Please check your network.';
                return;
            }}
            
            try {{
                document.getElementById('status').textContent = '🤖 Maya is thinking...';
                
                // Save conversation state before request
                saveConversationState();
                
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                
                const response = await fetch('/api/maya/conversation', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        user_message: userMessage,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}',
                        current_part: currentPart,
                        time_remaining: timeRemaining,
                        retry_attempt: mayaRetryAttempts
                    }}),
                    signal: controller.signal
                }});
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const result = await response.json();
                
                if (result.success) {{
                    addMessage('Maya', result.response, 'maya-message');
                    document.getElementById('status').textContent = '🔊 Maya is responding...';
                    
                    // Reset retry counter on success
                    mayaRetryAttempts = 0;
                    
                    if (result.audio_url) {{
                        const audio = document.getElementById('mayaAudio');
                        audio.src = result.audio_url;
                        
                        audio.onended = () => {{
                            document.getElementById('status').textContent = '✅ Maya finished - Your turn to speak';
                            updateButtons();
                            saveConversationState();
                        }};
                        
                        audio.onerror = () => {{
                            document.getElementById('status').textContent = '✅ Maya responded - Your turn to speak';
                            updateButtons();
                        }};
                        
                        audio.play();
                    }} else {{
                        document.getElementById('status').textContent = '✅ Maya responded - Your turn to speak';
                        updateButtons();
                    }}
                }} else {{
                    handleMayaError(result.error || 'Maya processing error', userMessage);
                }}
            }} catch (error) {{
                console.error('Error with Maya conversation:', error);
                
                if (error.name === 'AbortError') {{
                    handleMayaError('Maya response timed out', userMessage);
                }} else if (!navigator.onLine) {{
                    handleMayaError('Connection lost during conversation', userMessage);
                }} else {{
                    handleMayaError('Network error with Maya', userMessage);
                }}
            }}
        }}
        
        // Handle Maya errors with retry logic
        function handleMayaError(errorMessage, originalMessage) {{
            mayaRetryAttempts++;
            
            if (mayaRetryAttempts <= maxMayaRetries && navigator.onLine) {{
                document.getElementById('status').textContent = `${{errorMessage}} Retrying... (${{mayaRetryAttempts}}/${{maxMayaRetries}})`;
                
                setTimeout(() => {{
                    if (navigator.onLine) {{
                        sendToMaya(originalMessage);
                    }} else {{
                        document.getElementById('status').textContent = '📡 Connection lost. Please check your network and try again.';
                        updateButtons();
                    }}
                }}, 2000);
            }} else {{
                document.getElementById('status').textContent = `${{errorMessage}} Please try speaking again.`;
                updateButtons();
                
                // Add error message to conversation
                addMessage('System', 'Connection issue. Please repeat your response.', 'error-message');
            }}
        }}
        
        // Enhanced assessment completion with safeguards
        function completeAssessment() {{
            // Save final state
            saveConversationState();
            
            const {{ modal, modalContent }} = createSpeakingModal();
            modalContent.innerHTML = `
                <h3 style="color: #28a745; margin-bottom: 20px;">✅ Assessment Complete</h3>
                <p style="font-size: 18px; margin-bottom: 20px;">Your 14-minute speaking assessment has ended.</p>
                <p style="margin-bottom: 20px;">Your conversation has been saved and will be processed.</p>
                <p style="margin-bottom: 20px; font-size: 14px; color: #666;">If processing fails, you can access your results from the dashboard.</p>
                <div style="margin: 20px 0;">
                    <div style="
                        display: inline-block;
                        width: 40px;
                        height: 40px;
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #28a745;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    <p style="margin-top: 15px; font-style: italic;">Processing your results...</p>
                </div>
                <style>
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            `;
            
            modal.style.display = 'flex';
            
            // Disable controls
            document.getElementById('speakBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            
            // Try to submit assessment results
            setTimeout(() => {{
                if (navigator.onLine) {{
                    // Attempt to submit speaking assessment
                    submitSpeakingAssessment();
                }} else {{
                    modalContent.innerHTML = `
                        <h3 style="color: #dc3545; margin-bottom: 20px;">📡 Connection Issue</h3>
                        <p style="font-size: 18px; margin-bottom: 20px;">Unable to process results due to network connectivity.</p>
                        <p style="margin-bottom: 20px;">Your assessment has been saved and can be processed from your dashboard.</p>
                        <button onclick="window.location.href='/dashboard'" style="
                            background: #007bff;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            font-size: 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-weight: bold;
                        ">Go to Dashboard</button>
                    `;
                }}
            }}, 3000);
        }}
        
        // Submit speaking assessment with retry logic
        async function submitSpeakingAssessment() {{
            try {{
                const conversationData = JSON.parse(localStorage.getItem('ielts_speaking_state_{session_id}') || '{{}}');
                
                const response = await fetch('/api/maya/submit-assessment', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        conversation_data: conversationData,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}',
                        user_email: '{user_email}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    // Clear saved state after successful submission
                    localStorage.removeItem('ielts_speaking_state_{session_id}');
                    window.location.href = '/dashboard';
                }} else {{
                    throw new Error(result.error || 'Failed to submit assessment');
                }}
            }} catch (error) {{
                console.error('Speaking assessment submission error:', error);
                // Keep assessment data for manual retry
                setTimeout(() => {{
                    window.location.href = '/dashboard';
                }}, 5000);
            }}
        }}
        
        function updateButtons() {{
            const speakBtn = document.getElementById('speakBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            if (conversationActive && !isListening) {{
                speakBtn.disabled = false;
                speakBtn.textContent = '🎤 Speak to Maya';
                stopBtn.disabled = true;
            }} else if (isListening) {{
                speakBtn.disabled = true;
                stopBtn.disabled = false;
            }} else {{
                speakBtn.disabled = true;
                stopBtn.disabled = true;
            }}
        }}
        
        // Event listeners
        document.getElementById('speakBtn').addEventListener('click', function() {{
            if (recognition && !isListening) {{
                isListening = true;
                document.getElementById('status').textContent = '🎤 Listening... Speak now';
                updateButtons();
                recognition.start();
            }}
        }});
        
        document.getElementById('stopBtn').addEventListener('click', function() {{
            if (recognition && isListening) {{
                recognition.stop();
            }}
        }});
        
        document.getElementById('startBtn').addEventListener('click', function() {{
            if (!assessmentStarted) {{
                assessmentStarted = true;
                document.getElementById('startBtn').disabled = true;
                document.getElementById('startBtn').textContent = 'Assessment Started';
                
                // Start the 14-minute timer
                startSpeakingTimer();
                
                // Start Maya introduction
                startMayaIntroduction();
            }}
        }});
        
        // Initialize when page loads
        window.addEventListener('load', function() {{
            if (initializeSpeechRecognition()) {{
                // Ready to start when user clicks button
                document.getElementById('status').textContent = 'Ready to begin - Click "Start Assessment with Maya"';
            }}
        }});
    </script>
</body>
</html>
"""
    else:
        # Official IELTS Writing Format with Left/Right Page Divider
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS {assessment_type.replace('_', ' ').title()} - Official Format</title>
    <style>
        body {{ 
            font-family: 'Times New Roman', serif; 
            margin: 0; 
            padding: 0; 
            background: #f8f9fa;
            color: #000;
        }}
        
        .ielts-container {{
            max-width: 1200px;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            display: flex;
            min-height: 700px;
        }}
        
        /* Official IELTS Left Page - Question Paper */
        .question-page {{
            width: 50%;
            padding: 40px 30px;
            background: #fff;
            border-right: 2px solid #ddd;
            position: relative;
        }}
        
        .question-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #ccc;
        }}
        
        .ielts-logo {{
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
            margin-bottom: 10px;
        }}
        
        .test-info {{
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .task-box {{
            border: 2px solid #000;
            padding: 20px;
            margin: 20px 0;
            background: #fafafa;
        }}
        
        .task-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .task-instructions {{
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .task-topic {{
            font-size: 15px;
            line-height: 1.7;
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-left: 4px solid #0066cc;
        }}
        
        .word-requirements {{
            font-weight: bold;
            font-size: 14px;
            margin: 15px 0;
            padding: 10px;
            background: #e8f4fd;
        }}
        
        /* Official IELTS Right Page - Answer Sheet */
        .answer-page {{
            width: 50%;
            padding: 40px 30px;
            background: #fff;
            position: relative;
        }}
        
        .answer-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #ccc;
        }}
        
        .writing-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 10px;
            background: #f8f9fa;
            border: 1px solid #ddd;
        }}
        
        .word-counter {{
            font-weight: bold;
            color: #dc3545;
        }}
        
        .timer-display {{
            font-weight: bold;
            color: #0066cc;
            font-size: 16px;
        }}
        
        .answer-area {{
            width: 100%;
            min-height: 450px;
            padding: 15px;
            border: 2px solid #000;
            font-family: 'Times New Roman', serif;
            font-size: 16px;
            line-height: 1.8;
            resize: none;
            background: white;
        }}
        
        .answer-area:focus {{
            outline: none;
            border-color: #0066cc;
            box-shadow: 0 0 5px rgba(0,102,204,0.3);
        }}
        
        .submit-section {{
            margin-top: 20px;
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #ddd;
        }}
        
        .btn {{
            padding: 12px 25px;
            margin: 5px;
            border: none;
            font-size: 14px;
            cursor: pointer;
            font-weight: bold;
        }}
        
        .btn-submit {{
            background: #28a745;
            color: white;
        }}
        
        .btn-submit:disabled {{
            background: #6c757d;
            cursor: not-allowed;
        }}
        
        .btn-save {{
            background: #17a2b8;
            color: white;
        }}
        
        .status-bar {{
            text-align: center;
            padding: 10px;
            margin: 10px 0;
            font-weight: bold;
            border-radius: 4px;
        }}
        
        .status-waiting {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .status-ready {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-processing {{
            background: #cce7ff;
            color: #004085;
        }}
        
        /* Nova Micro Assessment Results */
        .assessment-results {{
            display: none;
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border: 2px solid #28a745;
            border-radius: 8px;
        }}
        
        .results-header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .overall-band {{
            font-size: 36px;
            font-weight: bold;
            color: #28a745;
            text-align: center;
            margin: 15px 0;
        }}
        
        .band-breakdown {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }}
        
        .band-criterion {{
            padding: 15px;
            background: white;
            border: 1px solid #ddd;
            text-align: center;
        }}
        
        .criterion-name {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .criterion-score {{
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
        }}
        
        .feedback-section {{
            margin-top: 20px;
            padding: 20px;
            background: white;
            border: 1px solid #ddd;
        }}
        
        .feedback-text {{
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .feedback-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        .feedback-category h5 {{
            color: #0066cc;
            margin-bottom: 10px;
        }}
        
        .feedback-category ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .feedback-category li {{
            margin-bottom: 5px;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .ielts-container {{
                flex-direction: column;
                margin: 10px;
            }}
            
            .question-page, .answer-page {{
                width: 100%;
                border-right: none;
                border-bottom: 2px solid #ddd;
            }}
            
            .answer-page {{
                border-bottom: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="ielts-container">
        <!-- Left Page - Official IELTS Question Paper -->
        <div class="question-page">
            <div class="question-header">
                <div class="ielts-logo">IELTS</div>
                <div class="test-info">International English Language Testing System</div>
                <div class="test-info">{assessment_type.replace('_', ' ').title()}</div>
                <div class="test-info">Time allowed: 60 minutes (Task 1: 20 min, Task 2: 40 min recommended)</div>
            </div>
            
            <div class="task-box">
                <div class="task-title">WRITING TASK 2</div>
                
                <div class="task-instructions">
                    You should spend about 40 minutes on this task.
                </div>
                
                <div class="word-requirements">
                    Write at least 250 words.
                </div>
                
                <div class="task-topic" id="taskPrompt">
                    <strong>Write about the following topic:</strong><br><br>
                    {prompt}<br><br>
                    Give reasons for your answer and include any relevant examples from your own knowledge or experience.
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #e8f4fd; border: 1px solid #0066cc;">
                <h4 style="margin: 0 0 10px 0; color: #0066cc;">Assessment Information</h4>
                <p style="margin: 5px 0; font-size: 14px;"><strong>User:</strong> {user_email}</p>
                <p style="margin: 5px 0; font-size: 14px;"><strong>Session:</strong> {session_id}</p>
                <p style="margin: 5px 0; font-size: 14px;"><strong>Question ID:</strong> {question_id} (from DynamoDB)</p>
                <p style="margin: 5px 0; font-size: 14px;">Your essay will be evaluated by Nova Micro using official IELTS band descriptors.</p>
            </div>
        </div>
        
        <!-- Right Page - Official IELTS Answer Sheet -->
        <div class="answer-page">
            <div class="answer-header">
                <div class="ielts-logo">ANSWER SHEET</div>
                <div class="test-info">Writing Task 2</div>
            </div>
            
            <div class="writing-controls">
                <div class="word-counter">
                    Words: <span id="wordCount">0</span> / <span id="minWords">250</span>
                </div>
                <div class="timer-display">
                    Time remaining: <span id="timer">60:00</span>
                </div>
            </div>
            
            <textarea 
                id="essayText" 
                class="answer-area"
                placeholder="Write your essay here. Use proper paragraphing and ensure you address both sides of the argument before giving your opinion."
            ></textarea>
            
            <div class="status-bar status-waiting" id="statusBar">
                Write at least 250 words to enable Nova Micro assessment
            </div>
            
            <div class="submit-section">
                <button class="btn btn-save" id="saveBtn">Save Draft</button>
                <button class="btn btn-submit" id="submitBtn" disabled>Submit for Assessment</button>
            </div>
            
            <!-- Nova Micro Assessment Results -->
            <div class="assessment-results" id="assessmentResults">
                <div class="results-header">
                    <h3>Nova Micro Assessment Results</h3>
                    <div class="overall-band" id="overallBand">7.0</div>
                    <p>Overall Band Score</p>
                </div>
                
                <div class="band-breakdown">
                    <div class="band-criterion">
                        <div class="criterion-name">Task Response</div>
                        <div class="criterion-score" id="taskScore">7.0</div>
                    </div>
                    <div class="band-criterion">
                        <div class="criterion-name">Coherence & Cohesion</div>
                        <div class="criterion-score" id="coherenceScore">6.5</div>
                    </div>
                    <div class="band-criterion">
                        <div class="criterion-name">Lexical Resource</div>
                        <div class="criterion-score" id="lexicalScore">7.0</div>
                    </div>
                    <div class="band-criterion">
                        <div class="criterion-name">Grammatical Range & Accuracy</div>
                        <div class="criterion-score" id="grammarScore">6.5</div>
                    </div>
                </div>
                
                <div class="feedback-section">
                    <div class="feedback-text" id="mainFeedback">
                        Loading detailed feedback from Nova Micro...
                    </div>
                    
                    <div class="feedback-details">
                        <div class="feedback-category">
                            <h5>Strengths</h5>
                            <ul id="strengthsList"></ul>
                        </div>
                        <div class="feedback-category">
                            <h5>Areas for Improvement</h5>
                            <ul id="improvementsList"></ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let timeRemaining = 60 * 60; // 60 minutes total for writing section
        let timerInterval = null;
        let assessmentSubmitted = false;
        let twoMinuteWarningShown = false;
        let screenLocked = false;
        
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const minWords = document.getElementById('minWords');
        const submitBtn = document.getElementById('submitBtn');
        const saveBtn = document.getElementById('saveBtn');
        const statusBar = document.getElementById('statusBar');
        const timer = document.getElementById('timer');
        const assessmentResults = document.getElementById('assessmentResults');
        
        // Create modal for warnings and time expiry
        function createTimerModal() {{
            const modal = document.createElement('div');
            modal.id = 'timerModal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            `;
            
            const modalContent = document.createElement('div');
            modalContent.style.cssText = `
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                max-width: 500px;
                margin: 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            `;
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            return {{ modal, modalContent }};
        }}
        
        // Show 2-minute warning modal
        function showTwoMinuteWarning() {{
            if (twoMinuteWarningShown) return;
            twoMinuteWarningShown = true;
            
            const {{ modal, modalContent }} = createTimerModal();
            modalContent.innerHTML = `
                <h3 style="color: #dc3545; margin-bottom: 20px;">⚠️ Time Warning</h3>
                <p style="font-size: 18px; margin-bottom: 20px;">You have <strong>2 minutes</strong> remaining!</p>
                <p style="margin-bottom: 20px;">Please finish your essay and submit it before time expires.</p>
                <button id="continueBtn" style="
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                ">Continue Writing</button>
            `;
            
            modal.style.display = 'flex';
            
            document.getElementById('continueBtn').onclick = function() {{
                modal.style.display = 'none';
                modal.remove();
            }};
        }}
        
        // Lock screen when time expires
        function lockScreenTimeExpired() {{
            if (screenLocked) return;
            screenLocked = true;
            
            const {{ modal, modalContent }} = createTimerModal();
            modalContent.innerHTML = `
                <h3 style="color: #dc3545; margin-bottom: 20px;">🔒 Time Expired</h3>
                <p style="font-size: 18px; margin-bottom: 20px;">The 60-minute writing assessment time has ended.</p>
                <p style="margin-bottom: 20px;">Your essay will be automatically submitted for Nova Micro assessment.</p>
                <div style="margin: 20px 0;">
                    <div style="
                        display: inline-block;
                        width: 40px;
                        height: 40px;
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #dc3545;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    <p style="margin-top: 15px; font-style: italic;">Submitting your essay...</p>
                </div>
                <style>
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            `;
            
            modal.style.display = 'flex';
            
            // Disable all form inputs
            essayText.disabled = true;
            essayText.style.backgroundColor = '#f8f9fa';
            essayText.style.color = '#6c757d';
            submitBtn.disabled = true;
            saveBtn.disabled = true;
            
            // Auto-submit after 3 seconds
            setTimeout(() => {{
                if (!assessmentSubmitted) {{
                    submitEssay();
                }}
            }}, 3000);
        }}
        
        // Start 60-minute timer with proper IELTS timing
        function startTimer() {{
            timerInterval = setInterval(() => {{
                timeRemaining--;
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
                timer.textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
                
                // 2-minute warning (120 seconds)
                if (timeRemaining === 120 && !twoMinuteWarningShown) {{
                    showTwoMinuteWarning();
                    timer.style.color = '#dc3545';
                    timer.style.fontSize = '18px';
                    timer.style.fontWeight = 'bold';
                }}
                
                // Last 5 minutes - red warning
                if (timeRemaining <= 300) {{
                    timer.style.color = '#dc3545';
                    timer.style.fontSize = '18px';
                    timer.style.fontWeight = 'bold';
                }}
                
                // Time expired - lock screen
                if (timeRemaining <= 0) {{
                    clearInterval(timerInterval);
                    timer.textContent = "TIME EXPIRED";
                    timer.style.color = '#dc3545';
                    timer.style.fontSize = '20px';
                    timer.style.fontWeight = 'bold';
                    lockScreenTimeExpired();
                }}
            }}, 1000);
        }}
        
        // Update word count and submission eligibility
        essayText.addEventListener('input', function() {{
            const words = this.value.trim().split(/\\s+/).filter(word => word.length > 0);
            const currentWordCount = words.length;
            wordCount.textContent = currentWordCount;
            
            // Update status based on word count
            if (currentWordCount >= parseInt(minWords.textContent)) {{
                submitBtn.disabled = false;
                submitBtn.className = 'btn btn-submit';
                statusBar.className = 'status-bar status-ready';
                statusBar.textContent = 'Ready for Nova Micro assessment';
            }} else {{
                submitBtn.disabled = true;
                submitBtn.className = 'btn btn-submit';
                submitBtn.disabled = true;
                statusBar.className = 'status-bar status-waiting';
                statusBar.textContent = `Write at least ${{minWords.textContent}} words to enable assessment`;
            }}
        }});
        
        // Enhanced connectivity safeguards and retry logic
        let retryAttempts = 0;
        const maxRetries = 5;
        let autoRetryInterval = null;
        
        // Auto-save essay content every 30 seconds
        setInterval(() => {{
            if (essayText.value.trim().length > 0) {{
                localStorage.setItem('ielts_essay_draft_{session_id}', essayText.value);
                localStorage.setItem('ielts_essay_timestamp_{session_id}', Date.now().toString());
            }}
        }}, 30000);
        
        // Enhanced connectivity check
        function checkNetworkStatus() {{
            return navigator.onLine && window.fetch;
        }}
        
        // Network status monitoring
        window.addEventListener('online', () => {{
            if (retryAttempts > 0) {{
                statusBar.className = 'status-bar status-ready';
                statusBar.textContent = 'Connection restored. You can retry your assessment.';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Retry Assessment';
            }}
        }});
        
        window.addEventListener('offline', () => {{
            statusBar.className = 'status-bar status-waiting';
            statusBar.textContent = 'No internet connection. Your work is saved locally. Assessment will retry when connection is restored.';
            clearInterval(autoRetryInterval);
        }});
        
        // Submit essay with comprehensive retry logic
        async function submitEssay() {{
            if (assessmentSubmitted) return;
            
            // Check network connectivity first
            if (!checkNetworkStatus()) {{
                statusBar.className = 'status-bar status-waiting';
                statusBar.textContent = 'No internet connection. Please check your network and try again.';
                return;
            }}
            
            assessmentSubmitted = true;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            statusBar.className = 'status-bar status-processing';
            statusBar.textContent = 'Nova Micro is analyzing your essay using IELTS band descriptors...';
            
            // Save essay before submission
            localStorage.setItem('ielts_essay_draft_{session_id}', essayText.value);
            localStorage.setItem('ielts_essay_timestamp_{session_id}', Date.now().toString());
            
            try {{
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 45000); // 45 second timeout
                
                const response = await fetch('/api/nova-micro/writing', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        essay_text: essayText.value,
                        prompt: document.getElementById('taskPrompt').textContent,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}',
                        user_email: '{user_email}',
                        retry_attempt: retryAttempts
                    }}),
                    signal: controller.signal
                }});
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const result = await response.json();
                
                if (result.success) {{
                    displayAssessmentResults(result.assessment_result);
                    statusBar.className = 'status-bar status-ready';
                    statusBar.textContent = 'Assessment completed successfully';
                    clearInterval(timerInterval); // Stop timer
                    retryAttempts = 0; // Reset retry counter
                    
                    // Clear saved draft after successful submission
                    localStorage.removeItem('ielts_essay_draft_{session_id}');
                    localStorage.removeItem('ielts_essay_timestamp_{session_id}');
                }} else {{
                    handleSubmissionError(result.error || 'Assessment processing failed');
                }}
            }} catch (error) {{
                console.error('Nova Micro assessment error:', error);
                
                if (error.name === 'AbortError') {{
                    handleSubmissionError('Assessment timed out. This may be due to high server load.');
                }} else if (!navigator.onLine) {{
                    handleSubmissionError('Connection lost. Your work is saved. Please retry when online.');
                }} else {{
                    handleSubmissionError('Network error. Please check your connection and try again.');
                }}
            }}
        }}
        
        // Handle submission errors with intelligent retry
        function handleSubmissionError(errorMessage) {{
            retryAttempts++;
            assessmentSubmitted = false;
            
            if (retryAttempts < maxRetries && checkNetworkStatus()) {{
                statusBar.className = 'status-bar status-waiting';
                statusBar.textContent = `${{errorMessage}} Retrying automatically... (Attempt ${{retryAttempts}}/${{maxRetries}})`;
                
                submitBtn.disabled = true;
                submitBtn.textContent = `Retrying... (${{retryAttempts}}/${{maxRetries}})`;
                
                // Auto-retry with exponential backoff
                const retryDelay = Math.min(2000 * Math.pow(2, retryAttempts - 1), 30000);
                autoRetryInterval = setTimeout(() => {{
                    if (checkNetworkStatus()) {{
                        submitEssay();
                    }} else {{
                        statusBar.className = 'status-bar status-waiting';
                        statusBar.textContent = 'Connection lost. Please check your network and manually retry.';
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Retry Assessment';
                    }}
                }}, retryDelay);
            }} else {{
                statusBar.className = 'status-bar status-waiting';
                statusBar.textContent = `${{errorMessage}} Please try again manually.`;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Retry Assessment';
                
                // Show extended retry options
                if (retryAttempts >= maxRetries) {{
                    statusBar.textContent += ' Contact support if issues persist.';
                }}
            }}
        }}
        
        // Enhanced screen lock with connectivity safeguards
        function lockScreenTimeExpired() {{
            if (screenLocked) return;
            screenLocked = true;
            
            // Save essay before locking
            localStorage.setItem('ielts_essay_draft_{session_id}', essayText.value);
            localStorage.setItem('ielts_essay_timestamp_{session_id}', Date.now().toString());
            
            const {{ modal, modalContent }} = createTimerModal();
            modalContent.innerHTML = `
                <h3 style="color: #dc3545; margin-bottom: 20px;">🔒 Time Expired</h3>
                <p style="font-size: 18px; margin-bottom: 20px;">The 60-minute writing assessment time has ended.</p>
                <p style="margin-bottom: 20px;">Your essay has been saved and will be submitted automatically.</p>
                <p style="margin-bottom: 20px; font-size: 14px; color: #666;">If submission fails due to connectivity, you can retry from your dashboard.</p>
                <div style="margin: 20px 0;">
                    <div style="
                        display: inline-block;
                        width: 40px;
                        height: 40px;
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #dc3545;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    <p style="margin-top: 15px; font-style: italic;">Submitting your essay...</p>
                </div>
                <style>
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            `;
            
            modal.style.display = 'flex';
            
            // Disable all inputs
            essayText.disabled = true;
            essayText.style.backgroundColor = '#f8f9fa';
            essayText.style.color = '#6c757d';
            submitBtn.disabled = true;
            saveBtn.disabled = true;
            
            // Try to submit with multiple attempts
            setTimeout(() => {{
                if (checkNetworkStatus()) {{
                    submitEssay();
                }} else {{
                    modalContent.innerHTML = `
                        <h3 style="color: #dc3545; margin-bottom: 20px;">📡 Connection Issue</h3>
                        <p style="font-size: 18px; margin-bottom: 20px;">Unable to submit due to network connectivity.</p>
                        <p style="margin-bottom: 20px;">Your essay has been saved locally and can be submitted from your dashboard.</p>
                        <button onclick="window.location.href='/dashboard'" style="
                            background: #007bff;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            font-size: 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-weight: bold;
                        ">Go to Dashboard</button>
                    `;
                }}
            }}, 3000);
        }}
        
        // Display Nova Micro assessment results
        function displayAssessmentResults(result) {{
            document.getElementById('overallBand').textContent = result.overall_band_score;
            document.getElementById('taskScore').textContent = result.task_achievement;
            document.getElementById('coherenceScore').textContent = result.coherence_cohesion;
            document.getElementById('lexicalScore').textContent = result.lexical_resource;
            document.getElementById('grammarScore').textContent = result.grammatical_accuracy;
            document.getElementById('mainFeedback').textContent = result.feedback;
            
            // Display detailed feedback
            const strengthsList = document.getElementById('strengthsList');
            const improvementsList = document.getElementById('improvementsList');
            
            strengthsList.innerHTML = '';
            improvementsList.innerHTML = '';
            
            if (result.detailed_feedback) {{
                result.detailed_feedback.strengths.forEach(strength => {{
                    const li = document.createElement('li');
                    li.textContent = strength;
                    strengthsList.appendChild(li);
                }});
                
                result.detailed_feedback.improvements.forEach(improvement => {{
                    const li = document.createElement('li');
                    li.textContent = improvement;
                    improvementsList.appendChild(li);
                }});
            }}
            
            assessmentResults.style.display = 'block';
            assessmentResults.scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        // Save draft functionality
        saveBtn.addEventListener('click', function() {{
            localStorage.setItem('ielts_essay_draft_{session_id}', essayText.value);
            statusBar.className = 'status-bar status-ready';
            statusBar.textContent = 'Draft saved successfully';
            setTimeout(() => {{
                if (!assessmentSubmitted) {{
                    const words = essayText.value.trim().split(/\\s+/).filter(word => word.length > 0);
                    if (words.length >= parseInt(minWords.textContent)) {{
                        statusBar.className = 'status-bar status-ready';
                        statusBar.textContent = 'Ready for Nova Micro assessment';
                    }} else {{
                        statusBar.className = 'status-bar status-waiting';
                        statusBar.textContent = `Write at least ${{minWords.textContent}} words to enable assessment`;
                    }}
                }}
            }}, 2000);
        }});
        
        // Submit button event
        submitBtn.addEventListener('click', submitEssay);
        
        // Initialize page
        window.addEventListener('load', function() {{
            // Start the 60-minute timer immediately
            startTimer();
            
            // Load saved draft if available
            const savedDraft = localStorage.getItem('ielts_essay_draft_{session_id}');
            if (savedDraft) {{
                essayText.value = savedDraft;
                essayText.dispatchEvent(new Event('input'));
                statusBar.className = 'status-bar status-ready';
                statusBar.textContent = 'Draft loaded - continue writing or submit for assessment';
            }}
            
            // Start official IELTS timer
            startTimer();
            
            // Focus on essay area
            essayText.focus();
        }});
    </script>
        let timeRemaining = 40 * 60; // 40 minutes in seconds
        let timerInterval = null;
        let assessmentSubmitted = false;
        
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const minWords = document.getElementById('minWords');
        const submitBtn = document.getElementById('submitBtn');
        const saveBtn = document.getElementById('saveBtn');
        const status = document.getElementById('status');
        const timer = document.getElementById('timer');
        const assessmentResult = document.getElementById('assessmentResult');
        
        // Start timer
        function startTimer() {{
            timerInterval = setInterval(() => {{
                timeRemaining--;
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
                timer.textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
                
                if (timeRemaining <= 0) {{
                    clearInterval(timerInterval);
                    timer.textContent = "Time's up!";
                    if (!assessmentSubmitted) {{
                        submitEssay();
                    }}
                }}
            }}, 1000);
        }}
        
        // Update word count and enable/disable submit button
        essayText.addEventListener('input', function() {{
            const words = this.value.trim().split(/\\s+/).filter(word => word.length > 0);
            const currentWordCount = words.length;
            wordCount.textContent = currentWordCount;
            
            // Enable submit button if minimum word count is met
            if (currentWordCount >= parseInt(minWords.textContent)) {{
                submitBtn.disabled = false;
                submitBtn.className = 'btn btn-primary';
                status.textContent = 'Ready for Nova Micro assessment';
            }} else {{
                submitBtn.disabled = true;
                submitBtn.className = 'btn btn-disabled';
                status.textContent = `Write at least ${{minWords.textContent}} words to enable assessment`;
            }}
        }});
        
        // Submit essay for Nova Micro assessment
        async function submitEssay() {{
            if (assessmentSubmitted) return;
            
            assessmentSubmitted = true;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting to Nova Micro...';
            status.textContent = 'Nova Micro is analyzing your writing...';
            
            try {{
                const response = await fetch('/api/nova-micro/writing', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        essay_text: essayText.value,
                        prompt: document.getElementById('taskPrompt').textContent,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}',
                        user_email: '{user_email}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    displayAssessmentResults(result.assessment_result);
                    status.textContent = 'Nova Micro assessment completed successfully';
                }} else {{
                    status.textContent = 'Assessment error: ' + (result.error || 'Unknown error');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Retry Assessment';
                    assessmentSubmitted = false;
                }}
            }} catch (error) {{
                console.error('Assessment error:', error);
                status.textContent = 'Connection error. Please try again.';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Retry Assessment';
                assessmentSubmitted = false;
            }}
        }}
        
        // Display Nova Micro assessment results
        function displayAssessmentResults(result) {{
            document.getElementById('overallScore').textContent = result.overall_band_score;
            document.getElementById('taskScore').textContent = result.task_achievement;
            document.getElementById('coherenceScore').textContent = result.coherence_cohesion;
            document.getElementById('lexicalScore').textContent = result.lexical_resource;
            document.getElementById('grammarScore').textContent = result.grammatical_accuracy;
            document.getElementById('mainFeedback').textContent = result.feedback;
            
            // Display strengths and improvements
            const strengthsList = document.getElementById('strengthsList');
            const improvementsList = document.getElementById('improvementsList');
            
            strengthsList.innerHTML = '';
            improvementsList.innerHTML = '';
            
            if (result.detailed_feedback) {{
                result.detailed_feedback.strengths.forEach(strength => {{
                    const li = document.createElement('li');
                    li.textContent = strength;
                    strengthsList.appendChild(li);
                }});
                
                result.detailed_feedback.improvements.forEach(improvement => {{
                    const li = document.createElement('li');
                    li.textContent = improvement;
                    improvementsList.appendChild(li);
                }});
            }}
            
            assessmentResult.style.display = 'block';
            assessmentResult.scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        // Save draft functionality
        saveBtn.addEventListener('click', function() {{
            localStorage.setItem('essay_draft_{session_id}', essayText.value);
            status.textContent = 'Draft saved locally';
            setTimeout(() => {{
                status.textContent = essayText.value.trim() ? 'Continue writing...' : 'Start writing to enable assessment...';
            }}, 2000);
        }});
        
        // Submit button click handler
        submitBtn.addEventListener('click', submitEssay);
        
        // Load saved draft if available
        window.addEventListener('load', function() {{
            const savedDraft = localStorage.getItem('essay_draft_{session_id}');
            if (savedDraft) {{
                essayText.value = savedDraft;
                essayText.dispatchEvent(new Event('input'));
            }}
            
            startTimer();
        }});
    </script>
</body>
</html>
"""

def handle_maya_introduction(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Maya's auto-start introduction for speaking assessments"""
    try:
        assessment_type = data.get('assessment_type')
        user_email = data.get('user_email')
        session_id = data.get('session_id')
        
        # Get assessment rubric and Nova Sonic prompts
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        nova_prompts = rubric.get('nova_sonic_prompts', {}) if rubric else {}
        
        # Generate Maya's introduction based on assessment type and proper IELTS structure
        if 'academic' in assessment_type:
            introduction = f"Hello, I'm Maya, your IELTS examiner. Today we'll be conducting the Academic Speaking test. This assessment has three parts: Part 1 is an interview lasting 4-5 minutes, Part 2 is a long turn where you'll speak for 2 minutes after 1 minute preparation, and Part 3 is a discussion lasting 4-5 minutes. The total test time is 11-14 minutes. Let's begin with Part 1. Can you tell me your name and where you're from?"
        else:
            introduction = f"Hello, I'm Maya, your IELTS examiner. Today we'll be conducting the General Training Speaking test. This assessment has three parts: Part 1 is an interview lasting 4-5 minutes, Part 2 is a long turn where you'll speak for 2 minutes after 1 minute preparation, and Part 3 is a discussion lasting 4-5 minutes. The total test time is 11-14 minutes. Let's start with Part 1. What's your name and what do you do for work?"
        
        print(f"[CLOUDWATCH] Maya introduction started for {user_email} - {assessment_type}")
        
        # In production, this would call Nova Sonic to generate audio
        # For now, return text response with mock audio URL
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'introduction': introduction,
                'audio_url': '/api/maya/audio/introduction.mp3',  # Mock audio URL
                'assessment_part': 1,
                'nova_sonic_status': 'connected'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Maya introduction error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_maya_conversation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Maya's conversation responses during speaking assessment"""
    try:
        user_message = data.get('user_message')
        assessment_type = data.get('assessment_type')
        session_id = data.get('session_id')
        
        # Get assessment rubric for context
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        nova_prompts = rubric.get('nova_sonic_prompts', {}) if rubric else {}
        
        # Generate Maya's response based on user input and proper IELTS 3-part structure
        # In production, this would use Nova Sonic bi-directional streaming
        assessment_part = data.get('assessment_part', 1)
        
        if assessment_part == 1:
            # Part 1: Interview questions (4-5 minutes)
            if 'name' in user_message.lower() and 'from' in user_message.lower():
                response = "Thank you. Now, let's talk about your work or studies. What do you do for a living, and how long have you been doing this?"
            elif 'work' in user_message.lower() or 'job' in user_message.lower() or 'study' in user_message.lower():
                response = "That's interesting. What do you enjoy most about your work? And what would you like to change about it if you could?"
            else:
                response = "I see. Let's move to another topic. Can you tell me about your hometown? What's it like there?"
        elif assessment_part == 2:
            # Part 2: Long turn (3-4 minutes total - 1 min prep, 2 min speaking)
            response = "Excellent. Now we're moving to Part 2. I'll give you a topic and you'll have 1 minute to prepare, then speak for 2 minutes. Here's your topic card."
        elif assessment_part == 3:
            # Part 3: Discussion (4-5 minutes)
            response = "Great. Now let's move to Part 3 - a discussion. I'll ask you some more abstract questions related to the topic you just spoke about."
        else:
            response = "Thank you for your response. Let's continue with the next question."
        
        print(f"[CLOUDWATCH] Maya conversation - User: {user_message[:50]}...")
        
        # Store conversation in assessment results
        aws_mock.store_assessment_result({
            'result_id': f"{session_id}_{int(time.time())}",
            'user_email': data.get('user_email', 'unknown'),
            'assessment_type': assessment_type,
            'conversation_turn': {
                'user_message': user_message,
                'maya_response': response,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'response': response,
                'audio_url': '/api/maya/audio/response.mp3',  # Mock audio URL
                'assessment_part': 1,
                'continue_conversation': True
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Maya conversation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_nova_micro_writing(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Nova Micro writing assessment requests"""
    try:
        essay_text = data.get('essay_text', '')
        prompt = data.get('prompt', '')
        assessment_type = data.get('assessment_type', 'academic_writing')
        session_id = data.get('session_id')
        
        if not essay_text or not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Essay text and prompt are required'
                })
            }
        
        # Get assessment rubric for Nova Micro prompts
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        nova_prompts = rubric.get('nova_micro_prompts', {}) if rubric else {}
        
        # Analyze essay using Nova Micro criteria
        word_count = len(essay_text.split())
        min_words = 250 if 'task_2' in assessment_type else 150
        
        # Task Achievement/Response analysis
        task_score = 7.0 if word_count >= min_words else 6.0
        if 'argument' in essay_text.lower() and 'conclusion' in essay_text.lower():
            task_score += 0.5
        
        # Coherence and Cohesion analysis
        coherence_score = 6.5
        if 'however' in essay_text.lower() or 'furthermore' in essay_text.lower():
            coherence_score += 0.5
        
        # Lexical Resource analysis
        lexical_score = 7.0 if len(set(essay_text.lower().split())) > 100 else 6.0
        
        # Grammatical Range and Accuracy
        grammar_score = 6.5
        if '.' in essay_text and ',' in essay_text:
            grammar_score += 0.5
        
        overall_score = round((task_score + coherence_score + lexical_score + grammar_score) / 4, 1)
        
        assessment_result = {
            'task_achievement': task_score,
            'coherence_cohesion': coherence_score,
            'lexical_resource': lexical_score,
            'grammatical_accuracy': grammar_score,
            'overall_band_score': overall_score,
            'word_count': word_count,
            'feedback': f"Your essay demonstrates {overall_score} band level writing. Strong areas include task response and lexical variety. Consider improving coherence devices and grammatical complexity.",
            'detailed_feedback': {
                'strengths': ['Clear position', 'Appropriate length', 'Good vocabulary range'],
                'improvements': ['Use more linking words', 'Vary sentence structures', 'Check minor grammar errors']
            },
            'processed_by': 'Nova Micro',
            'assessment_type': assessment_type
        }
        
        # Store assessment result
        if session_id:
            aws_mock.store_assessment_result({
                'result_id': f"{session_id}_{int(time.time())}",
                'user_email': data.get('user_email', 'unknown'),
                'assessment_type': assessment_type,
                'essay_text': essay_text,
                'prompt': prompt,
                'assessment_result': assessment_result,
                'created_at': datetime.utcnow().isoformat()
            })
        
        print(f"[CLOUDWATCH] Nova Micro assessment completed - Overall band: {overall_score}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'assessment_result': assessment_result,
                'nova_micro_status': 'completed'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Nova Micro writing error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_nova_micro_submit(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle writing assessment submission"""
    try:
        return handle_nova_micro_writing(data)
    except Exception as e:
        print(f"[CLOUDWATCH] Nova Micro submit error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_apple_purchase_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Apple App Store in-app purchase verification"""
    try:
        receipt_data = data.get('receipt_data')
        product_id = data.get('product_id')
        
        if not receipt_data or not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing receipt_data or product_id'
                })
            }
        
        print(f"[CLOUDWATCH] Apple purchase verification: {product_id}")
        
        # In development environment, simulate successful verification
        # In production, this would verify with Apple's App Store servers
        verification_result = {
            'success': True,
            'product_id': product_id,
            'transaction_id': f"apple_txn_{int(time.time())}",
            'verified': True,
            'environment': 'development'
        }
        
        # Store purchase record in DynamoDB
        purchase_record = {
            'transaction_id': verification_result['transaction_id'],
            'product_id': product_id,
            'platform': 'apple',
            'verified_at': datetime.utcnow().isoformat(),
            'receipt_data': receipt_data[:50] + "..." if len(receipt_data) > 50 else receipt_data
        }
        
        # Store in mock DynamoDB purchase records table
        aws_mock.purchase_records_table.put_item(purchase_record)
        
        print(f"[CLOUDWATCH] Apple purchase verified: {verification_result['transaction_id']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(verification_result)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Apple purchase verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_google_purchase_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Google Play Store in-app purchase verification"""
    try:
        purchase_token = data.get('purchase_token')
        product_id = data.get('product_id')
        
        if not purchase_token or not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing purchase_token or product_id'
                })
            }
        
        print(f"[CLOUDWATCH] Google purchase verification: {product_id}")
        
        # In development environment, simulate successful verification
        # In production, this would verify with Google Play Developer API
        verification_result = {
            'success': True,
            'product_id': product_id,
            'transaction_id': f"google_txn_{int(time.time())}",
            'verified': True,
            'environment': 'development'
        }
        
        # Store purchase record in DynamoDB
        purchase_record = {
            'transaction_id': verification_result['transaction_id'],
            'product_id': product_id,
            'platform': 'google',
            'verified_at': datetime.utcnow().isoformat(),
            'purchase_token': purchase_token[:50] + "..." if len(purchase_token) > 50 else purchase_token
        }
        
        # Store in mock DynamoDB purchase records table
        aws_mock.purchase_records_table.put_item(purchase_record)
        
        print(f"[CLOUDWATCH] Google purchase verified: {verification_result['transaction_id']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(verification_result)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Google purchase verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_website_qr_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle website QR authentication request - generates unique QR for website login"""
    try:
        # Generate unique website authentication token
        website_token_id = str(uuid.uuid4())
        
        # Create QR data with unique identifier and domain verification
        qr_data = {
            'type': 'website_auth',
            'token_id': website_token_id,
            'domain': 'ieltsaiprep.com',
            'timestamp': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
        # Store authentication token in DynamoDB with pending status
        auth_token = {
            'token_id': website_token_id,
            'type': 'website_auth',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            'authenticated_user': None,
            'user_products': None
        }
        
        aws_mock.store_qr_token(auth_token)
        
        # Generate QR code image
        qr_code_image = generate_qr_code(json.dumps(qr_data))
        
        print(f"[CLOUDWATCH] Website QR token generated: {website_token_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token_id': website_token_id,
                'qr_code_image': qr_code_image,
                'expires_at': auth_token['expires_at'],
                'expires_in_minutes': 10
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Website QR request error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_website_auth_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if website QR token has been authenticated by mobile app"""
    try:
        token_id = data.get('token_id')
        
        if not token_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'error': 'Missing token_id'})
            }
        
        # Get token from DynamoDB
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'expired': True})
            }
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.utcnow() > expires_at:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'expired': True})
            }
        
        # Check authentication status
        if token_data.get('status') == 'authenticated':
            # Create website session for authenticated user
            session_id = f"web_session_{int(time.time())}_{token_id[:8]}"
            session_data = {
                'session_id': session_id,
                'user_email': token_data['authenticated_user'],
                'products': token_data['user_products'],
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': time.time() + 3600,  # 1 hour
                'auth_method': 'mobile_qr'
            }
            
            aws_mock.create_session(session_data)
            
            print(f"[CLOUDWATCH] Website session created: {session_id} for {token_data['authenticated_user']}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Set-Cookie': f'web_session_id={session_id}; Max-Age=3600; Path=/'
                },
                'body': json.dumps({
                    'authenticated': True,
                    'user_email': token_data['authenticated_user'],
                    'products': token_data['user_products'],
                    'session_id': session_id
                })
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'waiting': True})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Website auth check error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'authenticated': False, 'error': str(e)})
        }

def handle_mobile_qr_scan(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle mobile app scanning website QR code - authenticates specific user"""
    try:
        qr_data = data.get('qr_data')
        user_email = data.get('user_email')
        user_products = data.get('user_products', [])
        
        if not qr_data or not user_email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing qr_data or user_email'
                })
            }
        
        # Parse QR data
        try:
            qr_info = json.loads(qr_data)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid QR code format'
                })
            }
        
        # Validate QR code structure
        if (qr_info.get('type') != 'website_auth' or 
            qr_info.get('domain') != 'ieltsaiprep.com' or 
            not qr_info.get('token_id')):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid QR code - not an IELTS GenAI Prep authentication code'
                })
            }
        
        token_id = qr_info['token_id']
        
        # Get and validate token
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code expired or invalid'
                })
            }
        
        # Check if already used
        if token_data.get('status') == 'authenticated':
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code already used'
                })
            }
        
        # Update token with user authentication
        token_data['status'] = 'authenticated'
        token_data['authenticated_user'] = user_email
        token_data['user_products'] = user_products
        token_data['authenticated_at'] = datetime.utcnow().isoformat()
        
        aws_mock.store_qr_token(token_data)
        
        print(f"[CLOUDWATCH] Mobile QR scan successful: {user_email} authenticated token {token_id}")
        print(f"[CLOUDWATCH] User products: {user_products}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Authentication successful',
                'user_email': user_email,
                'products': user_products
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Mobile QR scan error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_generate_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token generation after purchase verification"""
    try:
        user_email = data.get('user_email')
        product_id = data.get('product_id')
        purchase_verified = data.get('purchase_verified', False)
        
        if not all([user_email, product_id, purchase_verified]):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required fields: user_email, product_id, purchase_verified'
                })
            }
        
        # Generate unique token
        token_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Store in AuthTokens table (DynamoDB simulation)
        token_data = {
            'token_id': token_id,
            'user_email': user_email,
            'product_id': product_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': int(expires_at.timestamp()),
            'ttl': int(expires_at.timestamp()),
            'used': False,
            'purchase_verified': purchase_verified
        }
        
        # Store token using AWS mock service
        aws_mock.store_qr_token(token_data)
        
        # Generate QR code image
        qr_code_image = generate_qr_code(token_id)
        
        print(f"[CLOUDWATCH] QR Token Generated: {token_id} for {user_email} - Product: {product_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token_id': token_id,
                'user_email': user_email,
                'product_id': product_id,
                'expires_at': expires_at.isoformat(),
                'expires_in_minutes': 10,
                'qr_code_image': f'data:image/png;base64,{qr_code_image}'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Generation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_verify_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token verification and session creation"""
    try:
        token_id = data.get('token')
        
        if not token_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Token required'})
            }
        
        print(f"[CLOUDWATCH] QR Verification attempt: {token_id}")
        
        # Retrieve token from AuthTokens table
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            print(f"[CLOUDWATCH] QR Verification failed: Invalid token {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Invalid token'})
            }
        
        current_time = int(time.time())
        expires_at = token_data.get('expires_at', 0)
        
        # Check token expiry
        if current_time > expires_at:
            print(f"[CLOUDWATCH] QR Verification failed: Expired token {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code expired. Please generate a new one from your mobile app.'
                })
            }
        
        # Check if token already used
        if token_data.get('used'):
            print(f"[CLOUDWATCH] QR Verification failed: Token already used {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code already used. Please generate a new one.'
                })
            }
        
        # Mark token as used
        token_data['used'] = True
        token_data['used_at'] = datetime.utcnow().isoformat()
        
        # Create ElastiCache session (1-hour expiry)
        session_id = f"session_{int(time.time())}_{token_id[:8]}"
        session_data = {
            'session_id': session_id,
            'user_email': token_data['user_email'],
            'product_id': token_data.get('product_id'),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': time.time() + 3600,
            'authenticated_via': 'qr_token',
            'purchased_products': [token_data.get('product_id')]
        }
        
        # Store session using AWS mock service
        aws_mock.create_session(session_data)
        
        print(f"[CLOUDWATCH] QR Verification successful: {token_id} -> Session: {session_id}")
        print(f"[CLOUDWATCH] User {token_data['user_email']} authenticated with products: {session_data['purchased_products']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Set-Cookie': f'qr_session_id={session_id}; Max-Age=3600; Path=/'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Authentication successful',
                'session_id': session_id,
                'user_email': token_data['user_email'],
                'redirect_url': '/profile'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_assessment_access(path: str, headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment access with session verification"""
    try:
        # Extract assessment type from path
        assessment_type = path.split('/')[-1]
        
        # Get session from cookie header
        cookie_header = headers.get('Cookie', headers.get('cookie', ''))
        session_id = None
        
        for cookie in cookie_header.split(';'):
            if 'qr_session_id=' in cookie:
                session_id = cookie.split('qr_session_id=')[1].strip()
                break
        
        if not session_id:
            print(f"[CLOUDWATCH] Assessment access denied: No session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {'Location': '/'},
                'body': ''
            }
        
        # Verify session in ElastiCache
        session_data = aws_mock.get_session(session_id)
        
        if not session_data:
            print(f"[CLOUDWATCH] Assessment access denied: Invalid session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {'Location': '/'},
                'body': ''
            }
        
        user_email = session_data['user_email']
        purchased_products = session_data.get('purchased_products', [])
        
        # Check if user has purchased this assessment type
        if assessment_type not in purchased_products:
            print(f"[CLOUDWATCH] Assessment access denied: {user_email} has not purchased {assessment_type}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': f"""
                <!DOCTYPE html>
                <html>
                <head><title>Access Restricted</title></head>
                <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                    <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                        <h2>🔒 Assessment Access Restricted</h2>
                        <p>You need to purchase the <strong>{assessment_type.replace('_', ' ').title()}</strong> assessment to access this content.</p>
                        <div style="margin-top: 20px;">
                            <a href="/test-mobile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Purchase on Mobile App</a>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        
        print(f"[CLOUDWATCH] Assessment access granted: {user_email} accessing {assessment_type}")
        
        # Load appropriate assessment template based on type
        template_content = get_assessment_template(assessment_type, user_email, session_id)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': template_content
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Assessment access error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        health_data = aws_mock.get_health_status()
        health_data['lambda'] = {
            'status': 'healthy',
            'memory_usage': '128MB',
            'cold_starts': 0,
            'architecture': 'serverless'
        }
        
        print(f"[CLOUDWATCH] Health check: healthy")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(health_data)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Health check failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'unhealthy', 'error': str(e)})
        }

def handle_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration with DynamoDB storage"""
    try:
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not name or not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'All fields are required'})
            }
        
        if len(password) < 6:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Password must be at least 6 characters'})
            }
        
        # Check if user already exists
        existing_user = aws_mock.users_table.get_item(email)
        if existing_user:
            return {
                'statusCode': 409,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'User already exists with this email'})
            }
        
        # Hash password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user record
        user_data = {
            'user_id': email,
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'products': [],
            'last_login': None
        }
        
        # Store in DynamoDB
        success = aws_mock.users_table.put_item(user_data)
        
        if success:
            aws_mock.log_event('UserAuth', f'User registered: {email}')
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True, 
                    'user': {
                        'name': name,
                        'email': email,
                        'products': []
                    }
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Failed to create user account'})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] User registration error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': 'Registration failed'})
        }

def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login with bcrypt authentication and reCAPTCHA v2 verification"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        recaptcha_response = data.get('g-recaptcha-response', '')
        user_ip = data.get('user_ip')
        
        # Validate input
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Email and password are required'})
            }
        
        # Verify reCAPTCHA v2
        if not verify_recaptcha_v2(recaptcha_response, user_ip):
            aws_mock.log_event('SecurityAuth', f'reCAPTCHA verification failed for: {email}')
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Please complete the reCAPTCHA verification'})
            }
        
        # Verify credentials using bcrypt
        user_data = aws_mock.verify_credentials(email, password)
        
        if not user_data:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Invalid email or password'})
            }
        
        # Create web session (1 hour TTL)
        session_id = f"web_session_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        session_data = {
            'session_id': session_id,
            'user_email': email,
            'user_id': user_data['user_id'],
            'created_at': time.time(),
            'type': 'web'
        }
        aws_mock.create_session(session_data)
        
        aws_mock.log_event('UserAuth', f'User logged in via web: {email}')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Set-Cookie': f'web_session_id={session_id}; Path=/; HttpOnly; Max-Age=3600'
            },
            'body': json.dumps({
                'success': True,
                'user': {
                    'email': user_data['email'],
                    'purchases': user_data.get('purchases', [])
                },
                'redirect_url': '/dashboard'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] User login error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': 'Login failed'})
        }

def handle_robots_txt() -> Dict[str, Any]:
    """Serve robots.txt for AI crawling optimization"""
    try:
        with open('robots.txt', 'r', encoding='utf-8') as f:
            robots_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain',
                'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
                'Access-Control-Allow-Origin': '*'
            },
            'body': robots_content
        }
    except FileNotFoundError:
        # Fallback robots.txt content for AI crawling
        fallback_content = '''# AI Bot Crawlers - Explicitly Allow All Major AI Services
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bard
Allow: /

User-agent: Gemini
Allow: /

User-agent: PaLM
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: CCBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
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

User-agent: Baiduspider
Allow: /

User-agent: YandexBot
Allow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

# Allow All Other Crawlers
User-agent: *
Allow: /

# Crawl Delay (1 second between requests)
Crawl-delay: 1

# Sitemap Location
Sitemap: https://www.ieltsgenaiprep.com/sitemap.xml'''
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain',
                'Cache-Control': 'public, max-age=86400',
                'Access-Control-Allow-Origin': '*'
            },
            'body': fallback_content
        }