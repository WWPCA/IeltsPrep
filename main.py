"""
IELTS GenAI Prep with QR Code Authentication
Testing environment for QR-based website access before AWS deployment
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import os
import json
import logging
from qr_auth_service import qr_auth_service

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "test-secret-key-for-replit")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_qr_auth(f):
    """Decorator to require QR code authentication for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('qr_session_id')
        
        if not session_id:
            return render_template('qr_login.html', 
                message="Please authenticate via the mobile app")
        
        # Verify session is still valid
        session_data = qr_auth_service.verify_website_session(session_id)
        if not session_data:
            session.pop('qr_session_id', None)
            return render_template('qr_login.html', 
                message="Session expired. Please authenticate again via the mobile app")
        
        # Store user email in session for use in protected routes
        session['user_email'] = session_data['user_email']
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/')
def home():
    """Main homepage - redirect to assessments if authenticated, otherwise show login"""
    session_id = session.get('qr_session_id')
    
    if session_id and qr_auth_service.verify_website_session(session_id):
        return redirect(url_for('assessments'))
    
    return render_template('qr_login.html')

@app.route('/login')
def login_page():
    """QR code login page"""
    return render_template('qr_login.html')

@app.route('/assessments')
@require_qr_auth
def assessments():
    """Protected assessments page - requires QR authentication"""
    user_email = session.get('user_email')
    
    if not user_email:
        return redirect(url_for('login_page'))
    
    # Get user assessments
    assessments_data = qr_auth_service.get_user_assessments(str(user_email))
    
    return render_template('assessments.html', 
        user_email=user_email,
        assessments=assessments_data.get('assessments', []),
        total_count=assessments_data.get('total_count', 0))

@app.route('/auth/verify-qr', methods=['POST'])
def verify_qr_code():
    """API endpoint for QR code verification from mobile app"""
    try:
        data = request.get_json()
        token_id = data.get('token')
        
        if not token_id:
            return jsonify({
                'success': False,
                'error': 'Token required'
            }), 400
        
        # Verify QR token
        result = qr_auth_service.verify_qr_token(token_id)
        
        if result['success']:
            # Create website session
            session['qr_session_id'] = result['session_id']
            session['user_email'] = result['user_email']
            
            logger.info(f"QR authentication successful for {result['user_email']}")
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirect_url': '/assessments'
            })
        else:
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"QR verification error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Verification failed'
        }), 500

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr_token():
    """API endpoint for mobile app to generate QR tokens after purchase"""
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        purchase_verified = data.get('purchase_verified', False)
        
        if not user_email:
            return jsonify({
                'success': False,
                'error': 'User email required'
            }), 400
        
        # Generate QR token
        result = qr_auth_service.generate_qr_token(user_email, purchase_verified)
        
        if result['success']:
            logger.info(f"QR token generated for {user_email}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Token generation failed'
        }), 500

@app.route('/api/assessment/<user_id>')
@require_qr_auth
def get_user_assessment(user_id):
    """API endpoint to get user assessments - requires authentication"""
    user_email = session.get('user_email')
    
    # Verify user can access this assessment
    if user_email != user_id and not user_email.startswith(user_id):
        return jsonify({
            'error': 'Access denied'
        }), 403
    
    assessments_data = qr_auth_service.get_user_assessments(user_email)
    return jsonify(assessments_data)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('home'))

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'architecture': 'QR Authentication Test Environment',
        'qr_auth': 'enabled',
        'session_active': bool(session.get('qr_session_id'))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)