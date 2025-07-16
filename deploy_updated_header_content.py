#!/usr/bin/env python3
"""
Deploy updated header content with improved color contrast to production
"""
import boto3
import zipfile
import base64

def deploy_updated_header_content():
    """Deploy the updated header content to AWS Lambda production"""
    
    # Read the updated home template with new content and fixed contrast
    with open('working_template.html', 'r', encoding='utf-8') as f:
        home_template = f.read()
    
    # Read the login template
    with open('login.html', 'r', encoding='utf-8') as f:
        login_template = f.read()
    
    # Verify the updates are present
    if 'Welcome to IELTS GenAI Prep' not in home_template:
        print("ERROR: Updated welcome message not found in template")
        return False
    
    if 'As your personal GenAI IELTS Coach' not in home_template:
        print("ERROR: Personal coach section not found in template")
        return False
    
    if 'text-white' not in home_template:
        print("ERROR: Color contrast fixes not found in template")
        return False
    
    # Verify pricing is still correct
    pricing_count = home_template.count('$49.99')
    print(f"Template verified: Updated content present, contrast fixed, {pricing_count} instances of $49.99 pricing")
    
    # Encode templates
    home_b64 = base64.b64encode(home_template.encode('utf-8')).decode('ascii')
    login_b64 = base64.b64encode(login_template.encode('utf-8')).decode('ascii')
    
    # Create comprehensive privacy policy
    privacy_policy_html = '''<!DOCTYPE html>
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
                            <p><em>Last Updated: July 4, 2025</em></p>
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
</html>'''
    
    # Create comprehensive terms of service
    terms_of_service_html = '''<!DOCTYPE html>
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
                            <p><em>Last Updated: July 4, 2025</em></p>
                        </div>

                        <section class="terms-section mb-4">
                            <h2 class="h4">1. Service Description</h2>
                            <p>IELTS GenAI Prep provides AI-powered IELTS test preparation through TrueScore® Writing Assessment and ClearScore® Speaking Assessment technologies.</p>
                            <p>Our platform offers 4 unique assessment products:</p>
                            <ul>
                                <li>Academic Writing Assessment</li>
                                <li>General Writing Assessment</li>
                                <li>Academic Speaking Assessment</li>
                                <li>General Speaking Assessment</li>
                            </ul>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">2. Purchase Terms</h2>
                            <p>Each assessment package costs $49.99 CAD and includes 4 unique assessments.</p>
                            <p>Purchases are processed through mobile app stores (Apple App Store, Google Play Store) with their respective billing systems.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">3. AI Assessment Technology</h2>
                            <p>Our platform uses Amazon Nova Sonic for speaking assessments and Nova Micro for writing evaluations.</p>
                            <p>Voice data is processed in real-time for speaking assessments and is not stored permanently.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">4. Refund Policy</h2>
                            <p>Refunds are subject to the policies of the respective app stores where purchases are made:</p>
                            <ul>
                                <li>Apple App Store refunds are governed by Apple's refund policy</li>
                                <li>Google Play Store refunds are governed by Google's refund policy</li>
                            </ul>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">5. Limitation of Liability</h2>
                            <p>We provide educational assessment services for IELTS preparation. We do not guarantee specific IELTS test outcomes or results.</p>
                            <p>Our AI assessments are designed to help you prepare but do not replace official IELTS testing.</p>
                        </section>

                        <section class="terms-section mb-4">
                            <h2 class="h4">6. Contact Information</h2>
                            <p>For questions about these Terms of Service, please contact us through our website support channels.</p>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Encode the comprehensive templates
    privacy_b64 = base64.b64encode(privacy_policy_html.encode('utf-8')).decode('ascii')
    terms_b64 = base64.b64encode(terms_of_service_html.encode('utf-8')).decode('ascii')
    
    # Create Lambda function with updated templates
    lambda_code = f'''
import json
import base64

def lambda_handler(event, context):
    """Lambda handler with updated header content and improved color contrast"""
    path = event.get('path', '/')
    
    if path == '/':
        return serve_home_page()
    elif path == '/login':
        return serve_login_page()
    elif path == '/dashboard':
        return serve_dashboard_page()
    elif path == '/privacy-policy':
        return serve_privacy_policy()
    elif path == '/terms-of-service':
        return serve_terms_of_service()
    else:
        return serve_home_page()

def serve_home_page():
    """Serve home page with updated content and improved color contrast"""
    template_b64 = "{home_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_login_page():
    """Serve login page with working reCAPTCHA"""
    template_b64 = "{login_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_dashboard_page():
    """Serve dashboard page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body style="padding: 40px; font-family: Arial, sans-serif;">
<h2>Dashboard</h2>
<p>Welcome! Your assessments are ready.</p>
<p><strong>Test credentials:</strong> test@ieltsgenaiprep.com / testpassword123</p>
<a href="/" style="color: #667eea;">← Back to Home</a>
</body></html>"""
    }}

def serve_privacy_policy():
    """Serve comprehensive privacy policy"""
    template_b64 = "{privacy_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_terms_of_service():
    """Serve comprehensive terms of service"""
    template_b64 = "{terms_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('updated-header-content.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('updated-header-content.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying updated header content with improved color contrast...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Deployment completed!')
    return True

if __name__ == "__main__":
    deploy_updated_header_content()