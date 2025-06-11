"""
Cookie Consent Routes Module
Handles GDPR-compliant cookie consent tracking and preferences
"""

from flask import Blueprint, request, jsonify, session
from flask_login import current_user
from models import db, ConsentRecord
from datetime import datetime
import hashlib
import json
import structlog

logger = structlog.get_logger()

cookie_consent_bp = Blueprint('cookie_consent', __name__)

@cookie_consent_bp.route('/api/cookie-consent', methods=['POST'])
def save_cookie_consent():
    """Save user's cookie consent preferences with GDPR compliance"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract consent data
        consent_type = data.get('consent_type', 'cookie_preferences')
        preferences = data.get('preferences', {})
        consent_given = data.get('consent_given', False)
        version = data.get('version', '1.0')
        
        # Validate preferences structure
        if not isinstance(preferences, dict):
            return jsonify({'error': 'Invalid preferences format'}), 400
        
        # Get user information
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Privacy-compliant hashing of IP and user agent
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest() if ip_address else None
        ua_hash = hashlib.sha256(user_agent.encode()).hexdigest() if user_agent else None
        
        # Create consent record
        consent_record = ConsentRecord(
            user_id=user_id,
            consent_type=consent_type,
            consent_given=consent_given,
            version=version,
            timestamp=datetime.utcnow(),
            ip_address_hash=ip_hash,
            user_agent_hash=ua_hash
        )
        
        db.session.add(consent_record)
        
        # Store preferences in session for non-authenticated users
        if not user_id:
            session['cookie_preferences'] = {
                'preferences': preferences,
                'timestamp': datetime.utcnow().isoformat(),
                'consent_id': consent_record.id
            }
        
        db.session.commit()
        
        logger.info(f"Cookie consent saved", 
                   user_id=user_id, 
                   consent_type=consent_type,
                   preferences=preferences)
        
        return jsonify({
            'success': True,
            'consent_id': consent_record.id,
            'message': 'Cookie preferences saved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving cookie consent: {e}")
        return jsonify({'error': 'Failed to save consent preferences'}), 500

@cookie_consent_bp.route('/api/cookie-consent', methods=['GET'])
def get_cookie_consent():
    """Retrieve user's current cookie consent preferences"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        
        if user_id:
            # Get latest consent for authenticated user
            latest_consent = ConsentRecord.query.filter_by(
                user_id=user_id,
                consent_type='cookie_preferences'
            ).order_by(ConsentRecord.timestamp.desc()).first()
            
            if latest_consent:
                return jsonify({
                    'has_consent': True,
                    'consent_given': latest_consent.consent_given,
                    'timestamp': latest_consent.timestamp.isoformat(),
                    'version': latest_consent.version
                })
        else:
            # Check session for non-authenticated users
            preferences = session.get('cookie_preferences')
            if preferences:
                return jsonify({
                    'has_consent': True,
                    'consent_given': True,
                    'timestamp': preferences['timestamp'],
                    'version': '1.0'
                })
        
        return jsonify({
            'has_consent': False,
            'consent_given': False
        })
        
    except Exception as e:
        logger.error(f"Error retrieving cookie consent: {e}")
        return jsonify({'error': 'Failed to retrieve consent preferences'}), 500

@cookie_consent_bp.route('/api/cookie-consent/withdraw', methods=['POST'])
def withdraw_cookie_consent():
    """Allow users to withdraw their cookie consent"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        
        if not user_id:
            # Clear session for non-authenticated users
            session.pop('cookie_preferences', None)
            return jsonify({
                'success': True,
                'message': 'Cookie consent withdrawn from session'
            })
        
        # Create withdrawal record for authenticated users
        withdrawal_record = ConsentRecord(
            user_id=user_id,
            consent_type='cookie_preferences_withdrawal',
            consent_given=False,
            version='1.0',
            timestamp=datetime.utcnow()
        )
        
        db.session.add(withdrawal_record)
        db.session.commit()
        
        logger.info(f"Cookie consent withdrawn", user_id=user_id)
        
        return jsonify({
            'success': True,
            'message': 'Cookie consent withdrawn successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error withdrawing cookie consent: {e}")
        return jsonify({'error': 'Failed to withdraw consent'}), 500

@cookie_consent_bp.route('/api/cookie-consent/history', methods=['GET'])
def get_consent_history():
    """Get consent history for authenticated users (GDPR compliance)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        consent_records = ConsentRecord.query.filter_by(
            user_id=current_user.id
        ).filter(
            ConsentRecord.consent_type.like('cookie%')
        ).order_by(ConsentRecord.timestamp.desc()).limit(50).all()
        
        history = []
        for record in consent_records:
            history.append({
                'id': record.id,
                'consent_type': record.consent_type,
                'consent_given': record.consent_given,
                'version': record.version,
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'history': history,
            'total_records': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving consent history: {e}")
        return jsonify({'error': 'Failed to retrieve consent history'}), 500

def check_cookie_consent(cookie_type='essential'):
    """Utility function to check if specific cookie type is allowed"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        
        if user_id:
            # Check latest consent for authenticated user
            latest_consent = ConsentRecord.query.filter_by(
                user_id=user_id,
                consent_type='cookie_preferences'
            ).order_by(ConsentRecord.timestamp.desc()).first()
            
            if latest_consent and latest_consent.consent_given:
                # For now, we assume all consented users allow all cookie types
                # In a full implementation, you'd store detailed preferences
                return True
        else:
            # Check session preferences
            preferences = session.get('cookie_preferences', {}).get('preferences', {})
            return preferences.get(cookie_type, False)
        
        # Default: only essential cookies allowed
        return cookie_type == 'essential'
        
    except Exception as e:
        logger.error(f"Error checking cookie consent: {e}")
        return cookie_type == 'essential'

def get_user_cookie_preferences():
    """Get detailed cookie preferences for current user"""
    try:
        if current_user.is_authenticated:
            # In a full implementation, you'd store detailed preferences in the database
            return {
                'essential': True,
                'analytics': True,
                'preferences': True,
                'marketing': False
            }
        else:
            return session.get('cookie_preferences', {}).get('preferences', {
                'essential': True,
                'analytics': False,
                'preferences': False,
                'marketing': False
            })
    except Exception:
        return {
            'essential': True,
            'analytics': False,
            'preferences': False,
            'marketing': False
        }

# Register the blueprint
def register_cookie_consent_routes(app):
    """Register cookie consent routes with the app"""
    app.register_blueprint(cookie_consent_bp)