import json
import zipfile
import os

def create_simple_lambda():
    lambda_code = '''
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime

def lambda_handler(event, context):
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    if path == '/':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''<!DOCTYPE html>
<html><head><title>IELTS GenAI Prep</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;color:white;font-family:Arial,sans-serif}.hero{padding:80px 20px;text-align:center}.hero h1{font-size:3rem;margin-bottom:20px}.hero p{font-size:1.2rem;margin-bottom:30px}.btn{padding:15px 30px;font-size:1.1rem;border-radius:10px;margin:10px}.card{background:white;color:#333;border-radius:15px;padding:30px;margin:20px 0;box-shadow:0 5px 15px rgba(0,0,0,0.1)}.pricing{background:#28a745;color:white;padding:10px 20px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:15px}</style>
</head><body>
<div class="hero"><div class="container">
<h1>IELTS GenAI Prep</h1>
<p>AI-Powered IELTS Assessment Platform</p>
<a href="/login" class="btn btn-success btn-lg">Get Started - Login</a>
</div></div>
<div class="container">
<div class="row">
<div class="col-md-6"><div class="card">
<h3>TrueScore® Writing Assessment</h3>
<p>AI-powered writing evaluation with detailed feedback.</p>
<div class="pricing">$36.49 USD for 4 assessments</div>
</div></div>
<div class="col-md-6"><div class="card">
<h3>ClearScore® Speaking Assessment</h3>
<p>Interactive speaking practice with Maya AI examiner.</p>
<div class="pricing">$36.49 USD for 4 assessments</div>
</div></div>
</div></div>
<footer class="text-center mt-5 pb-4">
<p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
<p><a href="/privacy-policy" class="text-white">Privacy Policy</a> | <a href="/terms-of-service" class="text-white">Terms of Service</a></p>
</footer>
</body></html>'''
        }
    elif path == '/login':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
<style>body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:Arial,sans-serif}.login-container{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}.login-card{background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.3);padding:40px;max-width:500px;width:100%}.home-button{position:fixed;top:20px;left:20px;background:rgba(255,255,255,0.2);border:none;border-radius:50%;width:50px;height:50px;display:flex;align-items:center;justify-content:center;color:white;font-size:20px;text-decoration:none;z-index:1000}.mobile-info{background:#e3f2fd;padding:20px;border-radius:10px;margin-bottom:30px;border-left:4px solid #2196f3}.store-buttons{display:flex;gap:10px;margin-bottom:15px}.store-button{flex:1;padding:10px 15px;border:none;border-radius:8px;color:white;text-decoration:none;text-align:center;font-weight:500}.app-store{background:#000}.google-play{background:#01875f}.form-group{margin-bottom:20px}.form-control{border-radius:10px;padding:12px 15px;border:1px solid #ddd;font-size:16px}.btn-primary{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border:none;border-radius:10px;padding:12px 30px;font-size:16px;font-weight:600;width:100%}.g-recaptcha{margin:20px 0}.footer-links{text-align:center;margin-top:30px}.footer-links a{color:#999;text-decoration:none;margin:0 10px}</style>
</head><body>
<a href="/" class="home-button"><i class="fas fa-home"></i></a>
<div class="login-container"><div class="login-card">
<div class="text-center mb-4">
<h2>Welcome Back</h2>
<p>Sign in to access your IELTS assessments</p>
</div>
<div class="mobile-info">
<h5><i class="fas fa-mobile-alt"></i> Mobile-First Platform</h5>
<p>New to IELTS GenAI Prep? Register and purchase through our mobile app first.</p>
<div class="store-buttons">
<a href="#" class="store-button app-store"><i class="fab fa-apple"></i> App Store</a>
<a href="#" class="store-button google-play"><i class="fab fa-google-play"></i> Google Play</a>
</div>
<p style="font-size:14px">One account works on both mobile app and website!</p>
</div>
<form method="POST" action="/login">
<div class="form-group">
<label for="email">Email Address</label>
<input type="email" class="form-control" id="email" name="email" required>
</div>
<div class="form-group">
<label for="password">Password</label>
<input type="password" class="form-control" id="password" name="password" required>
</div>
<div class="g-recaptcha" data-sitekey="6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ"></div>
<button type="submit" class="btn btn-primary"><i class="fas fa-sign-in-alt"></i> Sign In</button>
</form>
<div class="text-center mt-3">
<a href="/forgot-password">Forgot your password?</a>
</div>
<div class="footer-links">
<a href="/privacy-policy">Privacy Policy</a>
<a href="/terms-of-service">Terms of Service</a>
</div>
</div></div>
</body></html>'''
        }
    elif path == '/privacy-policy':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''<!DOCTYPE html>
<html><head><title>Privacy Policy - IELTS GenAI Prep</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:Arial,sans-serif}.content-container{padding:40px 20px}.content-card{background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.3);padding:40px;max-width:800px;margin:0 auto}.header{background:linear-gradient(135deg,#2196f3 0%,#1976d2 100%);color:white;padding:20px;border-radius:10px;margin-bottom:30px;text-align:center}.back-button{background:rgba(255,255,255,0.2);border:none;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;display:inline-block;margin-bottom:20px}.section{margin-bottom:30px}.section h3{color:#1976d2;margin-bottom:15px}.section p{color:#666;line-height:1.6}</style>
</head><body>
<div class="content-container"><div class="content-card">
<div class="header">
<a href="/" class="back-button">← Back to Home</a>
<h1>Privacy Policy</h1>
<p>Last Updated: June 16, 2025</p>
</div>
<div class="section">
<h3>Data Collection and Usage</h3>
<p>IELTS GenAI Prep collects and processes user data solely for providing AI-powered IELTS assessment services.</p>
</div>
<div class="section">
<h3>Voice Recording Policy</h3>
<p><strong>Important:</strong> Voice recordings are processed in real-time for assessment purposes only. We do not save or store your voice recordings.</p>
</div>
<div class="section">
<h3>Data Protection</h3>
<p>We implement industry-standard security measures to protect your personal information. All data is encrypted in transit and at rest.</p>
</div>
</div></div>
</body></html>'''
        }
    elif path == '/terms-of-service':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''<!DOCTYPE html>
<html><head><title>Terms of Service - IELTS GenAI Prep</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:Arial,sans-serif}.content-container{padding:40px 20px}.content-card{background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.3);padding:40px;max-width:800px;margin:0 auto}.header{background:linear-gradient(135deg,#2196f3 0%,#1976d2 100%);color:white;padding:20px;border-radius:10px;margin-bottom:30px;text-align:center}.back-button{background:rgba(255,255,255,0.2);border:none;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;display:inline-block;margin-bottom:20px}.section{margin-bottom:30px}.section h3{color:#1976d2;margin-bottom:15px}.section p{color:#666;line-height:1.6}.highlight{background:#fff3cd;padding:15px;border-radius:5px;margin:15px 0;border-left:4px solid #ffc107}</style>
</head><body>
<div class="content-container"><div class="content-card">
<div class="header">
<a href="/" class="back-button">← Back to Home</a>
<h1>Terms of Service</h1>
<p>Last Updated: June 16, 2025</p>
</div>
<div class="section">
<h3>Service Overview</h3>
<p>IELTS GenAI Prep provides AI-powered IELTS assessment services through our mobile app and website platform.</p>
</div>
<div class="section">
<h3>Pricing and Payments</h3>
<p>Assessment products are priced at $36.49 USD each through our mobile app.</p>
<div class="highlight">
<p><strong>No Refund Policy:</strong> All assessment purchases are final and non-refundable.</p>
</div>
</div>
<div class="section">
<h3>AI Content Policy</h3>
<p>Our platform uses advanced AI technology including TrueScore® and ClearScore® systems.</p>
</div>
</div></div>
</body></html>'''
        }
    elif path == '/robots.txt':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': '''User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml'''
        }
    elif path == '/api/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        }
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>404 - Page Not Found</h1><p><a href="/">Return to Home</a></p>'
        }
'''
    return lambda_code

with zipfile.ZipFile('simple_fixed_lambda.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('lambda_function.py', create_simple_lambda())

print("✅ Created simple_fixed_lambda.zip")
print(f"📦 Package size: {os.path.getsize('simple_fixed_lambda.zip')} bytes")
