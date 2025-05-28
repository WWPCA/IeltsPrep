"""
Account Deletion Routes Module

This module provides account deletion functionality with proper warnings 
and email notifications for GDPR compliance.
"""

from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user, logout_user
from werkzeug.security import check_password_hash
import logging

from app import app, db
from models import User, UserAssessmentAttempt, UserAssessmentAssignment, PaymentRecord
from email_service import send_email

@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Display account deletion page with warnings and handle deletion request."""
    if request.method == 'GET':
        return render_template('delete_account.html', 
                             title='Delete My Account')
    
    # POST request - handle account deletion
    password = request.form.get('password')
    confirmation = request.form.get('confirmation')
    
    # Validate password
    if not password or not check_password_hash(current_user.password_hash, password):
        flash('Incorrect password. Please try again.', 'danger')
        return render_template('delete_account.html', title='Delete My Account')
    
    # Validate confirmation
    if confirmation != 'DELETE MY ACCOUNT':
        flash('Please type "DELETE MY ACCOUNT" exactly to confirm deletion.', 'danger')
        return render_template('delete_account.html', title='Delete My Account')
    
    try:
        # Store user info before deletion for email notification
        user_email = current_user.email
        user_name = current_user.username
        
        # Delete all related data
        delete_all_user_data(current_user.id)
        
        # Log out the user
        logout_user()
        
        # Send deletion confirmation email
        send_account_deletion_email(user_email, user_name)
        
        # Clear session
        session.clear()
        
        flash('Your account has been permanently deleted. A confirmation email has been sent.', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error deleting account: {e}")
        flash('An error occurred while deleting your account. Please contact support.', 'danger')
        return render_template('delete_account.html', title='Delete My Account')

def delete_all_user_data(user_id):
    """
    Permanently delete all user data from the database.
    
    Args:
        user_id (int): The ID of the user to delete
    """
    try:
        # Delete user assessment attempts
        UserAssessmentAttempt.query.filter_by(user_id=user_id).delete()
        
        # Delete user assessment assignments
        UserAssessmentAssignment.query.filter_by(user_id=user_id).delete()
        
        # Note: Keep payment records for tax compliance (7 years)
        # Mark them as anonymized instead of deleting
        payment_records = PaymentRecord.query.filter_by(user_id=user_id).all()
        for record in payment_records:
            record.user_id = None  # Anonymize
            record.customer_email = "deleted@example.com"  # Anonymize
        
        # Delete the user account
        User.query.filter_by(id=user_id).delete()
        
        # Commit all changes
        db.session.commit()
        
        logging.info(f"Successfully deleted all data for user ID: {user_id}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting user data: {e}")
        raise

def send_account_deletion_email(email, username):
    """
    Send account deletion confirmation email using professional template.
    
    Args:
        email (str): User's email address
        username (str): User's username (not used anymore, kept for compatibility)
    """
    from enhanced_email_service import send_account_deletion_confirmation
    
    try:
        result = send_account_deletion_confirmation(email)
        if result:
            logging.info(f"Account deletion confirmation email sent to {email}")
            return True
        else:
            logging.error(f"Failed to send account deletion email to {email}")
            return False
    except Exception as e:
        logging.error(f"Error sending account deletion email: {e}")
        return False