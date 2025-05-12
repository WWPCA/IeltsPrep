"""
Email Verification Routes Module

This module provides routes for email verification functionality.
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, render_template, flash, url_for, abort
from flask_login import login_required, current_user

from app import db
from models import User
from account_activation import send_verification_email_to_user, verify_and_activate_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
email_verification_bp = Blueprint('email_verification', __name__)

@email_verification_bp.route('/verify-email/<token>')
def verify_email(token):
    """
    Verify a user's email address using the token from the verification email.
    
    Args:
        token (str): The verification token
    """
    if not token:
        flash('Invalid verification link.', 'danger')
        return redirect(url_for('login'))
    
    # Verify the user's email
    success, user = verify_and_activate_email(token)
    
    if success:
        flash('Your email has been successfully verified! You can now access your account.', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid or expired verification link. Please request a new one.', 'danger')
        return redirect(url_for('login'))

@email_verification_bp.route('/email-verification-notice')
@login_required
def email_verification_notice():
    """
    Show a notice that the user needs to verify their email.
    """
    # If the user's email is already verified, redirect to dashboard
    if current_user.is_email_verified():
        return redirect(url_for('dashboard'))
    
    return render_template('email_verification_notice.html')

@email_verification_bp.route('/resend-verification-email', methods=['POST'])
@login_required
def resend_verification_email():
    """
    Resend the verification email to the user.
    """
    # Check if user's email is already verified
    if current_user.is_email_verified():
        flash('Your email is already verified.', 'info')
        return redirect(url_for('dashboard'))
    
    # Check if an email was sent recently (within the last 10 minutes)
    if (current_user.email_verification_sent_at and
            datetime.utcnow() - current_user.email_verification_sent_at < timedelta(minutes=10)):
        flash('A verification email was already sent recently. Please check your inbox or wait a few minutes before requesting another one.', 'info')
        return redirect(url_for('email_verification_notice'))
    
    # Send the verification email
    result = send_verification_email_to_user(current_user.id)
    
    if result:
        flash('A new verification email has been sent. Please check your inbox.', 'success')
    else:
        flash('Failed to send verification email. Please try again later.', 'danger')
    
    return redirect(url_for('email_verification_notice'))

def setup_email_verification_routes(app):
    """
    Register the email verification blueprint with the Flask app.
    
    Args:
        app (Flask): The Flask application
    """
    app.register_blueprint(email_verification_bp, url_prefix='/account')
    
    # Create the template directory if it doesn't exist
    import os
    if not os.path.exists('templates/account'):
        os.makedirs('templates/account')
    
    logger.info("Email verification routes set up successfully.")