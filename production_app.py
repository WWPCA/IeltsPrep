#!/usr/bin/env python3
"""
Production Flask Application for IELTS GenAI Prep
Serves the correct website templates with TrueScore® and ClearScore® branding
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    """Homepage with TrueScore® and ClearScore® branding"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register():
    """Registration page"""
    return render_template('register.html')

@app.route('/assessment-products')
def assessment_products():
    """Assessment products page"""
    return render_template('assessment_products.html')

@app.route('/qr-auth')
def qr_auth():
    """QR authentication page for mobile-to-web access"""
    return render_template('qr_auth_page.html')

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html')

@app.route('/forgot-password')
def forgot_password():
    """Forgot password page"""
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password():
    """Reset password page"""
    return render_template('reset_password.html')

@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'IELTS GenAI Prep',
        'version': '1.0.0'
    }

# AWS Lambda handler for production deployment
def lambda_handler(event, context):
    """AWS Lambda handler that runs the Flask app"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', '/'))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Handle different routes
        if path == '/' and method == 'GET':
            content = render_template('index.html')
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': content
            }
        elif path == '/login' and method == 'GET':
            content = render_template('login.html')
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': content
            }
        elif path == '/register' and method == 'GET':
            content = render_template('register.html')
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': content
            }
        elif path == '/assessment-products' and method == 'GET':
            content = render_template('assessment_products.html')
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': content
            }
        elif path == '/qr-auth' and method == 'GET':
            content = render_template('qr_auth_page.html')
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': content
            }
        elif path == '/api/health' and method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': '{"status": "healthy", "service": "IELTS GenAI Prep"}'
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': render_template('404.html')
            }
            
    except Exception as e:
        print(f"[ERROR] Lambda handler failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Internal server error: {str(e)}"}}'
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)