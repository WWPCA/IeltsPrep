"""
AWS SES Email Service - Handles all email sending functionality
"""

import json
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

# Environment detection
try:
    from environment_utils import is_development
    IS_DEVELOPMENT = is_development()
except ImportError:
    IS_DEVELOPMENT = True

# AWS SES client
try:
    if not IS_DEVELOPMENT:
        import boto3
        region = os.environ.get('AWS_REGION', 'us-east-1')
        ses_client = boto3.client('ses', region_name=region)
        SES_AVAILABLE = True
        logger.info(f"[PRODUCTION] AWS SES client initialized - region: {region}")
    else:
        from aws_mock_config import aws_mock
        ses_client = aws_mock
        SES_AVAILABLE = False
        logger.info("[DEVELOPMENT] Using mock SES service")
        
except Exception as e:
    logger.warning(f"SES initialization error: {e}")
    ses_client = None
    SES_AVAILABLE = False

# Email configuration
FROM_EMAIL_NOREPLY = 'donotreply@ieltsaiprep.com'
FROM_EMAIL_WELCOME = 'welcome@ieltsaiprep.com'
WEBSITE_URL = 'https://ieltsgenaiprep.com'

class EmailService:
    """AWS SES email service with templates"""
    
    @staticmethod
    def send_password_reset_email(email: str, reset_token: str) -> bool:
        """Send password reset email with secure link"""
        try:
            if not ses_client:
                logger.error("SES client not available")
                return False
            
            # Generate secure reset URL
            reset_url = f"{WEBSITE_URL}/reset_password?token={reset_token}"
            
            subject = "Reset Your Password - IELTS GenAI Prep"
            
            # HTML email template
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Reset Your Password - IELTS GenAI Prep</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        background-color: #f8f9fa;
                        margin: 0;
                        padding: 0;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .header .subtitle {{
                        margin: 10px 0 0 0;
                        font-size: 16px;
                        opacity: 0.9;
                    }}
                    .content {{
                        padding: 40px;
                    }}
                    .security-notice {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 24px 0;
                        border-left: 4px solid #f39c12;
                    }}
                    .security-notice strong {{
                        color: #8b6914;
                    }}
                    .reset-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #e74c3c, #c0392b);
                        color: white !important;
                        text-decoration: none;
                        padding: 16px 32px;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 16px;
                        text-align: center;
                        margin: 24px 0;
                        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
                        transition: all 0.3s ease;
                    }}
                    .reset-button:hover {{
                        background: linear-gradient(135deg, #c0392b, #a93226);
                        transform: translateY(-1px);
                        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
                    }}
                    .alternative-link {{
                        background: #f8f9fa;
                        border: 1px solid #e9ecef;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 24px 0;
                        word-break: break-all;
                        font-family: 'Courier New', monospace;
                        font-size: 14px;
                    }}
                    .footer {{
                        background: #2c3e50;
                        color: #bdc3c7;
                        padding: 30px;
                        text-align: center;
                        font-size: 14px;
                    }}
                    .footer a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                    .support-info {{
                        background: #e8f5e8;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 24px 0;
                    }}
                    .expiry-notice {{
                        color: #e74c3c;
                        font-weight: 600;
                        font-size: 14px;
                        margin: 16px 0;
                    }}
                    @media (max-width: 600px) {{
                        .content, .header, .footer {{
                            padding: 20px;
                        }}
                        .reset-button {{
                            padding: 14px 24px;
                            font-size: 15px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <!-- Header -->
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                        <div class="subtitle">IELTS GenAI Prep - Secure Account Access</div>
                    </div>
                    
                    <!-- Content -->
                    <div class="content">
                        <h2 style="color: #2c3e50; margin-bottom: 20px;">Hello,</h2>
                        
                        <p style="font-size: 16px; margin-bottom: 24px;">
                            We received a request to reset the password for your IELTS GenAI Prep account. 
                            If you made this request, click the button below to set a new password.
                        </p>
                        
                        <!-- Security Notice -->
                        <div class="security-notice">
                            <strong>🛡️ Security Notice:</strong> This link will expire in 1 hour for your security. 
                            If you didn't request this password reset, please ignore this email - your account remains secure.
                        </div>
                        
                        <!-- Reset Button -->
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="{reset_url}" class="reset-button">
                                🔑 Reset My Password
                            </a>
                        </div>
                        
                        <div class="expiry-notice">
                            ⏰ This secure link expires in 1 hour (60 minutes)
                        </div>
                        
                        <!-- Alternative Link -->
                        <p style="margin-top: 32px; font-size: 14px; color: #666;">
                            If the button doesn't work, copy and paste this link into your browser:
                        </p>
                        <div class="alternative-link">
                            {reset_url}
                        </div>
                        
                        <!-- Support Information -->
                        <div class="support-info">
                            <strong>📞 Need Help?</strong><br>
                            If you're having trouble resetting your password or didn't request this reset, 
                            please contact our support team immediately for assistance.
                        </div>
                        
                        <p style="margin-top: 32px; font-size: 16px; color: #2c3e50;">
                            Best regards,<br>
                            <strong>The IELTS GenAI Prep Team</strong><br>
                            <em>Featuring TrueScore® & ClearScore® AI Assessment</em>
                        </p>
                    </div>
                    
                    <!-- Footer -->
                    <div class="footer">
                        <p style="margin-bottom: 16px;">
                            <strong>IELTS GenAI Prep</strong> - AI-Powered IELTS Assessment Platform
                        </p>
                        
                        <p style="margin: 8px 0;">
                            Visit us at <a href="{WEBSITE_URL}">{WEBSITE_URL.replace('https://', '')}</a>
                        </p>
                        
                        <p style="margin: 16px 0 0 0; font-size: 12px; opacity: 0.8;">
                            © 2025 IELTS GenAI Prep. All rights reserved.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            text_body = f"""
IELTS GenAI Prep - Password Reset Request

Hello,

We received a request to reset the password for your IELTS GenAI Prep account.

To reset your password, please visit this secure link:
{reset_url}

IMPORTANT: This link will expire in 1 hour (60 minutes) for your security.

If you didn't request this password reset, please ignore this email - your account remains secure.

Need help? Contact our support team if you have any questions.

Best regards,
The IELTS GenAI Prep Team
Featuring TrueScore® & ClearScore® AI Assessment

Visit us at: {WEBSITE_URL.replace('https://', '')}

© 2025 IELTS GenAI Prep. All rights reserved.
            """
            
            if SES_AVAILABLE:
                # Send using AWS SES
                response = ses_client.send_email(
                    Source=FROM_EMAIL_NOREPLY,
                    Destination={
                        'ToAddresses': [email]
                    },
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {
                            'Html': {'Data': html_body},
                            'Text': {'Data': text_body}
                        }
                    }
                )
                
                message_id = response.get('MessageId')
                logger.info(f"Password reset email sent successfully to {email} - MessageId: {message_id}")
                return True
            else:
                # Development mode - log the email content
                logger.info(f"[DEVELOPMENT] Password reset email for {email}")
                logger.info(f"Reset URL: {reset_url}")
                logger.info("Email would be sent via AWS SES in production")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
    
    @staticmethod
    def send_password_changed_notification(email: str) -> bool:
        """Send notification email when password is successfully changed"""
        try:
            if not ses_client:
                logger.error("SES client not available")
                return False
            
            subject = "Password Changed Successfully - IELTS GenAI Prep"
            
            # HTML email template
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Changed - IELTS GenAI Prep</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        background-color: #f8f9fa;
                        margin: 0;
                        padding: 0;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 40px;
                    }}
                    .footer {{
                        background: #2c3e50;
                        color: #bdc3c7;
                        padding: 30px;
                        text-align: center;
                        font-size: 14px;
                    }}
                    .security-notice {{
                        background: #d1ecf1;
                        border: 1px solid #bee5eb;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 24px 0;
                        border-left: 4px solid #17a2b8;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>✅ Password Changed Successfully</h1>
                        <div class="subtitle">IELTS GenAI Prep - Account Security</div>
                    </div>
                    
                    <div class="content">
                        <h2 style="color: #2c3e50; margin-bottom: 20px;">Password Updated!</h2>
                        
                        <p style="font-size: 16px; margin-bottom: 24px;">
                            Your IELTS GenAI Prep account password has been successfully changed. 
                            You can now use your new password to access your account.
                        </p>
                        
                        <div class="security-notice">
                            <strong>🛡️ Security Notice:</strong> If you didn't make this change, 
                            please contact our support team immediately to secure your account.
                        </div>
                        
                        <p style="margin-top: 32px; font-size: 16px; color: #2c3e50;">
                            Best regards,<br>
                            <strong>The IELTS GenAI Prep Team</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p style="margin-bottom: 16px;">
                            <strong>IELTS GenAI Prep</strong> - AI-Powered IELTS Assessment Platform
                        </p>
                        <p style="margin: 16px 0 0 0; font-size: 12px; opacity: 0.8;">
                            © 2025 IELTS GenAI Prep. All rights reserved.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
IELTS GenAI Prep - Password Changed Successfully

Your account password has been successfully changed.

If you didn't make this change, please contact our support team immediately.

Best regards,
The IELTS GenAI Prep Team

© 2025 IELTS GenAI Prep. All rights reserved.
            """
            
            if SES_AVAILABLE:
                response = ses_client.send_email(
                    Source=FROM_EMAIL_NOREPLY,
                    Destination={
                        'ToAddresses': [email]
                    },
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {
                            'Html': {'Data': html_body},
                            'Text': {'Data': text_body}
                        }
                    }
                )
                
                message_id = response.get('MessageId')
                logger.info(f"Password changed notification sent to {email} - MessageId: {message_id}")
                return True
            else:
                # Development mode
                logger.info(f"[DEVELOPMENT] Password changed notification for {email}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send password changed notification to {email}: {e}")
            return False

# Global instance
email_service = EmailService()

# Export
__all__ = ['EmailService', 'email_service']