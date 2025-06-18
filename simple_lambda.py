#!/usr/bin/env python3
"""
Production AWS Lambda Handler for IELTS GenAI Prep
Fixed version with correct HTML template matching Replit preview
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
        if path == '/' and http_method == 'GET':
            return handle_website_home()
        elif path == '/health' and http_method == 'GET':
            return handle_health_check()
        elif path == '/api/register' and http_method == 'POST':
            return handle_user_registration(data, dynamodb)
        elif path == '/api/login' and http_method == 'POST':
            return handle_user_login(data, dynamodb)
        elif path.startswith('/assessments/') and http_method == 'GET':
            return handle_assessment_access(path, headers, dynamodb)
        else:
            return error_response("Endpoint not found", 404)
            
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return error_response(f"Internal server error: {str(e)}", 500)

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
    <meta name="description" content="IELTS GenAI Prep - Your comprehensive IELTS assessment preparation platform">
    <title>IELTS GenAI Prep</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
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
        
        /* Fix for mobile hero section spacing */
        @media (max-width: 768px) {
            .hero {
                padding: 60px 0;
            }
            
            .display-4 {
                font-size: 2rem;
            }
        }
    </style>
</head>

<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="#" aria-label="IELTS GenAI Prep Home">IELTS GenAI Prep</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#assessments">Assessments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            Legal
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
                            <li><a class="dropdown-item" href="/privacy-policy">Privacy Policy</a></li>
                            <li><a class="dropdown-item" href="/terms-of-service">Terms of Service</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="row">
                <div class="col-lg-12 text-center">
                    <h1 class="display-4 fw-bold mb-3">Master IELTS with the World's ONLY GenAI Assessment Platform</h1>
                    <div class="alert mx-auto mb-4" style="max-width: 700px; background: rgba(23, 162, 184, 0.9); border: none; color: white; padding: 15px; border-radius: 8px;">
                        <strong>Powered by TrueScore® & ClearScore® - Industry-Leading Standardized Assessment Technology</strong>
                    </div>
                    <p class="lead mb-4" style="max-width: 800px; margin: 0 auto;">IELTS GenAI Prep delivers precise, examiner-aligned feedback through our exclusive TrueScore® writing analysis and ClearScore® speaking assessment systems. Our proprietary technology applies the official IELTS marking criteria to provide consistent, accurate band scores and actionable feedback for both Academic and General Training.</p>
                    <div class="row justify-content-center mb-4">
                        <div class="col-auto" style="color: white;">
                            <i class="fas fa-circle me-2" style="font-size: 0.8rem;"></i>Standardized Assessment
                        </div>
                        <div class="col-auto" style="color: white;">
                            <i class="fas fa-circle me-2" style="font-size: 0.8rem;"></i>IELTS Criteria Aligned
                        </div>
                        <div class="col-auto" style="color: white;">
                            <i class="fas fa-circle me-2" style="font-size: 0.8rem;"></i>Personalized Feedback
                        </div>
                    </div>
                    <div class="d-flex justify-content-center gap-3 flex-wrap">
                        <a href="/login" class="btn btn-primary btn-lg px-4">
                            <i class="fas fa-sign-in-alt me-2"></i>Access Portal
                        </a>
                        <a href="#assessments" class="btn btn-outline-light btn-lg px-4">
                            View Assessments
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Exclusive Technology Showcase -->
    <section class="py-5 bg-white">
        <div class="container">
            <h2 class="text-center mb-5">The World's ONLY Standardized IELTS GenAI Assessment System</h2>
            <p class="text-center text-muted mb-5">Our proprietary technologies deliver consistent, examiner-aligned evaluations</p>
            
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card h-100 border-success">
                        <div class="card-header bg-success text-white text-center">
                            <h3 class="mb-0">TrueScore® Writing Assessment</h3>
                            <div class="mt-2">
                                <i class="fas fa-pencil-alt fa-2x"></i>
                                <small class="d-block mt-1">EXCLUSIVE TECHNOLOGY</small>
                            </div>
                        </div>
                        <div class="card-body">
                            <p>Our proprietary TrueScore® system is the only GenAI technology that standardizes writing assessment within the official IELTS marking criteria rubric. Receive detailed feedback on Task Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy for both Academic and General Training tasks.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6 mb-4">
                    <div class="card h-100 border-primary">
                        <div class="card-header bg-primary text-white text-center">
                            <h3 class="mb-0">ClearScore® Speaking Assessment</h3>
                            <div class="mt-2">
                                <i class="fas fa-microphone-alt fa-2x"></i>
                                <small class="d-block mt-1">EXCLUSIVE TECHNOLOGY</small>
                            </div>
                        </div>
                        <div class="card-body">
                            <p>ClearScore® is the world's first GenAI system to precisely assess IELTS speaking performance across all official criteria. Its sophisticated speech analysis delivers comprehensive feedback on Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, and Pronunciation for all three speaking assessment sections.</p>
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
                        <i class="fas fa-clipboard-check fa-4x text-primary mb-3"></i>
                        <h3 class="h4">Comprehensive IELTS Assessment Preparation</h3>
                        <p>Master the IELTS Writing and Speaking modules with the world's only GenAI-driven assessments aligned with the official IELTS band descriptors for accurate feedback for both IELTS Academic and General Training. Boost your skills and achieve your target score with confidence.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-user-graduate fa-4x text-success mb-3"></i>
                        <h3 class="h4">Your Personal GenAI IELTS Coach</h3>
                        <p>Get detailed feedback aligned with the official IELTS assessment criteria on both speaking and writing tasks with TrueScore® and ClearScore®.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-globe fa-4x text-info mb-3"></i>
                        <h3 class="h4">Global Assessment Preparation: At Your Own Pace, from Anywhere</h3>
                        <p>Whether you're a student striving for academic success or an individual chasing new horizons through study or career opportunities abroad, our inclusive platform empowers your goals, delivering world-class assessment preparation tailored to your journey, wherever you are.</p>
                    </div>
                </div>
            </div>
            
            <div class="row justify-content-center">
                <div class="col-md-8 text-center">
                    <div class="card p-3">
                        <i class="fas fa-mobile-alt fa-4x text-warning mb-3"></i>
                        <h3 class="h4">Cross-Platform Access</h3>
                        <p>Study anywhere with our mobile app and web platform synchronization</p>
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
                                <a href="/login" class="btn btn-lg btn-block btn-success w-100">Purchase via Mobile App</a>
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
                                <a href="/login" class="btn btn-lg btn-block btn-success w-100">Purchase via Mobile App</a>
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
                                <a href="/login" class="btn btn-lg btn-block btn-primary w-100">Purchase via Mobile App</a>
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
                                <a href="/login" class="btn btn-lg btn-block btn-primary w-100">Purchase via Mobile App</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-5" id="how-it-works">
        <div class="container">
            <h2 class="text-center mb-5">How to Access Your GenAI Assessments</h2>
            <div class="row">
                <div class="col-md-4 mb-4 text-center">
                    <div class="mb-3">
                        <i class="fas fa-mobile-alt fa-3x text-primary"></i>
                    </div>
                    <h4>1. Download Mobile App</h4>
                    <p>Get IELTS GenAI Prep from the App Store or Google Play Store</p>
                </div>
                <div class="col-md-4 mb-4 text-center">
                    <div class="mb-3">
                        <i class="fas fa-credit-card fa-3x text-warning"></i>
                    </div>
                    <h4>2. Purchase & Register</h4>
                    <p>Create your account and purchase assessment packages for $36.00 each through secure app store billing</p>
                </div>
                <div class="col-md-4 mb-4 text-center">
                    <div class="mb-3">
                        <i class="fas fa-laptop fa-3x text-success"></i>
                    </div>
                    <h4>3. Login Anywhere</h4>
                    <p>Use your mobile app credentials to login on this website for desktop access, or continue using the mobile app</p>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12 text-center">
                    <div class="alert alert-success">
                        <h5 class="mb-2"><i class="fas fa-shield-alt me-2"></i>Secure Cross-Platform Access</h5>
                        <p class="mb-0">One account, multiple platforms. After purchasing in the mobile app, use the same login credentials to access assessments on desktop/laptop through this website.</p>
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
                    <p class="mb-1">The World's ONLY GenAI Assessment Platform</p>
                    <p class="small">Powered by TrueScore® & ClearScore® Technology</p>
                </div>
                <div class="col-md-6">
                    <h6>Legal</h6>
                    <ul class="list-unstyled">
                        <li><a href="/privacy-policy" class="text-light">Privacy Policy</a></li>
                        <li><a href="/terms-of-service" class="text-light">Terms of Service</a></li>
                    </ul>
                </div>
            </div>
            <hr>
            <div class="row">
                <div class="col-12 text-center">
                    <p class="mb-0">&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

def handle_user_registration(data: Dict[str, Any], dynamodb):
    """Handle user registration with simple password hashing"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response("Email and password are required")
        
        # Simple password hashing
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), 
                                          email.encode(), 100000).hex()
        
        # Store user in DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        # Check if user exists
        response = users_table.get_item(Key={'email': email})
        if 'Item' in response:
            return error_response("User already exists")
        
        # Create user
        users_table.put_item(Item={
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'assessment_counts': {
                'academic_writing': 0,
                'general_writing': 0,
                'academic_speaking': 0,
                'general_speaking': 0
            }
        })
        
        logger.info(f"User registered: {email}")
        return success_response({'message': 'User registered successfully'})
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return error_response(f"Registration failed: {str(e)}")

def handle_user_login(data: Dict[str, Any], dynamodb):
    """Handle user login with password verification"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response("Email and password are required")
        
        # Get user from DynamoDB
        users_table = dynamodb.Table('ielts-genai-prep-users')
        response = users_table.get_item(Key={'email': email})
        
        if 'Item' not in response:
            return error_response("Invalid credentials")
        
        user = response['Item']
        
        # Verify password
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), 
                                          email.encode(), 100000).hex()
        
        if password_hash != user['password_hash']:
            return error_response("Invalid credentials")
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions_table = dynamodb.Table('ielts-genai-prep-sessions')
        
        sessions_table.put_item(Item={
            'session_id': session_id,
            'email': email,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        })
        
        logger.info(f"User logged in: {email}")
        return success_response({
            'message': 'Login successful',
            'session_id': session_id,
            'user': {
                'email': email,
                'assessment_counts': user.get('assessment_counts', {})
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return error_response(f"Login failed: {str(e)}")

def handle_assessment_access(path: str, headers: Dict[str, Any], dynamodb):
    """Handle assessment access with session verification"""
    try:
        # Extract session from Authorization header
        auth_header = headers.get('authorization', '')
        if not auth_header.startswith('Bearer '):
            return error_response("Authentication required", 401)
        
        session_id = auth_header.replace('Bearer ', '')
        
        # Verify session
        sessions_table = dynamodb.Table('ielts-genai-prep-sessions')
        response = sessions_table.get_item(Key={'session_id': session_id})
        
        if 'Item' not in response:
            return error_response("Invalid session", 401)
        
        session = response['Item']
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.utcnow() > expires_at:
            return error_response("Session expired", 401)
        
        # Assessment access granted
        return success_response({
            'message': 'Assessment access granted',
            'user_email': session['email'],
            'assessment_path': path
        })
        
    except Exception as e:
        logger.error(f"Assessment access error: {str(e)}")
        return error_response(f"Access denied: {str(e)}", 401)

def success_response(data: Dict[str, Any], status_code: int = 200):
    """Format success response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
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
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps({'error': message})
    }