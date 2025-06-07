"""
Domain Verification Dashboard
Admin interface for monitoring Amazon SES domain verification status
"""

from flask import Blueprint, render_template, jsonify, request
from enhanced_email_service import email_service
import logging

logger = logging.getLogger(__name__)

domain_verification_bp = Blueprint('domain_verification', __name__)

@domain_verification_bp.route('/admin/domain-verification')
def domain_verification_dashboard():
    """Domain verification status dashboard"""
    try:
        verification_status = email_service.check_domain_verification()
        
        return render_template('admin/domain_verification.html', 
                             verification_status=verification_status)
    except Exception as e:
        logger.error(f"Error loading domain verification dashboard: {e}")
        return render_template('admin/domain_verification.html', 
                             error="Unable to load verification status")

@domain_verification_bp.route('/admin/api/domain-verification-status')
def domain_verification_status_api():
    """API endpoint for domain verification status"""
    try:
        verification_status = email_service.check_domain_verification()
        
        return jsonify({
            'success': True,
            'data': verification_status
        })
    except Exception as e:
        logger.error(f"Error checking domain verification status: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to check verification status'
        }), 500

@domain_verification_bp.route('/admin/test-email', methods=['POST'])
def test_email_sending():
    """Test email sending functionality"""
    try:
        test_email = request.json.get('email', 'test@example.com')
        
        result = email_service.send_email(
            to_email=test_email,
            subject="IELTS GenAI Prep - Email Test",
            html_content="""
            <html>
            <body>
                <h2>Email Test Successful</h2>
                <p>This is a test email from IELTS GenAI Prep.</p>
                <p>If you receive this, your email service is working correctly.</p>
            </body>
            </html>
            """,
            text_content="Email Test Successful\n\nThis is a test email from IELTS GenAI Prep.\nIf you receive this, your email service is working correctly."
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error testing email: {e}")
        return jsonify({
            'success': False,
            'error': 'Email test failed'
        }), 500