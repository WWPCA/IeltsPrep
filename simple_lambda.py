"""
Simplified AWS Lambda Handler for IELTS GenAI Prep
Minimal dependencies for immediate website functionality
"""
import json
import base64
import os

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        headers = event.get('headers', {})
        
        print(f"[CLOUDWATCH] Processing {method} {path}")
        
        # Route requests
        if path == '/' and method == 'GET':
            return serve_home_page()
        elif path == '/login' and method == 'GET':
            return serve_login_page()
        elif path == '/api/health':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'healthy', 'service': 'ielts-genai-prep'})
            }
        elif path == '/privacy-policy' and method == 'GET':
            return serve_privacy_policy()
        elif path == '/terms-of-service' and method == 'GET':
            return serve_terms_of_service()
        else:
            # Default to home page for any unmatched GET request
            if method == 'GET':
                return serve_home_page()
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Endpoint not found'})
                }
    except Exception as e:
        print(f"[ERROR] Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def serve_home_page():
    """Serve the home page HTML"""
    html_content = """
<!DOCTYPE html>
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
        }
        
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
        }
        
        .feature-icon {
            font-size: 3rem;
            color: #007bff;
            margin-bottom: 20px;
        }
        
        .mobile-app-banner {
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .mobile-app-banner h4 {
            margin-bottom: 10px;
        }
        
        .step-number {
            background: #007bff;
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin: 0 auto 15px;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-graduation-cap me-2"></i>
                IELTS GenAI Prep
            </a>
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

    <!-- Hero Section -->
    <section class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 fw-bold mb-4">IELTS GenAI Prep</h1>
            <p class="lead mb-5">World's ONLY GenAI Assessment Platform for IELTS Test Preparation</p>
            
            <!-- Mobile App Banner -->
            <div class="mobile-app-banner">
                <h4><i class="fas fa-mobile-alt me-2"></i>Download Our Mobile App First</h4>
                <p class="mb-0">Purchase assessments through the app, then login here for desktop access</p>
            </div>
        </div>
    </section>

    <!-- GenAI Brand Section -->
    <section class="genai-brand-section py-5">
        <div class="container text-center">
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="brand-icon text-primary">
                        <i class="fas fa-pen-fancy"></i>
                    </div>
                    <h3 class="brand-title">TrueScore® GenAI Writing</h3>
                    <p class="brand-tagline">AI-powered writing assessment with instant feedback</p>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="brand-icon text-success">
                        <i class="fas fa-microphone"></i>
                    </div>
                    <h3 class="brand-title">ClearScore® GenAI Speaking</h3>
                    <p class="brand-tagline">Voice-to-voice AI conversations with Maya examiner</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Assessment Products -->
    <section class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">Choose Your Assessment</h2>
            <div class="row">
                <!-- Academic Writing -->
                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-primary text-white text-center">
                            <h4>Academic Writing</h4>
                            <h3>$36.00 CAD</h3>
                        </div>
                        <div class="card-body">
                            <h5>TrueScore® GenAI Writing Assessment</h5>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>4 Unique Writing Tasks</li>
                                <li><i class="fas fa-check text-success me-2"></i>AI-Powered Instant Feedback</li>
                                <li><i class="fas fa-check text-success me-2"></i>Band Score Predictions</li>
                                <li><i class="fas fa-check text-success me-2"></i>Detailed Improvement Tips</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Academic Speaking -->
                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-success text-white text-center">
                            <h4>Academic Speaking</h4>
                            <h3>$36.00 CAD</h3>
                        </div>
                        <div class="card-body">
                            <h5>ClearScore® GenAI Speaking Assessment</h5>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>4 Complete Speaking Tests</li>
                                <li><i class="fas fa-check text-success me-2"></i>AI Examiner Maya Conversations</li>
                                <li><i class="fas fa-check text-success me-2"></i>Real-time Voice Analysis</li>
                                <li><i class="fas fa-check text-success me-2"></i>Pronunciation & Fluency Feedback</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- General Writing -->
                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-info text-white text-center">
                            <h4>General Writing</h4>
                            <h3>$36.00 CAD</h3>
                        </div>
                        <div class="card-body">
                            <h5>TrueScore® GenAI Writing Assessment</h5>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>4 Unique Writing Tasks</li>
                                <li><i class="fas fa-check text-success me-2"></i>Letter & Essay Analysis</li>
                                <li><i class="fas fa-check text-success me-2"></i>Band Score Predictions</li>
                                <li><i class="fas fa-check text-success me-2"></i>Personalized Feedback</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- General Speaking -->
                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card h-100">
                        <div class="card-header bg-warning text-white text-center">
                            <h4>General Speaking</h4>
                            <h3>$36.00 CAD</h3>
                        </div>
                        <div class="card-body">
                            <h5>ClearScore® GenAI Speaking Assessment</h5>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>4 Complete Speaking Tests</li>
                                <li><i class="fas fa-check text-success me-2"></i>Interactive AI Conversations</li>
                                <li><i class="fas fa-check text-success me-2"></i>Fluency & Coherence Analysis</li>
                                <li><i class="fas fa-check text-success me-2"></i>Vocabulary Enhancement Tips</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works -->
    <section class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">How It Works</h2>
            <div class="row">
                <div class="col-md-4 text-center mb-4">
                    <div class="step-number">1</div>
                    <h5>Download Mobile App</h5>
                    <p>Download IELTS GenAI Prep from App Store or Google Play</p>
                </div>
                <div class="col-md-4 text-center mb-4">
                    <div class="step-number">2</div>
                    <h5>Purchase Assessment</h5>
                    <p>Buy your preferred assessment package through the mobile app</p>
                </div>
                <div class="col-md-4 text-center mb-4">
                    <div class="step-number">3</div>
                    <h5>Login Anywhere</h5>
                    <p>Use the same credentials to access assessments on mobile or web</p>
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
                    <p>World's only GenAI-powered IELTS assessment platform</p>
                </div>
                <div class="col-md-6">
                    <h6>Quick Links</h6>
                    <ul class="list-unstyled">
                        <li><a href="/privacy-policy" class="text-light">Privacy Policy</a></li>
                        <li><a href="/terms-of-service" class="text-light">Terms of Service</a></li>
                    </ul>
                </div>
            </div>
            <hr>
            <div class="text-center">
                <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

def serve_login_page():
    """Serve the login page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3 class="text-center">Login to IELTS GenAI Prep</h3>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <h5><i class="fas fa-mobile-alt me-2"></i>Mobile App Required</h5>
                            <p>You must first download our mobile app and purchase assessments before logging in here.</p>
                            <p><strong>Steps:</strong></p>
                            <ol>
                                <li>Download IELTS GenAI Prep mobile app</li>
                                <li>Create account and purchase assessments</li>
                                <li>Return here to login with same credentials</li>
                            </ol>
                        </div>
                        
                        <form>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <p>Don't have an account? <a href="#" onclick="alert('Please download our mobile app first to create an account and purchase assessments.')">Download Mobile App</a></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }

def serve_privacy_policy():
    """Serve privacy policy page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><body><h1>Privacy Policy</h1><p>Privacy policy content coming soon.</p></body></html>'
    }

def serve_terms_of_service():
    """Serve terms of service page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><body><h1>Terms of Service</h1><p>Terms of service content coming soon.</p></body></html>'
    }