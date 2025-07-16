"""
Minimal Lambda function to restore production website functionality
Removes bcrypt dependency to fix import errors
"""

import json
import os
import uuid
from typing import Dict, Any, Optional
from urllib.parse import unquote
import base64
import hashlib
import hmac
import time
import urllib.request
import urllib.parse

# Simple user storage without bcrypt
USERS_DB = {
    "test@ieltsgenaiprep.com": {
        "password": "test123",  # Plain text for testing
        "first_name": "Test",
        "last_name": "User"
    },
    "prodtest@ieltsgenaiprep.com": {
        "password": "prodtest123",
        "first_name": "Production",
        "last_name": "Test"
    }
}

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Get request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters') or {}
        
        # Parse body for POST requests
        body = event.get('body', '')
        if body:
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(body).decode('utf-8')
        
        # Check CloudFront security header
        cf_secret = headers.get('cf-secret', '')
        if cf_secret != 'CF-Secret-3140348d':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Forbidden - Direct access not allowed'})
            }
        
        # Route requests
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            if http_method == 'GET':
                return handle_login_page()
            elif http_method == 'POST':
                return handle_login_post(body)
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/dashboard':
            return handle_dashboard()
        elif path.startswith('/assessment/'):
            return handle_assessment(path)
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': get_404_page()
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>500 - Internal Server Error</h1><p>{str(e)}</p>'
        }

def handle_home_page():
    """Serve home page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_home_template()
    }

def handle_login_page():
    """Serve login page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_login_template()
    }

def handle_login_post(body):
    """Handle login POST request"""
    try:
        # Parse form data
        form_data = urllib.parse.parse_qs(body)
        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]
        
        # Check credentials
        if email in USERS_DB and USERS_DB[email]['password'] == password:
            # Login successful
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'session_id': str(uuid.uuid4()),
                    'redirect': '/dashboard'
                })
            }
        else:
            # Login failed
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid credentials'
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_privacy_policy():
    """Serve privacy policy page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_privacy_policy_template()
    }

def handle_terms_of_service():
    """Serve terms of service page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_terms_template()
    }

def handle_dashboard():
    """Serve dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_dashboard_template()
    }

def handle_assessment(path):
    """Serve assessment pages"""
    assessment_type = path.split('/')[-1]
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_assessment_template(assessment_type)
    }

def get_home_template():
    """Comprehensive home page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    <meta name="description" content="Master IELTS with AI-powered scoring. Get instant feedback aligned with official IELTS band descriptors for Writing and Speaking assessments.">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
        }
        .assessment-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .assessment-card:hover {
            transform: translateY(-5px);
        }
        .btn-primary {
            background: linear-gradient(135deg, #28a745, #20c997);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
        }
        .feature-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #2c3e50;">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain me-2"></i>IELTS GenAI Prep</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <section class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h1 class="display-4 fw-bold mb-4">Master IELTS with GenAI-Powered Scoring</h1>
                    <p class="lead mb-4">The only AI-based IELTS platform with official band-aligned feedback</p>
                    <div class="mb-4">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-brain me-3" style="color: #ffd700;"></i>
                            <span>AI-Powered Assessment Technology</span>
                        </div>
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-check-circle me-3" style="color: #28a745;"></i>
                            <span>Official IELTS Band Descriptors</span>
                        </div>
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-bullseye me-3" style="color: #17a2b8;"></i>
                            <span>Instant Detailed Feedback</span>
                        </div>
                    </div>
                    <a href="/login" class="btn btn-primary btn-lg me-3">Get Started</a>
                    <a href="#features" class="btn btn-outline-light btn-lg">Learn More</a>
                </div>
                <div class="col-lg-6">
                    <div class="text-center">
                        <i class="fas fa-graduation-cap" style="font-size: 10rem; opacity: 0.3;"></i>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="features" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">GenAI Assessed IELTS Modules</h2>
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card assessment-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-pen-nib feature-icon"></i>
                            <h4 class="card-title text-primary">TrueScore® Writing Assessment</h4>
                            <p class="card-text">Advanced AI evaluation of your writing skills with detailed feedback across all IELTS criteria.</p>
                            <ul class="list-unstyled text-start">
                                <li><i class="fas fa-check text-success me-2"></i>Task Achievement Analysis</li>
                                <li><i class="fas fa-check text-success me-2"></i>Coherence & Cohesion Review</li>
                                <li><i class="fas fa-check text-success me-2"></i>Lexical Resource Assessment</li>
                                <li><i class="fas fa-check text-success me-2"></i>Grammar Range & Accuracy</li>
                            </ul>
                            <p class="fw-bold text-success">$49.99 for 4 Assessments</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card assessment-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-microphone feature-icon"></i>
                            <h4 class="card-title text-info">ClearScore® Speaking Assessment</h4>
                            <p class="card-text">AI-powered speaking evaluation with Maya, your personal IELTS examiner.</p>
                            <ul class="list-unstyled text-start">
                                <li><i class="fas fa-check text-info me-2"></i>Fluency & Coherence Analysis</li>
                                <li><i class="fas fa-check text-info me-2"></i>Lexical Resource Evaluation</li>
                                <li><i class="fas fa-check text-info me-2"></i>Grammar Range Assessment</li>
                                <li><i class="fas fa-check text-info me-2"></i>Pronunciation Review</li>
                            </ul>
                            <p class="fw-bold text-info">$49.99 for 4 Assessments</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">Why Choose IELTS GenAI Prep?</h2>
            <div class="row">
                <div class="col-md-4 text-center mb-4">
                    <i class="fas fa-certificate feature-icon"></i>
                    <h4>Official Band-Descriptive Feedback</h4>
                    <p>Get feedback aligned with official IELTS marking criteria and band descriptors.</p>
                </div>
                <div class="col-md-4 text-center mb-4">
                    <i class="fas fa-mobile-alt feature-icon"></i>
                    <h4>Mobile & Desktop Access</h4>
                    <p>Purchase on mobile app, practice anywhere. Your progress syncs automatically.</p>
                </div>
                <div class="col-md-4 text-center mb-4">
                    <i class="fas fa-trophy feature-icon"></i>
                    <h4>Designed for Success</h4>
                    <p>Comprehensive preparation tools to help you achieve your target IELTS band score.</p>
                </div>
            </div>
        </div>
    </section>

    <section class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">How to Get Started</h2>
            <div class="row">
                <div class="col-md-4 text-center mb-4">
                    <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                        <span class="fs-2 fw-bold">1</span>
                    </div>
                    <h4 class="mt-3">Download Mobile App</h4>
                    <p>Get the IELTS GenAI Prep app from App Store or Google Play</p>
                </div>
                <div class="col-md-4 text-center mb-4">
                    <div class="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                        <span class="fs-2 fw-bold">2</span>
                    </div>
                    <h4 class="mt-3">Choose Your Assessment</h4>
                    <p>Select from Academic/General Writing or Speaking - $49.99 for 4 assessments</p>
                </div>
                <div class="col-md-4 text-center mb-4">
                    <div class="bg-info text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                        <span class="fs-2 fw-bold">3</span>
                    </div>
                    <h4 class="mt-3">Start Practicing</h4>
                    <p>Login here with your mobile app credentials and begin your IELTS preparation</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_login_template():
    """Professional login page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .login-container {
            max-width: 450px;
            margin: 50px auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .mobile-info {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
        }
        .app-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .app-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
        }
        .app-store {
            background: #000;
        }
        .google-play {
            background: #01875f;
        }
        .form-section {
            padding: 30px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            width: 100%;
        }
        .home-btn {
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        .home-btn:hover {
            background: rgba(255,255,255,0.3);
            color: white;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <a href="/" class="home-btn">
                <i class="fas fa-home me-2"></i>Home
            </a>
            <h2><i class="fas fa-brain me-2"></i>Welcome Back</h2>
            <p class="mb-0">Sign in to your IELTS GenAI Prep account</p>
        </div>
        
        <div class="mobile-info">
            <h5><i class="fas fa-mobile-alt me-2"></i>New to IELTS GenAI Prep?</h5>
            <p class="mb-2">Download our mobile app to purchase assessments and create your account. You can then login here to practice on desktop/laptop.</p>
            <div class="app-buttons">
                <a href="#" class="app-btn app-store">
                    <i class="fab fa-apple me-2"></i>App Store
                </a>
                <a href="#" class="app-btn google-play">
                    <i class="fab fa-google-play me-2"></i>Google Play
                </a>
            </div>
        </div>
        
        <div class="form-section">
            <form id="loginForm">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Sign In</button>
            </form>
            <div class="text-center mt-3">
                <a href="#" class="text-muted">Forgot your password?</a>
            </div>
        </div>
    </div>

    <footer class="text-center text-white mt-5">
        <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
        <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
        <a href="/terms-of-service" class="text-white">Terms of Service</a>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = new URLSearchParams(formData);
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: data
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    alert('Login failed: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during login');
            });
        });
    </script>
</body>
</html>"""

def get_privacy_policy_template():
    """Privacy policy page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .back-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
            color: white;
        }
        .content-section {
            padding: 60px 0;
        }
    </style>
</head>
<body>
    <div class="header-section">
        <div class="container">
            <a href="/" class="back-btn mb-3 d-inline-block">
                <i class="fas fa-arrow-left me-2"></i>Back to Home
            </a>
            <h1 class="display-4">Privacy Policy</h1>
            <p class="lead">Last Updated: July 14, 2025</p>
        </div>
    </div>

    <div class="content-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card">
                        <div class="card-body">
                            <h2>Information We Collect</h2>
                            <p>We collect information you provide directly to us, such as when you create an account, make a purchase, or use our assessment services.</p>
                            
                            <h2>How We Use Your Information</h2>
                            <p>We use the information we collect to provide, maintain, and improve our services, including our TrueScore® Writing Assessment and ClearScore® Speaking Assessment technologies.</p>
                            
                            <h2>Data Security</h2>
                            <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
                            
                            <h2>Contact Us</h2>
                            <p>If you have any questions about this Privacy Policy, please contact us through our mobile app or website.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_terms_template():
    """Terms of service page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .back-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
            color: white;
        }
        .content-section {
            padding: 60px 0;
        }
    </style>
</head>
<body>
    <div class="header-section">
        <div class="container">
            <a href="/" class="back-btn mb-3 d-inline-block">
                <i class="fas fa-arrow-left me-2"></i>Back to Home
            </a>
            <h1 class="display-4">Terms of Service</h1>
            <p class="lead">Last Updated: July 14, 2025</p>
        </div>
    </div>

    <div class="content-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card">
                        <div class="card-body">
                            <h2>Service Description</h2>
                            <p>IELTS GenAI Prep provides AI-powered IELTS assessment services including Writing and Speaking evaluations.</p>
                            
                            <h2>Pricing and Payment</h2>
                            <p>Each assessment product is priced at $49.99 CAD and includes 4 assessment attempts. All purchases are processed through Apple App Store or Google Play Store.</p>
                            
                            <h2>Refund Policy</h2>
                            <p>All purchases are non-refundable. Please contact Apple or Google for App Store refund policies.</p>
                            
                            <h2>User Responsibilities</h2>
                            <p>You are responsible for maintaining the confidentiality of your account credentials and for all activities under your account.</p>
                            
                            <h2>Contact Information</h2>
                            <p>For questions about these terms, please contact us through our mobile app or website.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_dashboard_template():
    """Dashboard page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
        }
        .assessment-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .assessment-card:hover {
            transform: translateY(-5px);
        }
        .btn-start {
            background: linear-gradient(135deg, #28a745, #20c997);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #2c3e50;">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain me-2"></i>IELTS GenAI Prep</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Home</a>
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <a class="nav-link" href="#" onclick="logout()">Logout</a>
            </div>
        </div>
    </nav>

    <div class="dashboard-header">
        <div class="container">
            <h1><i class="fas fa-tachometer-alt me-3"></i>Assessment Dashboard</h1>
            <p class="lead">Choose your IELTS assessment type to begin practicing</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-pen-nib text-primary" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">Academic Writing</h4>
                        <p class="card-text">Task 1 & Task 2 Academic Writing Assessment</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/academic-writing" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-pen-nib text-success" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">General Writing</h4>
                        <p class="card-text">Task 1 & Task 2 General Training Writing Assessment</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/general-writing" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-microphone text-info" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">Academic Speaking</h4>
                        <p class="card-text">Full Speaking Assessment with Maya AI Examiner</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/academic-speaking" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-microphone text-warning" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">General Speaking</h4>
                        <p class="card-text">Full Speaking Assessment with Maya AI Examiner</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/general-speaking" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function logout() {
            alert('Logout functionality coming soon!');
        }
    </script>
</body>
</html>"""

def get_assessment_template(assessment_type):
    """Assessment page template"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_type.title()} Assessment - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .assessment-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
        }}
        .timer {{
            font-size: 2rem;
            font-weight: bold;
            color: #dc3545;
        }}
        .question-panel {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            height: 500px;
            overflow-y: auto;
        }}
        .answer-panel {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            height: 500px;
        }}
        .word-count {{
            font-size: 0.9rem;
            color: #6c757d;
        }}
        .submit-btn {{
            background: linear-gradient(135deg, #28a745, #20c997);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            color: white;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #2c3e50;">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain me-2"></i>IELTS GenAI Prep</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <span class="nav-link">|</span>
                <span class="nav-link timer" id="timer">20:00</span>
            </div>
        </div>
    </nav>

    <div class="assessment-header">
        <div class="container">
            <h1><i class="fas fa-file-alt me-3"></i>{assessment_type.replace('-', ' ').title()} Assessment</h1>
            <p class="lead">Complete your IELTS assessment with AI-powered feedback</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-6">
                <div class="question-panel">
                    <h4>Task 1</h4>
                    <p>Write a description of the chart below. You should write at least 150 words.</p>
                    <div class="text-center">
                        <div class="border p-3 bg-light">
                            <p>[Sample Chart/Graph would appear here]</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="answer-panel">
                    <h4>Your Answer</h4>
                    <textarea class="form-control" rows="18" placeholder="Write your answer here..." id="answer" oninput="updateWordCount()"></textarea>
                    <div class="d-flex justify-content-between mt-3">
                        <span class="word-count" id="wordCount">Words: 0</span>
                        <button class="btn submit-btn" onclick="submitAnswer()">Submit Answer</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let timeLeft = 20 * 60; // 20 minutes in seconds
        
        function updateTimer() {{
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            document.getElementById('timer').textContent = 
                `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            
            if (timeLeft > 0) {{
                timeLeft--;
                setTimeout(updateTimer, 1000);
            }} else {{
                alert('Time is up! Submitting your answer...');
                submitAnswer();
            }}
        }}
        
        function updateWordCount() {{
            const text = document.getElementById('answer').value;
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            document.getElementById('wordCount').textContent = `Words: ${{wordCount}}`;
        }}
        
        function submitAnswer() {{
            const answer = document.getElementById('answer').value;
            if (answer.trim().length < 10) {{
                alert('Please write a longer answer before submitting.');
                return;
            }}
            
            alert('Assessment submitted! You will receive detailed feedback shortly.');
            window.location.href = '/dashboard';
        }}
        
        // Start the timer when the page loads
        updateTimer();
    </script>
</body>
</html>"""

def get_404_page():
    """404 error page"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .error-page {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="error-page">
        <div class="container text-center">
            <h1 class="display-1">404</h1>
            <h2>Page Not Found</h2>
            <p class="lead">The page you're looking for doesn't exist.</p>
            <a href="/" class="btn btn-light btn-lg">Go Home</a>
        </div>
    </div>
</body>
</html>"""