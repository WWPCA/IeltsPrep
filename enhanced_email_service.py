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
    get_account_deletion_template
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