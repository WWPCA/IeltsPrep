#!/usr/bin/env python3
"""
Deploy Clean Production Lambda with Approved Template
"""

import zipfile
import json
import boto3
import os
from datetime import datetime

def create_clean_lambda():
    """Create production Lambda with clean template structure"""
    
    # Create Lambda function code string
    lambda_code = '''import json
import boto3
import os
from datetime import datetime
import urllib.parse
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    """AWS Lambda Handler - Production IELTS GenAI Prep Platform"""
    
    # CloudFront security validation
    headers = event.get('headers', {})
    if headers.get('cf-secret-3140348d') != 'valid':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Access denied'})
        }
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    logger.info(f"Lambda processing {method} {path}")
    
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
        elif path.startswith('/assessment/'):
            return serve_assessment_page(path)
        elif path == '/dashboard':
            return serve_dashboard()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': get_404_page()
            }
    
    except Exception as e:
        logger.error(f"Error processing {method} {path}: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': get_500_page()
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
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        .pricing-card { border: 1px solid rgba(0, 0, 0, 0.125); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s; }
        .pricing-card:hover { transform: translateY(-5px); }
        .genai-brand-section { margin-bottom: 60px; }
        .brand-icon { font-size: 2.5rem; margin-bottom: 15px; }
        .brand-title { font-size: 2rem; margin-bottom: 0.5rem; }
        .brand-tagline { color: #666; margin-bottom: 2rem; font-size: 1.1rem; }
        .card { height: 100%; }
        .card-body { display: flex; flex-direction: column; min-height: 250px; }
        .card-header { height: 60px !important; display: flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="text-center mb-4">
                <h1 class="display-4 fw-bold mb-3">Master IELTS with the World's ONLY GenAI Assessment Platform</h1>
                <div class="p-2 mb-4" style="background-color: #3498db; color: white; border-radius: 4px; display: inline-block; width: 100%; max-width: 100%;">
                    Powered by TrueScore® & ClearScore® - Industry-Leading Standardized Assessment Technology
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-lg-10 mx-auto">
                    <p class="lead">IELTS GenAI Prep delivers precise, examiner-aligned feedback through our exclusive TrueScore® writing analysis and ClearScore® speaking assessment systems. Our proprietary technology applies the official IELTS marking criteria to provide consistent, accurate band scores and actionable feedback for both Academic and General Training.</p>
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
                        <div class="card-header bg-success text-white text-center py-3">
                            <h3 class="m-0">TrueScore® Writing Assessment</h3>
                        </div>
                        <div class="card-body text-center">
                            <i class="fas fa-pencil-alt fa-3x text-success mb-3"></i>
                            <div class="badge bg-light text-dark mb-3">EXCLUSIVE TECHNOLOGY</div>
                            <p>TrueScore® is the world's first GenAI system to precisely assess IELTS writing performance across all official criteria. Its comprehensive analysis delivers detailed feedback on Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy for both IELTS Academic and General Training writing tasks.</p>
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
                            <p>ClearScore® is the world's first GenAI system to precisely assess IELTS speaking performance across all official criteria. Its sophisticated speech analysis delivers comprehensive feedback on Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, and Pronunciation for all three speaking assessment sections.</p>
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
                        <p>Master the IELTS Writing and Speaking modules with the world's only GenAI-driven assessments aligned with the official IELTS band descriptors for accurate feedback for both IELTS Academic and General Training. Boost your skills and achieve your target score with confidence.</p>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100 p-3 text-center">
                        <i class="fas fa-graduation-cap fa-4x text-primary mb-3"></i>
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
        </div>
    </section>

    <!-- Product Plans Section -->
    <section class="pricing py-5 bg-light">
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
                
                <div class="row equal-height-cards">
                    <!-- Academic Writing Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-success text-white text-center">
                                <h3 class="my-0 font-weight-bold">Academic Writing</h3>
                            </div>
                            <div class="card-body d-flex flex-column">
                                <div class="pricing-features mt-3 mb-4">
                                    <ul class="list-unstyled">
                                        <li class="mb-2"><i class="fas fa-check text-success me-2"></i> 4 complete assessment sets of:</li>
                                        <li class="mb-2 ms-4">Task 1: Chart & Graph analysis</li>
                                        <li class="mb-2 ms-4">Task 2: Essay writing</li>
                                        <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Detailed band scoring (1-9)</li>
                                        <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Criteria-based feedback</li>
                                    </ul>
                                </div>
                                <div class="text-center mt-auto">
                                    <div class="mb-3">
                                        <span class="h4 text-success">$36.49 USD</span>
                                        <small class="text-muted d-block">for 4 assessments</small>
                                    </div>
                                    <a href="/login" class="btn btn-success btn-lg w-100">Start Assessment</a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- General Writing Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-success text-white text-center">
                                <h3 class="my-0 font-weight-bold">General Writing</h3>
                            </div>
                            <div class="card-body d-flex flex-column">
                                <div class="pricing-features mt-3 mb-4">
                                    <ul class="list-unstyled">
                                        <li class="mb-2"><i class="fas fa-check text-success me-2"></i> 4 complete assessment sets of:</li>
                                        <li class="mb-2 ms-4">Task 1: Letter writing</li>
                                        <li class="mb-2 ms-4">Task 2: Essay writing</li>
                                        <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Detailed band scoring (1-9)</li>
                                        <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Criteria-based feedback</li>
                                    </ul>
                                </div>
                                <div class="text-center mt-auto">
                                    <div class="mb-3">
                                        <span class="h4 text-success">$36.49 USD</span>
                                        <small class="text-muted d-block">for 4 assessments</small>
                                    </div>
                                    <a href="/login" class="btn btn-success btn-lg w-100">Start Assessment</a>
                                </div>
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
                    <p class="brand-tagline">Professional GenAI assessment of IELTS speaking performance with real-time AI examiner interaction, precise pronunciation analysis, and comprehensive feedback aligned with official IELTS speaking criteria</p>
                </div>
                
                <div class="row equal-height-cards">
                    <!-- Academic Speaking Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-primary text-white text-center">
                                <h3 class="my-0 font-weight-bold">Academic Speaking</h3>
                            </div>
                            <div class="card-body d-flex flex-column">
                                <div class="pricing-features mt-3 mb-4">
                                    <ul class="list-unstyled">
                                        <li class="mb-2"><i class="fas fa-check text-primary me-2"></i> 4 complete assessment sets of:</li>
                                        <li class="mb-2 ms-4">Part 1: Interview</li>
                                        <li class="mb-2 ms-4">Part 2: Long Turn</li>
                                        <li class="mb-2 ms-4">Part 3: Discussion</li>
                                        <li class="mb-2"><i class="fas fa-check text-primary me-2"></i> AI examiner interaction</li>
                                    </ul>
                                </div>
                                <div class="text-center mt-auto">
                                    <div class="mb-3">
                                        <span class="h4 text-primary">$36.49 USD</span>
                                        <small class="text-muted d-block">for 4 assessments</small>
                                    </div>
                                    <a href="/login" class="btn btn-primary btn-lg w-100">Start Assessment</a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- General Speaking Assessment -->
                    <div class="col-lg-6 mb-4">
                        <div class="card pricing-card">
                            <div class="card-header bg-primary text-white text-center">
                                <h3 class="my-0 font-weight-bold">General Speaking</h3>
                            </div>
                            <div class="card-body d-flex flex-column">
                                <div class="pricing-features mt-3 mb-4">
                                    <ul class="list-unstyled">
                                        <li class="mb-2"><i class="fas fa-check text-primary me-2"></i> 4 complete assessment sets of:</li>
                                        <li class="mb-2 ms-4">Part 1: Interview</li>
                                        <li class="mb-2 ms-4">Part 2: Long Turn</li>
                                        <li class="mb-2 ms-4">Part 3: Discussion</li>
                                        <li class="mb-2"><i class="fas fa-check text-primary me-2"></i> AI examiner interaction</li>
                                    </ul>
                                </div>
                                <div class="text-center mt-auto">
                                    <div class="mb-3">
                                        <span class="h4 text-primary">$36.49 USD</span>
                                        <small class="text-muted d-block">for 4 assessments</small>
                                    </div>
                                    <a href="/login" class="btn btn-primary btn-lg w-100">Start Assessment</a>
                                </div>
                            </div>
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
'''

    # Add all other function definitions here...
    lambda_code += '''
def serve_login_page():
    """Serve login page with reCAPTCHA integration"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head>
<body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container-fluid vh-100 d-flex align-items-center justify-content-center">
        <div class="col-11 col-sm-8 col-md-6 col-lg-4">
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white text-center">
                    <a href="/" class="btn btn-light btn-sm position-absolute" style="left: 10px; top: 50%; transform: translateY(-50%);">
                        <i class="fas fa-home"></i>
                    </a>
                    <h3 class="mb-0">Welcome Back</h3>
                </div>
                <div class="card-body p-4">
                    <div class="alert alert-info mb-4">
                        <strong><i class="fas fa-mobile-alt me-2"></i>New Users:</strong> Please download our mobile app first to create your account and purchase assessments.
                    </div>
                    
                    <form method="POST" action="/login">
                        <div class="mb-3">
                            <input type="email" class="form-control" name="email" placeholder="Email address" required>
                        </div>
                        <div class="mb-3">
                            <input type="password" class="form-control" name="password" placeholder="Password" required>
                        </div>
                        <div class="mb-3">
                            <div class="g-recaptcha" data-sitekey="6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ"></div>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-sign-in-alt me-2"></i>Sign In
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
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
        'body': """<!DOCTYPE html>
<html><head><title>Privacy Policy - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body><div class="container py-5">
<h1>Privacy Policy</h1><p>We use your data for IELTS assessment services only. Voice recordings are not saved.</p>
<a href="/" class="btn btn-primary">Back to Home</a>
</div></body></html>"""
    }

def serve_terms_of_service():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<!DOCTYPE html>
<html><head><title>Terms of Service - IELTS GenAI Prep</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body><div class="container py-5">
<h1>Terms of Service</h1><p>Assessments are $36.49 USD each. All purchases are non-refundable.</p>
<a href="/" class="btn btn-primary">Back to Home</a>
</div></body></html>"""
    }

def serve_robots_txt():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': """User-agent: *\\nAllow: /\\n\\nUser-agent: GPTBot\\nAllow: /\\n\\nUser-agent: ClaudeBot\\nAllow: /"""
    }

def serve_assessment_page(path):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<h1>Assessment Page</h1><p>Login required for assessments.</p>"""
    }

def serve_dashboard():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': """<h1>Dashboard</h1><p>Assessment dashboard ready.</p>"""
    }

def get_404_page():
    return """<h1>404 - Page Not Found</h1>"""

def get_500_page():
    return """<h1>500 - Internal Server Error</h1>"""
'''
    
    # Create deployment package
    package_name = f'clean_production_lambda_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
    
    return package_name

def deploy_to_aws(package_name):
    """Deploy to AWS Lambda"""
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(package_name, 'rb') as f:
            response = lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-api',
                ZipFile=f.read()
            )
        
        print(f"✅ DEPLOYMENT SUCCESSFUL")
        print(f"✅ Code Size: {response['CodeSize']} bytes")
        return True
    
    except Exception as e:
        print(f"❌ DEPLOYMENT FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Deploying clean production Lambda with approved template...")
    
    package_name = create_clean_lambda()
    if package_name:
        print(f"📦 Package created: {package_name}")
        
        if deploy_to_aws(package_name):
            print(f"🎉 SUCCESS! Website: https://www.ieltsaiprep.com")
        else:
            print("❌ Failed")
    else:
        print("❌ Package creation failed")
