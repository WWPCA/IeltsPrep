import boto3
import zipfile
import tempfile
import os

# Read the comprehensive working template
with open('working_template.html', 'r', encoding='utf-8') as f:
    home_template = f.read()

# Comprehensive Lambda code with robust reCAPTCHA handling
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

def verify_recaptcha_v2(recaptcha_response: str, user_ip: Optional[str] = None) -> bool:
    """
    Comprehensive reCAPTCHA v2 verification with enhanced error handling
    Following Google reCAPTCHA documentation best practices
    """
    if not recaptcha_response:
        print("reCAPTCHA ERROR: No response token provided by client")
        return False
    
    if len(recaptcha_response) < 20:
        print("reCAPTCHA ERROR: Response token too short, likely invalid")
        return False
    
    # Get secret key from environment
    recaptcha_secret = os.environ.get('RECAPTCHA_V2_SECRET_KEY', '')
    if not recaptcha_secret:
        print("reCAPTCHA ERROR: RECAPTCHA_V2_SECRET_KEY environment variable not configured")
        return False
    
    if len(recaptcha_secret) < 30:
        print("reCAPTCHA ERROR: Secret key appears to be invalid or truncated")
        return False
    
    try:
        # Prepare verification request according to Google documentation
        verification_data = {
            'secret': recaptcha_secret,
            'response': recaptcha_response
        }
        
        # Include remote IP if available (recommended by Google)
        if user_ip and user_ip != 'unknown':
            verification_data['remoteip'] = user_ip
            print(f"reCAPTCHA: Verifying with IP {user_ip}")
        
        # Encode data for POST request
        post_data = urllib.parse.urlencode(verification_data).encode('utf-8')
        
        # Create request with proper headers
        request = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=post_data,
            method='POST'
        )
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'IELTS-GenAI-Prep/1.0 (Production)')
        request.add_header('Accept', 'application/json')
        
        # Make verification request with timeout
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.getcode() != 200:
                print(f"reCAPTCHA ERROR: Google API returned status {response.getcode()}")
                return False
                
            response_text = response.read().decode('utf-8')
            
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"reCAPTCHA ERROR: Invalid JSON response from Google: {e}")
                return False
            
            # Extract verification results
            success = response_data.get('success', False)
            error_codes = response_data.get('error-codes', [])
            hostname = response_data.get('hostname', 'unknown')
            challenge_ts = response_data.get('challenge_ts', 'unknown')
            score = response_data.get('score', None)  # For v3, but harmless for v2
            
            if success:
                print(f"reCAPTCHA SUCCESS: Verified for hostname {hostname} at {challenge_ts}")
                if score is not None:
                    print(f"reCAPTCHA: Score {score}")
                return True
            else:
                print(f"reCAPTCHA FAILED: Error codes: {error_codes}")
                
                # Log specific error meanings for debugging
                error_meanings = {
                    'missing-input-secret': 'Secret key is missing',
                    'invalid-input-secret': 'Secret key is invalid or malformed',
                    'missing-input-response': 'Response parameter is missing',
                    'invalid-input-response': 'Response parameter is invalid or malformed',
                    'bad-request': 'Request is invalid or malformed',
                    'timeout-or-duplicate': 'Response has already been validated or is too old'
                }
                
                for error_code in error_codes:
                    meaning = error_meanings.get(error_code, 'Unknown error')
                    print(f"reCAPTCHA ERROR DETAIL: {error_code} - {meaning}")
                
                return False
                
    except urllib.error.HTTPError as e:
        print(f"reCAPTCHA ERROR: HTTP error {e.code} - {e.reason}")
        if hasattr(e, 'read'):
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"reCAPTCHA ERROR: Response body: {error_body}")
        return False
    except urllib.error.URLError as e:
        print(f"reCAPTCHA ERROR: Network error - {e.reason}")
        return False
    except Exception as e:
        print(f"reCAPTCHA ERROR: Unexpected error - {type(e).__name__}: {str(e)}")
        return False

def get_client_ip(headers: Dict[str, str]) -> str:
    """Extract client IP from headers following CloudFront/API Gateway patterns"""
    # Try CloudFront/API Gateway headers in order of preference
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP', 
        'X-Client-IP',
        'CF-Connecting-IP',
        'True-Client-IP'
    ]
    
    for header in ip_headers:
        ip_value = headers.get(header, '').strip()
        if ip_value:
            # X-Forwarded-For can contain multiple IPs, take the first one
            if ',' in ip_value:
                ip_value = ip_value.split(',')[0].strip()
            if ip_value and ip_value != 'unknown':
                return ip_value
    
    return 'unknown'

def lambda_handler(event, context):
    """Main AWS Lambda handler with comprehensive error handling"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        headers = event.get("headers", {})
        
        # Log request for debugging
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
            # Get reCAPTCHA site key from environment
            recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
            
            if not recaptcha_site_key:
                print("WARNING: RECAPTCHA_V2_SITE_KEY not configured")
                # Show error page instead of broken form
                error_html = """<!DOCTYPE html>
<html><head><title>Configuration Error</title></head>
<body style="font-family: Arial; text-align: center; padding: 50px;">
<h2 style="color: #dc3545;">reCAPTCHA Configuration Error</h2>
<p>The reCAPTCHA system is not properly configured.</p>
<p>Please contact support for assistance.</p>
<a href="/" style="color: #007bff;">Return to Home</a>
</body></html>"""
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "text/html"},
                    "body": error_html
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
    
    <!-- reCAPTCHA v2 API - Load early for better UX -->
    <script src="https://www.google.com/recaptcha/api.js?render=explicit" async defer></script>
    
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
        #submit-btn {{
            transition: all 0.3s ease;
        }}
        #submit-btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
        }}
        .error-message {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
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
                    
                    <div id="error-message" class="error-message">
                        <strong>Security Verification Required:</strong> Please complete the reCAPTCHA verification below.
                    </div>
                    
                    <form id="login-form" method="POST" action="/login">
                        <div class="mb-3">
                            <label class="form-label">Email Address</label>
                            <input type="email" class="form-control" name="email" id="email" required placeholder="Enter your email">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" id="password" required placeholder="Enter your password">
                        </div>
                        
                        <div class="recaptcha-container">
                            <div id="recaptcha-widget"></div>
                        </div>
                        
                        <button type="submit" id="submit-btn" class="btn btn-primary w-100 mb-3" disabled>
                            <i class="fas fa-sign-in-alt me-2"></i>Login to Dashboard
                        </button>
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
        let recaptchaToken = null;
        let widgetId = null;
        
        // reCAPTCHA callback functions
        window.onRecaptchaLoad = function() {{
            console.log('reCAPTCHA API loaded');
            try {{
                widgetId = grecaptcha.render('recaptcha-widget', {{
                    'sitekey': '{recaptcha_site_key}',
                    'callback': onRecaptchaSuccess,
                    'expired-callback': onRecaptchaExpired,
                    'error-callback': onRecaptchaError,
                    'theme': 'light',
                    'size': 'normal'
                }});
                console.log('reCAPTCHA widget rendered with ID:', widgetId);
            }} catch (error) {{
                console.error('Error rendering reCAPTCHA:', error);
                document.getElementById('error-message').innerHTML = 
                    '<strong>reCAPTCHA Error:</strong> Failed to load security verification. Please refresh the page.';
                document.getElementById('error-message').style.display = 'block';
            }}
        }};
        
        window.onRecaptchaSuccess = function(token) {{
            console.log('reCAPTCHA verification successful');
            recaptchaToken = token;
            document.getElementById('submit-btn').disabled = false;
            document.getElementById('error-message').style.display = 'none';
        }};
        
        window.onRecaptchaExpired = function() {{
            console.log('reCAPTCHA token expired');
            recaptchaToken = null;
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('error-message').innerHTML = 
                '<strong>Verification Expired:</strong> Please complete the reCAPTCHA verification again.';
            document.getElementById('error-message').style.display = 'block';
        }};
        
        window.onRecaptchaError = function() {{
            console.error('reCAPTCHA verification error');
            recaptchaToken = null;
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('error-message').innerHTML = 
                '<strong>Verification Error:</strong> reCAPTCHA failed to load. Please refresh the page and try again.';
            document.getElementById('error-message').style.display = 'block';
        }};
        
        // Form submission handling
        document.getElementById('login-form').addEventListener('submit', function(e) {{
            if (!recaptchaToken) {{
                e.preventDefault();
                document.getElementById('error-message').innerHTML = 
                    '<strong>Security Verification Required:</strong> Please complete the reCAPTCHA verification.';
                document.getElementById('error-message').style.display = 'block';
                return false;
            }}
            
            // Add reCAPTCHA token to form
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'g-recaptcha-response';
            tokenInput.value = recaptchaToken;
            this.appendChild(tokenInput);
            
            return true;
        }});
        
        // Initialize reCAPTCHA when API loads
        window.addEventListener('load', function() {{
            if (typeof grecaptcha !== 'undefined') {{
                grecaptcha.ready(function() {{
                    onRecaptchaLoad();
                }});
            }} else {{
                // Fallback: try again after a short delay
                setTimeout(function() {{
                    if (typeof grecaptcha !== 'undefined') {{
                        grecaptcha.ready(function() {{
                            onRecaptchaLoad();
                        }});
                    }} else {{
                        console.error('reCAPTCHA API failed to load');
                        document.getElementById('error-message').innerHTML = 
                            '<strong>reCAPTCHA Loading Error:</strong> Security verification failed to load. Please refresh the page.';
                        document.getElementById('error-message').style.display = 'block';
                    }}
                }}, 2000);
            }}
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
            
            print(f"LOGIN ATTEMPT: Email={email}, reCAPTCHA token length={len(recaptcha_response)}")
            
            # Validate required fields
            if not email or not password:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="font-family: 'Roboto', sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #dc3545;">Login Error</h2>
                        <p>Email and password are required.</p>
                        <a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                    </body></html>"""
                }
            
            # Get client IP for reCAPTCHA verification
            user_ip = get_client_ip(headers)
            print(f"CLIENT IP: {user_ip}")
            
            # Verify reCAPTCHA
            if not verify_recaptcha_v2(recaptcha_response, user_ip):
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="font-family: 'Roboto', sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #dc3545;">Security Verification Failed</h2>
                        <p>reCAPTCHA verification failed. This could be due to:</p>
                        <ul style="text-align: left; display: inline-block; margin: 20px 0;">
                            <li>Incomplete reCAPTCHA challenge</li>
                            <li>Expired verification token</li>
                            <li>Network connectivity issues</li>
                            <li>Invalid or misconfigured reCAPTCHA keys</li>
                        </ul>
                        <div style="margin: 20px 0; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; color: #856404;">
                            <strong>What to try:</strong><br>
                            1. Refresh the page and try again<br>
                            2. Ensure you completed the "I'm not a robot" verification<br>
                            3. Check your internet connection<br>
                            4. Try a different browser if the issue persists
                        </div>
                        <a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                    </body></html>"""
                }
            
            print("reCAPTCHA verification passed, proceeding with authentication")
            
            # Authenticate user
            if email in users:
                stored_hash = users[email]["password_hash"]
                input_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), b"production_salt_2025", 100000).hex()
                
                if stored_hash == input_hash:
                    # Create session
                    session_id = secrets.token_urlsafe(32)
                    sessions[session_id] = {
                        "user_email": email,
                        "expires_at": datetime.now(timezone.utc).timestamp() + 3600,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "user_ip": user_ip,
                        "recaptcha_verified": True
                    }
                    
                    print(f"LOGIN SUCCESS: Created session {session_id} for {email}")
                    
                    cookie_value = f"session_id={session_id}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=3600"
                    
                    return {
                        "statusCode": 302,
                        "headers": {
                            "Location": "/dashboard",
                            "Set-Cookie": cookie_value,
                            "Cache-Control": "no-cache"
                        },
                        "body": ""
                    }
            
            print(f"LOGIN FAILED: Invalid credentials for {email}")
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "text/html"},
                "body": """<html><body style="font-family: 'Roboto', sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #dc3545;">Login Failed</h2>
                    <p>Invalid email or password.</p>
                    <div style="margin: 20px 0; padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;">
                        Please check your credentials and try again.
                    </div>
                    <a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Try Again</a>
                </body></html>"""
            }
        
        elif path == "/dashboard":
            # Session verification
            cookie_header = headers.get("Cookie", "")
            session_id = None
            
            for cookie in cookie_header.split(";"):
                if "session_id=" in cookie:
                    session_id = cookie.split("session_id=")[1].strip()
                    break
            
            if not session_id or session_id not in sessions:
                print("DASHBOARD ACCESS DENIED: No valid session")
                return {"statusCode": 302, "headers": {"Location": "/login"}, "body": ""}
            
            session = sessions[session_id]
            if session["expires_at"] < datetime.now(timezone.utc).timestamp():
                print("DASHBOARD ACCESS DENIED: Session expired")
                del sessions[session_id]
                return {"statusCode": 302, "headers": {"Location": "/login"}, "body": ""}
            
            user_email = session["user_email"]
            print(f"DASHBOARD ACCESS: User {user_email}")
            
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
            <h5><i class="fas fa-shield-alt me-2"></i>Secure Login Confirmed</h5>
            <p class="mb-0">Your login was verified with reCAPTCHA security. All assessment types are now available.</p>
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
                "headers": {
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "private, no-cache"
                },
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
            
            assessment_html = f"""<!DOCTYPE html>
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
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": assessment_html
            }
        
        elif path == "/privacy-policy":
            privacy_html = """<!DOCTYPE html>
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
                        <a href="/" class="btn btn-primary">Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": privacy_html
            }
        
        elif path == "/terms-of-service":
            terms_html = """<!DOCTYPE html>
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
                        <p>Each assessment product costs $49.99 CAD and provides 4 unique assessment attempts.</p>
                        <a href="/" class="btn btn-success">Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": terms_html
            }
        
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "text/html"},
                "body": """<html><body style="font-family: Arial; text-align: center; padding: 50px;">
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
            "body": """<html><body style="font-family: Arial; text-align: center; padding: 50px;">
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
    
    print('✅ COMPREHENSIVE reCAPTCHA FIX DEPLOYED!')
    print(f'Function ARN: {response["FunctionArn"]}')
    print('Production URL: https://www.ieltsaiprep.com')
    print('')
    print('🔧 Comprehensive Fixes Applied:')
    print('  • Enhanced reCAPTCHA v2 integration with explicit rendering')
    print('  • Comprehensive error handling with detailed logging')
    print('  • Client-side JavaScript validation and callbacks')
    print('  • Proper token validation and expiration handling')
    print('  • Robust IP extraction from CloudFront/API Gateway headers')
    print('  • Enhanced security verification with detailed error messages')
    print('  • Configuration validation with graceful degradation')
    print('  • Production-ready error handling and user feedback')
    print('')
    print('✅ Features Added:')
    print('  • Real-time reCAPTCHA status feedback')
    print('  • Automatic button state management')
    print('  • Detailed error messages for troubleshooting')
    print('  • Fallback loading mechanisms')
    print('  • Enhanced session security')
    print('')
    print('🎯 Test the complete flow:')
    print('  1. Visit: https://www.ieltsaiprep.com/login')
    print('  2. reCAPTCHA should load without errors')
    print('  3. Complete verification to enable login button')
    print('  4. Submit form for secure authentication')
    print('  5. Access dashboard with verified session')
    
    os.unlink(zip_file_path)
    
except Exception as e:
    print(f'✗ Error: {str(e)}')
    if os.path.exists(zip_file_path):
        os.unlink(zip_file_path)
