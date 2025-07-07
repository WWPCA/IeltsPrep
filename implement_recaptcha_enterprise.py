import boto3
import zipfile
import tempfile
import os

# Read the comprehensive working template
with open('working_template.html', 'r', encoding='utf-8') as f:
    home_template = f.read()

# Lambda code with Google Cloud reCAPTCHA Enterprise integration
lambda_code = '''
import json
import hashlib
import secrets
import urllib.parse
import urllib.request
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

test_email = "prodtest_20250704_165313_kind@ieltsaiprep.com"
test_password = "TestProd2025!"
test_hash = hashlib.pbkdf2_hmac("sha256", test_password.encode(), b"production_salt_2025", 100000).hex()

users = {test_email: {"password_hash": test_hash, "email": test_email}}
sessions = {}

def verify_recaptcha_enterprise(token: str, user_ip: Optional[str] = None) -> bool:
    """
    Verify reCAPTCHA Enterprise token using Google Cloud reCAPTCHA Enterprise API
    Based on official Google Cloud documentation
    """
    if not token:
        print("reCAPTCHA Enterprise ERROR: No token provided")
        return False
    
    # Get reCAPTCHA Enterprise configuration from environment
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '')
    site_key = os.environ.get('RECAPTCHA_ENTERPRISE_SITE_KEY', '')
    
    if not project_id or not site_key:
        print("reCAPTCHA Enterprise ERROR: Missing GOOGLE_CLOUD_PROJECT_ID or RECAPTCHA_ENTERPRISE_SITE_KEY")
        # For development/testing, allow if no Enterprise config
        print("Falling back to standard reCAPTCHA verification for compatibility")
        return verify_standard_recaptcha(token, user_ip)
    
    try:
        # Create assessment request for reCAPTCHA Enterprise
        assessment_data = {
            "event": {
                "token": token,
                "siteKey": site_key,
                "expectedAction": "LOGIN"  # Action name for login verification
            }
        }
        
        # Add user IP if available
        if user_ip and user_ip != 'unknown':
            assessment_data["event"]["userIpAddress"] = user_ip
        
        # Google Cloud reCAPTCHA Enterprise API endpoint
        url = f"https://recaptchaenterprise.googleapis.com/v1/projects/{project_id}/assessments"
        
        # Prepare request data
        post_data = json.dumps(assessment_data).encode('utf-8')
        
        # Create request with proper headers
        request = urllib.request.Request(url, data=post_data, method='POST')
        request.add_header('Content-Type', 'application/json')
        request.add_header('User-Agent', 'IELTS-GenAI-Prep/1.0 (Enterprise)')
        
        # Add authentication header (API key or service account token)
        api_key = os.environ.get('GOOGLE_CLOUD_API_KEY', '')
        if api_key:
            url_with_key = f"{url}?key={api_key}"
            request = urllib.request.Request(url_with_key, data=post_data, method='POST')
            request.add_header('Content-Type', 'application/json')
            request.add_header('User-Agent', 'IELTS-GenAI-Prep/1.0 (Enterprise)')
        
        # Make API request
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.getcode() != 200:
                print(f"reCAPTCHA Enterprise ERROR: API returned status {response.getcode()}")
                return False
            
            response_text = response.read().decode('utf-8')
            assessment_result = json.loads(response_text)
            
            # Extract assessment results
            token_properties = assessment_result.get('tokenProperties', {})
            risk_analysis = assessment_result.get('riskAnalysis', {})
            
            # Check token validity
            if not token_properties.get('valid', False):
                invalid_reason = token_properties.get('invalidReason', 'Unknown')
                print(f"reCAPTCHA Enterprise FAILED: Token invalid - {invalid_reason}")
                return False
            
            # Check expected action
            actual_action = token_properties.get('action', '')
            if actual_action != 'LOGIN':
                print(f"reCAPTCHA Enterprise WARNING: Expected action LOGIN, got {actual_action}")
            
            # Get risk score (0.0 = very likely a bot, 1.0 = very likely a human)
            risk_score = risk_analysis.get('score', 0.0)
            reasons = risk_analysis.get('reasons', [])
            
            print(f"reCAPTCHA Enterprise SUCCESS: Score {risk_score}, Reasons: {reasons}")
            
            # Accept scores above threshold (configurable)
            score_threshold = float(os.environ.get('RECAPTCHA_SCORE_THRESHOLD', '0.5'))
            if risk_score >= score_threshold:
                print(f"reCAPTCHA Enterprise ACCEPTED: Score {risk_score} >= threshold {score_threshold}")
                return True
            else:
                print(f"reCAPTCHA Enterprise REJECTED: Score {risk_score} < threshold {score_threshold}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"reCAPTCHA Enterprise HTTP ERROR: {e.code} - {e.reason}")
        if hasattr(e, 'read'):
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"reCAPTCHA Enterprise ERROR: Response: {error_body}")
        return False
    except Exception as e:
        print(f"reCAPTCHA Enterprise EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

def verify_standard_recaptcha(token: str, user_ip: Optional[str] = None) -> bool:
    """
    Fallback to standard reCAPTCHA v2 verification for compatibility
    """
    if not token:
        print("Standard reCAPTCHA ERROR: No token provided")
        return False
    
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY', '')
    if not secret_key:
        print("Standard reCAPTCHA ERROR: No secret key configured")
        return False
    
    try:
        verification_data = {
            'secret': secret_key,
            'response': token
        }
        
        if user_ip and user_ip != 'unknown':
            verification_data['remoteip'] = user_ip
        
        post_data = urllib.parse.urlencode(verification_data).encode('utf-8')
        
        request = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=post_data,
            method='POST'
        )
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            success = response_data.get('success', False)
            
            if success:
                print("Standard reCAPTCHA SUCCESS")
                return True
            else:
                error_codes = response_data.get('error-codes', [])
                print(f"Standard reCAPTCHA FAILED: {error_codes}")
                return False
                
    except Exception as e:
        print(f"Standard reCAPTCHA ERROR: {str(e)}")
        return False

def get_client_ip(headers: Dict[str, str]) -> str:
    """Extract client IP from headers"""
    ip_headers = ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP', 'CF-Connecting-IP']
    
    for header in ip_headers:
        ip_value = headers.get(header, '').strip()
        if ip_value:
            if ',' in ip_value:
                ip_value = ip_value.split(',')[0].strip()
            if ip_value and ip_value != 'unknown':
                return ip_value
    
    return 'unknown'

def lambda_handler(event, context):
    """Main AWS Lambda handler with reCAPTCHA Enterprise support"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        headers = event.get("headers", {})
        
        print(f"REQUEST: {method} {path}")
        
        if path == "/" and method == "GET":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "public, max-age=300"
                },
                "body": """''' + home_template.replace('"""', '\\"').replace("'", "\\'") + '''"""
            }
        
        elif path == "/login" and method == "GET":
            # Detect reCAPTCHA type based on environment variables
            enterprise_site_key = os.environ.get('RECAPTCHA_ENTERPRISE_SITE_KEY', '')
            standard_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
            
            if enterprise_site_key:
                recaptcha_site_key = enterprise_site_key
                recaptcha_type = "enterprise"
                script_url = "https://www.google.com/recaptcha/enterprise.js"
                print("Using reCAPTCHA Enterprise")
            elif standard_site_key:
                recaptcha_site_key = standard_site_key
                recaptcha_type = "standard"
                script_url = "https://www.google.com/recaptcha/api.js"
                print("Using standard reCAPTCHA v2")
            else:
                print("ERROR: No reCAPTCHA configuration found")
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2 style="color: #dc3545;">reCAPTCHA Configuration Error</h2>
                        <p>No reCAPTCHA configuration found. Please configure either:</p>
                        <ul style="text-align: left; display: inline-block;">
                            <li>RECAPTCHA_ENTERPRISE_SITE_KEY for reCAPTCHA Enterprise</li>
                            <li>RECAPTCHA_V2_SITE_KEY for standard reCAPTCHA v2</li>
                        </ul>
                        <a href="/" style="color: #007bff;">Return to Home</a>
                    </body></html>"""
                }
            
            login_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Load appropriate reCAPTCHA script -->
    <script src="{script_url}?render={recaptcha_site_key}" async defer></script>
    
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }}
        .login-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 3rem;
        }}
        .home-btn {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            border-radius: 12px;
            padding: 12px 20px;
            text-decoration: none;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        .home-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            color: white;
            transform: translateY(-2px);
        }}
        .recaptcha-container {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
            min-height: 78px;
        }}
        .recaptcha-info {{
            background: #e7f3ff;
            border: 1px solid #b8daff;
            color: #004085;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <a href="/" class="home-btn">
        <i class="fas fa-home me-2"></i>Home
    </a>
    
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <div class="text-center mb-4">
                        <h2 class="mb-3">Login to IELTS GenAI Prep</h2>
                        <p class="text-muted">Access your AI-powered IELTS assessments</p>
                    </div>
                    
                    <div class="alert alert-info mb-4">
                        <h6><i class="fas fa-mobile-alt me-2"></i>Mobile-First Authentication</h6>
                        <p class="mb-2"><strong>New users:</strong> Download our mobile app first to register and purchase assessments.</p>
                        <p class="mb-0"><strong>Existing users:</strong> Login below with your mobile app credentials.</p>
                    </div>
                    
                    <div class="recaptcha-info">
                        <i class="fas fa-shield-alt me-1"></i>
                        <strong>Security:</strong> Using Google Cloud reCAPTCHA {recaptcha_type.title()} protection
                    </div>
                    
                    <form id="login-form" method="POST" action="/login">
                        <div class="mb-3">
                            <label class="form-label">Email Address</label>
                            <input type="email" class="form-control" name="email" required placeholder="Enter your email">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" required placeholder="Enter your password">
                        </div>
                        
                        <div class="recaptcha-container">
                            <div class="g-recaptcha" data-sitekey="{recaptcha_site_key}" data-action="LOGIN"></div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            <i class="fas fa-sign-in-alt me-2"></i>Login to Dashboard
                        </button>
                        
                        <input type="hidden" name="recaptcha_type" value="{recaptcha_type}">
                    </form>
                    
                    <div class="text-center">
                        <small class="text-muted">
                            By logging in, you agree to our 
                            <a href="/privacy-policy">Privacy Policy</a> and 
                            <a href="/terms-of-service">Terms of Service</a>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Handle form submission with reCAPTCHA validation
        document.getElementById('login-form').addEventListener('submit', function(e) {{
            const recaptchaResponse = document.querySelector('[name="g-recaptcha-response"]');
            
            if (!recaptchaResponse || !recaptchaResponse.value) {{
                e.preventDefault();
                alert('Please complete the reCAPTCHA verification before submitting.');
                return false;
            }}
            
            console.log('Form submitted with reCAPTCHA token');
            return true;
        }});
        
        // Log reCAPTCHA loading
        window.addEventListener('load', function() {{
            console.log('reCAPTCHA {recaptcha_type} script loaded');
        }});
    </script>
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                },
                "body": login_html
            }
        
        elif path == "/login" and method == "POST":
            body = event.get("body", "")
            data = dict(urllib.parse.parse_qsl(body))
            
            email = data.get("email", "").strip()
            password = data.get("password", "").strip()
            recaptcha_response = data.get("g-recaptcha-response", "").strip()
            recaptcha_type = data.get("recaptcha_type", "standard")
            
            print(f"LOGIN ATTEMPT: Email={email}, reCAPTCHA type={recaptcha_type}, token length={len(recaptcha_response)}")
            
            if not email or not password:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="text-align: center; padding: 50px; font-family: Arial;">
                        <h2 style="color: #dc3545;">Login Error</h2>
                        <p>Email and password are required.</p>
                        <a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                    </body></html>"""
                }
            
            user_ip = get_client_ip(headers)
            
            # Verify reCAPTCHA based on type
            if recaptcha_type == "enterprise":
                recaptcha_valid = verify_recaptcha_enterprise(recaptcha_response, user_ip)
            else:
                recaptcha_valid = verify_standard_recaptcha(recaptcha_response, user_ip)
            
            if not recaptcha_valid:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="text-align: center; padding: 50px; font-family: Arial;">
                        <h2 style="color: #dc3545;">Security Verification Failed</h2>
                        <p>reCAPTCHA verification failed. This could be due to:</p>
                        <ul style="text-align: left; display: inline-block; margin: 20px 0;">
                            <li>Incomplete reCAPTCHA challenge</li>
                            <li>Expired verification token</li>
                            <li>Low risk assessment score</li>
                            <li>Network connectivity issues</li>
                            <li>Configuration problems</li>
                        </ul>
                        <div style="margin: 20px 0; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; color: #856404;">
                            <strong>Solutions:</strong><br>
                            1. Refresh the page and try again<br>
                            2. Ensure you completed the verification<br>
                            3. Check your internet connection<br>
                            4. Try a different browser if needed
                        </div>
                        <a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                    </body></html>"""
                }
            
            print("reCAPTCHA verification successful, proceeding with authentication")
            
            # Authenticate user
            if email in users:
                stored_hash = users[email]["password_hash"]
                input_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), b"production_salt_2025", 100000).hex()
                
                if stored_hash == input_hash:
                    session_id = secrets.token_urlsafe(32)
                    sessions[session_id] = {
                        "user_email": email,
                        "expires_at": datetime.now(timezone.utc).timestamp() + 3600,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "user_ip": user_ip,
                        "recaptcha_type": recaptcha_type,
                        "recaptcha_verified": True
                    }
                    
                    print(f"LOGIN SUCCESS: Created session {session_id} for {email}")
                    
                    cookie_value = f"session_id={session_id}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=3600"
                    
                    return {
                        "statusCode": 302,
                        "headers": {
                            "Location": "/dashboard",
                            "Set-Cookie": cookie_value
                        },
                        "body": ""
                    }
            
            print(f"LOGIN FAILED: Invalid credentials for {email}")
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "text/html"},
                "body": """<html><body style="text-align: center; padding: 50px; font-family: Arial;">
                    <h2 style="color: #dc3545;">Login Failed</h2>
                    <p>Invalid email or password.</p>
                    <div style="margin: 20px 0; padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;">
                        Please check your credentials and try again.
                    </div>
                    <a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                </body></html>"""
            }
        
        elif path == "/dashboard":
            cookie_header = headers.get("Cookie", "")
            session_id = None
            
            for cookie in cookie_header.split(";"):
                if "session_id=" in cookie:
                    session_id = cookie.split("session_id=")[1].strip()
                    break
            
            if not session_id or session_id not in sessions:
                return {"statusCode": 302, "headers": {"Location": "/login"}, "body": ""}
            
            session = sessions[session_id]
            if session["expires_at"] < datetime.now(timezone.utc).timestamp():
                del sessions[session_id]
                return {"statusCode": 302, "headers": {"Location": "/login"}, "body": ""}
            
            user_email = session["user_email"]
            recaptcha_type = session.get("recaptcha_type", "standard")
            
            dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background: #f8f9fa;
        }}
        .navbar {{
            background-color: #fff !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .assessment-card {{
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            border: none;
            overflow: hidden;
        }}
        .assessment-card:hover {{
            transform: translateY(-8px);
        }}
        .welcome-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">IELTS GenAI Prep</a>
            <div class="d-flex">
                <a href="/" class="btn btn-outline-primary">
                    <i class="fas fa-home me-1"></i>Home
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container py-5" style="margin-top: 76px;">
        <div class="welcome-section">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="mb-2">Welcome to Your Assessment Dashboard</h1>
                    <p class="mb-0 opacity-75">Logged in as: {user_email}</p>
                </div>
                <div class="col-md-4 text-center">
                    <i class="fas fa-user-graduate fa-4x opacity-75"></i>
                </div>
            </div>
        </div>
        
        <div class="alert alert-success">
            <h5><i class="fas fa-shield-alt me-2"></i>Security Verified</h5>
            <p class="mb-0">
                Login secured with Google Cloud reCAPTCHA {recaptcha_type.title()}. 
                All assessment types are now available.
            </p>
        </div>
        
        <h2 class="mb-4">Available Assessments</h2>
        
        <div class="row">
            <div class="col-lg-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-header bg-success text-white text-center" style="padding: 2rem 1.5rem 1rem;">
                        <i class="fas fa-pencil-alt fa-3x mb-3"></i>
                        <h4>Academic Writing</h4>
                        <p class="mb-0">TrueScore GenAI Assessment</p>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <span class="badge bg-light text-dark">4 attempts available</span>
                        </div>
                        <p class="text-muted">AI-powered evaluation of academic writing tasks</p>
                        <a href="/assessment/academic-writing" class="btn btn-success btn-lg">
                            <i class="fas fa-play me-2"></i>Start Assessment
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-header bg-primary text-white text-center" style="padding: 2rem 1.5rem 1rem;">
                        <i class="fas fa-microphone fa-3x mb-3"></i>
                        <h4>Academic Speaking</h4>
                        <p class="mb-0">ClearScore GenAI Assessment</p>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <span class="badge bg-light text-dark">4 attempts available</span>
                        </div>
                        <p class="text-muted">AI conversation with Maya examiner</p>
                        <a href="/assessment/academic-speaking" class="btn btn-primary btn-lg">
                            <i class="fas fa-play me-2"></i>Start Assessment
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-header bg-info text-white text-center" style="padding: 2rem 1.5rem 1rem;">
                        <i class="fas fa-edit fa-3x mb-3"></i>
                        <h4>General Writing</h4>
                        <p class="mb-0">TrueScore GenAI Assessment</p>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <span class="badge bg-light text-dark">4 attempts available</span>
                        </div>
                        <p class="text-muted">General training writing evaluation</p>
                        <a href="/assessment/general-writing" class="btn btn-info btn-lg">
                            <i class="fas fa-play me-2"></i>Start Assessment
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-header bg-warning text-white text-center" style="padding: 2rem 1.5rem 1rem;">
                        <i class="fas fa-comments fa-3x mb-3"></i>
                        <h4>General Speaking</h4>
                        <p class="mb-0">ClearScore GenAI Assessment</p>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <span class="badge bg-light text-dark">4 attempts available</span>
                        </div>
                        <p class="text-muted">General training speaking practice</p>
                        <a href="/assessment/general-speaking" class="btn btn-warning btn-lg">
                            <i class="fas fa-play me-2"></i>Start Assessment
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html; charset=utf-8"},
                "body": dashboard_html
            }
        
        elif path.startswith("/assessment/"):
            assessment_type = path.replace("/assessment/", "")
            titles = {
                "academic-writing": "Academic Writing Assessment",
                "academic-speaking": "Academic Speaking Assessment", 
                "general-writing": "General Writing Assessment",
                "general-speaking": "General Speaking Assessment"
            }
            title = titles.get(assessment_type, "Assessment")
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-body text-center p-5">
                        <i class="fas fa-play-circle fa-5x text-primary mb-3"></i>
                        <h1 class="mb-3">{title}</h1>
                        <p class="lead">Assessment functionality will be integrated in the next phase.</p>
                        <a href="/dashboard" class="btn btn-primary btn-lg">
                            <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            }
        
        elif path == "/privacy-policy":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h1 class="mb-0">Privacy Policy</h1>
                    </div>
                    <div class="card-body">
                        <p><strong>Last updated:</strong> July 7, 2025</p>
                        <h3>Data Collection</h3>
                        <p>We collect information you provide when using our TrueScore® and ClearScore® assessment technologies.</p>
                        <h3>Security</h3>
                        <p>We use Google Cloud reCAPTCHA Enterprise for enhanced security and fraud protection.</p>
                        <a href="/" class="btn btn-primary">Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            }
        
        elif path == "/terms-of-service":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h1 class="mb-0">Terms of Service</h1>
                    </div>
                    <div class="card-body">
                        <p><strong>Last updated:</strong> July 7, 2025</p>
                        <h3>Assessment Products</h3>
                        <p>Each assessment product costs $36 CAD and provides 4 unique assessment attempts.</p>
                        <h3>Security</h3>
                        <p>Our platform uses Google Cloud reCAPTCHA Enterprise for user verification and security.</p>
                        <a href="/" class="btn btn-success">Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            }
        
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "text/html"},
                "body": """<html><body style="text-align: center; padding: 50px; font-family: Arial;">
                    <h1>404 Not Found</h1>
                    <p>The page you requested could not be found.</p>
                    <a href="/" style="color: #007bff;">Return to Home</a>
                </body></html>"""
            }
    
    except Exception as e:
        print(f"LAMBDA ERROR: {type(e).__name__}: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/html"},
            "body": """<html><body style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #dc3545;">Internal Server Error</h2>
                <p>An unexpected error occurred. Please try again later.</p>
                <a href="/" style="color: #007bff;">Return to Home</a>
            </body></html>"""
        }
'''

with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
    with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    zip_file_path = tmp_file.name

try:
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    with open(zip_file_path, 'rb') as zip_file:
        zip_bytes = zip_file.read()
    
    response = lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_bytes
    )
    
    print('✅ reCAPTCHA ENTERPRISE INTEGRATION DEPLOYED!')
    print(f'Function ARN: {response["FunctionArn"]}')
    print('Production URL: https://www.ieltsaiprep.com')
    print('')
    print('🔧 Google Cloud reCAPTCHA Enterprise Features:')
    print('  • Automatic detection of Enterprise vs Standard reCAPTCHA')
    print('  • Google Cloud reCAPTCHA Enterprise API integration')
    print('  • Risk analysis with configurable score thresholds')
    print('  • Token validation with action verification')
    print('  • Comprehensive error handling and logging')
    print('  • Fallback to standard reCAPTCHA v2 for compatibility')
    print('  • Enhanced security with Enterprise-grade protection')
    print('')
    print('🔧 Required Environment Variables:')
    print('  For reCAPTCHA Enterprise:')
    print('    • RECAPTCHA_ENTERPRISE_SITE_KEY')
    print('    • GOOGLE_CLOUD_PROJECT_ID')
    print('    • GOOGLE_CLOUD_API_KEY (or service account token)')
    print('    • RECAPTCHA_SCORE_THRESHOLD (optional, default: 0.5)')
    print('')
    print('  For Standard reCAPTCHA v2 (fallback):')
    print('    • RECAPTCHA_V2_SITE_KEY')
    print('    • RECAPTCHA_V2_SECRET_KEY')
    print('')
    print('✅ System will automatically:')
    print('  • Use Enterprise if RECAPTCHA_ENTERPRISE_SITE_KEY is configured')
    print('  • Fall back to standard v2 if only RECAPTCHA_V2_SITE_KEY is configured')
    print('  • Show appropriate error if no reCAPTCHA is configured')
    print('')
    print('🎯 Test with your current setup:')
    print('  1. Visit: https://www.ieltsaiprep.com/login')
    print('  2. System will detect and use appropriate reCAPTCHA type')
    print('  3. Complete verification for secure authentication')
    print('  4. Dashboard will show which security type was used')
    
    os.unlink(zip_file_path)
    
except Exception as e:
    print(f'✗ Error: {str(e)}')
    if os.path.exists(zip_file_path):
        os.unlink(zip_file_path)
