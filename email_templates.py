"""
Professional Email Templates for IELTS AI Prep
This module provides HTML and text templates for all automated emails.
"""

def get_email_template_base():
    """Base HTML template with IELTS AI Prep branding"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS AI Prep</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .email-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 16px;
        }
        .content {
            padding: 40px;
        }
        .content h2 {
            color: #007bff;
            margin-top: 0;
            font-size: 24px;
        }
        .button {
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 500;
            margin: 20px 0;
            text-align: center;
        }
        .button:hover {
            background-color: #0056b3;
        }
        .security-note {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .footer {
            background-color: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }
        .footer a {
            color: #007bff;
            text-decoration: none;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .content, .header, .footer { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>IELTS AI Prep</h1>
            <p>Your AI-Powered IELTS Preparation Platform</p>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p>© 2025 IELTS AI Prep. All rights reserved.</p>
            <p>
                <a href="https://ieltsaiprep.com/terms">Terms of Service</a> | 
                <a href="https://ieltsaiprep.com/privacy">Privacy Policy</a> | 
                <a href="https://ieltsaiprep.com/contact">Contact Support</a>
            </p>
            <p style="margin-top: 20px; font-size: 12px;">
                This email was sent to you because you have an account with IELTS AI Prep.<br>
                If you did not request this email, please contact our support team.
            </p>
        </div>
    </div>
</body>
</html>
    """

def get_password_reset_email_template(reset_url, user_email):
    """Password reset email template"""
    content = f"""
        <h2>Password Reset Request</h2>
        <p>Hello,</p>
        <p>We received a request to reset the password for your IELTS AI Prep account associated with <strong>{user_email}</strong>.</p>
        
        <p>Click the button below to reset your password:</p>
        <p style="text-align: center;">
            <a href="{reset_url}" class="button">Reset My Password</a>
        </p>
        
        <div class="security-note">
            <strong>Security Notice:</strong> This link will expire in 1 hour for your security. If you didn't request this reset, please ignore this email - your password will remain unchanged.
        </div>
        
        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace;">
            {reset_url}
        </p>
        
        <p>Best regards,<br>The IELTS AI Prep Team</p>
    """
    
    html_template = get_email_template_base().format(content=content)
    
    text_template = f"""
IELTS AI Prep - Password Reset Request

Hello,

We received a request to reset the password for your IELTS AI Prep account associated with {user_email}.

To reset your password, please visit the following link:
{reset_url}

SECURITY NOTICE: This link will expire in 1 hour for your security. If you didn't request this reset, please ignore this email - your password will remain unchanged.

Best regards,
The IELTS AI Prep Team

© 2025 IELTS AI Prep. All rights reserved.
    """
    
    return html_template, text_template

def get_email_verification_template(verification_url, user_email):
    """Email verification template"""
    content = f"""
        <h2>Verify Your Email Address</h2>
        <p>Hello,</p>
        <p>Welcome to IELTS AI Prep! Please verify your email address <strong>{user_email}</strong> to complete your account setup.</p>
        
        <p>Click the button below to verify your email:</p>
        <p style="text-align: center;">
            <a href="{verification_url}" class="button">Verify My Email</a>
        </p>
        
        <div class="security-note">
            <strong>Important:</strong> You'll need to verify your email before you can access assessments and make purchases.
        </div>
        
        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace;">
            {verification_url}
        </p>
        
        <p>Best regards,<br>The IELTS AI Prep Team</p>
    """
    
    html_template = get_email_template_base().format(content=content)
    
    text_template = f"""
IELTS AI Prep - Verify Your Email Address

Hello,

Welcome to IELTS AI Prep! Please verify your email address {user_email} to complete your account setup.

To verify your email, please visit the following link:
{verification_url}

IMPORTANT: You'll need to verify your email before you can access assessments and make purchases.

Best regards,
The IELTS AI Prep Team

© 2025 IELTS AI Prep. All rights reserved.
    """
    
    return html_template, text_template

def get_payment_confirmation_template(user_email, package_details, payment_amount):
    """Payment confirmation email template"""
    content = f"""
        <h2>Payment Confirmation</h2>
        <p>Hello,</p>
        <p>Thank you for your purchase! Your payment has been successfully processed.</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #155724;">Order Details</h3>
            <p><strong>Package:</strong> {package_details}</p>
            <p><strong>Amount Paid:</strong> ${payment_amount}</p>
            <p><strong>Account:</strong> {user_email}</p>
        </div>
        
        <p>Your assessments are now available in your dashboard. Start practicing with our AI-powered TrueScore® writing assessments and Elaris® speaking assessments!</p>
        
        <p style="text-align: center;">
            <a href="https://ieltsaiprep.com/dashboard" class="button">Access My Assessments</a>
        </p>
        
        <p>Best regards,<br>The IELTS AI Prep Team</p>
    """
    
    html_template = get_email_template_base().format(content=content)
    
    text_template = f"""
IELTS AI Prep - Payment Confirmation

Hello,

Thank you for your purchase! Your payment has been successfully processed.

ORDER DETAILS:
Package: {package_details}
Amount Paid: ${payment_amount}
Account: {user_email}

Your assessments are now available in your dashboard. Start practicing with our AI-powered TrueScore® writing assessments and Elaris® speaking assessments!

Visit: https://ieltsaiprep.com/dashboard

Best regards,
The IELTS AI Prep Team

© 2025 IELTS AI Prep. All rights reserved.
    """
    
    return html_template, text_template

def get_assessment_completion_template(user_email, assessment_type, score_details):
    """Assessment completion email template"""
    content = f"""
        <h2>Assessment Complete - Results Available</h2>
        <p>Hello,</p>
        <p>Great job completing your {assessment_type} assessment! Your detailed feedback is now ready for review.</p>
        
        <div style="background-color: #e3f2fd; border: 1px solid #bbdefb; border-radius: 4px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #0d47a1;">Assessment Summary</h3>
            <p><strong>Type:</strong> {assessment_type}</p>
            <p><strong>Results:</strong> {score_details}</p>
        </div>
        
        <p>Your detailed feedback includes band scores, improvement suggestions, and personalized recommendations based on official IELTS criteria.</p>
        
        <p style="text-align: center;">
            <a href="https://ieltsaiprep.com/dashboard" class="button">View Full Results</a>
        </p>
        
        <p>Keep practicing to improve your scores. Your next assessments are waiting in your dashboard!</p>
        
        <p>Best regards,<br>The IELTS AI Prep Team</p>
    """
    
    html_template = get_email_template_base().format(content=content)
    
    text_template = f"""
IELTS AI Prep - Assessment Complete

Hello,

Great job completing your {assessment_type} assessment! Your detailed feedback is now ready for review.

ASSESSMENT SUMMARY:
Type: {assessment_type}
Results: {score_details}

Your detailed feedback includes band scores, improvement suggestions, and personalized recommendations based on official IELTS criteria.

View your full results: https://ieltsaiprep.com/dashboard

Keep practicing to improve your scores. Your next assessments are waiting in your dashboard!

Best regards,
The IELTS AI Prep Team

© 2025 IELTS AI Prep. All rights reserved.
    """
    
    return html_template, text_template

def get_account_deletion_template(user_email):
    """Account deletion confirmation email template"""
    content = f"""
        <h2>Account Deletion Confirmation</h2>
        <p>Hello,</p>
        <p>This confirms that your IELTS AI Prep account associated with <strong>{user_email}</strong> has been permanently deleted as requested.</p>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #856404;">What's Been Deleted</h3>
            <ul>
                <li>Your account and profile information</li>
                <li>All assessment results and feedback</li>
                <li>Payment history and subscription data</li>
                <li>All personal data per GDPR requirements</li>
            </ul>
        </div>
        
        <p>If you ever decide to return to IELTS preparation, you're always welcome to create a new account with us.</p>
        
        <p>Thank you for using IELTS AI Prep. We wish you the best in your future endeavors!</p>
        
        <p>Best regards,<br>The IELTS AI Prep Team</p>
    """
    
    html_template = get_email_template_base().format(content=content)
    
    text_template = f"""
IELTS AI Prep - Account Deletion Confirmation

Hello,

This confirms that your IELTS AI Prep account associated with {user_email} has been permanently deleted as requested.

WHAT'S BEEN DELETED:
- Your account and profile information
- All assessment results and feedback  
- Payment history and subscription data
- All personal data per GDPR requirements

If you ever decide to return to IELTS preparation, you're always welcome to create a new account with us.

Thank you for using IELTS AI Prep. We wish you the best in your future endeavors!

Best regards,
The IELTS AI Prep Team

© 2025 IELTS AI Prep. All rights reserved.
    """
    
    return html_template, text_template