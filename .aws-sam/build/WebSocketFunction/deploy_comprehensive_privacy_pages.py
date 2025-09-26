#!/usr/bin/env python3
"""
Deploy comprehensive privacy policy and terms of service pages matching preview design
"""

import boto3
import json
import zipfile
import io

def create_lambda_with_comprehensive_privacy():
    """Create Lambda with comprehensive privacy policy and terms pages"""
    
    # Read the enhanced template
    try:
        with open('working_template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except:
        template_content = "Error loading template"
    
    # Read the complete login page
    try:
        with open('login.html', 'r', encoding='utf-8') as f:
            login_content = f.read()
    except:
        login_content = "Error loading login page"
    
    # Create comprehensive privacy policy HTML
    privacy_policy_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }
        .container {
            max-width: 900px;
        }
        .policy-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 20px auto;
        }
        .policy-header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .policy-header h1 {
            font-size: 28px;
            font-weight: 600;
            margin: 0;
        }
        .policy-content {
            padding: 40px;
        }
        .policy-section {
            margin-bottom: 30px;
        }
        .policy-section h2 {
            color: #333;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .policy-section p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .policy-section ul {
            color: #666;
            line-height: 1.6;
        }
        .policy-section li {
            margin-bottom: 8px;
        }
        .highlight {
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }
        .back-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            font-weight: 500;
            transition: transform 0.2s;
        }
        .back-btn:hover {
            color: white;
            text-decoration: none;
            transform: translateY(-1px);
        }
        .back-btn i {
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="policy-card">
            <div class="policy-header">
                <h1><i class="fas fa-shield-alt"></i> Privacy Policy</h1>
                <p class="mb-0">How IELTS GenAI Prep protects your information</p>
            </div>
            
            <div class="policy-content">
                <div class="highlight">
                    <strong>TrueScore® & ClearScore® Technology:</strong> Our AI-powered assessment tools are designed with privacy-first principles to protect your IELTS preparation data.
                </div>

                <section class="policy-section">
                    <h2><i class="fas fa-info-circle"></i> 1. Introduction</h2>
                    <p>Welcome to IELTS GenAI Prep, featuring TrueScore® and ClearScore® - the world's ONLY GenAI assessor tools for IELTS test preparation. We respect your privacy and are committed to protecting your personal data.</p>
                    <p>This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our IELTS preparation services.</p>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-database"></i> 2. Information We Collect</h2>
                    <p>We collect information necessary to provide our assessment services:</p>
                    <ul>
                        <li>Account information (email address)</li>
                        <li>Assessment responses and performance data</li>
                        <li>Voice recordings for speaking assessments (processed in real-time, not stored)</li>
                        <li>Usage data to improve our AI algorithms</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-cogs"></i> 3. How We Use Your Information</h2>
                    <p>Your information is used exclusively to:</p>
                    <ul>
                        <li>Provide personalized IELTS assessment and feedback through TrueScore® and ClearScore®</li>
                        <li>Generate detailed band scores and improvement recommendations</li>
                        <li>Improve our AI algorithms for better assessment accuracy</li>
                        <li>Maintain your account and provide customer support</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-lock"></i> 4. Data Protection & Security</h2>
                    <p>We implement industry-standard security measures:</p>
                    <ul>
                        <li>End-to-end encryption for all data transmission</li>
                        <li>Secure cloud storage with AWS infrastructure</li>
                        <li>Voice data processed in real-time without permanent storage</li>
                        <li>Regular security audits and updates</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-share-alt"></i> 5. Information Sharing</h2>
                    <p>We do not sell, trade, or share your personal information with third parties. Your assessment data remains confidential and is used solely for providing our services.</p>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-user-cog"></i> 6. Your Rights</h2>
                    <p>You have the right to:</p>
                    <ul>
                        <li>Access your personal data</li>
                        <li>Request correction of inaccurate information</li>
                        <li>Delete your account and associated data</li>
                        <li>Export your assessment history</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-envelope"></i> 7. Contact Information</h2>
                    <p>If you have questions about this Privacy Policy or your data, please contact us through our support channels in the mobile app.</p>
                </section>

                <div class="text-center mt-4">
                    <a href="/" class="back-btn">
                        <i class="fas fa-home"></i> Back to Home
                    </a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

    # Create comprehensive terms of service HTML
    terms_of_service_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }
        .container {
            max-width: 900px;
        }
        .policy-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 20px auto;
        }
        .policy-header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .policy-header h1 {
            font-size: 28px;
            font-weight: 600;
            margin: 0;
        }
        .policy-content {
            padding: 40px;
        }
        .policy-section {
            margin-bottom: 30px;
        }
        .policy-section h2 {
            color: #333;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .policy-section p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .policy-section ul {
            color: #666;
            line-height: 1.6;
        }
        .policy-section li {
            margin-bottom: 8px;
        }
        .highlight {
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
        }
        .back-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            font-weight: 500;
            transition: transform 0.2s;
        }
        .back-btn:hover {
            color: white;
            text-decoration: none;
            transform: translateY(-1px);
        }
        .back-btn i {
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="policy-card">
            <div class="policy-header">
                <h1><i class="fas fa-file-contract"></i> Terms of Service</h1>
                <p class="mb-0">Terms and conditions for using IELTS GenAI Prep</p>
            </div>
            
            <div class="policy-content">
                <div class="highlight">
                    <strong>Assessment Products:</strong> Each TrueScore® and ClearScore® assessment product costs $36 CAD and provides 4 unique assessment attempts.
                </div>

                <section class="policy-section">
                    <h2><i class="fas fa-handshake"></i> 1. Agreement to Terms</h2>
                    <p>By accessing and using IELTS GenAI Prep, you agree to be bound by these Terms of Service and all applicable laws and regulations.</p>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-graduation-cap"></i> 2. Service Description</h2>
                    <p>IELTS GenAI Prep provides AI-powered IELTS assessment preparation through:</p>
                    <ul>
                        <li>TrueScore® GenAI Writing Assessment for Academic and General Training</li>
                        <li>ClearScore® GenAI Speaking Assessment with AI examiner Maya</li>
                        <li>Detailed band scoring and personalized feedback</li>
                        <li>Cross-platform access via mobile app and website</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-credit-card"></i> 3. Payment Terms</h2>
                    <p>Assessment purchases are processed through official app stores:</p>
                    <ul>
                        <li>Each assessment product costs $36 CAD</li>
                        <li>Provides 4 unique assessment attempts per purchase</li>
                        <li>Payments processed through Apple App Store or Google Play Store</li>
                        <li>All sales are final - no refunds available</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-user-check"></i> 4. User Responsibilities</h2>
                    <p>As a user, you agree to:</p>
                    <ul>
                        <li>Provide accurate information during registration</li>
                        <li>Use the service for legitimate IELTS preparation purposes</li>
                        <li>Not share account credentials with others</li>
                        <li>Respect intellectual property rights</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-ban"></i> 5. Prohibited Uses</h2>
                    <p>You may not use our service to:</p>
                    <ul>
                        <li>Attempt to reverse engineer our AI algorithms</li>
                        <li>Share or distribute assessment content</li>
                        <li>Use automated systems to access the service</li>
                        <li>Violate any applicable laws or regulations</li>
                    </ul>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-shield-alt"></i> 6. Disclaimer</h2>
                    <p>IELTS GenAI Prep is an independent preparation tool and is not affiliated with or endorsed by the official IELTS testing organization.</p>
                </section>

                <section class="policy-section">
                    <h2><i class="fas fa-envelope"></i> 7. Contact Information</h2>
                    <p>For questions about these terms, please contact us through our support channels in the mobile app.</p>
                </section>

                <div class="text-center mt-4">
                    <a href="/" class="back-btn">
                        <i class="fas fa-home"></i> Back to Home
                    </a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

    # Create Lambda code with comprehensive privacy and terms pages
    lambda_code = '''import json
import os

def lambda_handler(event, context):
    """Lambda handler for IELTS GenAI Prep with comprehensive privacy and terms pages"""
    
    # Enhanced template content
    template = """''' + template_content.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Complete login page content
    login_page = """''' + login_content.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Comprehensive privacy policy
    privacy_policy = """''' + privacy_policy_html.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Comprehensive terms of service
    terms_of_service = """''' + terms_of_service_html.replace('\\', '\\\\').replace('"', '\\"') + '''"""
    
    # Get request details
    path = event.get('path', '/')
    
    # Handle home page
    if path == '/' or path == '':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': template
        }
    
    # Handle login page with dynamic reCAPTCHA key
    elif path == '/login':
        # Replace reCAPTCHA site key with environment variable
        recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
        login_html = login_page.replace('6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix', recaptcha_site_key)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': login_html
        }
    
    # Handle comprehensive privacy policy
    elif path == '/privacy-policy':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': privacy_policy
        }
    
    # Handle comprehensive terms of service
    elif path == '/terms-of-service':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            },
            'body': terms_of_service
        }
    
    # Handle API health check
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'recaptcha_key': os.environ.get('RECAPTCHA_V2_SITE_KEY', 'not_set')[:10] + '...'
            })
        }
    
    # Handle API requests
    elif path.startswith('/api/'):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'API endpoint active', 'path': path})
        }
    
    # Handle 404
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>404 Not Found</h1><p><a href="/">Return to Home</a></p>'
        }
'''
    
    return lambda_code

def deploy_comprehensive_privacy():
    """Deploy Lambda with comprehensive privacy policy and terms pages"""
    
    print("Deploying comprehensive privacy policy and terms of service pages...")
    
    # Create Lambda code
    lambda_code = create_lambda_with_comprehensive_privacy()
    
    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Deploy
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda deployed: {response['LastModified']}")
        return True
        
    except Exception as e:
        print(f"Deploy failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_comprehensive_privacy()
    if success:
        print("SUCCESS: Comprehensive privacy policy and terms pages deployed")
        print("Privacy Policy: https://www.ieltsaiprep.com/privacy-policy")
        print("Terms of Service: https://www.ieltsaiprep.com/terms-of-service")
    else:
        print("FAILED: Could not deploy comprehensive privacy pages")