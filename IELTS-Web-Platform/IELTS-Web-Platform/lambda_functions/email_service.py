import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize AWS SES
ses_client = boto3.client('ses', region_name='us-east-1')

# Email configuration
SENDER_EMAIL = 'donotreply@ieltsaiprep.com'
REPLY_TO_EMAIL = 'support@ieltsaiprep.com'

def send_welcome_email(recipient_email, user_name=None):
    """
    Send welcome email to newly registered users
    """
    subject = "🎉 Welcome to IELTS AI Prep - Your Journey to Success Starts Now!"
    
    # HTML email body
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .highlight { background: #e8f4fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }
            .checklist { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .check-item { margin: 10px 0; }
            .footer { text-align: center; margin-top: 30px; color: #666; }
            .cta-button { background: #2196F3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 Welcome to IELTS AI Prep!</h1>
            <p>Your Journey to Success Starts Now!</p>
        </div>
        
        <div class="content">
            <p>Congratulations and welcome to the IELTS AI Prep family! 🌟</p>
            
            <p>We're thrilled to confirm that your registration has been successfully completed, and you now have full cross-platform access to your AI assessment tools. Whether you're on your computer, tablet, or mobile device, your personalized IELTS preparation is now at your fingertips wherever you go.</p>
            
            <div class="highlight">
                <h3>What's Next?</h3>
                <div class="checklist">
                    <div class="check-item">✅ <strong>Cross-Platform Access:</strong> Log in from any device using your credentials</div>
                    <div class="check-item">✅ <strong>AI-Powered Assessments:</strong> Get instant, detailed feedback on your practice tests</div>
                    <div class="check-item">✅ <strong>Personalized Learning:</strong> Track your progress and focus on areas that need improvement</div>
                    <div class="check-item">✅ <strong>24/7 Availability:</strong> Study at your own pace, whenever and wherever suits you best</div>
                </div>
            </div>
            
            <p>Your dedication to improving your English proficiency is truly commendable, and we're honored to be part of your IELTS journey. Our advanced AI technology is designed to provide you with the most accurate, helpful feedback to boost your confidence and skills.</p>
            
            <p>Remember, every great achievement starts with a single step, and you've just taken yours! We believe in your potential and are here to support you every step of the way toward achieving your target IELTS score.</p>
            
            <div class="highlight">
                <h3>Ready to Get Started?</h3>
                <p>Simply log in to your account at <strong>www.ieltsaiprep.com</strong> and begin exploring your personalized dashboard. If you have any questions or need assistance, our support team is always here to help.</p>
                <a href="https://www.ieltsaiprep.com" class="cta-button">Start Your Journey</a>
            </div>
            
            <p>Wishing you tremendous success in your IELTS preparation and beyond. We can't wait to celebrate your achievements with you!</p>
            
            <p><strong>Best of luck on your exciting journey ahead! 🚀</strong></p>
            
            <div class="footer">
                <p>Warm regards,<br><strong>The IELTS AI Prep Team</strong></p>
                <hr>
                <p><small>This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this email.</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    text_body = """
Congratulations and welcome to the IELTS AI Prep family! 🌟

We're thrilled to confirm that your registration has been successfully completed, and you now have full cross-platform access to your AI assessment tools. Whether you're on your computer, tablet, or mobile device, your personalized IELTS preparation is now at your fingertips wherever you go.

What's Next?
✅ Cross-Platform Access: Log in from any device using your credentials
✅ AI-Powered Assessments: Get instant, detailed feedback on your practice tests
✅ Personalized Learning: Track your progress and focus on areas that need improvement
✅ 24/7 Availability: Study at your own pace, whenever and wherever suits you best

Your dedication to improving your English proficiency is truly commendable, and we're honored to be part of your IELTS journey. Our advanced AI technology is designed to provide you with the most accurate, helpful feedback to boost your confidence and skills.

Remember, every great achievement starts with a single step, and you've just taken yours! We believe in your potential and are here to support you every step of the way toward achieving your target IELTS score.

Ready to Get Started?
Simply log in to your account at www.ieltsaiprep.com and begin exploring your personalized dashboard. If you have any questions or need assistance, our support team is always here to help.

Wishing you tremendous success in your IELTS preparation and beyond. We can't wait to celebrate your achievements with you!

Best of luck on your exciting journey ahead! 🚀

Warm regards,
The IELTS AI Prep Team

---
This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this email.
    """
    
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [recipient_email]
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
            },
            ReplyToAddresses=[REPLY_TO_EMAIL]
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Welcome email sent successfully',
                'messageId': response['MessageId']
            })
        }
        
    except ClientError as e:
        print(f"Error sending email: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to send welcome email',
                'details': str(e)
            })
        }

def send_password_reset_email(recipient_email, reset_token, user_name=None):
    """
    Send password reset email to users
    """
    subject = "🔐 Reset Your IELTS AI Prep Password"
    
    # Create reset URL
    reset_url = f"https://www.ieltsaiprep.com/reset-password?token={reset_token}"
    
    # HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .reset-box {{ background: white; padding: 25px; border-radius: 8px; margin: 20px 0; text-align: center; border: 2px solid #2196F3; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            .cta-button {{ background: #2196F3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; font-weight: bold; }}
            .security-note {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
            <p>IELTS AI Prep Account Security</p>
        </div>
        
        <div class="content">
            <p>Hello{f", {user_name}" if user_name else ""},</p>
            
            <p>We received a request to reset the password for your IELTS AI Prep account associated with this email address.</p>
            
            <div class="alert">
                <strong>⚠️ Important:</strong> If you did not request this password reset, please ignore this email. Your account remains secure.
            </div>
            
            <div class="reset-box">
                <h3>Reset Your Password</h3>
                <p>Click the button below to create a new password for your account:</p>
                <a href="{reset_url}" class="cta-button">Reset My Password</a>
                <p><small>This link will expire in 1 hour for security reasons.</small></p>
            </div>
            
            <div class="security-note">
                <h4>🛡️ Security Tips:</h4>
                <ul>
                    <li>Choose a strong password with at least 8 characters</li>
                    <li>Include uppercase, lowercase, numbers, and special characters</li>
                    <li>Don't reuse passwords from other accounts</li>
                    <li>Consider using a password manager</li>
                </ul>
            </div>
            
            <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace;">{reset_url}</p>
            
            <p>If you continue to have trouble accessing your account, please contact our support team at support@ieltsaiprep.com.</p>
            
            <div class="footer">
                <p>Best regards,<br><strong>The IELTS AI Prep Security Team</strong></p>
                <hr>
                <p><small>This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this email.</small></p>
                <p><small>For security reasons, this password reset link will expire in 1 hour.</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_body = f"""
Password Reset Request - IELTS AI Prep

Hello{f", {user_name}" if user_name else ""},

We received a request to reset the password for your IELTS AI Prep account associated with this email address.

IMPORTANT: If you did not request this password reset, please ignore this email. Your account remains secure.

To reset your password, please visit the following link:
{reset_url}

This link will expire in 1 hour for security reasons.

Security Tips:
- Choose a strong password with at least 8 characters
- Include uppercase, lowercase, numbers, and special characters
- Don't reuse passwords from other accounts
- Consider using a password manager

If you continue to have trouble accessing your account, please contact our support team at support@ieltsaiprep.com.

Best regards,
The IELTS AI Prep Security Team

---
This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this email.
For security reasons, this password reset link will expire in 1 hour.
    """
    
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [recipient_email]
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
            },
            ReplyToAddresses=[REPLY_TO_EMAIL]
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Password reset email sent successfully',
                'messageId': response['MessageId']
            })
        }
        
    except ClientError as e:
        print(f"Error sending password reset email: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to send password reset email',
                'details': str(e)
            })
        }

def lambda_handler(event, context):
    """
    Main Lambda handler for email service
    """
    try:
        # Parse the incoming event
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        email_type = body.get('type', 'welcome')
        recipient_email = body.get('email')
        user_name = body.get('name')
        reset_token = body.get('reset_token')
        
        if not recipient_email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email address is required'})
            }
        
        # Handle different email types
        if email_type == 'welcome':
            return send_welcome_email(recipient_email, user_name)
        elif email_type == 'password_reset':
            if not reset_token:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Reset token is required for password reset emails'})
                }
            return send_password_reset_email(recipient_email, reset_token, user_name)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unsupported email type: {email_type}'})
            }
            
    except Exception as e:
        print(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
    