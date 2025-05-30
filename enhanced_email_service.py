"""
Enhanced Email Service with Professional Templates
This module provides AWS SES integration with professional HTML email templates.
"""

import os
import logging
from botocore.exceptions import ClientError
import boto3
from email_templates import (
    get_password_reset_email_template,
    get_email_verification_template, 
    get_payment_confirmation_template,
    get_assessment_completion_template,
    get_account_deletion_template,
    get_contact_form_notification_template,
    get_contact_auto_reply_template
)

# Configure logging
logger = logging.getLogger(__name__)

class ProfessionalEmailService:
    """Professional email service using AWS SES with branded templates"""
    
    def __init__(self):
        self.sender_email = "info@ieltsaiprep.com"
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        try:
            self.ses_client = boto3.client(
                'ses',
                region_name=self.aws_region,
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            logger.info("AWS SES client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS SES client: {e}")
            self.ses_client = None
    
    def _send_email(self, to_email, subject, html_body, text_body):
        """Send email via AWS SES with both HTML and text versions"""
        if not self.ses_client:
            logger.error("SES client not available")
            return False
            
        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        },
                        'Text': {
                            'Data': text_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            message_id = response['MessageId']
            logger.info(f"Email sent successfully to {to_email}. Message ID: {message_id}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to send email to {to_email}: {error_code} - {error_message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False
    
    def send_password_reset_email(self, user_email, reset_url):
        """Send password reset email with professional template"""
        html_body, text_body = get_password_reset_email_template(reset_url, user_email)
        subject = "Reset Your IELTS AI Prep Password"
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def send_email_verification(self, user_email, verification_url):
        """Send email verification with professional template"""
        html_body, text_body = get_email_verification_template(verification_url, user_email)
        subject = "Verify Your IELTS AI Prep Email Address"
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def send_payment_confirmation(self, user_email, package_details, payment_amount):
        """Send payment confirmation with professional template"""
        html_body, text_body = get_payment_confirmation_template(user_email, package_details, payment_amount)
        subject = "Payment Confirmation - IELTS AI Prep"
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def send_assessment_completion(self, user_email, assessment_type, score_details):
        """Send assessment completion notification with professional template"""
        html_body, text_body = get_assessment_completion_template(user_email, assessment_type, score_details)
        subject = f"Assessment Complete - {assessment_type} Results Available"
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def send_account_deletion_confirmation(self, user_email):
        """Send account deletion confirmation with professional template"""
        html_body, text_body = get_account_deletion_template(user_email)
        subject = "Account Deletion Confirmation - IELTS AI Prep"
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def send_contact_form_notification(self, admin_email, name, user_email, message):
        """Send contact form notification to admin with professional template"""
        html_body, text_body = get_contact_form_notification_template(name, user_email, message)
        subject = f"New Contact Form Submission from {name}"
        
        return self._send_email(admin_email, subject, html_body, text_body)
    
    def send_contact_auto_reply(self, user_email, name):
        """Send auto-reply to user who submitted contact form"""
        html_body, text_body = get_contact_auto_reply_template(name)
        subject = "Thank You for Contacting IELTS AI Prep"
        
        return self._send_email(user_email, subject, html_body, text_body)

# Create global instance
professional_email_service = ProfessionalEmailService()

# Convenience functions for easy integration
def send_password_reset_email(user_email, reset_url):
    """Send password reset email"""
    return professional_email_service.send_password_reset_email(user_email, reset_url)

def send_email_verification(user_email, verification_url):
    """Send email verification"""
    return professional_email_service.send_email_verification(user_email, verification_url)

def send_payment_confirmation(user_email, package_details, payment_amount):
    """Send payment confirmation"""
    return professional_email_service.send_payment_confirmation(user_email, package_details, payment_amount)

def send_assessment_completion(user_email, assessment_type, score_details):
    """Send assessment completion notification"""
    return professional_email_service.send_assessment_completion(user_email, assessment_type, score_details)

def send_account_deletion_confirmation(user_email):
    """Send account deletion confirmation"""
    return professional_email_service.send_account_deletion_confirmation(user_email)

def send_contact_form_notification(admin_email, name, user_email, message):
    """Send contact form notification to admin"""
    return professional_email_service.send_contact_form_notification(admin_email, name, user_email, message)

def send_contact_auto_reply(user_email, name):
    """Send auto-reply to contact form submitter"""
    return professional_email_service.send_contact_auto_reply(user_email, name)

def send_gdpr_notification(user_email, notification_type, details=None):
    """Send GDPR-related notifications to users"""
    try:
        if notification_type == 'data_export':
            subject = "Your Data Export Request - IELTS GenAI Prep"
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>IELTS GenAI Prep</h1>
                    <p>Data Export Request</p>
                </div>
                <div class="content">
                    <h2>Your Data Export is Ready</h2>
                    <p>Your personal data export has been prepared as requested under GDPR Article 20.</p>
                    <p>The export includes all data associated with your account that you have the right to receive.</p>
                    <p>If you have any questions about your data export, please contact our support team.</p>
                </div>
                <div class="footer">
                    <p>IELTS GenAI Prep - Professional IELTS Test Preparation</p>
                    <p>This email was sent in response to your data export request.</p>
                </div>
            </body>
            </html>
            """
            text_body = "Your data export request has been completed. Please contact support if you have questions."
            
        elif notification_type == 'data_deletion':
            subject = "Account Deletion Confirmation - IELTS GenAI Prep"
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>IELTS GenAI Prep</h1>
                    <p>Account Deletion Confirmation</p>
                </div>
                <div class="content">
                    <h2>Your Account Has Been Deleted</h2>
                    <p>Your account and all associated personal data have been permanently deleted as requested.</p>
                    <p>This action cannot be undone. If you wish to use our services again, you will need to create a new account.</p>
                    <p>Thank you for using IELTS GenAI Prep.</p>
                </div>
                <div class="footer">
                    <p>IELTS GenAI Prep - Professional IELTS Test Preparation</p>
                </div>
            </body>
            </html>
            """
            text_body = "Your account and all associated data have been permanently deleted as requested."
            
        else:
            logger.error(f"Unknown GDPR notification type: {notification_type}")
            return False
            
        return professional_email_service._send_email(user_email, subject, html_body, text_body)
        
    except Exception as e:
        logger.error(f"Failed to send GDPR notification: {e}")
        return False