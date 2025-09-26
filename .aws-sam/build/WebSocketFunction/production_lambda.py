import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

def verify_recaptcha_v2(recaptcha_response, user_ip=None):
    if not recaptcha_response:
        return False
    
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    if not secret_key:
        return False
    
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
    if user_ip:
        data['remoteip'] = user_ip
    
    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=encoded_data,
            method='POST'
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        data = {}
        if body and http_method == 'POST':
            try:
                data = json.loads(body)
            except:
                pass
        
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            return handle_login_page()
        elif path == '/dashboard':
            return handle_dashboard_page()
        elif path == '/api/login' and http_method == 'POST':
            user_ip = headers.get('x-forwarded-for', '').split(',')[0].strip()
            data['user_ip'] = user_ip
            return handle_user_login(data)
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/health':
            return handle_health_check()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Page not found</h1>'
            }
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Internal server error</h1>'
        }

def handle_home_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>IELTS GenAI Prep</title></head><body><h1>IELTS GenAI Prep</h1><p>AI-Powered IELTS Practice</p><a href="/login">Login</a></body></html>'
    }

def handle_login_page():
    recaptcha_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Google reCAPTCHA -->
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 3rem;
            max-width: 450px;
            width: 100%;
        }
        
        .home-btn {
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
        }
        
        .home-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            color: white;
        }
        
        .login-title {
            background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .login-subtitle {
            color: #6c757d;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .form-control {
            border-radius: 12px;
            border: 2px solid #e9ecef;
            padding: 12px 16px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: #4361ee;
            box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.15);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%);
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(67, 97, 238, 0.3);
        }
        
        .mobile-instructions {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 2rem;
        }
        
        .mobile-instructions h5 {
            color: #1976d2;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .mobile-instructions p {
            color: #424242;
            margin-bottom: 0;
            font-size: 0.95rem;
        }
        
        .recaptcha-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        
        @media (max-width: 768px) {
            .login-container {
                margin: 20px;
                padding: 2rem;
            }
            
            .login-title {
                font-size: 2rem;
            }
            
            .home-btn {
                top: 10px;
                left: 10px;
                padding: 8px 16px;
            }
        }
    </style>
</head>
<body>
    <a href="/" class="home-btn">
        <i class="fas fa-home me-2"></i>Home
    </a>
    
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="login-container">
                    <div class="text-center">
                        <h1 class="login-title">Welcome Back</h1>
                        <p class="login-subtitle">Sign in to your IELTS GenAI Prep account</p>
                    </div>
                    
                    <div class="mobile-instructions">
                        <h5><i class="fas fa-mobile-alt me-2"></i>New to IELTS GenAI Prep?</h5>
                        <p>Download our mobile app first to purchase assessments, then return here to login with the same credentials for desktop access.</p>
                    </div>
                    
                    <form id="loginForm">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" required>
                        </div>
                        
                        <div class="recaptcha-container">
                            <div class="g-recaptcha" data-sitekey="''' + recaptcha_site_key + '''"></div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-sign-in-alt me-2"></i>Sign In
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const recaptchaResponse = grecaptcha.getResponse();
        
        if (!recaptchaResponse) {
            alert('Please complete the reCAPTCHA verification');
            return;
        }
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    recaptcha_response: recaptchaResponse
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                window.location.href = '/dashboard';
            } else {
                alert(result.message || 'Login failed');
                grecaptcha.reset();
            }
        } catch (error) {
            alert('Login failed. Please try again.');
            grecaptcha.reset();
        }
    });
    </script>
</body>
</html>'''
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html_content
    }

def handle_dashboard_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Dashboard - IELTS GenAI Prep</title></head><body><h1>Dashboard</h1><p>Welcome to your IELTS GenAI Prep dashboard!</p></body></html>'
    }

def handle_user_login(data):
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    recaptcha_response = data.get('recaptcha_response', '')
    user_ip = data.get('user_ip')
    
    if not verify_recaptcha_v2(recaptcha_response, user_ip):
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Please complete the reCAPTCHA verification'})
        }
    
    if email == 'test@ieltsgenaiprep.com' and password == 'Test123!':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Login successful', 'redirect': '/dashboard'})
        }
    else:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Invalid email or password'})
        }

def handle_privacy_policy():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Privacy Policy - IELTS GenAI Prep</title></head><body><h1>Privacy Policy</h1><p>Privacy policy content here.</p></body></html>'
    }

def handle_terms_of_service():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<html><head><title>Terms of Service - IELTS GenAI Prep</title></head><body><h1>Terms of Service</h1><p>Terms of service content here.</p></body></html>'
    }

def handle_health_check():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    }
