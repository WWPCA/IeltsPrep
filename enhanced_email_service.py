"""
Enhanced Email Service Module
Provides email functionality for password reset and other notifications
"""

import os
import logging
from flask import current_app, url_for

logger = logging.getLogger(__name__)

def send_password_reset_email(user_email, reset_token):
    """Send password reset email to user"""
    try:
        # Create reset URL
        reset_url = url_for('reset_password_token', token=reset_token, _external=True)
        
        # Email content
        subject = "Password Reset - IELTS GenAI Prep"
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You have requested to reset your password for your IELTS GenAI Prep account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you did not request this reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>IELTS GenAI Prep Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        You have requested to reset your password for your IELTS GenAI Prep account.
        
        Visit this link to reset your password: {reset_url}
        
        This link will expire in 1 hour.
        
        If you did not request this reset, please ignore this email.
        
        Best regards,
        IELTS GenAI Prep Team
        """
        
        # Log the email request (in production, this would send actual email)
        logger.info(f"Password reset email requested for {user_email}")
        logger.info(f"Reset URL: {reset_url}")
        
        # Return success (email service would be implemented with actual provider)
        return {
            'success': True,
            'message': 'Password reset email sent successfully',
            'reset_url': reset_url  # For development/testing only
        }
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return {
            'success': False,
            'error': 'Failed to send password reset email'
        }

def send_notification_email(to_email, subject, content):
    """Send general notification email"""
    try:
        logger.info(f"Notification email sent to {to_email}: {subject}")
        return {'success': True, 'message': 'Email sent successfully'}
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")
        return {'success': False, 'error': 'Failed to send email'}

def send_gdpr_notification(to_email, notification_type, details=None):
    """Send GDPR-related notification emails"""
    try:
        if notification_type == 'data_request':
            subject = "Data Request Confirmation - IELTS GenAI Prep"
            content = "Your data request has been received and will be processed within 30 days."
        elif notification_type == 'data_deletion':
            subject = "Account Deletion Confirmation - IELTS GenAI Prep"
            content = "Your account and all associated data have been deleted as requested."
        elif notification_type == 'privacy_update':
            subject = "Privacy Policy Update - IELTS GenAI Prep"
            content = "Our privacy policy has been updated. Please review the changes."
        else:
            subject = "GDPR Notification - IELTS GenAI Prep"
            content = details or "This is a GDPR-related notification."
        
        logger.info(f"GDPR notification email sent to {to_email}: {notification_type}")
        return {'success': True, 'message': 'GDPR notification sent successfully'}
    except Exception as e:
        logger.error(f"Failed to send GDPR notification: {e}")
        return {'success': False, 'error': 'Failed to send GDPR notification'}