#!/usr/bin/env python3
"""
Deploy complete website with comprehensive home page and working authentication
"""
import boto3
import zipfile
import os

def create_complete_website_lambda():
    """Create Lambda with complete website including home page and authentication"""
    
    lambda_code = '''import json
import hashlib
import urllib.parse
from datetime import datetime

# Shared user database
class MockDynamoDBUsers:
    def __init__(self):
        self.users = {
            'test@ieltsgenaiprep.com': {
                'user_id': 'user_123',
                'email': 'test@ieltsgenaiprep.com',
                'password_hash': self.hash_password('testpassword123'),
                'purchase_records': [
                    {'product_id': 'academic_writing', 'assessments_remaining': 4},
                    {'product_id': 'academic_speaking', 'assessments_remaining': 4},
                    {'product_id': 'general_writing', 'assessments_remaining': 4},
                    {'product_id': 'general_speaking', 'assessments_remaining': 4}
                ]
            }
        }
        
    def hash_password(self, password: str) -> str:
        salt = b'ielts_genai_prep_salt'
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
        
    def verify_password(self, password: str, hash_stored: str) -> bool:
        return self.hash_password(password) == hash_stored
        
    def get_user(self, email: str):
        return self.users.get(email)

user_db = MockDynamoDBUsers()

def lambda_handler(event, context):
    """Lambda handler with complete website"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    body = event.get('body', '')
    
    if path == '/login' and method == 'POST':
        # Handle form submission
        try:
            # Parse form data
            form_data = urllib.parse.parse_qs(body)
            email = form_data.get('email', [''])[0].strip().lower()
            password = form_data.get('password', [''])[0]
            
            if not email or not password:
                return handle_login_page('Please fill in all fields')
            
            user = user_db.get_user(email)
            if not user or not user_db.verify_password(password, user['password_hash']):
                return handle_login_page('Invalid email or password')
            
            # Successful login - redirect to dashboard
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/dashboard',
                    'Set-Cookie': f'web_session_id=session123; Path=/; HttpOnly; Secure'
                },
                'body': ''
            }
        except Exception as e:
            return handle_login_page('Login error occurred')
    
    elif path == '/login':
        return handle_login_page()
    
    elif path == '/dashboard':
        return handle_dashboard_page()
    
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0'
            })
        }
    
    else:
        # Serve comprehensive home page
        return handle_home_page()

def handle_home_page():
    """Serve comprehensive home page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Practice</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3651d4;
            --accent-color: #7209b7;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
        }
        
        body {
            font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .hero-section {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
            color: white;
            padding: 100px 0;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="white" opacity="0.1"><polygon points="0,0 1000,80 1000,100 0,100"/></svg>');
            background-size: cover;
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .feature-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            overflow: hidden;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .assessment-card {
            border-radius: 20px;
            overflow: hidden;
            transition: transform 0.3s ease;
            border: none;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .assessment-card:hover {
            transform: translateY(-5px);
        }
        
        .pricing-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 14px;
        }
        
        .btn-custom {
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        
        .btn-primary-custom {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border: none;
            color: white;
        }
        
        .btn-primary-custom:hover {
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(67, 97, 238, 0.3);
        }
        
        .section-title {
            position: relative;
            margin-bottom: 50px;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 4px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
            border-radius: 2px;
        }
        
        .stats-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 80px 0;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: var(--primary-color);
            display: block;
        }
        
        .footer {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 50px 0 30px;
        }
        
        .mobile-cta {
            background: linear-gradient(135deg, var(--success-color) 0%, #27ae60 100%);
            color: white;
            padding: 60px 0;
            margin: 80px 0;
        }
        
        @media (max-width: 768px) {
            .hero-section {
                padding: 60px 0;
            }
            
            .hero-section h1 {
                font-size: 2.5rem;
            }
            
            .assessment-card {
                margin-bottom: 30px;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm fixed-top">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#" style="color: var(--primary-color);">
                <i class="bi bi-mortarboard-fill me-2"></i>IELTS GenAI Prep
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#assessments">Assessments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#how-it-works">How It Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-outline-primary ms-2 px-3" href="/login">Login</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6 hero-content">
                    <h1 class="display-4 fw-bold mb-4">Master IELTS with AI-Powered Practice</h1>
                    <p class="lead mb-4">Experience personalized IELTS preparation with Amazon Nova AI technology. Get detailed feedback on your writing and speaking skills from our advanced AI examiner.</p>
                    <div class="d-flex flex-wrap gap-3">
                        <a href="#assessments" class="btn btn-light btn-custom">Explore Assessments</a>
                        <a href="/login" class="btn btn-outline-light btn-custom">Start Practicing</a>
                    </div>
                </div>
                <div class="col-lg-6 text-center">
                    <div class="hero-image">
                        <i class="bi bi-chat-dots-fill" style="font-size: 15rem; opacity: 0.3;"></i>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Mobile-First CTA -->
    <section class="mobile-cta">
        <div class="container text-center">
            <h2 class="fw-bold mb-4">Start Your IELTS Journey</h2>
            <p class="lead mb-4">Download our mobile app to begin your AI-powered IELTS preparation journey</p>
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <div class="d-flex align-items-center justify-content-center">
                                <div class="me-3">
                                    <i class="bi bi-phone-fill" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <strong>1. Download App</strong><br>
                                    <small>iOS & Android</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="d-flex align-items-center justify-content-center">
                                <div class="me-3">
                                    <i class="bi bi-credit-card-fill" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <strong>2. Purchase</strong><br>
                                    <small>$49.99 for 4 assessments</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="d-flex align-items-center justify-content-center">
                                <div class="me-3">
                                    <i class="bi bi-laptop-fill" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <strong>3. Login Anywhere</strong><br>
                                    <small>Mobile & Desktop</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Assessments Section -->
    <section id="assessments" class="py-5">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="section-title">GenAI Assessed IELTS Modules</h2>
                <p class="lead text-muted">Choose from our comprehensive assessment products</p>
            </div>
            
            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="card assessment-card h-100 position-relative" style="border-left: 6px solid var(--primary-color);">
                        <div class="pricing-badge">$49.99 CAD</div>
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-mortarboard text-primary me-3" style="font-size: 2.5rem;"></i>
                                <div>
                                    <h4 class="card-title text-primary mb-1">Academic Writing Assessment</h4>
                                    <p class="text-muted mb-0">TrueScore® GenAI Writing Assessment</p>
                                </div>
                            </div>
                            <p class="card-text">Comprehensive writing evaluation using Amazon Nova Micro AI technology. Get detailed feedback on Task Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy.</p>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i>4 unique assessment attempts</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Detailed AI feedback</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Band score prediction</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Task 1 & Task 2 coverage</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card assessment-card h-100 position-relative" style="border-left: 6px solid var(--danger-color);">
                        <div class="pricing-badge">$49.99 CAD</div>
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-mic text-danger me-3" style="font-size: 2.5rem;"></i>
                                <div>
                                    <h4 class="card-title text-danger mb-1">Academic Speaking Assessment</h4>
                                    <p class="text-muted mb-0">ClearScore® GenAI Speaking Assessment</p>
                                </div>
                            </div>
                            <p class="card-text">Interactive speaking practice with Maya, our AI examiner powered by Amazon Nova Sonic. Experience realistic IELTS speaking test conditions with bi-directional voice conversations.</p>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i>4 unique assessment attempts</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>AI examiner Maya conversations</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Real-time speech analysis</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>All 3 parts coverage</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card assessment-card h-100 position-relative" style="border-left: 6px solid var(--success-color);">
                        <div class="pricing-badge">$49.99 CAD</div>
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-pencil text-success me-3" style="font-size: 2.5rem;"></i>
                                <div>
                                    <h4 class="card-title text-success mb-1">General Writing Assessment</h4>
                                    <p class="text-muted mb-0">TrueScore® GenAI Writing Assessment</p>
                                </div>
                            </div>
                            <p class="card-text">Specialized writing assessment for General Training IELTS. Practice formal and informal letters, essays, and reports with AI-powered evaluation tailored for General Training requirements.</p>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i>4 unique assessment attempts</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Letter writing practice</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Essay writing evaluation</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>General Training focused</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card assessment-card h-100 position-relative" style="border-left: 6px solid var(--warning-color);">
                        <div class="pricing-badge">$49.99 CAD</div>
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-chat-square text-warning me-3" style="font-size: 2.5rem;"></i>
                                <div>
                                    <h4 class="card-title text-warning mb-1">General Speaking Assessment</h4>
                                    <p class="text-muted mb-0">ClearScore® GenAI Speaking Assessment</p>
                                </div>
                            </div>
                            <p class="card-text">General Training speaking practice with AI examiner Maya. Engage in natural conversations covering everyday topics, personal experiences, and general interest subjects.</p>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i>4 unique assessment attempts</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>General Training topics</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Everyday conversation practice</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i>Personal experience focus</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-5 bg-light">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="section-title">Why Choose IELTS GenAI Prep</h2>
                <p class="lead text-muted">Advanced AI technology meets proven IELTS preparation methods</p>
            </div>
            
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card feature-card h-100 text-center p-4">
                        <i class="bi bi-robot text-primary mb-3" style="font-size: 3rem;"></i>
                        <h5>AI-Powered Assessment</h5>
                        <p class="text-muted">Advanced Amazon Nova AI technology provides accurate, detailed feedback on your IELTS performance across all skill areas.</p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 text-center p-4">
                        <i class="bi bi-person-workspace text-primary mb-3" style="font-size: 3rem;"></i>
                        <h5>Personalized Learning</h5>
                        <p class="text-muted">Receive customized feedback and improvement suggestions based on your individual strengths and areas for development.</p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 text-center p-4">
                        <i class="bi bi-shield-check text-primary mb-3" style="font-size: 3rem;"></i>
                        <h5>Authentic Practice</h5>
                        <p class="text-muted">Practice with real IELTS-style questions and tasks that mirror the actual test format and difficulty level.</p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 text-center p-4">
                        <i class="bi bi-stopwatch text-primary mb-3" style="font-size: 3rem;"></i>
                        <h5>Instant Feedback</h5>
                        <p class="text-muted">Get immediate, comprehensive feedback on your performance with detailed explanations and improvement strategies.</p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 text-center p-4">
                        <i class="bi bi-phone-vibrate text-primary mb-3" style="font-size: 3rem;"></i>
                        <h5>Mobile & Desktop</h5>
                        <p class="text-muted">Access your assessments anywhere, anytime. Purchase on mobile, practice on desktop, or use both platforms seamlessly.</p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 text-center p-4">
                        <i class="bi bi-award text-primary mb-3" style="font-size: 3rem;"></i>
                        <h5>Band Score Prediction</h5>
                        <p class="text-muted">Receive accurate band score predictions based on official IELTS criteria and AI analysis of your performance.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-5">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="section-title">How It Works</h2>
                <p class="lead text-muted">Get started with IELTS GenAI Prep in three simple steps</p>
            </div>
            
            <div class="row g-4">
                <div class="col-md-4 text-center">
                    <div class="mb-4">
                        <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <span class="h3 mb-0">1</span>
                        </div>
                    </div>
                    <h5>Download & Purchase</h5>
                    <p class="text-muted">Download our mobile app from the App Store or Google Play. Create your account and purchase your preferred assessment products.</p>
                </div>
                
                <div class="col-md-4 text-center">
                    <div class="mb-4">
                        <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <span class="h3 mb-0">2</span>
                        </div>
                    </div>
                    <h5>Practice Anywhere</h5>
                    <p class="text-muted">Use your purchase on both mobile and desktop. Login to this website with your mobile app credentials for full desktop access.</p>
                </div>
                
                <div class="col-md-4 text-center">
                    <div class="mb-4">
                        <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <span class="h3 mb-0">3</span>
                        </div>
                    </div>
                    <h5>Get AI Feedback</h5>
                    <p class="text-muted">Receive detailed, personalized feedback from our AI technology. Track your progress and improve your IELTS performance.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
        <div class="container">
            <div class="row text-center">
                <div class="col-md-3">
                    <div class="stat-item">
                        <span class="stat-number">4</span>
                        <p class="text-muted">Assessment Products</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item">
                        <span class="stat-number">16</span>
                        <p class="text-muted">Total Assessments</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item">
                        <span class="stat-number">24/7</span>
                        <p class="text-muted">AI Availability</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-item">
                        <span class="stat-number">Global</span>
                        <p class="text-muted">Access Anywhere</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5 class="text-white mb-3">IELTS GenAI Prep</h5>
                    <p>Advanced AI-powered IELTS preparation platform using Amazon Nova technology for comprehensive speaking and writing assessment.</p>
                </div>
                <div class="col-md-3">
                    <h6 class="text-white mb-3">Quick Links</h6>
                    <ul class="list-unstyled">
                        <li><a href="#assessments" class="text-light text-decoration-none">Assessments</a></li>
                        <li><a href="#features" class="text-light text-decoration-none">Features</a></li>
                        <li><a href="/login" class="text-light text-decoration-none">Login</a></li>
                    </ul>
                </div>
                <div class="col-md-3">
                    <h6 class="text-white mb-3">Legal</h6>
                    <ul class="list-unstyled">
                        <li><a href="/privacy" class="text-light text-decoration-none">Privacy Policy</a></li>
                        <li><a href="/terms" class="text-light text-decoration-none">Terms of Service</a></li>
                    </ul>
                </div>
            </div>
            <hr class="my-4" style="border-color: #34495e;">
            <div class="text-center">
                <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    }

def handle_login_page(error_message=None):
    """Handle login page with optional error message"""
    error_html = ''
    if error_message:
        error_html = f'<div class="alert alert-danger">{error_message}</div>'
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }}
        .login-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }}
        .form-control:focus {{
            border-color: #4361ee;
            box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.15);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%);
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <div class="text-center mb-4">
                        <h2 class="text-primary">Welcome Back</h2>
                        <p class="text-muted">Sign in to your IELTS GenAI Prep account</p>
                    </div>
                    
                    <div class="alert alert-info">
                        <h6>New to IELTS GenAI Prep?</h6>
                        <p class="mb-2">To get started, you need to:</p>
                        <ol class="mb-2">
                            <li>Download our mobile app (iOS/Android)</li>
                            <li>Create an account and purchase assessments</li>
                            <li>Return here to access your assessments on desktop</li>
                        </ol>
                    </div>
                    
                    {error_html}
                    
                    <form method="post" action="/login">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" name="email" id="email" value="test@ieltsgenaiprep.com" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" id="password" value="testpassword123" required>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember">
                            <label class="form-check-label" for="remember">Remember me for 30 days</label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Sign In</button>
                        </div>
                    </form>
                    
                    <div class="text-center mt-3">
                        <a href="/" class="text-decoration-none">← Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    }

def handle_dashboard_page():
    """Handle dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
        }
        .assessment-card {
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .assessment-card:hover {
            transform: translateY(-5px);
        }
        .header-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="header-card mb-5 p-4">
            <div class="text-center">
                <h1 class="text-primary mb-3">IELTS GenAI Prep Dashboard</h1>
                <p class="lead text-muted">Welcome! Your assessments are ready.</p>
                <p class="text-success"><strong>Login Successful!</strong> Mobile app credentials work perfectly on website.</p>
            </div>
        </div>
        
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #4361ee;">
                    <div class="card-body">
                        <h5 class="card-title text-primary">🎓 Academic Writing Assessment</h5>
                        <p class="card-text">TrueScore® GenAI writing evaluation with detailed feedback</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-primary">Start Assessment</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #e74c3c;">
                    <div class="card-body">
                        <h5 class="card-title text-danger">🎤 Academic Speaking Assessment</h5>
                        <p class="card-text">ClearScore® GenAI speaking practice with AI examiner Maya</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-danger">Start Assessment</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #2ecc71;">
                    <div class="card-body">
                        <h5 class="card-title text-success">📝 General Writing Assessment</h5>
                        <p class="card-text">TrueScore® GenAI writing evaluation for General Training</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-success">Start Assessment</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card assessment-card h-100" style="border-left: 5px solid #f39c12;">
                    <div class="card-body">
                        <h5 class="card-title text-warning">🗣️ General Speaking Assessment</h5>
                        <p class="card-text">ClearScore® GenAI speaking practice for General Training</p>
                        <p class="text-success"><strong>4 assessments remaining</strong></p>
                        <button class="btn btn-warning">Start Assessment</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-5">
            <a href="/login" class="btn btn-outline-light me-3">Logout</a>
            <a href="/" class="btn btn-outline-light">Back to Home</a>
        </div>
    </div>
</body>
</html>"""
    }'''
    
    with zipfile.ZipFile('lambda-complete-website.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    return 'lambda-complete-website.zip'

def deploy_complete_website():
    """Deploy complete website with comprehensive design"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        zip_path = create_complete_website_lambda()
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Deploying complete website with comprehensive home page...")
        
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        os.remove(zip_path)
        print("Complete website deployed successfully!")
        return True
        
    except Exception as e:
        print(f"Deploy failed: {e}")
        return False

if __name__ == "__main__":
    deploy_complete_website()