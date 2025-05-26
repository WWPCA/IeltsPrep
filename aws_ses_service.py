"""
AWS SES Email Service for IELTS GenAI Prep Platform

This module provides email functionality using AWS Simple Email Service (SES)
for user verification emails and Nova Sonic assessment feedback emails.
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSEmailService:
    def __init__(self):
        """Initialize AWS SES client with configured credentials."""
        try:
            self.region = os.environ.get('AWS_REGION', 'us-east-1')
            self.ses_client = boto3.client(
                'ses',
                region_name=self.region,
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            
            # Default sender email - using your verified email
            self.sender_email = "info@ieltsaiprep.com"
            
            logger.info(f"AWS SES initialized successfully in region: {self.region}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS SES: {e}")
            raise

    def verify_email_address(self, email_address):
        """
        Verify an email address with AWS SES (required for sending).
        This is needed the first time you use a 'from' email address.
        """
        try:
            response = self.ses_client.verify_email_identity(
                EmailAddress=email_address
            )
            logger.info(f"Verification email sent to: {email_address}")
            return True
        except ClientError as e:
            logger.error(f"Failed to verify email {email_address}: {e}")
            return False

    def send_verification_email(self, to_email, verification_token, username):
        """
        Send email verification email to new users.
        
        Args:
            to_email (str): Recipient email address
            verification_token (str): Unique verification token
            username (str): User's name
        """
        subject = "Verify Your IELTS GenAI Prep Account"
        
        # Create verification URL
        base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        verification_url = f"https://{base_url}/verify-email/{verification_token}"
        
        html_body = f"""
        <html>
        <head></head>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Welcome to IELTS GenAI Prep!</h2>
                
                <p>Hello {username},</p>
                
                <p>Thank you for registering with IELTS GenAI Prep - the world's only platform featuring TrueScore® and Elaris® GenAI assessment technologies!</p>
                
                <p>To activate your account and access our revolutionary AI-powered IELTS assessments, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #2563eb; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Verify My Email Address
                    </a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #2563eb;">{verification_url}</p>
                
                <p>Once verified, you'll be able to:</p>
                <ul>
                    <li>Purchase assessment packages</li>
                    <li>Experience TrueScore® writing assessments</li>
                    <li>Test Elaris® speaking pronunciation analysis</li>
                    <li>Access your personalized learning dashboard</li>
                </ul>
                
                <p>If you didn't create this account, please ignore this email.</p>
                
                <p>Best regards,<br>
                The IELTS GenAI Prep Team</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    This email was sent from an automated system. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to IELTS GenAI Prep!
        
        Hello {username},
        
        Thank you for registering with IELTS GenAI Prep - the world's only platform featuring TrueScore® and Elaris® GenAI assessment technologies!
        
        To activate your account, please verify your email address by visiting:
        {verification_url}
        
        Once verified, you'll have access to our revolutionary AI-powered IELTS assessments.
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The IELTS GenAI Prep Team
        """
        
        return self._send_email(to_email, subject, html_body, text_body)

    def send_assessment_feedback_email(self, to_email, username, assessment_type, 
                                     band_scores, detailed_feedback, assessment_id):
        """
        Send Nova Sonic assessment feedback email to users.
        
        Args:
            to_email (str): Recipient email address
            username (str): User's name
            assessment_type (str): Type of assessment (Academic Speaking, etc.)
            band_scores (dict): IELTS band scores breakdown
            detailed_feedback (str): Detailed assessment feedback
            assessment_id (str): Unique assessment identifier
        """
        subject = f"Your {assessment_type} Assessment Results - IELTS GenAI Prep"
        
        html_body = f"""
        <html>
        <head></head>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Your {assessment_type} Assessment Results</h2>
                
                <p>Hello {username},</p>
                
                <p>Your {assessment_type} assessment has been completed and analyzed using our revolutionary Elaris® GenAI technology. Here are your results:</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1e40af; margin-top: 0;">IELTS Band Scores</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div><strong>Overall Band Score:</strong> {band_scores.get('overall', 'N/A')}</div>
                        <div><strong>Fluency & Coherence:</strong> {band_scores.get('fluency', 'N/A')}</div>
                        <div><strong>Lexical Resource:</strong> {band_scores.get('vocabulary', 'N/A')}</div>
                        <div><strong>Grammatical Range:</strong> {band_scores.get('grammar', 'N/A')}</div>
                        <div><strong>Pronunciation:</strong> {band_scores.get('pronunciation', 'N/A')}</div>
                    </div>
                </div>
                
                <h3 style="color: #1e40af;">Detailed Feedback</h3>
                <div style="background-color: #fefefe; padding: 20px; border-left: 4px solid #2563eb; margin: 20px 0;">
                    {detailed_feedback.replace(chr(10), '<br>')}
                </div>
                
                <div style="background-color: #ecfdf5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #065f46;">
                        <strong>🎯 Next Steps:</strong> Log into your account to access additional practice assessments 
                        and track your progress with our AI-powered learning system.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')}/profile" 
                       style="background-color: #2563eb; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;">
                        View Full Results
                    </a>
                </div>
                
                <p>Assessment ID: {assessment_id}</p>
                <p>Date: {datetime.now().strftime('%B %d, %Y')}</p>
                
                <p>Thank you for using IELTS GenAI Prep!</p>
                
                <p>Best regards,<br>
                The IELTS GenAI Prep Team</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    This assessment was powered by Elaris® GenAI technology - the world's only AI assessor for IELTS speaking evaluation.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Your {assessment_type} Assessment Results
        
        Hello {username},
        
        Your assessment has been completed using Elaris® GenAI technology.
        
        IELTS Band Scores:
        - Overall: {band_scores.get('overall', 'N/A')}
        - Fluency & Coherence: {band_scores.get('fluency', 'N/A')}
        - Lexical Resource: {band_scores.get('vocabulary', 'N/A')}
        - Grammatical Range: {band_scores.get('grammar', 'N/A')}
        - Pronunciation: {band_scores.get('pronunciation', 'N/A')}
        
        Detailed Feedback:
        {detailed_feedback}
        
        Assessment ID: {assessment_id}
        Date: {datetime.now().strftime('%B %d, %Y')}
        
        Log into your account to view full results and access more assessments.
        
        Thank you for using IELTS GenAI Prep!
        """
        
        return self._send_email(to_email, subject, html_body, text_body)

    def _send_email(self, to_email, subject, html_body, text_body):
        """
        Internal method to send email via AWS SES.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_body (str): HTML email content
            text_body (str): Plain text email content
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [to_email]
                },
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
            
            if error_code == 'MessageRejected':
                logger.error(f"Email rejected: {error_message}")
            elif error_code == 'MailFromDomainNotVerified':
                logger.error(f"Sender email not verified: {self.sender_email}")
            else:
                logger.error(f"Failed to send email: {error_code} - {error_message}")
            
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False

    def check_ses_status(self):
        """Check AWS SES service status and configuration."""
        try:
            # Check sending quota
            quota_response = self.ses_client.get_send_quota()
            
            # Check verified email addresses
            verified_response = self.ses_client.list_verified_email_addresses()
            
            status = {
                'service_available': True,
                'region': self.region,
                'daily_quota': quota_response.get('Max24HourSend', 0),
                'quota_used': quota_response.get('SentLast24Hours', 0),
                'sending_rate': quota_response.get('MaxSendRate', 0),
                'verified_emails': verified_response.get('VerifiedEmailAddresses', [])
            }
            
            logger.info(f"AWS SES Status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Failed to check SES status: {e}")
            return {'service_available': False, 'error': str(e)}

# Initialize the email service
email_service = AWSEmailService()