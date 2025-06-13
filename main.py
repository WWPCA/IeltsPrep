"""
QR Authentication Test Server for .replit environment
Serves frontend and provides local test endpoints that simulate Lambda backend
"""

from flask import Flask, send_from_directory, render_template, request, jsonify, redirect, url_for
import json
import uuid
import time
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# In-memory storage for testing
qr_tokens = {}
sessions = {}
# Actual assessment data structure to match existing templates
user_assessments = {
    "test@ieltsaiprep.com": {
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
                'essay_text': 'Education plays a crucial role in shaping society. Universities should balance theoretical knowledge with practical skills to prepare graduates for evolving workplace demands...',
                'feedback': 'Well-structured response with clear task achievement and coherent organization.',
                'task1_score': 7.0,
                'task2_score': 7.0
            }
        ],
        "general_speaking": [
            {
                'id': 3,
                'title': 'General Training Speaking Assessment 1',
                'description': 'IELTS General Training Speaking test focusing on everyday situations',
                'assessment_type': 'general_speaking',
                'created_at': '2024-12-02T09:15:00Z',
                'completed': True,
                'score': 6.5,
                'transcript': 'Discussed daily routines, travel experiences, and future plans with natural flow.',
                'feedback': 'Good interaction skills with appropriate use of informal language.',
                'audio_available': False
            }
        ],
        "general_writing": [
            {
                'id': 4,
                'title': 'General Training Writing Assessment 1',
                'description': 'IELTS General Training Writing Tasks 1 & 2',
                'assessment_type': 'general_writing',
                'created_at': '2024-12-02T16:45:00Z',
                'completed': True,
                'score': 6.5,
                'essay_text': 'Letter writing task completed with appropriate tone and format, followed by opinion essay on technology in education...',
                'feedback': 'Clear communication with good task fulfillment and appropriate language use.',
                'task1_score': 6.5,
                'task2_score': 6.5
            }
        ]
    }
}

@app.route('/')
def home():
    """Serve QR login page"""
    return render_template('qr_login.html')

@app.route('/profile')
def profile():
    """Serve profile/assessments page with QR authentication"""
    # Check QR session
    session_id = request.cookies.get('qr_session_id')
    if not session_id or session_id not in sessions:
        return redirect(url_for('home'))
    
    session_data = sessions[session_id]
    if time.time() > session_data['expires_at']:
        return redirect(url_for('home'))
    
    user_email = session_data['user_email']
    user_data = user_assessments.get(user_email, {})
    
    # Mock user data for template compatibility
    class MockUser:
        def __init__(self, email):
            self.email = email
            self.account_activated = True
            self.last_login = datetime.utcnow()
            self.assessment_package_status = "active"
            self.assessment_package_expiry = datetime.utcnow() + timedelta(days=30)
        
        def has_active_assessment_package(self):
            return True
    
    # Prepare assessment data for profile template
    all_assessments = []
    for assessment_type, assessments in user_data.items():
        for assessment in assessments:
            assessment['assessment_type'] = assessment_type
            all_assessments.append(assessment)
    
    return render_template('profile.html', 
                         current_user=MockUser(user_email),
                         assessments=all_assessments,
                         assessment_types=['academic_speaking', 'academic_writing', 'general_speaking', 'general_writing'])

@app.route('/assessment/<assessment_type>')
def assessment_list(assessment_type):
    """Assessment list page with Lambda integration"""
    # Check QR session
    session_id = request.cookies.get('qr_session_id')
    if not session_id or session_id not in sessions:
        return redirect(url_for('home'))
    
    return render_template(f'assessments/{assessment_type}_selection.html',
                         assessment_type=assessment_type)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session_id = request.cookies.get('qr_session_id')
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response = redirect(url_for('home'))
    response.set_cookie('qr_session_id', '', expires=0)
    return response

@app.route('/test-mobile')
def test_mobile():
    """Serve mobile purchase simulator for testing"""
    return render_template('test_mobile.html')

# Test endpoints that simulate Lambda backend
@app.route('/api/auth/generate-qr', methods=['POST'])
def generate_qr_token():
    """Test endpoint - Generate QR token (simulates Lambda)"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', 'test@ieltsaiprep.com')
        purchase_verified = data.get('purchase_verified', True)
        
        if not purchase_verified:
            return jsonify({
                'success': False,
                'error': 'Purchase verification required'
            }), 400
        
        # Generate token
        token_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=10)
        
        qr_tokens[token_id] = {
            'token_id': token_id,
            'user_email': user_email,
            'created_at': created_at.isoformat(),
            'expires_at': int(expires_at.timestamp()),
            'used': False
        }
        
        qr_data = {
            'token': token_id,
            'domain': 'ieltsaiprep.com',
            'timestamp': int(created_at.timestamp())
        }
        
        return jsonify({
            'success': True,
            'token_id': token_id,
            'qr_data': json.dumps(qr_data),
            'expires_in_minutes': 10,
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/auth/verify-qr', methods=['POST'])
def verify_qr_token():
    """Test endpoint - Verify QR token (simulates Lambda)"""
    try:
        data = request.get_json()
        token_id = data.get('token')
        
        if not token_id or token_id not in qr_tokens:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        token_data = qr_tokens[token_id]
        
        # Check if expired
        if time.time() > token_data['expires_at']:
            return jsonify({
                'success': False,
                'error': 'Token expired'
            }), 401
        
        # Check if already used
        if token_data.get('used'):
            return jsonify({
                'success': False,
                'error': 'Token already used'
            }), 401
        
        # Mark as used
        token_data['used'] = True
        
        # Create session
        session_id = f"session_{int(time.time())}_{token_id[:8]}"
        sessions[session_id] = {
            'user_email': token_data['user_email'],
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': time.time() + 3600
        }
        
        response = jsonify({
            'success': True,
            'user_email': token_data['user_email'],
            'session_id': session_id,
            'message': 'Authentication successful',
            'redirect_url': '/profile'
        })
        
        # Set session cookie
        response.set_cookie('qr_session_id', session_id, max_age=3600)
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/assessment/<user_email>')
def get_assessments(user_email):
    """Test endpoint - Get user assessments (simulates Lambda)"""
    try:
        # Check session
        auth_header = request.headers.get('Authorization', '')
        session_id = auth_header.replace('Bearer ', '') if auth_header else None
        
        if not session_id or session_id not in sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 401
        
        session_data = sessions[session_id]
        
        # Check session expiry
        if time.time() > session_data['expires_at']:
            return jsonify({
                'success': False,
                'error': 'Session expired'
            }), 401
        
        # Get assessments from proper data structure
        user_data = user_assessments.get(user_email, {})
        all_assessments = []
        for assessment_type, assessments in user_data.items():
            for assessment in assessments:
                assessment_copy = assessment.copy()
                assessment_copy['assessment_type'] = assessment_type
                all_assessments.append(assessment_copy)
        
        return jsonify({
            'success': True,
            'assessments': all_assessments,
            'total_count': len(all_assessments)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)