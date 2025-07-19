#!/usr/bin/env python3

import zipfile
import json
import boto3
from datetime import datetime

def create_corrected_lambda():
    """Create Lambda with proper CloudFront validation"""
    
    lambda_code = '''import json
import boto3
import os
from datetime import datetime
import urllib.parse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    """AWS Lambda Handler with CloudFront validation"""
    
    # Log incoming headers for debugging
    headers = event.get('headers', {})
    logger.info(f"Headers: {headers}")
    
    # CloudFront security validation - check multiple possible header formats
    cf_secret_found = False
    for header_name in ['cf-secret-3140348d', 'CF-Secret-3140348d', 'x-cf-secret-3140348d']:
        if headers.get(header_name) == 'valid':
            cf_secret_found = True
            break
    
    if not cf_secret_found:
        logger.warning(f"CloudFront security validation failed. Headers: {list(headers.keys())}")
        return {
            'statusCode': 403,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Access denied - CloudFront validation failed'})
        }
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    logger.info(f"Processing {method} {path}")
    
    try:
        if path == '/' or path == '/home':
            return serve_home_page()
        elif path == '/login':
            return serve_login_page() if method == 'GET' else handle_login(event)
        elif path == '/privacy-policy':
            return serve_privacy_policy()
        elif path == '/terms-of-service':
            return serve_terms_of_service()
        elif path == '/robots.txt':
            return serve_robots_txt()
        elif path == '/api/health':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>404 - Page Not Found</h1><a href="/">Return Home</a>'
            }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>500 - Internal Server Error</h1><a href="/">Return Home</a>'
        }

def serve_home_page():
    """Serve comprehensive home page with approved template structure"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="The only AI-powered IELTS assessment platform with standardized band scoring. Prepare for IELTS Writing and Speaking with TrueScore® and ClearScore® technologies.">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        .pricing-card { border: 1px solid rgba(0, 0, 0, 0.125); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s; }
        .pricing-card:hover { transform: translateY(-5px); }
        .genai-brand-section { margin-bottom: 60px; }
        .brand-icon { font-size: 2.5rem; margin-bottom: 15px; }
        .brand-title { font-size: 2rem; margin-bottom: 0.5rem; }
        .brand-tagline { color: #666; margin-bottom: 2rem; font-size: 1.1rem; }
        .card { height: 100%; }
        .card-body { display: flex; flex-direction: column; }
        .card-header { height: 60px !important; display: flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero py-5">
        <div class="container">
            <div class="text-center mb-4">
                <h1 class="display-4 fw-bold mb-3">Master IELTS with the World's ONLY GenAI Assessment Platform</h1>
                <div class="p-2 mb-4" style="background-color: #3498db; color: white; border-radius: 4px; display: inline-block; width: 100%;">
                    Powered by TrueScore® & ClearScore® - Industry-Leading Standardized Assessment Technology
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-lg-10 mx-auto">
                    <p class="lead">IELTS GenAI Prep delivers precise, examiner-aligned feedback through our exclusive TrueScore® writing analysis and ClearScore® speaking assessment systems.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Assessment Technology Section -->
    <section class="py-5 bg-light">
        <div class="container">
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card h-100 border-success">
                        <div class="card-header bg-success text-white text-center">
                            <h3 class="m-0">TrueScore® Writing Assessment</h3>
                        </div>
                        <div class="card-body text-center">
                            <i class="fas fa-pencil-alt fa-3x text-success mb-3"></i>
                            <div class="badge bg-light text-dark mb-3">EXCLUSIVE TECHNOLOGY</div>
                            <p>TrueScore® delivers comprehensive analysis with detailed feedback on Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card h-100 border-primary">
                        <div class="card-header bg-primary text-white text-center">
                            <h3 class="m-0">ClearScore® Speaking Assessment</h3>
                        </div>
                        <div class="card-body text-center">
                            <i class="fas fa-microphone-alt fa-3x text-primary mb-3"></i>
                            <div class="badge bg-light text-dark mb-3">EXCLUSIVE TECHNOLOGY</div>
                            <p>ClearScore® provides sophisticated speech analysis with comprehensive feedback on Fluency, Lexical Resource, Grammar, and Pronunciation.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features py-5">
        <div class="container">
            <h2 class="text-center mb-5">Why Choose IELTS GenAI Prep for Your Assessment Preparation?</h2>
            
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                        <h3 class="h4">Comprehensive IELTS Assessment Preparation</h3>
                        <p>Master IELTS Writing and Speaking with GenAI-driven assessments aligned with official band descriptors for both Academic and General Training.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-graduation-cap fa-4x text-primary mb-3"></i>
                        <h3 class="h4">Your Personal GenAI IELTS Coach</h3>
                        <p>Get detailed feedback aligned with official IELTS criteria on both speaking and writing tasks with TrueScore® and ClearScore®.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-globe fa-4x text-info mb-3"></i>
                        <h3 class="h4">Global Assessment Preparation</h3>
                        <p>Access world-class assessment preparation from anywhere, empowering your academic and career goals.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section class="pricing py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-4">GenAI Assessed IELTS Modules</h2>
            <p class="text-center mb-5">Specialized GenAI technologies provide accurate assessment for IELTS preparation</p>
            
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card">
                        <div class="card-header bg-success text-white text-center">
                            <h3 class="my-0">Academic Writing</h3>
                        </div>
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <span class="h4 text-success">$36.49 USD</span>
                                <small class="text-muted d-block">for 4 assessments</small>
                            </div>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i> Task 1: Chart & Graph analysis</li>
                                <li><i class="fas fa-check text-success me-2"></i> Task 2: Essay writing</li>
                                <li><i class="fas fa-check text-success me-2"></i> Band scoring (1-9)</li>
                                <li><i class="fas fa-check text-success me-2"></i> Detailed feedback</li>
                            </ul>
                            <a href="/login" class="btn btn-success btn-lg w-100 mt-3">Start Assessment</a>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card">
                        <div class="card-header bg-success text-white text-center">
                            <h3 class="my-0">General Writing</h3>
                        </div>
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <span class="h4 text-success">$36.49 USD</span>
                                <small class="text-muted d-block">for 4 assessments</small>
                            </div>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i> Task 1: Letter writing</li>
                                <li><i class="fas fa-check text-success me-2"></i> Task 2: Essay writing</li>
                                <li><i class="fas fa-check text-success me-2"></i> Band scoring (1-9)</li>
                                <li><i class="fas fa-check text-success me-2"></i> Detailed feedback</li>
                            </ul>
                            <a href="/login" class="btn btn-success btn-lg w-100 mt-3">Start Assessment</a>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card">
                        <div class="card-header bg-primary text-white text-center">
                            <h3 class="my-0">Academic Speaking</h3>
                        </div>
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <span class="h4 text-primary">$36.49 USD</span>
                                <small class="text-muted d-block">for 4 assessments</small>
                            </div>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-primary me-2"></i> Part 1: Interview</li>
                                <li><i class="fas fa-check text-primary me-2"></i> Part 2: Long Turn</li>
                                <li><i class="fas fa-check text-primary me-2"></i> Part 3: Discussion</li>
                                <li><i class="fas fa-check text-primary me-2"></i> AI examiner interaction</li>
                            </ul>
                            <a href="/login" class="btn btn-primary btn-lg w-100 mt-3">Start Assessment</a>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6 mb-4">
                    <div class="card pricing-card">
                        <div class="card-header bg-primary text-white text-center">
                            <h3 class="my-0">General Speaking</h3>
                        </div>
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <span class="h4 text-primary">$36.49 USD</span>
                                <small class="text-muted d-block">for 4 assessments</small>
                            </div>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-primary me-2"></i> Part 1: Interview</li>
                                <li><i class="fas fa-check text-primary me-2"></i> Part 2: Long Turn</li>
                                <li><i class="fas fa-check text-primary me-2"></i> Part 3: Discussion</li>
                                <li><i class="fas fa-check text-primary me-2"></i> AI examiner interaction</li>
                            </ul>
                            <a href="/login" class="btn btn-primary btn-lg w-100 mt-3">Start Assessment</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
            <div class="mt-2">
                <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                <a href="/terms-of-service" class="text-white">Terms of Service</a>
            </div>
        </div>
    </footer>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': template
    }

def serve_login_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head><body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
<div class="container-fluid vh-100 d-flex align-items-center justify-content-center">
<div class="col-11 col-sm-8 col-md-6 col-lg-4">
<div class="card shadow-lg">
<div class="card-header bg-primary text-white text-center">
<a href="/" class="btn btn-light btn-sm float-start"><i class="fas fa-home"></i></a>
<h3>Welcome Back</h3>
</div>
<div class="card-body p-4">
<div class="alert alert-info">
<strong>New Users:</strong> Download our mobile app first to create account and purchase assessments.
</div>
<form method="POST">
<div class="mb-3"><input type="email" class="form-control" name="email" placeholder="Email" required></div>
<div class="mb-3"><input type="password" class="form-control" name="password" placeholder="Password" required></div>
<div class="mb-3"><div class="g-recaptcha" data-sitekey="6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ"></div></div>
<button type="submit" class="btn btn-primary w-100">Sign In</button>
</form>
</div></div></div></div>
</body></html>"""
    }

def handle_login(event):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'success'})
    }

def serve_privacy_policy():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<h1>Privacy Policy</h1><p>Voice recordings not saved, only feedback retained.</p><a href="/">Home</a>"""
    }

def serve_terms_of_service():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<h1>Terms of Service</h1><p>$36.49 USD per assessment. Non-refundable.</p><a href="/">Home</a>"""
    }

def serve_robots_txt():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': "User-agent: *\\nAllow: /\\nUser-agent: GPTBot\\nAllow: /"
    }
'''
    
    package_name = f'corrected_production_lambda_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
    
    return package_name

def deploy_to_aws(package_name):
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(package_name, 'rb') as f:
            response = lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-api',
                ZipFile=f.read()
            )
        
        print(f"✅ CORRECTED DEPLOYMENT SUCCESSFUL")
        print(f"✅ Code Size: {response['CodeSize']} bytes")
        return True
    
    except Exception as e:
        print(f"❌ DEPLOYMENT FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Deploying corrected production Lambda...")
    
    package_name = create_corrected_lambda()
    if deploy_to_aws(package_name):
        print(f"🎉 SUCCESS! Website: https://www.ieltsaiprep.com")
    else:
        print("❌ Failed")
