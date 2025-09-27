"""
IELTS GenAI Prep - Production Flask Application
Secure web platform with database integration and proper authentication
"""

import os
import json
import uuid
import time
import qrcode
import io
import base64
import hashlib
from datetime import datetime, timedelta
import secrets
import requests
from urllib.parse import urlparse, urljoin

from flask import Flask, send_from_directory, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, AnonymousUserMixin, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from botocore.exceptions import ClientError

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Real CSRF token generation
def csrf_token():
    return secrets.token_urlsafe(32)

# Production configuration class
class ProductionConfig:
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_V2_SITE_KEY")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_V2_SECRET_KEY")

# Create Flask app with proper security
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Simple user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # For now, return None since we're using QR authentication
    # This can be enhanced later when full user login is implemented
    return None

# Anonymous user class for templates
class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

# Make Flask-Login current_user available in templates
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = ProductionConfig()

# Initialize AWS SES client
def get_ses_client():
    """Get AWS SES client for sending emails"""
    return boto3.client('ses', region_name='us-east-1')

def verify_recaptcha(recaptcha_response):
    """Verify reCAPTCHA response with Google"""
    if not recaptcha_response:
        return False
    
    secret_key = ProductionConfig.RECAPTCHA_SECRET_KEY
    if not secret_key:
        return False
        
    data = {
        'secret': secret_key,
        'response': recaptcha_response,
        'remoteip': request.environ.get('REMOTE_ADDR')
    }
    
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        app.logger.error(f"reCAPTCHA verification error: {e}")
        return False

def is_safe_url(target):
    """Check if redirect URL is safe"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def send_password_reset_email(email, token):
    """Send password reset email via AWS SES"""
    try:
        ses_client = get_ses_client()
        
        reset_url = url_for('reset_password', token=token, _external=True)
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reset Your IELTS GenAI Prep Password</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">Reset Your Password</h1>
                    <p style="margin: 10px 0 0; opacity: 0.9;">IELTS GenAI Prep - TrueScore® & ClearScore® Technologies</p>
                </div>
                
                <div style="background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 10px 10px;">
                    <p>Hi there,</p>
                    
                    <p>We received a request to reset your IELTS GenAI Prep account password. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Reset My Password</a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">This link will expire in 1 hour for security reasons.</p>
                    
                    <p style="color: #666; font-size: 14px;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px;">
                        If the button doesn't work, copy and paste this link into your browser:<br>
                        <a href="{reset_url}" style="color: #4361ee;">{reset_url}</a>
                    </p>
                    
                    <p style="color: #999; font-size: 12px;">
                        This email was sent from IELTS GenAI Prep. If you have questions, contact us at support@ieltsaiprep.com
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text version for email clients that don't support HTML
        text_body = f"""
        Reset Your IELTS GenAI Prep Password
        
        We received a request to reset your account password. Click the link below to create a new password:
        
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        
        IELTS GenAI Prep Support Team
        """
        
        response = ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Reset Your IELTS GenAI Prep Password'},
                'Body': {
                    'Html': {'Data': html_body},
                    'Text': {'Data': text_body}
                }
            }
        )
        
        message_id = response['MessageId']
        app.logger.info(f"[SES] Password reset email sent to {email}: {message_id}")
        return True
        
    except ClientError as e:
        app.logger.error(f"SES Error sending password reset email: {e}")
        return False
    except Exception as e:
        app.logger.error(f"Error sending password reset email: {e}")
        return False

# Import models after app creation
with app.app_context():
    import models  # This will now work since db is defined
    db.create_all()

@app.route('/')
def home():
    """Serve working template with comprehensive FAQ and all features"""
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        class AnonymousUser:
            is_authenticated = False
            email = None
        return render_template('index.html')

@app.route('/index')
def index():
    """Index route for template compatibility"""
    class AnonymousUser:
        is_authenticated = False
        email = None
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page with enhanced mobile-first design"""
    return render_template('login.html')

@app.route('/forgot_password')
def forgot_password():
    """Forgot password page"""
    class AnonymousUser:
        is_authenticated = False
        email = None
    return render_template('forgot_password.html')

@app.route('/reset_password')
def reset_password():
    """Reset password page with token"""
    token = request.args.get('token')
    if not token:
        flash('Invalid reset link. Please request a new password reset.', 'danger')
        return redirect(url_for('forgot_password'))
    
    # Verify token exists in database
    user = models.User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        flash('This reset link has expired. Please request a new password reset.', 'danger')
        return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', token=token)

@app.route('/api/login', methods=['POST'])
def api_login():
    """Secure login endpoint with reCAPTCHA validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        recaptcha_response = data.get('g-recaptcha-response', '')
        
        # Validate inputs
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        # Verify reCAPTCHA
        if not verify_recaptcha(recaptcha_response):
            return jsonify({'success': False, 'message': 'reCAPTCHA verification failed'}), 400
        
        # Find user in database
        user = models.User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Create secure session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['logged_in'] = True
        session.permanent = True
        
        app.logger.info(f"User {email} logged in successfully")
        
        return jsonify({'success': True, 'message': 'Login successful'})
        
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Secure forgot password endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid request data'}), 400
        
        email = data.get('email', '').strip().lower()
        recaptcha_response = data.get('g-recaptcha-response', '')
        
        # Validate inputs
        if not email:
            return jsonify({'status': 'error', 'message': 'Email address is required'}), 400
        
        # Verify reCAPTCHA
        if not verify_recaptcha(recaptcha_response):
            return jsonify({'status': 'error', 'message': 'reCAPTCHA verification failed'}), 400
        
        # Always return success message for security (don't reveal if email exists)
        success_message = "If this email is registered, you will receive password reset instructions."
        
        # Check if user exists
        user = models.User.query.filter_by(email=email).first()
        if user:
            # Generate secure reset token
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            # Save token to database
            user.reset_token = reset_token
            user.reset_token_expires = reset_expires
            db.session.commit()
            
            # Send email
            if send_password_reset_email(email, reset_token):
                app.logger.info(f"Password reset email sent to {email}")
            else:
                app.logger.error(f"Failed to send password reset email to {email}")
        
        return jsonify({'status': 'success', 'message': success_message})
        
    except Exception as e:
        app.logger.error(f"Forgot password error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Secure password reset endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid request data'}), 400
        
        token = data.get('token', '')
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validate inputs
        if not token or not password or not confirm_password:
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
        
        if len(password) < 8:
            return jsonify({'status': 'error', 'message': 'Password must be at least 8 characters'}), 400
        
        # Find user with valid token
        user = models.User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return jsonify({'status': 'error', 'message': 'Invalid or expired reset token. Please request a new password reset.'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        app.logger.info(f"Password reset successful for user {user.email}")
        
        return jsonify({'status': 'success', 'message': 'Password updated successfully. You will be redirected to login.'})
        
    except Exception as e:
        app.logger.error(f"Reset password error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

@app.route('/dashboard')
def dashboard():
    """User dashboard - requires authentication"""
    if 'logged_in' not in session or not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user_email=session.get('user_email'))

@app.route('/logout')
def logout():
    """Secure logout"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/assessment-products')
def assessment_products_page():
    """Assessment products page"""
    class AnonymousUser:
        is_authenticated = False
        email = None
    return render_template('assessment_products.html')

@app.route('/qr-auth')
def qr_auth_page():
    """QR code authentication page"""
    return render_template('qr_auth_page.html')

@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

# QR Authentication Security Implementation
@app.route('/api/qr/generate', methods=['POST'])
def generate_qr():
    """Generate secure QR authentication code"""
    try:
        browser_session_id = session.get('_id')  # Flask session ID
        if not browser_session_id:
            return jsonify({'success': False, 'message': 'Invalid session'}), 400
        
        # Create secure QR session
        qr_session = models.QRSession.create_session(browser_session_id, ttl_seconds=120)
        
        return jsonify({
            'success': True,
            'code': qr_session.code,
            'expires_at': qr_session.expires_at.isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"QR generation error: {e}")
        return jsonify({'success': False, 'message': 'QR generation failed'}), 500

@app.route('/api/qr/status/<code>')
def qr_status(code):
    """Check QR authentication status (long polling)"""
    try:
        qr_session = models.QRSession.query.filter_by(code=code).first()
        if not qr_session:
            return jsonify({'status': 'invalid'})
        
        if qr_session.expires_at < datetime.utcnow():
            qr_session.status = 'expired'
            db.session.commit()
            return jsonify({'status': 'expired'})
        
        if qr_session.status == 'claimed':
            # Log in the user
            user = models.User.query.get(qr_session.claimed_user_id)
            if user:
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['logged_in'] = True
                session.permanent = True
                return jsonify({'status': 'success', 'redirect': '/dashboard'})
        
        return jsonify({'status': qr_session.status})
        
    except Exception as e:
        app.logger.error(f"QR status error: {e}")
        return jsonify({'status': 'error'})

@app.route('/api/qr/claim', methods=['POST'])
def claim_qr():
    """Claim QR code from authenticated mobile session"""
    try:
        data = request.get_json()
        if not data or not data.get('code'):
            return jsonify({'success': False, 'message': 'QR code required'}), 400
        
        # Verify user is logged in on mobile
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        qr_session = models.QRSession.query.filter_by(code=data['code']).first()
        if not qr_session:
            return jsonify({'success': False, 'message': 'Invalid QR code'}), 400
        
        if qr_session.expires_at < datetime.utcnow():
            return jsonify({'success': False, 'message': 'QR code expired'}), 400
        
        if qr_session.status != 'pending':
            return jsonify({'success': False, 'message': 'QR code already used'}), 400
        
        # Claim the QR session
        qr_session.status = 'claimed'
        qr_session.claimed_user_id = user_id
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'QR authentication successful'})
        
    except Exception as e:
        app.logger.error(f"QR claim error: {e}")
        return jsonify({'success': False, 'message': 'QR claim failed'}), 500

# Assessment Access Control Implementation
@app.route('/api/assessment/start', methods=['POST'])
def start_assessment():
    """Start assessment with entitlement validation"""
    try:
        data = request.get_json()
        if not data or not data.get('product_id'):
            return jsonify({'success': False, 'message': 'Product ID required'}), 400
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        product_id = data['product_id']
        device_session_id = session.get('_id')
        
        # Transactional entitlement check with SELECT FOR UPDATE
        try:
            entitlement = models.AssessmentEntitlement.query.filter_by(
                user_id=user_id, product_id=product_id
            ).with_for_update().first()
            
            if not entitlement or entitlement.remaining_uses <= 0:
                return jsonify({'success': False, 'message': 'No assessments remaining'}), 403
            
            if entitlement.expires_at and entitlement.expires_at < datetime.utcnow():
                return jsonify({'success': False, 'message': 'Assessment package expired'}), 403
            
            # Atomically decrement and create attempt
            entitlement.remaining_uses -= 1
            
            attempt = models.AssessmentAttempt(
                user_id=user_id,
                product_id=product_id,
                device_session_id=device_session_id
            )
            db.session.add(attempt)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'attempt_id': attempt.id,
                'remaining_uses': entitlement.remaining_uses
            })
            
        except Exception as e:
            db.session.rollback()
            raise e
        
    except Exception as e:
        app.logger.error(f"Assessment start error: {e}")
        return jsonify({'success': False, 'message': 'Assessment start failed'}), 500

@app.route('/api/assessment/validate/<int:attempt_id>')
def validate_attempt(attempt_id):
    """Validate active assessment attempt"""
    try:
        user_id = session.get('user_id')
        device_session_id = session.get('_id')
        
        if not user_id:
            return jsonify({'valid': False, 'message': 'Authentication required'}), 401
        
        attempt = models.AssessmentAttempt.query.filter_by(
            id=attempt_id,
            user_id=user_id,
            device_session_id=device_session_id,
            status='active'
        ).first()
        
        if not attempt:
            return jsonify({'valid': False, 'message': 'Invalid assessment attempt'})
        
        return jsonify({'valid': True, 'product_id': attempt.product_id})
        
    except Exception as e:
        app.logger.error(f"Attempt validation error: {e}")
        return jsonify({'valid': False, 'message': 'Validation failed'})

@app.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@app.route('/register')
def register():
    """Register page - redirects to mobile app"""
    return render_template('register.html')

# Session hardening and security configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)  # Session expiry
)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)