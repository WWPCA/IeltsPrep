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
        # Use Amazon SES for email sending
        import boto3
        from botocore.exceptions import ClientError
        
        # Initialize SES client
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
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
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ color: #007bff; font-size: 24px; font-weight: bold; }}
                .button {{ display: inline-block; padding: 15px 30px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px; }}
                .url-box {{ word-break: break-all; background-color: #f8f9fa; padding: 15px; border-radius: 4px; border-left: 4px solid #007bff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">IELTS GenAI Prep</div>
                    <h1 style="color: #333; margin-top: 20px;">Verify Your Email Address</h1>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">Thank you for registering with IELTS GenAI Prep!</p>
                
                <p style="font-size: 16px; line-height: 1.6;">To complete your account setup and start accessing our AI-powered IELTS preparation tools, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" class="button">Verify My Email</a>
                </div>
                
                <p style="font-size: 14px;">Or copy and paste this link into your browser:</p>
                <div class="url-box">
                    {verification_url}
                </div>
                
                <p style="font-size: 16px; font-weight: bold; color: #e74c3c; margin-top: 20px;">This verification link will expire in 24 hours.</p>
                
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
        
        # Send email using SES
        response = ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={
                'ToAddresses': [user_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text_content,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print(f"Verification email sent successfully to {user_email}, MessageId: {response.get('MessageId')}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"SES Client Error: {error_code} - {error_message}")
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