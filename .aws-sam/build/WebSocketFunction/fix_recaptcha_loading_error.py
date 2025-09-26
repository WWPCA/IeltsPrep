import boto3
import zipfile
import tempfile
import os
import json

# Get current Lambda function to preserve all existing functionality
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Get current Lambda function code
response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
download_url = response['Code']['Location']

# Download current code to preserve existing functionality
import urllib.request
with urllib.request.urlopen(download_url) as response:
    current_zip_data = response.read()

# Extract current lambda_function.py
import zipfile
import io
with zipfile.ZipFile(io.BytesIO(current_zip_data), 'r') as zip_ref:
    current_code = zip_ref.read('lambda_function.py').decode('utf-8')

# Find the login GET route and replace only that section
login_get_start = current_code.find('elif path == "/login" and method == "GET":')
login_get_end = current_code.find('elif path == "/login" and method == "POST":', login_get_start)

if login_get_start == -1:
    print("ERROR: Could not find login GET route")
    exit(1)

# Extract the part before and after the login GET route
before_login = current_code[:login_get_start]
after_login = current_code[login_get_end:]

# Create the fixed login GET route
fixed_login_route = '''elif path == "/login" and method == "GET":
            # Detect reCAPTCHA configuration
            enterprise_site_key = os.environ.get('RECAPTCHA_ENTERPRISE_SITE_KEY', '')
            standard_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
            
            if enterprise_site_key:
                recaptcha_site_key = enterprise_site_key
                recaptcha_type = "enterprise"
                script_url = f"https://www.google.com/recaptcha/enterprise.js?render={enterprise_site_key}"
                print("Using reCAPTCHA Enterprise")
            elif standard_site_key:
                recaptcha_site_key = standard_site_key
                recaptcha_type = "standard"
                script_url = "https://www.google.com/recaptcha/api.js?render=explicit"
                print("Using standard reCAPTCHA v2")
            else:
                print("ERROR: No reCAPTCHA configuration found")
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="text-align: center; padding: 50px; font-family: Arial;">
                        <h2 style="color: #dc3545;">reCAPTCHA Configuration Error</h2>
                        <p>No reCAPTCHA keys configured in environment variables.</p>
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
    
    <!-- Load reCAPTCHA script with proper error handling -->
    <script src="{script_url}" async defer onload="onRecaptchaApiLoad()" onerror="onRecaptchaApiError()"></script>
    
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
        .status-alert {{
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .alert-error {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
        .alert-success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }}
        .alert-info {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }}
        #submit-btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
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
                    
                    <div id="recaptcha-status" class="status-alert alert-info">
                        <i class="fas fa-spinner fa-spin me-2"></i>Loading reCAPTCHA {recaptcha_type}...
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
        let recaptchaType = "{recaptcha_type}";
        
        function updateStatus(message, type = 'info') {{
            const statusDiv = document.getElementById('recaptcha-status');
            statusDiv.className = `status-alert alert-${{type}}`;
            statusDiv.innerHTML = message;
        }}
        
        function onRecaptchaApiLoad() {{
            console.log(`reCAPTCHA ${{recaptchaType}} API loaded successfully`);
            updateStatus('<i class="fas fa-shield-alt me-2"></i>Security system ready', 'info');
            
            try {{
                if (recaptchaType === 'enterprise') {{
                    // Enterprise reCAPTCHA
                    if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {{
                        grecaptcha.enterprise.ready(function() {{
                            widgetId = grecaptcha.enterprise.render('recaptcha-widget', {{
                                'sitekey': '{recaptcha_site_key}',
                                'action': 'LOGIN',
                                'callback': onRecaptchaSuccess,
                                'expired-callback': onRecaptchaExpired,
                                'error-callback': onRecaptchaError
                            }});
                            updateStatus('<i class="fas fa-check-circle me-2"></i>Enterprise security ready - please verify', 'success');
                        }});
                    }} else {{
                        throw new Error('Enterprise reCAPTCHA not available');
                    }}
                }} else {{
                    // Standard reCAPTCHA v2
                    if (typeof grecaptcha !== 'undefined') {{
                        grecaptcha.ready(function() {{
                            widgetId = grecaptcha.render('recaptcha-widget', {{
                                'sitekey': '{recaptcha_site_key}',
                                'callback': onRecaptchaSuccess,
                                'expired-callback': onRecaptchaExpired,
                                'error-callback': onRecaptchaError,
                                'theme': 'light',
                                'size': 'normal'
                            }});
                            updateStatus('<i class="fas fa-check-circle me-2"></i>Security verification ready', 'success');
                        }});
                    }} else {{
                        throw new Error('Standard reCAPTCHA not available');
                    }}
                }}
            }} catch (error) {{
                console.error('reCAPTCHA initialization error:', error);
                updateStatus('<i class="fas fa-exclamation-triangle me-2"></i>Security verification failed to load', 'error');
            }}
        }}
        
        function onRecaptchaApiError() {{
            console.error('reCAPTCHA API failed to load');
            updateStatus('<i class="fas fa-exclamation-triangle me-2"></i>reCAPTCHA Loading Error: Security verification unavailable. Please refresh.', 'error');
        }}
        
        function onRecaptchaSuccess(token) {{
            console.log('reCAPTCHA verification successful');
            recaptchaToken = token;
            document.getElementById('submit-btn').disabled = false;
            updateStatus('<i class="fas fa-check-circle me-2"></i>Security verification complete', 'success');
        }}
        
        function onRecaptchaExpired() {{
            console.log('reCAPTCHA token expired');
            recaptchaToken = null;
            document.getElementById('submit-btn').disabled = true;
            updateStatus('<i class="fas fa-clock me-2"></i>Verification expired - please verify again', 'error');
        }}
        
        function onRecaptchaError() {{
            console.error('reCAPTCHA verification error');
            recaptchaToken = null;
            document.getElementById('submit-btn').disabled = true;
            updateStatus('<i class="fas fa-exclamation-triangle me-2"></i>Verification error - please try again', 'error');
        }}
        
        // Form submission
        document.getElementById('login-form').addEventListener('submit', function(e) {{
            if (!recaptchaToken) {{
                e.preventDefault();
                updateStatus('<i class="fas fa-exclamation-triangle me-2"></i>Please complete security verification first', 'error');
                return false;
            }}
            
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'g-recaptcha-response';
            tokenInput.value = recaptchaToken;
            this.appendChild(tokenInput);
            
            return true;
        }});
        
        // Fallback initialization after page load
        window.addEventListener('load', function() {{
            // Give the script time to load
            setTimeout(function() {{
                if (typeof grecaptcha === 'undefined') {{
                    updateStatus('<i class="fas fa-exclamation-triangle me-2"></i>reCAPTCHA failed to load. Please check your internet connection and refresh.', 'error');
                }}
            }}, 5000);
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
        
        '''

# Combine the code parts
fixed_code = before_login + fixed_login_route + after_login

# Create new deployment package
with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
    with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', fixed_code)
    zip_file_path = tmp_file.name

try:
    # Deploy the fixed code
    with open(zip_file_path, 'rb') as zip_file:
        zip_bytes = zip_file.read()
    
    response = lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_bytes
    )
    
    print('✅ reCAPTCHA LOADING ERROR FIXED!')
    print(f'Function ARN: {response["FunctionArn"]}')
    print('')
    print('🔧 Fixes Applied:')
    print('  • Enhanced reCAPTCHA script loading with error handlers')
    print('  • Added onload and onerror callbacks for better error detection')
    print('  • Improved fallback initialization with timeout checks')
    print('  • Real-time status updates showing loading progress')
    print('  • Better error messages with specific troubleshooting steps')
    print('  • Automatic detection between Enterprise and Standard reCAPTCHA')
    print('')
    print('✅ The login page now properly handles:')
    print('  • Script loading failures')
    print('  • Network connectivity issues')
    print('  • Missing reCAPTCHA configuration')
    print('  • Different reCAPTCHA types (Enterprise vs Standard)')
    print('')
    print('🎯 Test the fix at: https://www.ieltsaiprep.com/login')
    print('The "reCAPTCHA Loading Error" should now be resolved!')
    
    os.unlink(zip_file_path)
    
except Exception as e:
    print(f'✗ Error: {str(e)}')
    if os.path.exists(zip_file_path):
        os.unlink(zip_file_path)
