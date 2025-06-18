#!/usr/bin/env python3
"""
Production AWS Lambda Handler for IELTS GenAI Prep
Simplified version with working authentication and session management
"""

import json
import os
import uuid
import boto3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal objects in JSON serialization"""
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    """Main AWS Lambda handler for production environment"""
    try:
        logger.info(f"Processing: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', '/')}")
        
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
                logger.warning("Invalid JSON in request body")
                pass
        
        # Initialize AWS services
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Route requests
        if path == '/health' or path == '/api/health':
            return handle_health_check()
        elif path == '/' and http_method == 'GET':
            return handle_website_home()
        elif path == '/api/auth/register' and http_method == 'POST':
            return handle_user_registration(data, dynamodb)
        elif path == '/api/auth/login' and http_method == 'POST':
            return handle_user_login(data, dynamodb)
        elif path.startswith('/assessment/'):
            return handle_assessment_access(path, headers, dynamodb)
        else:
            return success_response({
                'message': 'IELTS GenAI Prep API - Production Ready',
                'version': '1.0',
                'environment': 'AWS Lambda',
                'path': path,
                'method': http_method
            })
            
    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}")
        return error_response(f"Service temporarily unavailable", 500)

def handle_health_check():
    """Health check endpoint"""
    return success_response({
        'status': 'healthy',
        'service': 'ielts-genai-prep-api',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'region': 'us-east-1',
        'environment': 'production'
    })

def handle_website_home():
    """Serve IELTS GenAI Prep website homepage"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Test Preparation</title>
    <meta name="description" content="Master IELTS with AI-powered assessment and personalized feedback. Get real-time speaking practice with Maya AI examiner and detailed writing evaluations.">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #667eea;
        }
        
        .hero {
            padding: 120px 0 80px;
            text-align: center;
            color: white;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .btn-primary {
            background: #ff6b6b;
            color: white;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .features {
            padding: 80px 0;
            background: white;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 3rem;
            margin-top: 3rem;
        }
        
        .feature-card {
            text-align: center;
            padding: 2rem;
            border-radius: 20px;
            background: #f8f9fa;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .pricing {
            padding: 80px 0;
            background: #f8f9fa;
            text-align: center;
        }
        
        .pricing-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin: 1rem;
        }
        
        .price {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 1rem 0;
        }
        
        .section-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .assessment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            max-width: 600px;
            margin: 0 auto 4rem;
        }
        
        .writing-card {
            border: 2px solid #4CAF50;
        }
        
        .speaking-card {
            border: 2px solid #2196F3;
        }
        
        .purchase-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            width: 100%;
            font-weight: 600;
            cursor: pointer;
        }
        
        .purchase-btn.speaking {
            background: #2196F3;
        }
        
        .feature-list {
            text-align: left;
            margin: 1.5rem 0;
            color: #666;
            font-size: 0.9rem;
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            margin: 0.5rem 0;
            padding-left: 1rem;
        }
        
        .feature-list li:before {
            content: "✓";
            color: #4CAF50;
            font-weight: bold;
            margin-right: 0.5rem;
            margin-left: -1rem;
        }
        
        .download-section {
            padding: 80px 0;
            background: #2c3e50;
            color: white;
            text-align: center;
        }
        
        .app-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        
        .app-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 12px 24px;
            background: #34495e;
            color: white;
            text-decoration: none;
            border-radius: 10px;
            transition: background 0.3s;
        }
        
        .app-btn:hover {
            background: #4a6741;
        }
        
        footer {
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 2rem 0;
        }
        
        .api-status {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 10px;
            margin: 2rem 0;
            text-align: center;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            margin-right: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .nav-links {
                display: none;
            }
            
            .cta-buttons {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">IELTS GenAI Prep</div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#download">Download</a></li>
            </ul>
        </nav>
    </header>

    <section class="hero">
        <div class="container">
            <h1>Master IELTS with AI</h1>
            <p>Get personalized feedback and real-time practice with our AI-powered IELTS preparation platform</p>
            
            <div class="api-status">
                <span class="status-indicator"></span>
                Production API Active - Ready for App Store Testing
            </div>
            
            <div class="cta-buttons">
                <a href="#download" class="btn btn-primary">
                    <i class="fas fa-download"></i>
                    Download App
                </a>
                <a href="/health" class="btn btn-secondary">
                    <i class="fas fa-heartbeat"></i>
                    API Status
                </a>
            </div>
        </div>
    </section>

    <section id="features" class="features">
        <div class="container">
            <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 1rem;">Why Choose IELTS GenAI Prep?</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-microphone"></i>
                    </div>
                    <h3>ClearScore® Speaking Assessment</h3>
                    <p>Practice with Maya, our AI examiner, for real-time speaking feedback using Amazon Nova Sonic technology.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-edit"></i>
                    </div>
                    <h3>TrueScore® Writing Assessment</h3>
                    <p>Get detailed writing evaluations with AI-powered feedback on coherence, grammar, and vocabulary.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3>Personalized Learning</h3>
                    <p>Adaptive algorithms track your progress and provide customized study recommendations.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-mobile-alt"></i>
                    </div>
                    <h3>Cross-Platform Access</h3>
                    <p>Study anywhere with our mobile app and web platform synchronization.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="pricing" class="pricing">
        <div class="container">
            <div class="section-header">
                <h2 style="font-size: 2rem; margin-bottom: 0.5rem; color: #333; font-weight: 600;">GenAI Assessed IELTS Modules</h2>
                <p style="font-size: 0.95rem; color: #666; max-width: 600px; margin: 0 auto;">Our specialized GenAI technologies provide accurate assessment for IELTS preparation</p>
            </div>
            
            <!-- TrueScore Writing Assessment -->
            <div style="margin-bottom: 3rem;">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✏️</div>
                    <h3 style="font-size: 1.4rem; color: #333; margin-bottom: 0.5rem; font-weight: 600;">TrueScore® Writing Assessment</h3>
                    <p style="color: #666; font-size: 0.9rem; max-width: 700px; margin: 0 auto;">Professional GenAI assessment of IELTS writing tasks aligned with the Official IELTS Band Descriptors on Task Achievement, Coherence and Cohesion, Lexical Resource and Grammatical Range and Accuracy</p>
                </div>
                
                <div class="assessment-grid">
                    <div class="pricing-card writing-card">
                        <div style="background: #4CAF50; color: white; padding: 0.8rem; margin: -2rem -2rem 1.5rem; border-radius: 10px 10px 0 0; font-weight: 600;">Academic Writing</div>
                        <div class="price" style="color: #333;">$36</div>
                        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem;"><strong>for 4 assessments</strong></p>
                        <ul class="feature-list">
                            <li>4 Unique Assessments Included</li>
                            <li>Task 1 & Task 2 Assessment</li>
                            <li>TrueScore® GenAI Evaluation</li>
                            <li>Official IELTS Criteria Alignment</li>
                            <li>Detailed Band Score Feedback</li>
                            <li>Writing Improvement Recommendations</li>
                        </ul>
                        <button class="purchase-btn">Purchase via Mobile App</button>
                    </div>
                    
                    <div class="pricing-card writing-card">
                        <div style="background: #4CAF50; color: white; padding: 0.8rem; margin: -2rem -2rem 1.5rem; border-radius: 10px 10px 0 0; font-weight: 600;">General Training Writing</div>
                        <div class="price" style="color: #333;">$36</div>
                        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem;"><strong>for 4 assessments</strong></p>
                        <ul class="feature-list">
                            <li>4 Unique Assessments Included</li>
                            <li>Letter & Essay Assessment</li>
                            <li>TrueScore® GenAI Evaluation</li>
                            <li>Official IELTS Criteria Alignment</li>
                            <li>Detailed Band Score Feedback</li>
                            <li>Target Band Achievement Support</li>
                        </ul>
                        <button class="purchase-btn">Purchase via Mobile App</button>
                    </div>
                </div>
            </div>
            
            <!-- ClearScore Speaking Assessment -->
            <div>
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎤</div>
                    <h3 style="font-size: 1.4rem; color: #333; margin-bottom: 0.5rem; font-weight: 600;">ClearScore® Speaking Assessment</h3>
                    <p style="color: #666; font-size: 0.9rem; max-width: 700px; margin: 0 auto;">Revolutionary GenAI speaking assessment with real-time conversation analysis covering Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, and Pronunciation</p>
                </div>
                
                <div class="assessment-grid">
                    <div class="pricing-card speaking-card">
                        <div style="background: #2196F3; color: white; padding: 0.8rem; margin: -2rem -2rem 1.5rem; border-radius: 10px 10px 0 0; font-weight: 600;">Academic Speaking</div>
                        <div class="price" style="color: #333;">$36</div>
                        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem;"><strong>for 4 assessments</strong></p>
                        <ul class="feature-list">
                            <li>4 Unique Assessments Included</li>
                            <li>Interactive Maya AI Examiner</li>
                            <li>ClearScore® GenAI Analysis</li>
                            <li>Real-time Speech Assessment</li>
                            <li>Detailed Performance Metrics</li>
                            <li>Pronunciation & Fluency Feedback</li>
                        </ul>
                        <button class="purchase-btn speaking">Purchase via Mobile App</button>
                    </div>
                    
                    <div class="pricing-card speaking-card">
                        <div style="background: #2196F3; color: white; padding: 0.8rem; margin: -2rem -2rem 1.5rem; border-radius: 10px 10px 0 0; font-weight: 600;">General Training Speaking</div>
                        <div class="price" style="color: #333;">$36</div>
                        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem;"><strong>for 4 assessments</strong></p>
                        <ul class="feature-list">
                            <li>4 Unique Assessments Included</li>
                            <li>Maya AI Conversation Partner</li>
                            <li>ClearScore® GenAI Technology</li>
                            <li>Comprehensive Speaking Analysis</li>
                            <li>Real-time Performance Feedback</li>
                            <li>Instant Performance Feedback</li>
                        </ul>
                        <button class="purchase-btn speaking">Purchase via Mobile App</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="download" class="download-section">
        <div class="container">
            <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">Download IELTS GenAI Prep</h2>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">Available on iOS and Android</p>
            <div class="app-buttons">
                <a href="#" class="app-btn">
                    <i class="fab fa-apple"></i>
                    App Store
                </a>
                <a href="#" class="app-btn">
                    <i class="fab fa-google-play"></i>
                    Google Play
                </a>
            </div>
            <p style="margin-top: 2rem; opacity: 0.8;">Ready for App Store deployment and testing</p>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
            <p>Powered by Amazon Nova AI Technology</p>
            <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
                Production API: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod
            </p>
        </div>
    </footer>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

        // API health check
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                console.log('API Status:', data);
                if (data.status === 'healthy') {
                    document.querySelector('.status-indicator').style.background = '#4CAF50';
                }
            })
            .catch(error => {
                console.log('API check failed:', error);
                document.querySelector('.status-indicator').style.background = '#f44336';
            });
    </script>
</body>
</html>'''
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=3600'
        },
        'body': html_content
    }

def handle_user_registration(data: Dict[str, Any], dynamodb):
    """Handle user registration with simple password hashing"""
    try:
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not email or not password:
            return error_response('Email and password required', 400)
        
        # Simple password hashing (SHA-256 with salt)
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        stored_password = salt + password_hash
        
        # Store user in DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        user_id = str(uuid.uuid4())
        
        # Check if user already exists
        response = users_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if response['Items']:
            return error_response('User already exists', 409)
        
        users_table.put_item(
            Item={
                'user_id': user_id,
                'email': email,
                'name': name,
                'password_hash': stored_password.hex(),
                'created_at': datetime.utcnow().isoformat(),
                'assessment_counts': {
                    'academic_writing': {'remaining': 0, 'used': 0},
                    'general_writing': {'remaining': 0, 'used': 0},
                    'academic_speaking': {'remaining': 0, 'used': 0},
                    'general_speaking': {'remaining': 0, 'used': 0}
                }
            }
        )
        
        logger.info(f"User registered successfully: {email}")
        return success_response({
            'message': 'Registration successful',
            'user_id': user_id,
            'email': email
        })
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return error_response('Registration failed', 500)

def handle_user_login(data: Dict[str, Any], dynamodb):
    """Handle user login with password verification"""
    try:
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return error_response('Email and password required', 400)
        
        # Query user from DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        try:
            response = users_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if not response['Items']:
                return error_response('Invalid credentials', 401)
            
            user = response['Items'][0]
            logger.info(f"Found user: {user.get('email', 'unknown')}")
        except Exception as e:
            logger.error(f"DynamoDB scan error: {str(e)}")
            return error_response('Authentication service unavailable', 500)
        
        # Verify password
        try:
            stored_password = bytes.fromhex(user['password_hash'])
            salt = stored_password[:32]
            stored_hash = stored_password[32:]
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            
            if password_hash != stored_hash:
                return error_response('Invalid credentials', 401)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return error_response('Invalid credentials', 401)
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            'token_id': session_id,  # Match table primary key
            'user_email': email,
            'user_id': user['user_id'],
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store session in DynamoDB
        try:
            auth_table = dynamodb.Table('ielts-genai-prep-auth-tokens')
            auth_table.put_item(Item=session_data)
            logger.info(f"Session created successfully for: {email}")
        except Exception as session_error:
            logger.error(f"Session creation error: {str(session_error)}")
            return error_response('Session creation failed', 500)
        
        logger.info(f"User login successful: {email}")
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
    """Handle assessment access with session verification"""
    try:
        assessment_type = path.split('/')[-1]
        
        # Verify session from Authorization header
        auth_header = headers.get('Authorization', headers.get('authorization', ''))
        session_id = auth_header.replace('Bearer ', '') if auth_header else ''
        
        if not session_id:
            return error_response('Authentication required', 401)
        
        # Check session validity
        auth_table = dynamodb.Table('ielts-genai-prep-auth-tokens')
        response = auth_table.get_item(Key={'token_id': session_id})
        
        if 'Item' not in response:
            return error_response('Invalid session', 401)
        
        session = response['Item']
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.utcnow() > expires_at:
            return error_response('Session expired', 401)
        
        logger.info(f"Assessment access granted: {assessment_type} for {session['user_email']}")
        return success_response({
            'assessment_type': assessment_type,
            'user_email': session['user_email'],
            'session_valid': True,
            'access_granted': True,
            'message': f'Access granted to {assessment_type} assessment'
        })
        
    except Exception as e:
        logger.error(f"Assessment access error: {str(e)}")
        return error_response('Assessment access failed', 500)

def success_response(data: Dict[str, Any], status_code: int = 200):
    """Format success response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps(data, cls=DecimalEncoder)
    }

def error_response(message: str, status_code: int = 400):
    """Format error response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps({'error': message, 'status': status_code})
    }