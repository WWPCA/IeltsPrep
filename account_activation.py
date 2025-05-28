"""
Account activation functionality.
This module provides account activation and email verification functionality.
"""

import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import request, redirect, render_template, flash, url_for
from flask_login import current_user, login_required

from app import db
from models import User
from email_service import send_verification_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def active_account_required(f):
    """
    Decorator to ensure the user has an activated account (payment processed).
    
    Note: This uses User.is_active property which checks account_activated field
    to maintain compatibility with flask_login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_active:
            flash('Your account has not been activated yet. Please complete the payment process.', 'warning')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def verified_email_required(f):
    """
    Decorator to ensure the user has verified their email.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_email_verified():
            flash('Please verify your email address before accessing this page.', 'warning')
            return redirect(url_for('email_verification.email_verification_notice'))
            
        return f(*args, **kwargs)
    return decorated_function

def authenticated_user_required(f):
    """
    Decorator to ensure the user is authenticated, has an active account,
    and has verified their email address.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_active:
            flash('Your account has not been activated yet. Please complete the payment process.', 'warning')
            return redirect(url_for('dashboard'))
        
        if not current_user.is_email_verified():
            flash('Please verify your email address before accessing this page.', 'warning')
            return redirect(url_for('email_verification.email_verification_notice'))
            
        return f(*args, **kwargs)
    return decorated_function

def send_verification_email_to_user(user_id):
    """
    Send a verification email to a user using professional templates.
    
    Args:
        user_id (int): The ID of the user to send the verification email to
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    from enhanced_email_service import send_email_verification
    from flask import url_for
    
    user = User.query.get(user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found.")
        return False
    
    # Check if an email was already sent recently (within the last 10 minutes)
    if (user.email_verification_sent_at and 
            datetime.utcnow() - user.email_verification_sent_at < timedelta(minutes=10)):
        logger.info(f"Verification email already sent to user {user_id} within the last 10 minutes.")
        return False
    
    # Generate verification URL
    verification_url = url_for('email_verification.verify_email', token=user.email_verification_token, _external=True)
    
    # Send the verification email using professional template
    result = send_email_verification(user.email, verification_url)
    
    if result:
        # Update the sent timestamp
        user.email_verification_sent_at = datetime.utcnow()
        db.session.commit()
        logger.info(f"Professional verification email sent to user {user_id}.")
    else:
        logger.error(f"Failed to send verification email to user {user_id}.")
    
    return result

def verify_and_activate_email(token):
    """
    Verify a user's email using the provided token.
    
    Args:
        token (str): The verification token
        
    Returns:
        tuple: (success, user) where success is a boolean and user is the User object
    """
    if not token:
        return False, None
    
    # Find the user with this token
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        logger.warning(f"No user found with verification token {token[:10]}...")
        return False, None
    
    # Verify the user's email
    success = user.verify_email(token)
    if success:
        logger.info(f"Email verified for user {user.id}.")
    else:
        logger.warning(f"Failed to verify email for user {user.id}.")
    
    return success, user