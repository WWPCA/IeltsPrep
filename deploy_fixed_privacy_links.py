#!/usr/bin/env python3
"""
Deploy login template with fixed privacy policy and terms of service links
"""
import boto3
import zipfile
import base64

def deploy_fixed_privacy_links():
    """Deploy login template with corrected privacy policy and terms links"""
    
    # Read the updated login template
    with open('login.html', 'r', encoding='utf-8') as f:
        login_template = f.read()
    
    # Read the working home page template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        home_template = f.read()
    
    # Verify login template has our own privacy policy links
    if '/privacy-policy' not in login_template or '/terms-of-service' not in login_template:
        print("ERROR: Login template not updated with our privacy policy links")
        return False
    
    # Verify home template still has correct pricing
    if '$36' not in home_template:
        print("ERROR: Home template missing $36 pricing")
        return False
    
    print("Templates verified - deploying...")
    
    # Encode templates
    home_b64 = base64.b64encode(home_template.encode('utf-8')).decode('ascii')
    login_b64 = base64.b64encode(login_template.encode('utf-8')).decode('ascii')
    
    # Create Lambda function with privacy policy and terms of service handlers
    lambda_code = f'''
import json
import base64

def lambda_handler(event, context):
    """Lambda handler with privacy policy and terms of service pages"""
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
    """Serve home page with correct $36 pricing"""
    template_b64 = "{home_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_login_page():
    """Serve login page with working reCAPTCHA and fixed privacy links"""
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
    """Serve privacy policy page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': """<!DOCTYPE html>
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
                        <h2>Information Collection and Use</h2>
                        <p>We collect information you provide directly to us, such as when you create an account, make a purchase, or contact us for support.</p>
                        
                        <h2>AI Technology and Data Processing</h2>
                        <p>Our platform uses Amazon Nova Sonic and Nova Micro AI technologies to provide assessment services. Voice data is processed in real-time and not stored permanently.</p>
                        
                        <h2>Data Security</h2>
                        <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
                        
                        <h2>Contact Information</h2>
                        <p>If you have any questions about this Privacy Policy, please contact us through our support channels.</p>
                        
                        <p class="text-muted"><small>Last updated: July 2025</small></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    }}

def serve_terms_of_service():
    """Serve terms of service page"""
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': """<!DOCTYPE html>
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
                        <h2>Service Description</h2>
                        <p>IELTS GenAI Prep provides AI-powered IELTS test preparation services through mobile applications and web platform access.</p>
                        
                        <h2>Purchase Terms</h2>
                        <p>Assessment packages are purchased through mobile app stores (Apple App Store, Google Play) at $36 CAD each for 4 unique assessments.</p>
                        
                        <h2>AI Assessment Services</h2>
                        <p>Our platform uses advanced AI technology including Amazon Nova Sonic for speaking assessments and Nova Micro for writing evaluations.</p>
                        
                        <h2>Refund Policy</h2>
                        <p>Refunds are subject to the policies of the respective app stores (Apple App Store, Google Play Store) where purchases are made.</p>
                        
                        <h2>Limitation of Liability</h2>
                        <p>We provide educational assessment services and do not guarantee specific IELTS test outcomes.</p>
                        
                        <p class="text-muted"><small>Last updated: July 2025</small></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('privacy-links-fixed.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('privacy-links-fixed.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying privacy policy and terms of service links fix...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Deployment completed!')
    return True

if __name__ == "__main__":
    deploy_fixed_privacy_links()