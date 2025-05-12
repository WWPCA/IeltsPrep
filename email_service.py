"""
Email Service Module
This module provides functionality for sending emails, including verification emails.
"""

import os
import logging
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import url_for
from tenacity import retry, stop_after_attempt, wait_fixed

from app import db
from models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'worldwidepublishingco@gmail.com')
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'worldwidepublishingco@gmail.com')

def generate_verification_token():
    """
    Generate a secure token for email verification.
    
    Returns:
        str: A secure random token
    """
    return secrets.token_urlsafe(64)

def send_email(recipient, subject, text_body, html_body=None):
    """
    Send an email to a recipient.
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str, optional): HTML email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD]):
        logger.error("Email configuration is incomplete. Cannot send email.")
        return False
        
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = SENDER_EMAIL
        message['To'] = recipient
        
        # Attach text part
        message.attach(MIMEText(text_body, 'plain'))
        
        # Attach HTML part if provided
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
            
        logger.info(f"Email sent to {recipient}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def send_verification_email(user):
    """
    Send an email verification link to a user.
    
    Args:
        user (User): The user to send the verification email to
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Generate a verification token
    token = generate_verification_token()
    
    # Update user with verification token
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.utcnow()
    db.session.commit()
    
    # Verification link
    verification_url = url_for('verify_email', token=token, _external=True)
    
    # Email subject
    subject = "IELTS GenAI Prep - Verify Your Email Address"
    
    # Plain text email
    text_body = f"""
Hello {user.username},

Thank you for registering with IELTS GenAI Prep!

To complete your registration and access your account, please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email or use our Contact Us form on the website if you have any questions.

Best regards,
The IELTS GenAI Prep Team
    """
    
    # HTML email
    html_body = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #3F51B5;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            padding: 20px;
            background-color: #f9f9f9;
            border-left: 1px solid #dddddd;
            border-right: 1px solid #dddddd;
            border-bottom: 1px solid #dddddd;
            border-radius: 0 0 5px 5px;
        }}
        .button {{
            display: inline-block;
            background-color: #3F51B5;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 3px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 20px;
            text-align: center;
            color: #888888;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Verification</h1>
        </div>
        <div class="content">
            <p>Hello {user.username},</p>
            
            <p>Thank you for registering with IELTS GenAI Prep!</p>
            
            <p>To complete your registration and access your account, please verify your email address by clicking the button below:</p>
            
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            
            <p>This link will expire in 24 hours.</p>
            
            <p>If you don't see the button above, you can also click on this link: <a href="{verification_url}">{verification_url}</a></p>
            
            <p>If you didn't create this account, please ignore this email or use our Contact Us form on the website if you have any questions.</p>
            
            <p>Best regards,<br>The IELTS GenAI Prep Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Send the email
    return send_email(user.email, subject, text_body, html_body)