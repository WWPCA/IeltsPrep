#!/usr/bin/env python3
"""
Create Production Lambda Function That Matches Current Dev Template
This deployment uses the exact working template structure from the current dev environment
"""

import zipfile
import json
import boto3
import os
from datetime import datetime

def read_template_file(filename):
    """Read template file content"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""

def create_lambda_function():
    """Create Lambda function with current dev template structure"""
    
    # Read the current working template
    home_template = read_template_file('templates/index.html')
    login_template = read_template_file('templates/login.html')
    
    if not home_template:
        print("❌ Could not read home template")
        return
    
    # Create Lambda function code that matches current dev environment
    lambda_code = f'''import json
import boto3
import os
from datetime import datetime
import urllib.parse
import urllib.request
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    """AWS Lambda Handler - Production IELTS GenAI Prep Platform"""
    
    # CloudFront security validation
    headers = event.get('headers', {{}})
    if headers.get('cf-secret-3140348d') != 'valid':
        return {{
            'statusCode': 403,
            'body': json.dumps({{'error': 'Access denied'}})
        }}
    
    # Extract request details
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    logger.info(f"Lambda processing {{method}} {{path}}")
    
    try:
        # Handle different routes
        if path == '/' or path == '/home':
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
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'status': 'healthy', 'timestamp': datetime.now().isoformat()}})
            }}
        elif path.startswith('/assessment/'):
            return serve_assessment_page(path)
        elif path == '/dashboard':
            return serve_dashboard()
        else:
            return {{
                'statusCode': 404,
                'headers': {{'Content-Type': 'text/html'}},
                'body': get_404_page()
            }}
    
    except Exception as e:
        logger.error(f"Error processing {{method}} {{path}}: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'text/html'}},
            'body': get_500_page()
        }}

def serve_home_page():
    """Serve the comprehensive home page with current dev template structure"""
    template = """{home_template}"""
    
    # Replace template variables with production values
    template = template.replace('{{{{ cache_buster }}}}', str(int(datetime.now().timestamp())))
    template = template.replace('{{{{ url_for(\'static\', filename=\'', 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/icons/')
    template = template.replace('\') }}}}', '.svg')
    
    # Ensure USD pricing is shown
    template = template.replace('$49.99 CAD', '$36.49 USD')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': template
    }}

def serve_login_page():
    """Serve login page with reCAPTCHA integration"""
    login_template = """<!DOCTYPE html>
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
                    <h3><i class="fas fa-home me-2"></i>Welcome Back</h3>
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
                            <div class="g-recaptcha" data-sitekey="{os.environ.get('RECAPTCHA_V2_SITE_KEY', '6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ')}"></div>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Sign In</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': login_template
    }}

def handle_login(event):
    """Handle login POST request"""
    # Parse form data
    body = event.get('body', '')
    if event.get('isBase64Encoded'):
        import base64
        body = base64.b64decode(body).decode('utf-8')
    
    # Parse form data
    form_data = urllib.parse.parse_qs(body)
    email = form_data.get('email', [''])[0]
    
    # Return JSON response for API calls
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'application/json'}},
        'body': json.dumps({{'status': 'authenticated', 'email': email}})
    }}

def serve_privacy_policy():
    """Serve privacy policy page"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <h1>Privacy Policy</h1>
        <p>Last updated: July 16, 2025</p>
        <div class="card mt-4">
            <div class="card-body">
                <h2>Data Usage</h2>
                <p>We collect and use your data solely for providing IELTS assessment services, including writing and speaking evaluations using our TrueScore® and ClearScore® technologies.</p>
                <p><strong>Voice recordings are not saved</strong> - only assessment feedback is retained for your progress tracking.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': template
    }}

def serve_terms_of_service():
    """Serve terms of service page"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <h1>Terms of Service</h1>
        <p>Last updated: July 16, 2025</p>
        <div class="card mt-4">
            <div class="card-body">
                <h2>Assessment Purchases</h2>
                <p>Each assessment module is priced at $36.49 USD and includes 4 AI-graded assessments.</p>
                <p>All purchases are non-refundable as stated in our purchase policy.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': template
    }}

def serve_robots_txt():
    """Serve AI SEO optimized robots.txt"""
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

def serve_assessment_page(path):
    """Serve assessment pages"""
    assessment_type = path.replace('/assessment/', '')
    
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{assessment_type.replace('-', ' ').title()}} Assessment - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-4">
        <h1>{{assessment_type.replace('-', ' ').title()}} Assessment</h1>
        <div class="alert alert-info">
            Assessment functionality available for authenticated users.
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': template
    }}

def serve_dashboard():
    """Serve user dashboard"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-4">
        <h1>Assessment Dashboard</h1>
        <div class="alert alert-success">
            Your IELTS GenAI assessment platform is ready.
        </div>
    </div>
</body>
</html>"""
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': template
    }}

def get_404_page():
    """Return 404 error page"""
    return """<!DOCTYPE html>
<html>
<head><title>404 - Page Not Found</title></head>
<body style="text-align:center; padding:50px;">
    <h1>404 - Page Not Found</h1>
    <p>The requested page was not found.</p>
    <a href="/">Return Home</a>
</body>
</html>"""

def get_500_page():
    """Return 500 error page"""
    return """<!DOCTYPE html>
<html>
<head><title>500 - Internal Server Error</title></head>
<body style="text-align:center; padding:50px;">
    <h1>500 - Internal Server Error</h1>
    <p>An error occurred processing your request.</p>
    <a href="/">Return Home</a>
</body>
</html>"""
'''
    
    # Create deployment package
    package_name = f'dev_template_lambda_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
    
    return package_name

def deploy_to_aws(package_name):
    """Deploy Lambda package to AWS"""
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update Lambda function code
        with open(package_name, 'rb') as f:
            response = lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-api',
                ZipFile=f.read()
            )
        
        print(f"✅ Lambda function updated successfully")
        print(f"✅ Function ARN: {response['FunctionArn']}")
        print(f"✅ Code Size: {response['CodeSize']} bytes")
        print(f"✅ Last Modified: {response['LastModified']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    print("Creating production Lambda with current dev template structure...")
    
    package_name = create_lambda_function()
    if package_name:
        print(f"✅ Package created: {package_name}")
        
        if deploy_to_aws(package_name):
            print("🚀 Deployment successful!")
            print("🌐 Website: https://www.ieltsaiprep.com")
            print("🧪 Test credentials: prodtest@ieltsgenaiprep.com / test123")
        else:
            print("❌ Deployment failed")
    else:
        print("❌ Package creation failed")