"""
IELTS GenAI Prep - Production Flask Application
Uses real AWS DynamoDB instead of mock services
"""

import os
import json
import uuid
import time
import qrcode
import io
import base64
import secrets
import hashlib
from datetime import datetime, timedelta

from flask import Flask, send_from_directory, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Import production DynamoDB connection
from dynamodb_dal import DynamoDBConnection, UserDAL, AssessmentDAL, SessionDAL

# Production configuration
def csrf_token():
    return secrets.token_urlsafe(32)

class ProductionConfig:
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_V2_SITE_KEY")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_V2_SECRET_KEY")

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_urlsafe(32))
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = ProductionConfig()

# Initialize AWS DynamoDB connections
try:
    # Use production DynamoDB
    region = os.environ.get('AWS_REGION', 'us-east-1')
    db_connection = DynamoDBConnection(region=region)
    
    # Initialize Data Access Layers
    user_dal = UserDAL(db_connection)
    
    print(f"[PRODUCTION] Connected to DynamoDB in region: {region}")
    
except Exception as e:
    print(f"[ERROR] Failed to connect to DynamoDB: {e}")
    print("[FALLBACK] Using mock services for development")
    # Fallback to mock services if DynamoDB unavailable
    from aws_mock_config import aws_mock
    db_connection = aws_mock
    user_dal = None

# Real assessment data (replace this with DynamoDB queries in production)
def get_user_assessments(email):
    """Get user assessments from DynamoDB"""
    if user_dal:
        try:
            # Get user first
            user = user_dal.get_user_by_email(email)
            if user:
                # In production, this would query AssessmentDAL
                return {
                    "academic_speaking": [],
                    "academic_writing": [],
                    "general_speaking": [],
                    "general_writing": []
                }
        except Exception as e:
            print(f"[ERROR] Failed to get user assessments: {e}")
    
    # Fallback data for development
    return {
        "test@ieltsgenaiprep.com": {
            "academic_speaking": [
                {
                    'id': 1,
                    'title': 'Academic Speaking Assessment 1',
                    'description': 'Comprehensive IELTS Academic Speaking test with AI examiner Maya',
                    'assessment_type': 'academic_speaking',
                    'created_at': '2024-12-01T10:00:00Z',
                    'completed': True,
                    'score': 7.5,
                    'transcript': 'User discussed education systems with excellent fluency and vocabulary range.',
                    'feedback': 'Strong performance with natural conversation flow and appropriate register.',
                    'audio_available': False
                }
            ],
            "academic_writing": [
                {
                    'id': 2,
                    'title': 'Academic Writing Assessment 1',
                    'description': 'IELTS Academic Writing Tasks 1 & 2 with TrueScore feedback',
                    'assessment_type': 'academic_writing',
                    'created_at': '2024-12-01T14:30:00Z',
                    'completed': True,
                    'score': 7.0,
                    'essay_text': 'Education plays a crucial role in shaping society.',
                    'feedback': 'Well-structured response with clear task achievement.',
                    'task1_score': 7.0,
                    'task2_score': 7.0
                }
            ],
            "general_speaking": [],
            "general_writing": []
        }
    }.get(email, {"academic_speaking": [], "academic_writing": [], "general_speaking": [], "general_writing": []})

@app.route('/')
def home():
    """Serve working template with comprehensive FAQ and all features"""
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        # Fallback to index.html if working template not found
        class AnonymousUser:
            is_authenticated = False
            email = None
        return render_template('index.html', current_user=AnonymousUser())

@app.route('/login')
def login():
    """Login page with reCAPTCHA"""
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login API request"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'})
        
        # Verify credentials using DynamoDB
        if user_dal:
            user = user_dal.get_user_by_email(email)
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                return jsonify({'success': True, 'message': 'Login successful'})
        else:
            # Fallback for development
            if email == "test@ieltsgenaiprep.com" and password == "testpassword123":
                session['user_id'] = 'test-user-id'
                session['email'] = email
                return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
        
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return jsonify({'success': False, 'message': 'Login failed'})

@app.route('/dashboard')
def dashboard():
    """User dashboard showing available assessments"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    email = session.get('email')
    assessments = get_user_assessments(email)
    
    class User:
        is_authenticated = True
        email = session.get('email')
    
    return render_template('dashboard.html', 
                         current_user=User(),
                         user_assessments=assessments)

@app.route('/qr-auth')
def qr_auth():
    """QR authentication page"""
    return render_template('qr_auth_page.html')

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file"""
    try:
        with open('robots.txt', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return "User-agent: *\nAllow: /", 200, {'Content-Type': 'text/plain'}

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)