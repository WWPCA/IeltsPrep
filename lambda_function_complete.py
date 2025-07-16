import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

def verify_recaptcha_v2(recaptcha_response, user_ip=None):
    if not recaptcha_response:
        return False
    
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    if not secret_key:
        return False
    
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
    if user_ip:
        data['remoteip'] = user_ip
    
    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=encoded_data,
            method='POST'
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    except Exception as e:
        print(f'reCAPTCHA verification error: {e}')
        return False

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        data = {}
        if body and http_method == 'POST':
            try:
                data = json.loads(body)
            except:
                pass
        
        if path == '/' or path == '/home':
            return handle_home_page()
        elif path == '/login':
            return handle_login_page()
        elif path == '/dashboard':
            return handle_dashboard_page()
        elif path == '/api/login' and http_method == 'POST':
            user_ip = headers.get('x-forwarded-for', '').split(',')[0].strip()
            data['user_ip'] = user_ip
            return handle_user_login(data)
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/health':
            return handle_health_check()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Page not found</h1>'
            }
    except Exception as e:
        print(f'Lambda error: {e}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Internal server error</h1>'
        }

def handle_home_page():
    """Handle comprehensive home page with full approved template"""
    
    # The comprehensive template content
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
        }
        
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
            margin-top: 76px;
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
        
        .hero h1 {
            font-size: 3.5rem;
            line-height: 1.2;
            letter-spacing: -0.02em;
            color: #ffffff;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            animation: fadeInUp 0.8s ease-out;
        }
        
        .hero h2 {
            font-size: 1.5rem;
            line-height: 1.4;
            font-weight: 500;
            color: rgba(255,255,255,0.95);
            margin-bottom: 2rem;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            font-size: 1.2rem;
            padding: 15px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
            transition: all 0.3s ease;
        }
        
        .btn-success:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.6);
        }
        
        .btn-outline-light {
            font-size: 1.2rem;
            padding: 15px 30px;
            border-radius: 12px;
            border: 2px solid rgba(255,255,255,0.8);
            transition: all 0.3s ease;
        }
        
        .btn-outline-light:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,1);
            backdrop-filter: blur(10px);
            transform: translateY(-3px);
        }
        
        .pricing-card {
            border: 1px solid rgba(0, 0, 0, 0.125);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .pricing-card:hover {
            transform: translateY(-5px);
        }
        
        .features {
            padding: 80px 0;
            background: #f8f9fa;
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
        
        @media (max-width: 768px) {
            .hero {
                padding: 60px 0;
            }
            
            .hero h1 {
                font-size: 2.5rem !important;
            }
            
            .hero h2 {
                font-size: 1.3rem !important;
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
                        <a class="nav-link" href="#features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#assessments">Assessments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6 text-center text-lg-start mb-5 mb-lg-0">
                    <h1 class="display-3 fw-bold mb-3">
                        Master IELTS with GenAI-Powered Scoring
                    </h1>
                    
                    <h2 class="h4 mb-4">
                        The only AI-based IELTS platform with official band-aligned feedback
                    </h2>
                    
                    <div class="mb-4">
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-3">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <i class="fas fa-brain text-white"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">AI-Powered Scoring Technology</span>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-3">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <i class="fas fa-check-circle text-white"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">Official IELTS Criteria Alignment</span>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-4">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                <i class="fas fa-bullseye text-white"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">Academic & General Training Modules</span>
                        </div>
                    </div>
                    
                    <p class="mb-5" style="font-size: 1.1rem; color: rgba(255,255,255,0.9);">
                        Experience TrueScore® and ClearScore® technologies that deliver standardized IELTS assessments based on official scoring criteria.
                    </p>
                    
                    <div class="text-center text-lg-start">
                        <a href="/login" class="btn btn-success btn-lg me-3 mb-3">
                            <i class="fas fa-rocket me-2"></i>
                            Get Started
                        </a>
                        <a href="#features" class="btn btn-outline-light btn-lg mb-3">
                            <i class="fas fa-info-circle me-2"></i>
                            Learn More
                        </a>
                    </div>
                </div>
                
                <div class="col-lg-6 text-center">
                    <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; backdrop-filter: blur(15px);">
                        <div class="mb-3">
                            <span class="badge bg-primary text-white px-3 py-2">
                                <i class="fas fa-star me-1"></i>
                                YOUR SCORE PREVIEW
                            </span>
                        </div>
                        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 15px; padding: 30px; margin-bottom: 20px;">
                            <h3 class="text-white mb-2">
                                <i class="fas fa-certificate me-2"></i>
                                See Exactly How Your IELTS Score Will Look
                            </h3>
                            <div class="mb-3">
                                <span class="badge bg-light text-dark px-3 py-1">
                                    <i class="fas fa-pencil-alt me-1"></i>
                                    Academic Writing Assessment Sample
                                </span>
                            </div>
                            <p class="text-white mb-4">
                                Instant feedback. Official IELTS alignment. No guesswork.
                            </p>
                            
                            <div class="text-white">
                                <div class="mb-4 text-center" style="padding: 12px; background: rgba(255,255,255,0.15); border-radius: 10px;">
                                    <strong style="font-size: 1.3rem;">Overall Band Score: 7.5</strong>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Task Achievement (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 8</span>
                                    </div>
                                    <small style="opacity: 0.9;">Sufficiently addresses all parts with well-developed ideas</small>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Coherence & Cohesion (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 7</span>
                                    </div>
                                    <small style="opacity: 0.9;">Logically organizes information with clear progression</small>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Lexical Resource (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 7</span>
                                    </div>
                                    <small style="opacity: 0.9;">Flexible vocabulary to discuss variety of topics</small>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <span><strong>Grammar Range & Accuracy (25%)</strong></span>
                                        <span class="badge bg-light text-dark">Band 8</span>
                                    </div>
                                    <small style="opacity: 0.9;">Wide range of structures with good control</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <div class="text-white mb-2">
                                <i class="fas fa-robot me-1"></i>
                                Powered by TrueScore® & ClearScore® Technologies
                            </div>
                            <div class="text-white" style="opacity: 0.8;">
                                This is an exact preview of the detailed report you'll receive after completing your first assessment.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="features">
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
                            <ul class="text-start mb-3" style="list-style-type: none; padding-left: 0;">
                                <li class="mb-2"><span style="color: #28a745;">●</span> <strong>Task Achievement</strong></li>
                                <li class="mb-2"><span style="color: #28a745;">●</span> <strong>Coherence and Cohesion</strong></li>
                                <li class="mb-2"><span style="color: #28a745;">●</span> <strong>Lexical Resource</strong></li>
                                <li class="mb-2"><span style="color: #28a745;">●</span> <strong>Grammatical Range and Accuracy</strong></li>
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
                            <ul class="text-start mb-3" style="list-style-type: none; padding-left: 0;">
                                <li class="mb-2"><span style="color: #007bff;">●</span> <strong>Fluency and Coherence</strong></li>
                                <li class="mb-2"><span style="color: #007bff;">●</span> <strong>Lexical Resource</strong></li>
                                <li class="mb-2"><span style="color: #007bff;">●</span> <strong>Grammatical Range and Accuracy</strong></li>
                                <li class="mb-2"><span style="color: #007bff;">●</span> <strong>Pronunciation</strong></li>
                            </ul>
                            <p>Practice with Maya, our AI examiner, who conducts authentic 3-part speaking assessments with instant feedback on your performance.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Assessment Products Section -->
    <section class="py-5" id="assessments">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="mb-3">Choose Your Assessment</h2>
                <p class="text-muted">$36 for 4 unique assessments per product</p>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-success text-white text-center">
                            <h4>Academic Writing</h4>
                        </div>
                        <div class="card-body text-center">
                            <div class="display-4 mb-3">$49.99</div>
                            <p class="text-muted">4 unique assessments</p>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>Task 1 & Task 2 Practice</li>
                                <li><i class="fas fa-check text-success me-2"></i>Instant Band Scoring</li>
                                <li><i class="fas fa-check text-success me-2"></i>Detailed Feedback</li>
                                <li><i class="fas fa-check text-success me-2"></i>Progress Tracking</li>
                            </ul>
                            <a href="/login" class="btn btn-success btn-lg">Start Assessment</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-primary text-white text-center">
                            <h4>Academic Speaking</h4>
                        </div>
                        <div class="card-body text-center">
                            <div class="display-4 mb-3">$49.99</div>
                            <p class="text-muted">4 unique assessments</p>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-primary me-2"></i>3-Part Speaking Test</li>
                                <li><i class="fas fa-check text-primary me-2"></i>AI Examiner Maya</li>
                                <li><i class="fas fa-check text-primary me-2"></i>Real-time Analysis</li>
                                <li><i class="fas fa-check text-primary me-2"></i>Pronunciation Feedback</li>
                            </ul>
                            <a href="/login" class="btn btn-primary btn-lg">Start Assessment</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-success text-white text-center">
                            <h4>General Writing</h4>
                        </div>
                        <div class="card-body text-center">
                            <div class="display-4 mb-3">$49.99</div>
                            <p class="text-muted">4 unique assessments</p>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>Letter & Essay Practice</li>
                                <li><i class="fas fa-check text-success me-2"></i>Instant Band Scoring</li>
                                <li><i class="fas fa-check text-success me-2"></i>Detailed Feedback</li>
                                <li><i class="fas fa-check text-success me-2"></i>Progress Tracking</li>
                            </ul>
                            <a href="/login" class="btn btn-success btn-lg">Start Assessment</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-primary text-white text-center">
                            <h4>General Speaking</h4>
                        </div>
                        <div class="card-body text-center">
                            <div class="display-4 mb-3">$49.99</div>
                            <p class="text-muted">4 unique assessments</p>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-primary me-2"></i>3-Part Speaking Test</li>
                                <li><i class="fas fa-check text-primary me-2"></i>AI Examiner Maya</li>
                                <li><i class="fas fa-check text-primary me-2"></i>Real-time Analysis</li>
                                <li><i class="fas fa-check text-primary me-2"></i>Pronunciation Feedback</li>
                            </ul>
                            <a href="/login" class="btn btn-primary btn-lg">Start Assessment</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-5 bg-light">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="mb-3">How to Get Started</h2>
                <p class="text-muted">Simple 3-step process to access your AI-powered IELTS assessments</p>
            </div>
            
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="text-center">
                        <div class="bg-primary text-white rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="fas fa-mobile-alt fa-2x"></i>
                        </div>
                        <h4>Download Mobile App</h4>
                        <p class="text-muted">Download our mobile app from the App Store or Google Play Store to get started.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="text-center">
                        <div class="bg-success text-white rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="fas fa-credit-card fa-2x"></i>
                        </div>
                        <h4>Purchase Assessments</h4>
                        <p class="text-muted">Choose your assessment type and purchase $49.99 for 4 unique assessments through secure app store billing.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="text-center">
                        <div class="bg-warning text-white rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="fas fa-desktop fa-2x"></i>
                        </div>
                        <h4>Login Anywhere</h4>
                        <p class="text-muted">Use the same credentials to access assessments on mobile or desktop. Your progress syncs automatically.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>IELTS GenAI Prep</h5>
                    <p class="text-muted">AI-powered IELTS assessment platform with standardized scoring.</p>
                </div>
                <div class="col-md-6">
                    <h5>Legal</h5>
                    <ul class="list-unstyled">
                        <li><a href="/privacy-policy" class="text-muted">Privacy Policy</a></li>
                        <li><a href="/terms-of-service" class="text-muted">Terms of Service</a></li>
                    </ul>
                </div>
            </div>
            <hr class="bg-light">
            <div class="text-center">
                <p class="text-muted mb-0">© 2025 IELTS GenAI Prep. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': template_content
    }
