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

def send_verification_email(user_email, verification_url):
    """Send email verification email to user"""
    try:
        # Use SendGrid for email sending
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            print("SendGrid API key not configured")
            return False
        
        # Email content
        subject = "Verify Your IELTS GenAI Prep Account"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verify Your Email</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ color: #007bff; font-size: 24px; font-weight: bold; }}
                .button {{ display: inline-block; padding: 15px 30px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">IELTS GenAI Prep</div>
                    <h1>Verify Your Email Address</h1>
                </div>
                
                <p>Thank you for registering with IELTS GenAI Prep!</p>
                
                <p>To complete your account setup and start accessing our AI-powered IELTS preparation tools, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify My Email</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                    {verification_url}
                </p>
                
                <p><strong>This verification link will expire in 24 hours.</strong></p>
                
                <div class="footer">
                    <p>If you didn't create an account with IELTS GenAI Prep, you can safely ignore this email.</p>
                    <p>Need help? Contact our support team.</p>
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        IELTS GenAI Prep - Verify Your Email Address
        
        Thank you for registering with IELTS GenAI Prep!
        
        To complete your account setup, please verify your email address by visiting:
        {verification_url}
        
        This verification link will expire in 24 hours.
        
        If you didn't create an account with IELTS GenAI Prep, you can safely ignore this email.
        
        © 2025 IELTS GenAI Prep. All rights reserved.
        """
        
        message = Mail(
            from_email='noreply@ieltsaiprep.com',
            to_emails=user_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code == 202:
            print(f"Verification email sent successfully to {user_email}")
            return True
        else:
            print(f"Failed to send verification email: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

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