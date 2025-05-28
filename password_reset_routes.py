"""
Password Reset Routes Module
Provides secure password reset functionality for registered users.
"""

import os
import secrets
from datetime import datetime, timedelta
from flask import render_template, request, flash, redirect, url_for, current_app
from werkzeug.security import generate_password_hash
from app import app, db
from models import User
from enhanced_email_service import send_password_reset_email

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot_password.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate secure reset token
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            
            # Save token to user record
            user.password_reset_token = reset_token
            user.password_reset_expires = reset_expires
            db.session.commit()
            
            # Send reset email using professional template
            reset_url = url_for('reset_password', token=reset_token, _external=True)
            
            try:
                send_result = send_password_reset_email(email, reset_url)
                
                if send_result:
                    flash('Password reset instructions have been sent to your email.', 'success')
                else:
                    flash('There was an error sending the reset email. Please try again.', 'error')
                    
            except Exception as e:
                flash('There was an error sending the reset email. Please try again.', 'error')
                current_app.logger.error(f"Password reset email error: {e}")
        else:
            # Don't reveal if email exists or not for security
            flash('If that email address is in our system, you will receive password reset instructions.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    # Find user with valid token
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
        flash('Invalid or expired reset token. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate passwords
        if not new_password or len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()
        
        flash('Your password has been successfully updated! You can now log in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# Add the forgot password link to login template context
@app.context_processor
def inject_forgot_password_link():
    """Make forgot password link available in templates"""
    return {'forgot_password_url': url_for('forgot_password')}