import os
import json
import time
import uuid
import base64
import urllib
import logging
import random
import requests
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session, abort, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from functools import wraps
from app import app, db, recaptcha_v3
from models import User, AssessmentStructure, SpeakingPrompt, Assessment, UserAssessmentAssignment, PaymentRecord
from utils import get_user_region, get_translation, compress_audio
from payment_services import create_stripe_checkout_session, create_payment_record, verify_stripe_payment, create_stripe_checkout_speaking
import assessment_assignment_service
from nova_writing_assessment import assess_writing_task1, assess_writing_task2, assess_complete_writing_test
from aws_services import analyze_speaking_response, analyze_pronunciation, transcribe_audio, generate_polly_speech
# Using only get_country_from_ip since we've moved to fixed pricing
from geoip_services import get_country_from_ip
from country_restrictions import country_access_required, is_country_restricted, RESTRICTION_MESSAGE

# Import comprehensive security system
from security_manager import (
    security_manager, 
    rate_limit, 
    validate_inputs, 
    secure_session, 
    api_protection, 
    account_lockout_protection,
    setup_global_security
)

# Initialize security system
setup_global_security(app)

# Import the assessment details route
from add_assessment_details_route import assessment_details_route

# Speaking assessment selection route - catches the old URL
@app.route('/assessments/speaking')
@login_required
def speaking_assessment_redirect():
    """Redirect old speaking route to new 4 Elaris® assessment interface"""
    return render_template('assessments/speaking_selection.html', 
                         title='Academic Speaking Assessments',
                         assessment_type='academic_speaking')

@app.route('/assessments/academic_speaking')
@login_required
def academic_speaking_selection():
    """Display 4 identical Elaris® Academic Speaking assessments"""
    return render_template('assessments/speaking_selection.html', 
                         title='Academic Speaking Assessments',
                         assessment_type='academic_speaking')

@app.route('/assessments/general_speaking')
@login_required
def general_speaking_selection():
    """Display 4 identical Elaris® General Training Speaking assessments"""
    return render_template('assessments/general_speaking_selection.html',
                         title='General Training Speaking Assessments', 
                         assessment_type='general_speaking')

@app.route('/assessments/academic_writing')
@login_required
def academic_writing_selection():
    """Display 4 identical TrueScore® Academic Writing assessments"""
    return render_template('assessments/academic_writing_selection.html',
                         title='Academic Writing Assessments',
                         assessment_type='academic_writing')

@app.route('/assessments/general_writing')
@login_required
def general_writing_selection():
    """Display 4 identical TrueScore® General Training Writing assessments"""
    return render_template('assessments/general_writing_selection.html',
                         title='General Training Writing Assessments',
                         assessment_type='general_writing')

@app.route('/assessments/<assessment_type>/assessment/<int:assessment_number>')
@login_required
def assessment_start(assessment_type, assessment_number):
    """Start a specific assessment (speaking or writing) with proper setup"""
    valid_types = ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing']
    if assessment_type not in valid_types:
        flash('Invalid assessment type.', 'danger')
        return redirect(url_for('profile'))
    
    if assessment_number not in [1, 2, 3, 4]:
        flash('Invalid assessment number.', 'danger')
        return redirect(url_for('profile'))
    
    # Check if user has active assessment package for this type
    package_status = current_user.assessment_package_status or ""
    has_access = False
    
    if 'academic_speaking' in assessment_type and ('Academic Speaking' in package_status or 'All Products' in package_status):
        has_access = True
    elif 'general_speaking' in assessment_type and ('General Speaking' in package_status or 'All Products' in package_status):
        has_access = True
    elif 'academic_writing' in assessment_type and ('Academic Writing' in package_status or 'All Products' in package_status):
        has_access = True
    elif 'general_writing' in assessment_type and ('General Writing' in package_status or 'All Products' in package_status):
        has_access = True
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        has_access = True
    
    if not has_access:
        flash('You do not have access to this assessment type. Please purchase an assessment package.', 'danger')
        return redirect(url_for('profile'))
    
    # Determine which template to use based on assessment type
    if 'speaking' in assessment_type:
        template = 'assessments/speaking_start.html'
    else:  # writing assessments
        template = 'assessments/writing_start.html'
    
    return render_template(template,
                         title=f'Assessment {assessment_number} - {assessment_type.replace("_", " ").title()}',
                         assessment_type=assessment_type,
                         assessment_number=assessment_number)

@app.route('/speaking/assessment/<assessment_type>/<int:assessment_number>')
@login_required
def speaking_assessment_interface(assessment_type, assessment_number):
    """Main speaking assessment interface with AI examiner"""
    # Validate assessment type and number
    valid_types = ['academic_speaking', 'general_speaking']
    if assessment_type not in valid_types:
        flash('Invalid assessment type.', 'danger')
        return redirect(url_for('profile'))
    
    if assessment_number not in [1, 2, 3, 4]:
        flash('Invalid assessment number.', 'danger')
        return redirect(url_for('profile'))
    
    # Check if user has access to this assessment type
    package_status = current_user.assessment_package_status or ""
    has_access = False
    
    if 'academic_speaking' in assessment_type and ('Academic Speaking' in package_status or 'All Products' in package_status):
        has_access = True
    elif 'general_speaking' in assessment_type and ('General Speaking' in package_status or 'All Products' in package_status):
        has_access = True
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        has_access = True
    
    if not has_access:
        flash('You do not have access to this assessment type. Please purchase an assessment package.', 'danger')
        return redirect(url_for('profile'))
    
    return render_template('assessments/speaking_assessment.html', 
                         assessment_type=assessment_type, 
                         assessment_number=assessment_number)

@app.route('/writing/assessment/<assessment_type>/<int:assessment_number>')
@login_required
def writing_assessment_interface(assessment_type, assessment_number):
    """Main writing assessment interface with AI examiner"""
    # Validate assessment type and number
    valid_types = ['academic_writing', 'general_writing']
    if assessment_type not in valid_types:
        flash('Invalid assessment type.', 'danger')
        return redirect(url_for('profile'))
    
    if assessment_number not in [1, 2, 3, 4]:
        flash('Invalid assessment number.', 'danger')
        return redirect(url_for('profile'))
    
    # Check if user has access to this assessment type
    package_status = current_user.assessment_package_status or ""
    has_access = False
    
    if 'academic_writing' in assessment_type and ('Academic Writing' in package_status or 'All Products' in package_status):
        has_access = True
    elif 'general_writing' in assessment_type and ('General Writing' in package_status or 'All Products' in package_status):
        has_access = True
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        has_access = True
    
    if not has_access:
        flash('You do not have access to this assessment type. Please purchase an assessment package.', 'danger')
        return redirect(url_for('profile'))
    
    return render_template('assessments/writing_assessment.html', 
                         assessment_type=assessment_type, 
                         assessment_number=assessment_number)

# Main index route
@app.route('/')
def index():
    """Home page with overview of IELTS GenAI Prep platform"""
    return render_template('index.html', title='IELTS GenAI Prep - TrueScore® and Elaris® Assessments')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with enhanced security validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        identifier = security_manager.get_client_identifier()
        
        # Enhanced validation
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return render_template('login.html', title='Login')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Successful login - clear failed attempts
            security_manager.clear_failed_attempts(identifier)
            security_manager.log_security_event('successful_login', {'user_id': user.id})
            
            login_user(user)
            
            # Enhanced session security
            session.permanent = True
            session['user_agent_hash'] = hashlib.md5(
                request.headers.get('User-Agent', '').encode()
            ).hexdigest()
            session['last_activity'] = datetime.now().isoformat()
            
            next_page = request.args.get('next')
            if next_page and urlparse(next_page).netloc == '':
                return redirect(next_page)
            
            return redirect(url_for('index'))
        else:
            # Failed login - record attempt
            failed_count = security_manager.record_failed_login(identifier)
            security_manager.log_security_event(
                'failed_login', 
                {'email': email, 'attempt_count': failed_count}
            )
            
            if failed_count >= security_manager.max_login_attempts:
                flash('Account temporarily locked due to multiple failed attempts. Please try again later.', 'danger')
            else:
                remaining = security_manager.max_login_attempts - failed_count
                flash(f'Invalid email or password. {remaining} attempts remaining.', 'danger')
    
    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    """Log user out and redirect to home page"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        flash('Password change feature coming soon!', 'info')
        return redirect(url_for('profile'))
    return render_template('change_password.html', title='Change Password')

@app.route('/register', methods=['GET', 'POST'])
@rate_limit('login')
@validate_inputs(email='email', password='password', name='name')
def register():
    """Registration page with enhanced security validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        age_verified = request.form.get('age_verified')
        
        # Enhanced validation
        if not email or not password or not name:
            flash('Please provide all required fields', 'danger')
            return render_template('register.html', title='Register')
        
        # Age verification check
        if not age_verified:
            flash('You must confirm that you are 16 years or older to register', 'danger')
            return render_template('register.html', title='Register')
        
        # Check password complexity
        if not security_manager.validate_input(password, 'password'):
            flash('Password must be at least 8 characters with uppercase, lowercase, number, and special character', 'danger')
            return render_template('register.html', title='Register')
        
        # Check if email exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User()
        new_user.email = email
        new_user.name = name
        new_user.assessment_preference = 'academic'  # Default value
        new_user.set_password(password)
        
        # Store region information
        region = get_user_region(request)
        if region:
            new_user.region = region
        
        # Set account as activated (auto-activation for now)
        new_user.account_activated = True
        new_user.email_verified = True  # Auto-verify for simplicity
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register')

# Note: Assessment products route is defined in add_assessment_routes.py

# Custom cache buster to force browsers to reload CSS, JS on new deployments
@app.context_processor
def inject_cache_buster():
    """Add cache_buster variable to all templates to prevent browser caching"""
    cache_buster = int(time.time())
    return dict(cache_buster=cache_buster)

def assessment_package_required(f):
    """
    Decorator to check if user has active assessment packages
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('login'))
            
        if not current_user.has_active_assessment_package():
            flash('This feature requires an active assessment package. Please purchase a package to access this feature.', 'warning')
            return redirect(url_for('assessment_products_page'))
            
        return f(*args, **kwargs)
    return decorated_function

# Remove this after all routes are updated
# Legacy name mapping for backward compatibility with any old code
# Removed legacy backward compatibility line

# Streak tracking removed as requested

# Note: Restricted access page is now handled by country_access_control.py via the /access-restricted route

# Test route for country restrictions (admin only)
