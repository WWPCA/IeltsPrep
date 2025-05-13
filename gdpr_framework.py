"""
Enhanced GDPR Compliance Framework

This module provides a comprehensive framework for GDPR compliance,
implementing the data protection principles, user rights, and necessary
technical measures to ensure regulatory compliance across regions.

Key features:
- User consent management
- Data access requests
- Right to be forgotten
- Data portability
- Data protection impact assessments
- Breach notification management
- Comprehensive data processing records
"""

import os
import json
import logging
import csv
import datetime
from io import StringIO
from datetime import datetime, timedelta
from flask import current_app, session, request, jsonify, render_template, redirect, url_for
from app import app, db
from models import User, AssessmentSession
import gcp_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================================================
# Consent Management
# ==================================================

def get_user_consent_settings(user_id):
    """
    Get the current consent settings for a user
    
    Args:
        user_id (int): The user ID
    
    Returns:
        dict: User's consent settings
    """
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Get consent settings from user profile or settings
            # This assumes consent data is stored in a JSON field or similar
            if hasattr(user, 'consent_settings') and user.consent_settings:
                if isinstance(user.consent_settings, str):
                    return json.loads(user.consent_settings)
                return user.consent_settings
            
            # Default settings if none exist
            return {
                'marketing_emails': False,
                'data_processing': True,  # Required for service functionality
                'audio_processing': True,
                'analytics': False,
                'third_party_sharing': False,
                'consent_version': '1.0',
                'consent_date': datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error retrieving consent settings: {str(e)}")
        return None

def update_user_consent(user_id, consent_data):
    """
    Update a user's consent settings
    
    Args:
        user_id (int): The user ID
        consent_data (dict): The consent settings to update
    
    Returns:
        bool: True if update was successful
    """
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Get current settings
            current_settings = get_user_consent_settings(user_id) or {}
            
            # Update with new settings
            current_settings.update(consent_data)
            
            # Add/update metadata
            current_settings['consent_version'] = current_settings.get('consent_version', '1.0')
            current_settings['consent_date'] = datetime.utcnow().isoformat()
            current_settings['ip_address'] = request.remote_addr
            current_settings['user_agent'] = request.user_agent.string if request.user_agent else 'Unknown'
            
            # Save back to user
            if hasattr(User, 'consent_settings'):
                setattr(user, 'consent_settings', json.dumps(current_settings))
                db.session.commit()
                logger.info(f"Updated consent settings for user {user_id}")
                return True
            else:
                logger.error(f"User model does not have consent_settings field")
                return False
    except Exception as e:
        logger.error(f"Error updating consent settings: {str(e)}")
        return False

def log_consent_activity(user_id, activity_type, details):
    """
    Log a consent-related activity for audit purposes
    
    Args:
        user_id (int): The user ID
        activity_type (str): Type of activity (e.g., 'consent_updated', 'data_access_request')
        details (dict): Additional details about the activity
    
    Returns:
        bool: True if logging was successful
    """
    try:
        log_entry = {
            'user_id': user_id,
            'activity_type': activity_type,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr if request else 'N/A',
            'user_agent': request.user_agent.string if request and request.user_agent else 'N/A',
            'details': details
        }
        
        # Log to file
        log_dir = 'gdpr_logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'consent_activity_{datetime.utcnow().strftime("%Y%m%d")}.log')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Logged consent activity: {activity_type} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error logging consent activity: {str(e)}")
        return False

# ==================================================
# Data Access and Portability
# ==================================================

def generate_user_data_report(user_id, report_format='json'):
    """
    Generate a comprehensive data report for a user
    
    Args:
        user_id (int): The user ID
        report_format (str): Format of the report ('json' or 'csv')
    
    Returns:
        tuple: (success (bool), report_data (str) or error message)
    """
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Collect all user data
            user_data = {
                'account_info': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'region': user.region,
                    'join_date': user.join_date.isoformat() if user.join_date else None,
                    'last_login': None,  # Add if tracked
                    'subscription_status': user.subscription_status,
                    'subscription_expiry': user.subscription_expiry.isoformat() if user.subscription_expiry else None,
                    'preferred_language': user.preferred_language,
                    'test_preference': user.test_preference
                },
                'activity': {
                    'current_streak': user.current_streak,
                    'longest_streak': user.longest_streak,
                    'last_activity_date': user.last_activity_date.isoformat() if user.last_activity_date else None,
                    'activity_history': user.activity_history,
                    'test_history': user.test_history
                },
                'test_attempts': []
            }
            
            # Add assessment sessions
            sessions = AssessmentSession.query.filter_by(user_id=user_id).all()
            for session in sessions:
                attempt_data = {
                    'id': session.id,
                    'product_id': session.product_id,
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'status': session.status
                }
                
                # Only include assessment summary, not full details
                if session.assessment_data:
                    try:
                        assessment = json.loads(session.assessment_data)
                        if isinstance(assessment, dict):
                            summary = {
                                'overall_band': assessment.get('overall_band', 0),
                                'scores': assessment.get('scores', {})
                            }
                            attempt_data['assessment_summary'] = summary
                    except:
                        attempt_data['assessment_summary'] = None
                
                user_data['test_attempts'].append(attempt_data)
            
            # Format the report
            if report_format == 'json':
                return True, json.dumps(user_data, indent=2)
            elif report_format == 'csv':
                output = StringIO()
                writer = csv.writer(output)
                
                # Write account info
                writer.writerow(['Account Information'])
                for key, value in user_data['account_info'].items():
                    writer.writerow([key, value])
                
                writer.writerow([])
                writer.writerow(['Activity Information'])
                for key, value in user_data['activity'].items():
                    if key not in ['activity_history', 'test_history']:
                        writer.writerow([key, value])
                
                writer.writerow([])
                writer.writerow(['Test Attempts'])
                writer.writerow(['ID', 'Test ID', 'Date', 'Score', 'Overall Band'])
                
                for attempt in user_data['test_attempts']:
                    overall_band = attempt.get('assessment_summary', {}).get('overall_band', 'N/A')
                    writer.writerow([
                        attempt['id'], 
                        attempt['test_id'], 
                        attempt['attempt_date'], 
                        attempt['score'],
                        overall_band
                    ])
                
                return True, output.getvalue()
            else:
                return False, "Unsupported report format"
    except Exception as e:
        logger.error(f"Error generating user data report: {str(e)}")
        return False, f"Error generating report: {str(e)}"

def export_user_data(user_id, include_assessments=True):
    """
    Export user data for portability (GDPR Article 20)
    
    Args:
        user_id (int): The user ID
        include_assessments (bool): Whether to include detailed assessment data
    
    Returns:
        tuple: (success (bool), export_data (dict) or error message)
    """
    try:
        success, report_data = generate_user_data_report(user_id)
        if not success:
            return False, report_data
        
        export_data = json.loads(report_data)
        
        # Log the export
        log_consent_activity(user_id, 'data_export', {
            'timestamp': datetime.utcnow().isoformat(),
            'include_assessments': include_assessments
        })
        
        return True, export_data
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        return False, f"Error: {str(e)}"

# ==================================================
# Right to be Forgotten (Data Deletion)
# ==================================================

def process_deletion_request(user_id, deletion_type='partial', verification_code=None):
    """
    Process a data deletion request (GDPR Article 17)
    
    Args:
        user_id (int): The user ID
        deletion_type (str): Type of deletion ('partial' or 'complete')
        verification_code (str): Verification code for security
    
    Returns:
        tuple: (success (bool), message (str))
    """
    try:
        # Verify request with code (implementation depends on how codes are generated/stored)
        # This is a stub - real implementation would verify the code
        code_verified = True  # For example purposes
        
        if not code_verified:
            return False, "Verification failed"
        
        # Import specific deletion utility
        from delete_user_data import (
            delete_user_cloud_data,
            delete_transcript_data,
            fully_delete_user_data
        )
        
        # Log the deletion request
        log_consent_activity(user_id, 'deletion_request', {
            'deletion_type': deletion_type,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Perform deletion
        if deletion_type == 'partial':
            # Delete sensitive data but keep account
            cloud_success = delete_user_cloud_data(user_id)
            transcript_success = delete_transcript_data(user_id)
            
            if cloud_success and transcript_success:
                return True, "Sensitive data has been deleted while maintaining your account"
            else:
                return False, "Partial deletion encountered errors"
        
        elif deletion_type == 'complete':
            # Complete account deletion
            success = fully_delete_user_data(user_id, confirm=True)
            
            if success:
                return True, "Your account and all associated data have been permanently deleted"
            else:
                return False, "Complete deletion encountered errors"
        else:
            return False, "Invalid deletion type"
    
    except Exception as e:
        logger.error(f"Error processing deletion request: {str(e)}")
        return False, f"Error: {str(e)}"

# ==================================================
# Data Protection Impact Assessment (DPIA)
# ==================================================

def record_dpia_activity(activity_data):
    """
    Record a Data Protection Impact Assessment activity
    
    Args:
        activity_data (dict): Data about the DPIA activity
    
    Returns:
        bool: True if recording was successful
    """
    try:
        # Ensure required fields
        required_fields = ['title', 'description', 'data_types', 'risk_level', 'mitigation']
        for field in required_fields:
            if field not in activity_data:
                logger.error(f"Missing required DPIA field: {field}")
                return False
        
        # Add metadata
        activity_data['timestamp'] = datetime.utcnow().isoformat()
        activity_data['recorded_by'] = activity_data.get('recorded_by', 'system')
        
        # Write to DPIA log
        dpia_dir = 'gdpr_logs/dpia'
        os.makedirs(dpia_dir, exist_ok=True)
        
        log_file = os.path.join(dpia_dir, f"dpia_{activity_data.get('id', datetime.utcnow().strftime('%Y%m%d%H%M%S'))}.json")
        with open(log_file, 'w') as f:
            json.dump(activity_data, f, indent=2)
        
        logger.info(f"Recorded DPIA activity: {activity_data['title']}")
        return True
    
    except Exception as e:
        logger.error(f"Error recording DPIA activity: {str(e)}")
        return False

# ==================================================
# Breach Notification Management
# ==================================================

def record_data_breach(breach_data):
    """
    Record a data breach incident
    
    Args:
        breach_data (dict): Data about the breach
    
    Returns:
        tuple: (success (bool), breach_id (str) or error message)
    """
    try:
        # Ensure required fields
        required_fields = ['description', 'severity', 'affected_data', 'affected_users']
        for field in required_fields:
            if field not in breach_data:
                logger.error(f"Missing required breach field: {field}")
                return False, f"Missing required field: {field}"
        
        # Add metadata
        breach_id = breach_data.get('id', datetime.utcnow().strftime('%Y%m%d%H%M%S'))
        breach_data['breach_id'] = breach_id
        breach_data['timestamp'] = datetime.utcnow().isoformat()
        breach_data['recorded_by'] = breach_data.get('recorded_by', 'system')
        breach_data['status'] = breach_data.get('status', 'recorded')
        
        # Write to breach log
        breach_dir = 'gdpr_logs/breaches'
        os.makedirs(breach_dir, exist_ok=True)
        
        log_file = os.path.join(breach_dir, f"breach_{breach_id}.json")
        with open(log_file, 'w') as f:
            json.dump(breach_data, f, indent=2)
        
        logger.info(f"Recorded data breach: {breach_id}")
        
        # If severe, trigger notification process
        if breach_data.get('severity') in ['high', 'critical']:
            # This would trigger email alerts, etc.
            logger.warning(f"CRITICAL DATA BREACH RECORDED: {breach_id}")
        
        return True, breach_id
    
    except Exception as e:
        logger.error(f"Error recording data breach: {str(e)}")
        return False, f"Error: {str(e)}"

def update_breach_status(breach_id, status_update):
    """
    Update the status of a recorded breach
    
    Args:
        breach_id (str): ID of the breach to update
        status_update (dict): Status update information
    
    Returns:
        bool: True if update was successful
    """
    try:
        breach_file = os.path.join('gdpr_logs/breaches', f"breach_{breach_id}.json")
        
        if not os.path.exists(breach_file):
            logger.error(f"Breach file not found: {breach_file}")
            return False
        
        # Read existing breach data
        with open(breach_file, 'r') as f:
            breach_data = json.load(f)
        
        # Update status
        breach_data['status'] = status_update.get('status', breach_data.get('status'))
        breach_data['resolution'] = status_update.get('resolution', breach_data.get('resolution'))
        breach_data['last_updated'] = datetime.utcnow().isoformat()
        breach_data['updated_by'] = status_update.get('updated_by', 'system')
        
        # Add update to history
        if 'update_history' not in breach_data:
            breach_data['update_history'] = []
        
        breach_data['update_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'status': status_update.get('status'),
            'notes': status_update.get('notes'),
            'updated_by': status_update.get('updated_by', 'system')
        })
        
        # Write updated data
        with open(breach_file, 'w') as f:
            json.dump(breach_data, f, indent=2)
        
        logger.info(f"Updated breach status: {breach_id} to {status_update.get('status')}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating breach status: {str(e)}")
        return False

# ==================================================
# Processing Records (Article 30)
# ==================================================

def record_processing_activity(activity_type, details):
    """
    Record data processing activity for compliance with GDPR Article 30
    
    Args:
        activity_type (str): Type of processing activity
        details (dict): Details about the activity
    
    Returns:
        bool: True if recording was successful
    """
    try:
        # Add metadata
        record = {
            'activity_type': activity_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        
        # Write to processing log
        processing_dir = 'gdpr_logs/processing'
        os.makedirs(processing_dir, exist_ok=True)
        
        # Use daily log files
        log_file = os.path.join(processing_dir, f"processing_{datetime.utcnow().strftime('%Y%m%d')}.log")
        with open(log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        logger.debug(f"Recorded processing activity: {activity_type}")
        return True
    
    except Exception as e:
        logger.error(f"Error recording processing activity: {str(e)}")
        return False

# ==================================================
# Cookie Management
# ==================================================

def get_cookie_categories():
    """
    Get the cookie categories used by the application
    
    Returns:
        list: List of cookie categories with details
    """
    return [
        {
            'id': 'essential',
            'name': 'Essential',
            'description': 'Essential cookies are necessary for the website to function and cannot be disabled.',
            'required': True
        },
        {
            'id': 'functional',
            'name': 'Functional',
            'description': 'Functional cookies help perform certain functionalities like sharing content, collecting feedback, and other third-party features.',
            'required': False
        },
        {
            'id': 'analytics',
            'name': 'Analytics',
            'description': 'Analytics cookies are used to understand how visitors interact with the website.',
            'required': False
        },
        {
            'id': 'marketing',
            'name': 'Marketing',
            'description': 'Marketing cookies are used to provide visitors with relevant ads and marketing campaigns.',
            'required': False
        }
    ]

def get_user_cookie_preferences(user_id=None):
    """
    Get cookie preferences for a user or from session
    
    Args:
        user_id (int, optional): User ID. If None, get from session.
    
    Returns:
        dict: Cookie preferences
    """
    try:
        # Default preferences
        defaults = {
            'essential': True,  # Always required
            'functional': False,
            'analytics': False,
            'marketing': False,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        if user_id:
            # Get from user profile if available
            with app.app_context():
                user = User.query.get(user_id)
                if user and hasattr(user, 'cookie_preferences') and user.cookie_preferences:
                    try:
                        if isinstance(user.cookie_preferences, str):
                            prefs = json.loads(user.cookie_preferences)
                        else:
                            prefs = user.cookie_preferences
                        
                        # Ensure essential cookies are always enabled
                        prefs['essential'] = True
                        return prefs
                    except:
                        return defaults
        
        # Get from session if user_id not provided
        if 'cookie_preferences' in session:
            prefs = session['cookie_preferences']
            # Ensure essential cookies are always enabled
            prefs['essential'] = True
            return prefs
        
        return defaults
    
    except Exception as e:
        logger.error(f"Error getting cookie preferences: {str(e)}")
        return {'essential': True}  # Fallback to essential only

def update_cookie_preferences(preferences, user_id=None):
    """
    Update cookie preferences for a user or in session
    
    Args:
        preferences (dict): Cookie preferences to set
        user_id (int, optional): User ID. If None, set in session.
    
    Returns:
        bool: True if update was successful
    """
    try:
        # Ensure essential cookies are always enabled
        preferences['essential'] = True
        preferences['last_updated'] = datetime.utcnow().isoformat()
        
        if user_id:
            # Update in user profile if available
            with app.app_context():
                user = User.query.get(user_id)
                if user and hasattr(user, 'cookie_preferences'):
                    setattr(user, 'cookie_preferences', json.dumps(preferences))
                    db.session.commit()
        
        # Always update session
        session['cookie_preferences'] = preferences
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating cookie preferences: {str(e)}")
        return False

# ==================================================
# Utilities
# ==================================================

def generate_verification_code(user_id, purpose, expiry_minutes=30):
    """
    Generate a verification code for sensitive operations
    
    Args:
        user_id (int): User ID
        purpose (str): Purpose of the code (e.g., 'deletion', 'export')
        expiry_minutes (int): Minutes until code expires
    
    Returns:
        str: Verification code
    """
    import random
    import string
    import hashlib
    
    # Generate a random code
    code_length = 8
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
    
    # Store code in session with expiry
    session[f'verification_code_{purpose}_{user_id}'] = {
        'code': code,
        'expires': (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()
    }
    
    return code

def verify_code(user_id, purpose, code):
    """
    Verify a verification code
    
    Args:
        user_id (int): User ID
        purpose (str): Purpose of the code
        code (str): Code to verify
    
    Returns:
        bool: True if code is valid
    """
    try:
        session_key = f'verification_code_{purpose}_{user_id}'
        
        if session_key not in session:
            return False
        
        code_data = session[session_key]
        stored_code = code_data.get('code')
        expires = datetime.fromisoformat(code_data.get('expires'))
        
        # Check if code matches and has not expired
        if code == stored_code and datetime.utcnow() < expires:
            # Remove code after successful verification
            session.pop(session_key, None)
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error verifying code: {str(e)}")
        return False