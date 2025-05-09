"""
Account activation functionality.
This module provides decorators to ensure users have active accounts.
"""
from functools import wraps
from flask import flash, redirect, url_for, session
from flask_login import current_user

def active_account_required(f):
    """
    Decorator to ensure the user has an activated account (payment processed).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If user is authenticated but account is not active
        if current_user.is_authenticated and not current_user.is_active:
            # Show a message that account activation is required
            flash('Please complete your payment to activate your account.', 'warning')
            
            # Check if there's pending_activation flag in session
            if session.get('pending_activation'):
                # Redirect to checkout if they need to complete payment
                return redirect(url_for('cart.checkout'))
            else:
                # Redirect to products page if no payment process is in progress
                return redirect(url_for('assessment_products_page'))
                
        # If the account is active or user is not logged in (other decorators will handle that)
        return f(*args, **kwargs)
    return decorated_function