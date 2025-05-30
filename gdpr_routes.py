"""
GDPR Compliance Routes
Implements comprehensive GDPR-compliant privacy features including consent management,
data portability, user rights implementation, and privacy dashboard.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from celery import shared_task

from app import db
from models import User, UserAssessmentAttempt, ConsentRecord
from enhanced_email_service import send_gdpr_notification
from security_manager import security_manager

# Configure logging
logger = logging.getLogger(__name__)

# Initialize blueprint
gdpr_bp = Blueprint('gdpr', __name__, url_prefix='/gdpr')

# Configuration
CONSENT_VERSION = os.environ.get("CONSENT_VERSION", "2.0")
DATA_EXPORT_TIMEOUT = timedelta(hours=24)
DELETION_VERIFICATION_TIMEOUT = timedelta(hours=48)

class GDPRComplianceManager:
    """Manages GDPR compliance operations with audit trails"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv']
        self.consent_types = [
            'essential_cookies',
            'analytics_cookies', 
            'marketing_communications',
            'speech_processing',
            'assessment_data_processing',
            'ai_feedback_storage'
        ]
    
    def record_consent(self, user_id, consent_type, consent_given=True):
        """
        Record user consent with versioning and audit trail
        
        Args:
            user_id (int): User ID
            consent_type (str): Type of consent
            consent_given (bool): Whether consent was given
            
        Returns:
            bool: Success status
        """
        try:
            # Validate consent type
            if consent_type not in self.consent_types:
                logger.error(f"Invalid consent type: {consent_type}")
                return False
            
            consent = ConsentRecord(
                user_id=user_id,
                consent_type=consent_type,
                consent_given=consent_given,
                version=CONSENT_VERSION,
                timestamp=datetime.utcnow(),
                ip_address_hash=security_manager._hash_ip(request.remote_addr),
                user_agent_hash=security_manager._hash_ip(request.headers.get('User-Agent', ''))
            )
            
            db.session.add(consent)
            db.session.commit()
            
            logger.info("Consent recorded", 
                       extra={'user_id': user_id, 'consent_type': consent_type, 
                              'consent_given': consent_given, 'version': CONSENT_VERSION})
            
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Consent recording error for user {user_id}: {e}")
            return False
    
    def get_user_consents(self, user_id):
        """Get all current consents for a user"""
        try:
            consents = ConsentRecord.query.filter_by(user_id=user_id).order_by(
                ConsentRecord.consent_type, ConsentRecord.timestamp.desc()
            ).all()
            
            # Get latest consent for each type
            latest_consents = {}
            for consent in consents:
                if consent.consent_type not in latest_consents:
                    latest_consents[consent.consent_type] = {
                        'given': consent.consent_given,
                        'timestamp': consent.timestamp.isoformat(),
                        'version': consent.version
                    }
            
            return latest_consents
            
        except Exception as e:
            logger.error(f"Error retrieving consents for user {user_id}: {e}")
            return {}
    
    def withdraw_consent(self, user_id, consent_type):
        """Withdraw specific consent and handle data implications"""
        try:
            # Record withdrawal
            success = self.record_consent(user_id, consent_type, consent_given=False)
            
            if success:
                # Handle data implications of consent withdrawal
                self._handle_consent_withdrawal(user_id, consent_type)
                
                logger.info(f"Consent withdrawn: {consent_type} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Consent withdrawal error for user {user_id}: {e}")
            return False
    
    def _handle_consent_withdrawal(self, user_id, consent_type):
        """Handle data processing changes when consent is withdrawn"""
        try:
            user = User.query.get(user_id)
            if not user:
                return
            
            # Handle specific consent withdrawals
            if consent_type == 'speech_processing':
                # Stop storing speech transcripts
                user.speech_processing_enabled = False
                
            elif consent_type == 'ai_feedback_storage':
                # Mark for AI feedback deletion
                user.ai_feedback_retention = False
                
            elif consent_type == 'analytics_cookies':
                # Clear analytics tracking
                user.analytics_enabled = False
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error handling consent withdrawal for user {user_id}: {e}")
    
    def prepare_data_export(self, user_id, export_format='json'):
        """Prepare comprehensive data export for user"""
        try:
            if export_format not in self.supported_formats:
                return None, "Unsupported export format"
            
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            
            # Gather all user data
            export_data = {
                'export_metadata': {
                    'user_id': user_id,
                    'export_date': datetime.utcnow().isoformat(),
                    'format': export_format,
                    'gdpr_version': CONSENT_VERSION
                },
                'profile_data': {
                    'email': user.email,
                    'account_created': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                    'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') else None,
                    'account_status': 'active' if user.account_activated else 'inactive',
                    'email_verified': user.email_verified,
                    'assessment_package_status': user.assessment_package_status
                },
                'assessment_history': [],
                'consent_records': [],
                'privacy_settings': self.get_user_consents(user_id)
            }
            
            # Get assessment attempts
            attempts = UserAssessmentAttempt.query.filter_by(user_id=user_id).all()
            for attempt in attempts:
                export_data['assessment_history'].append({
                    'attempt_id': attempt.id,
                    'assessment_type': attempt.assessment_type,
                    'start_time': attempt.start_time.isoformat(),
                    'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
                    'status': attempt.status,
                    'has_feedback': bool(attempt.ai_assessment_data)
                })
            
            # Get consent records
            consents = ConsentRecord.query.filter_by(user_id=user_id).all()
            for consent in consents:
                export_data['consent_records'].append({
                    'consent_type': consent.consent_type,
                    'consent_given': consent.consent_given,
                    'timestamp': consent.timestamp.isoformat(),
                    'version': consent.version
                })
            
            return export_data, None
            
        except Exception as e:
            logger.error(f"Data export preparation error for user {user_id}: {e}")
            return None, "Export preparation failed"

# Global instance
gdpr_manager = GDPRComplianceManager()

@gdpr_bp.route('/privacy-dashboard')
@login_required
def privacy_dashboard():
    """Display comprehensive privacy dashboard"""
    try:
        # Get user consent status
        consents = gdpr_manager.get_user_consents(current_user.id)
        
        # Get data processing summary
        user_data_summary = {
            'total_assessments': UserAssessmentAttempt.query.filter_by(user_id=current_user.id).count(),
            'account_age_days': (datetime.utcnow() - (current_user.created_at if hasattr(current_user, 'created_at') else datetime.utcnow())).days,
            'last_export': None,  # Could track in separate table
            'data_retention_policy': '2 years from last activity'
        }
        
        return render_template('gdpr/privacy_dashboard.html',
                             consents=consents,
                             data_summary=user_data_summary,
                             consent_types=gdpr_manager.consent_types)
        
    except Exception as e:
        logger.error(f"Privacy dashboard error for user {current_user.id}: {e}")
        flash('Unable to load privacy dashboard. Please try again.', 'error')
        return redirect(url_for('index'))

@gdpr_bp.route('/update-consent', methods=['POST'])
@login_required
def update_consent():
    """Update user consent preferences"""
    try:
        data = request.get_json()
        consent_type = data.get('consent_type')
        consent_given = data.get('consent_given', False)
        
        if not consent_type or consent_type not in gdpr_manager.consent_types:
            return jsonify({
                'success': False, 
                'error': 'Invalid consent type'
            }), 400
        
        # Record consent change
        success = gdpr_manager.record_consent(
            current_user.id, consent_type, consent_given
        )
        
        if success:
            # Log GDPR action
            security_manager.log_security_event(
                'gdpr_consent_updated',
                current_user.id,
                {'consent_type': consent_type, 'consent_given': consent_given}
            )
            
            # Send confirmation email if withdrawing important consent
            if not consent_given and consent_type in ['speech_processing', 'ai_feedback_storage']:
                send_gdpr_notification(
                    current_user.email,
                    'consent_withdrawal',
                    {'consent_type': consent_type, 'withdrawal_date': datetime.utcnow()}
                )
            
            return jsonify({
                'success': True,
                'message': 'Consent preference updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update consent preference'
            }), 500
            
    except Exception as e:
        logger.error(f"Consent update error for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Consent update failed'
        }), 500

@gdpr_bp.route('/request-data-export', methods=['POST'])
@login_required
def request_data_export():
    """Request comprehensive data export"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'json')
        
        # Validate format
        if export_format not in gdpr_manager.supported_formats:
            return jsonify({
                'success': False,
                'error': f'Unsupported format. Available: {gdpr_manager.supported_formats}'
            }), 400
        
        # Start async export process
        task = export_user_data_async.delay(current_user.id, export_format)
        
        # Log GDPR action
        security_manager.log_security_event(
            'gdpr_data_export_requested',
            current_user.id,
            {'format': export_format, 'task_id': task.id}
        )
        
        return jsonify({
            'success': True,
            'message': 'Data export initiated. You will receive an email when ready.',
            'task_id': task.id,
            'estimated_time': '5-10 minutes'
        })
        
    except Exception as e:
        logger.error(f"Data export request error for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Export request failed'
        }), 500

@gdpr_bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Handle account deletion with verification"""
    if request.method == 'GET':
        return render_template('gdpr/delete_account.html',
                             deletion_effects=[
                                 'All assessment history will be permanently deleted',
                                 'AI feedback and transcripts will be removed',
                                 'Account cannot be recovered after deletion',
                                 'You will receive a confirmation email'
                             ])
    
    try:
        data = request.get_json()
        confirmation = data.get('confirmation', '')
        verification_code = data.get('verification_code', '')
        
        # Verify deletion request
        if confirmation.lower() != 'delete my account':
            return jsonify({
                'success': False,
                'error': 'Please type "delete my account" to confirm'
            }), 400
        
        # Send verification email and schedule deletion
        success = schedule_account_deletion(current_user.id, current_user.email)
        
        if success:
            security_manager.log_security_event(
                'gdpr_account_deletion_requested',
                current_user.id,
                {'verification_required': True}
            )
            
            return jsonify({
                'success': True,
                'message': 'Deletion verification email sent. Please check your email and click the link to confirm.',
                'verification_expires': '48 hours'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Deletion request failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Account deletion request error for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Deletion request failed'
        }), 500

@gdpr_bp.route('/confirm-deletion/<token>')
def confirm_deletion(token):
    """Confirm and execute account deletion"""
    try:
        # Verify deletion token (implement token verification)
        user_id = verify_deletion_token(token)
        
        if not user_id:
            flash('Invalid or expired deletion link.', 'error')
            return redirect(url_for('index'))
        
        # Execute complete data deletion
        success = execute_user_data_deletion(user_id)
        
        if success:
            flash('Your account has been permanently deleted.', 'info')
            return render_template('gdpr/deletion_confirmed.html')
        else:
            flash('Account deletion failed. Please contact support.', 'error')
            return redirect(url_for('gdpr.privacy_dashboard'))
            
    except Exception as e:
        logger.error(f"Account deletion confirmation error: {e}")
        flash('Deletion confirmation failed.', 'error')
        return redirect(url_for('index'))

# Async tasks for data processing
@shared_task
def export_user_data_async(user_id, export_format='json'):
    """Asynchronously export user data"""
    try:
        export_data, error = gdpr_manager.prepare_data_export(user_id, export_format)
        
        if error:
            logger.error(f"Data export failed for user {user_id}: {error}")
            return {'success': False, 'error': error}
        
        # Save export file
        filename = f"user_{user_id}_data_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        filepath = f"/tmp/{filename}"
        
        if export_format == 'json':
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        # Add CSV export logic if needed
        
        # Send email with download link
        user = User.query.get(user_id)
        if user:
            send_gdpr_notification(
                user.email,
                'data_export_ready',
                {'filename': filename, 'download_expires': '24 hours'}
            )
        
        logger.info(f"Data export completed for user {user_id}")
        return {'success': True, 'filename': filename}
        
    except Exception as e:
        logger.error(f"Async data export error for user {user_id}: {e}")
        return {'success': False, 'error': str(e)}

def schedule_account_deletion(user_id, email):
    """Schedule account deletion with verification"""
    try:
        # Generate deletion token
        token = generate_deletion_token(user_id)
        
        # Send verification email
        send_gdpr_notification(
            email,
            'account_deletion_verification',
            {'verification_token': token, 'expires_hours': 48}
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Account deletion scheduling error for user {user_id}: {e}")
        return False

def execute_user_data_deletion(user_id):
    """Execute complete and verified user data deletion"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Delete all related data
        UserAssessmentAttempt.query.filter_by(user_id=user_id).delete()
        ConsentRecord.query.filter_by(user_id=user_id).delete()
        
        # Delete user account
        db.session.delete(user)
        db.session.commit()
        
        # Log deletion completion
        security_manager.log_security_event(
            'gdpr_account_deleted',
            user_id,
            {'deletion_completed': True, 'email': user.email}
        )
        
        logger.info(f"User data deletion completed for user {user_id}")
        return True
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"User data deletion error for user {user_id}: {e}")
        return False

def generate_deletion_token(user_id):
    """Generate secure deletion verification token"""
    import secrets
    import jwt
    
    payload = {
        'user_id': user_id,
        'action': 'delete_account',
        'exp': datetime.utcnow() + DELETION_VERIFICATION_TIMEOUT
    }
    
    secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_deletion_token(token):
    """Verify deletion token and return user ID"""
    try:
        import jwt
        
        secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        if payload.get('action') == 'delete_account':
            return payload.get('user_id')
        
        return None
        
    except jwt.ExpiredSignatureError:
        logger.warning("Expired deletion token")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid deletion token")
        return None