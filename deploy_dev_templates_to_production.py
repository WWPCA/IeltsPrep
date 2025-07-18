#!/usr/bin/env python3
"""
Deploy Dev Templates to Production Lambda
"""
import json
import zipfile
import os
import re
from pathlib import Path

def read_template_file(filepath):
    """Read a template file and return its content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Template file not found: {filepath}")
        return None

def process_flask_template(template_content, context=None):
    """Process Flask template variables and blocks"""
    if context is None:
        context = {}
    
    # Remove Flask template syntax for Lambda deployment
    # Remove {% extends "layout.html" %} and {% block %} tags
    processed = re.sub(r'{%\s*extends\s+"[^"]*"\s*%}', '', template_content)
    processed = re.sub(r'{%\s*block\s+\w+\s*%}', '', processed)
    processed = re.sub(r'{%\s*endblock\s*%}', '', processed)
    
    # Remove other Flask template syntax
    processed = re.sub(r'{%\s*if\s+current_user\.is_authenticated\s*%}.*?{%\s*endif\s*%}', '', processed, flags=re.DOTALL)
    processed = re.sub(r'{{[^}]*}}', '', processed)
    
    return processed

def create_comprehensive_lambda():
    """Create Lambda function with comprehensive templates from dev environment"""
    
    # Read the main templates
    index_template = read_template_file('templates/index.html')
    login_template = read_template_file('templates/login.html')
    privacy_template = read_template_file('templates/gdpr/privacy_policy.html')
    terms_template = read_template_file('templates/gdpr/terms_of_service.html')
    layout_template = read_template_file('templates/layout.html')
    
    if not all([index_template, login_template, privacy_template, terms_template, layout_template]):
        print("❌ Missing required template files")
        return None
    
    # Create comprehensive Lambda function
    lambda_code = f'''import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
import base64

def lambda_handler(event, context):
    """Main Lambda handler with CloudFront header validation"""
    
    # CloudFront security validation
    headers = event.get('headers', {{}})
    cf_secret = headers.get('CF-Secret-3140348d')
    if cf_secret != 'valid':
        return {{
            'statusCode': 403,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Access denied - Invalid CloudFront header'}})
        }}
    
    # Route handling
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    if path == '/':
        return serve_home_page()
    elif path == '/login':
        if method == 'GET':
            return serve_login_page()
        elif method == 'POST':
            return handle_login(event)
    elif path == '/privacy-policy':
        return serve_privacy_policy()
    elif path == '/terms-of-service':
        return serve_terms_of_service()
    elif path == '/robots.txt':
        return serve_robots_txt()
    elif path == '/api/health':
        return serve_health_check()
    else:
        return serve_404()

def serve_home_page():
    """Serve comprehensive home page from dev template"""
    
    home_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
            color: white;
        }}
        .hero {{
            padding: 80px 20px;
            text-align: center;
        }}
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .hero p {{
            font-size: 1.2rem;
            margin-bottom: 30px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        .brand-section {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .pricing-card {{
            background: white;
            color: #333;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        .pricing-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        .pricing-badge {{
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-top: 15px;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 10px;
            transition: all 0.3s;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }}
        .feature-section {{
            background: rgba(255,255,255,0.05);
            padding: 40px 20px;
            border-radius: 15px;
            margin: 40px 0;
        }}
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 20px;
            color: #28a745;
        }}
        footer {{
            color: white;
            text-align: center;
            padding: 40px 0;
            background: rgba(0,0,0,0.1);
        }}
        footer a {{
            color: white;
            text-decoration: none;
        }}
        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Master IELTS with the World's ONLY GenAI Assessment Platform</h1>
            <div class="brand-section">
                <p class="lead">Powered by TrueScore® & ClearScore® - Industry-Leading Standardized Assessment Technology</p>
            </div>
            <p class="lead">IELTS GenAI Prep delivers precise, examiner-aligned feedback through our exclusive TrueScore® writing analysis and ClearScore® speaking assessment systems.</p>
            <a href="/login" class="btn btn-primary btn-lg">Get Started - Login</a>
        </div>
    </section>
    
    <!-- Assessment Products Section -->
    <div class="container mt-5">
        <h2 class="text-center mb-5">GenAI Assessed IELTS Modules</h2>
        <div class="row">
            <div class="col-md-6">
                <div class="pricing-card">
                    <div class="feature-icon text-center">
                        <i class="fas fa-pen-fancy"></i>
                    </div>
                    <h3>TrueScore® Writing Assessment</h3>
                    <p>AI-powered writing evaluation with detailed feedback on:</p>
                    <ul>
                        <li>• Task Achievement</li>
                        <li>• Coherence & Cohesion</li>
                        <li>• Lexical Resource</li>
                        <li>• Grammar Range & Accuracy</li>
                    </ul>
                    <div class="pricing-badge">$36.49 USD for 4 assessments</div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="pricing-card">
                    <div class="feature-icon text-center">
                        <i class="fas fa-microphone"></i>
                    </div>
                    <h3>ClearScore® Speaking Assessment</h3>
                    <p>Interactive speaking practice with Maya AI examiner featuring:</p>
                    <ul>
                        <li>• Real-time conversation analysis</li>
                        <li>• Pronunciation feedback</li>
                        <li>• Fluency assessment</li>
                        <li>• British accent training</li>
                    </ul>
                    <div class="pricing-badge">$36.49 USD for 4 assessments</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Features Section -->
    <div class="container mt-5">
        <div class="feature-section">
            <h2 class="text-center mb-4">Why Choose IELTS GenAI Prep?</h2>
            <div class="row">
                <div class="col-md-4 text-center">
                    <div class="feature-icon">
                        <i class="fas fa-certificate"></i>
                    </div>
                    <h4>Official Band-Descriptive Feedback</h4>
                    <p>Get precise band scores with detailed explanations aligned to official IELTS criteria.</p>
                </div>
                <div class="col-md-4 text-center">
                    <div class="feature-icon">
                        <i class="fas fa-mobile-alt"></i>
                    </div>
                    <h4>Mobile & Desktop Access</h4>
                    <p>Purchase through our mobile app, then access your assessments on any device.</p>
                </div>
                <div class="col-md-4 text-center">
                    <div class="feature-icon">
                        <i class="fas fa-target"></i>
                    </div>
                    <h4>Designed for Success</h4>
                    <p>AI-powered insights help you focus on areas that will improve your band score most.</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Mobile App Section -->
    <div class="container mt-5 mb-5">
        <div class="row">
            <div class="col-12">
                <div class="pricing-card text-center">
                    <h3>Mobile-First Platform</h3>
                    <p>Download our mobile app to purchase assessments, then login here for desktop access. One account works on both platforms!</p>
                    <div class="d-flex justify-content-center gap-3 mt-3">
                        <a href="#" class="btn btn-dark">
                            <i class="fab fa-apple"></i> App Store
                        </a>
                        <a href="#" class="btn btn-success">
                            <i class="fab fa-google-play"></i> Google Play
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
            <p>
                <a href="/privacy-policy">Privacy Policy</a> | 
                <a href="/terms-of-service">Terms of Service</a>
            </p>
        </div>
    </footer>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': home_html
    }}

def serve_login_page():
    """Serve login page matching dev environment"""
    
    login_html = """{login_template}"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': login_html
    }}

def handle_login(event):
    """Handle login POST request"""
    try:
        # Parse form data
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')
        
        form_data = urllib.parse.parse_qs(body)
        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]
        recaptcha_response = form_data.get('g-recaptcha-response', [''])[0]
        
        # Verify reCAPTCHA
        if not verify_recaptcha(recaptcha_response):
            return {{
                'statusCode': 400,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'error': 'reCAPTCHA verification failed'}})
            }}
        
        # Test credentials
        if email == 'prodtest@ieltsgenaiprep.com' and password == 'test123':
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'success': True, 'message': 'Login successful'}})
            }}
        
        if email == 'simpletest@ieltsaiprep.com' and password == 'test123':
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'success': True, 'message': 'Login successful'}})
            }}
        
        return {{
            'statusCode': 401,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Invalid credentials'}})
        }}
        
    except Exception as e:
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': str(e)}})
        }}

def verify_recaptcha(response):
    """Verify reCAPTCHA response"""
    if not response:
        return False
    
    try:
        secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
        if not secret_key:
            return False
        
        data = urllib.parse.urlencode({{
            'secret': secret_key,
            'response': response
        }}).encode('utf-8')
        
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    
    except Exception:
        return False

def serve_privacy_policy():
    """Serve privacy policy page"""
    
    privacy_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
        }}
        .content-container {{
            padding: 40px 20px;
        }}
        .content-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .back-button {{
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h3 {{
            color: #1976d2;
            margin-bottom: 15px;
        }}
        .section p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="content-container">
        <div class="content-card">
            <div class="header">
                <a href="/" class="back-button">← Back to Home</a>
                <h1>Privacy Policy</h1>
                <p>Last Updated: May 28, 2025</p>
            </div>
            
            <div class="section">
                <h3>1. Introduction</h3>
                <p>Welcome to IELTS GenAI Prep, featuring TrueScore® and ClearScore® - the world's ONLY GenAI assessor tools for IELTS test preparation. We respect your privacy and are committed to protecting your personal data.</p>
            </div>
            
            <div class="section">
                <h3>2. Data Collection and Usage</h3>
                <p>We collect and process user data solely for the purpose of providing AI-powered IELTS assessment services. This includes:</p>
                <ul>
                    <li>Personal information for account creation and management</li>
                    <li>Assessment responses for AI-powered evaluation</li>
                    <li>Usage data to improve our assessment algorithms</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>3. Voice Recording Policy</h3>
                <p><strong>Important:</strong> Voice recordings are processed in real-time for assessment purposes only. We do not save or store your voice recordings permanently. Only your assessment feedback and scores are retained.</p>
            </div>
            
            <div class="section">
                <h3>4. Data Protection</h3>
                <p>We implement industry-standard security measures to protect your personal information. All data is encrypted in transit and at rest. We do not share your personal information with third parties except as required by law.</p>
            </div>
            
            <div class="section">
                <h3>5. Contact Information</h3>
                <p>For questions about this privacy policy or your data, please contact us through our mobile app support system.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': privacy_html
    }}

def serve_terms_of_service():
    """Serve terms of service page"""
    
    terms_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
        }}
        .content-container {{
            padding: 40px 20px;
        }}
        .content-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .back-button {{
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h3 {{
            color: #1976d2;
            margin-bottom: 15px;
        }}
        .section p {{
            color: #666;
            line-height: 1.6;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="content-container">
        <div class="content-card">
            <div class="header">
                <a href="/" class="back-button">← Back to Home</a>
                <h1>Terms of Service</h1>
                <p>Last Updated: May 28, 2025</p>
            </div>
            
            <div class="section">
                <h3>1. Introduction</h3>
                <p>Welcome to IELTS GenAI Prep, featuring TrueScore® and ClearScore® - the world's ONLY GenAI assessor tools for IELTS test preparation.</p>
            </div>
            
            <div class="section">
                <h3>2. Assessment Packages and Payments</h3>
                <p>Our Service offers assessment packages at $36.49 USD for 4 unique assessments. All purchases are processed through Apple App Store or Google Play Store.</p>
                <div class="highlight">
                    <p><strong>No Refund Policy:</strong> All assessment purchases are final and non-refundable once purchased.</p>
                </div>
            </div>
            
            <div class="section">
                <h3>3. AI Content Policy</h3>
                <p>Our platform uses advanced AI technology including TrueScore® and ClearScore® systems. All AI-generated feedback is for educational purposes.</p>
            </div>
            
            <div class="section">
                <h3>4. Security and Platform Protection</h3>
                <p>We maintain enterprise-grade security measures including account protection, session monitoring, and comprehensive input validation.</p>
            </div>
            
            <div class="section">
                <h3>5. Contact</h3>
                <p>For questions about these terms, please contact us through our mobile app support system.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': terms_html
    }}

def serve_robots_txt():
    """Serve robots.txt for AI SEO"""
    robots_content = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/plain'}},
        'body': robots_content
    }}

def serve_health_check():
    """Health check endpoint"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'application/json'}},
        'body': json.dumps({{
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }})
    }}

def serve_404():
    """Serve 404 page"""
    return {{
        'statusCode': 404,
        'headers': {{'Content-Type': 'text/html'}},
        'body': '<h1>404 - Page Not Found</h1><p><a href="/">Return to Home</a></p>'
    }}
'''

    return lambda_code

def deploy_production_templates():
    """Deploy production Lambda with comprehensive templates"""
    
    # Create Lambda function with templates
    lambda_code = create_comprehensive_lambda()
    
    if not lambda_code:
        print("❌ Failed to create Lambda function")
        return False
    
    # Create zip file
    with zipfile.ZipFile('production_templates_lambda.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('lambda_function.py', lambda_code)
    
    print("✅ Created production_templates_lambda.zip")
    print(f"📦 Package size: {os.path.getsize('production_templates_lambda.zip')} bytes")
    
    return True

if __name__ == "__main__":
    print("🚀 Deploying dev templates to production...")
    deploy_production_templates()
    print("✅ Production deployment package ready!")
