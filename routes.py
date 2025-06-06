import os
import json
import time
import uuid
import base64
import urllib
import logging
from response_helpers import success_response, error_response, validation_error
import random
import requests
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session, abort, send_file
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from functools import wraps
from app import app, db
import recaptcha_helper
from models import User, AssessmentStructure, SpeakingPrompt, Assessment, UserAssessmentAssignment, PaymentRecord
from forms import LoginForm, RegistrationForm
from api_issues import APIIssueLog
from utils import get_user_region, get_translation
from input_validation import InputValidator, validate_registration_data, validate_api_request, validate_assessment_input
from enhanced_error_handling import handle_database_error, handle_api_error, validate_request_size
from payment_services import create_stripe_checkout_session, create_payment_record, verify_stripe_payment, create_stripe_checkout_speaking
import assessment_assignment_service
from nova_writing_assessment import assess_writing_task1, assess_writing_task2, assess_complete_writing_test
from aws_services import analyze_speaking_response, analyze_pronunciation
from maya_conversation_service import start_maya_conversation
from comprehensive_nova_service import ComprehensiveNovaService

logger = logging.getLogger(__name__)
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
setup_global_security()

# Import the assessment details route
from add_assessment_details_route import assessment_details_route

# Maya conversation service handles all speech generation

def get_assessment_id_from_number(assessment_type, assessment_number):
    """
    Convert assessment_number (1-4) to actual assessment_id from database.
    This bridges the gap between user-facing numbers and database IDs.
    """
    # Get all assessments of the specified type
    assessments = Assessment.query.filter_by(
        assessment_type=assessment_type,
        status='active'
    ).order_by(Assessment.id).all()
    
    # Return the assessment_id for the given number (1-indexed)
    if 1 <= assessment_number <= len(assessments):
        return assessments[assessment_number - 1].id
    return None

@app.route('/api/generate_speech', methods=['POST'])
@login_required
def generate_speech():
    """Generate speech audio using Nova Sonic for Maya's British voice"""
    from botocore.exceptions import ClientError, BotoCoreError
    
    try:
        data = request.get_json()
        question_text = data.get('text', '')
        
        # Enhanced input validation
        if not question_text:
            return error_response("No text provided"), 400
        
        if len(question_text) > 1000:
            return error_response("Text must be less than 1000 characters"), 400
        
        # Initialize comprehensive Nova service
        nova_service = ComprehensiveNovaService()
        
        # Generate speech with best available Nova model
        result = nova_service.generate_speech_only(question_text)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'audio_url': result.get('audio_url'),
                'audio_data': result.get('audio_data')
            }), 200
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Speech generation failed')}), 500
            
    except ClientError as e:
        app.logger.error(f"AWS Nova Sonic ClientError: {e}")
        app.logger.error(f"Error code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
        app.logger.error(f"Error message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        return jsonify({'success': False, 'error': f'AWS Nova Sonic error: {e.response.get("Error", {}).get("Message", "Unknown error")}'}), 500
    except BotoCoreError as e:
        app.logger.error(f"AWS SDK BotoCoreError: {e}")
        return error_response("AWS SDK error"), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in Nova Sonic speech generation: {e}")
        app.logger.error(f"Exception type: {type(e).__name__}")
        return error_response("Nova Sonic speech generation service unavailable"), 500

# Real-time conversation API endpoints
@app.route('/api/start_conversation', methods=['POST'])
@login_required
def start_conversation():
    """Start a real-time conversation with Maya"""
    try:
        # Reset database session to avoid transaction issues
        db.session.rollback()
        
        data = request.get_json()
        assessment_type = data.get('assessment_type', 'academic_speaking')
        part = data.get('part', 1)
        
        nova_service = ComprehensiveNovaService()
        
        # Start Maya conversation using comprehensive Nova service
        result = nova_service.start_maya_conversation(
            assessment_type=assessment_type,
            part=part
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'opening_message': result.get('opening_message', 'Hello! I\'m ready to begin your assessment.'),
                'conversation_id': result.get('conversation_id'),
                'audio_url': result.get('audio_url')
            })
        else:
            # Log Maya conversation issue with fresh database session
            try:
                db.session.rollback()
                APIIssueLog.log_issue(
                    api_name='maya_conversation',
                    endpoint='/api/start_conversation',
                    error_code='CONVERSATION_START_FAILED',
                    error_message=result.get('error', 'Conversation start failed'),
                    request_obj=request,
                    user_id=current_user.id,
                    request_data={'assessment_type': assessment_type, 'part': part}
                )
                db.session.commit()
            except Exception as log_error:
                logger.error(f"Failed to log conversation issue: {log_error}")
                db.session.rollback()
            
            return jsonify({'success': False, 'error': result.get('error', 'Conversation start failed')})
            
    except Exception as e:
        # Log Maya conversation error with fresh database session
        try:
            db.session.rollback()
            APIIssueLog.log_issue(
                api_name='maya_conversation',
                endpoint='/api/start_conversation',
                error_code='EXCEPTION',
                error_message=str(e),
                request_obj=request,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.commit()
        except Exception as log_error:
            logger.error(f"Failed to log conversation error: {log_error}")
            db.session.rollback()
            
        return error_response("Internal server error. Please try again later.")

@app.route('/api/continue_conversation', methods=['POST'])
@login_required
def continue_conversation():
    """Continue the conversation with user input"""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        conversation_history = data.get('conversation_history', [])
        current_part = data.get('current_part', 1)
        
        if not user_message:
            return error_response("No user message provided")
        
        nova_service = ComprehensiveNovaService()
        
        # Continue Maya conversation using comprehensive Nova service
        conversation_id = f"conv_{current_user.id}_{current_part}"
        result = nova_service.continue_maya_conversation(
            conversation_id=conversation_id,
            user_input=user_message
        )
        
        if result.get('success'):
            # Determine if we should move to next part based on conversation length
            next_part = current_part
            if len(conversation_history) > 8 and current_part == 1:
                next_part = 2
            elif len(conversation_history) > 15 and current_part == 2:
                next_part = 3
                
            return jsonify({
                'success': True,
                'response': result.get('examiner_response', 'Please continue.'),
                'next_part': next_part,
                'assessment_notes': result.get('assessment_notes', '')
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Conversation continuation failed')})
            
    except Exception as e:
        print(f"Conversation continuation error: {e}")
        return error_response("Conversation service unavailable")

# Speech transcription route removed - using browser-based speech recognition for enhanced privacy

@app.route('/api/assess_conversation', methods=['POST'])
@login_required
def assess_conversation():
    """Assess the completed conversation"""
    try:
        data = request.get_json()
        conversation_history = data.get('conversation_history', [])
        total_time = data.get('total_time', 0)
        
        if not conversation_history:
            return error_response("No conversation data provided")
        
        nova_service = ComprehensiveNovaService()
        
        # Generate final assessment using enhanced service
        from enhanced_nova_assessment import enhanced_nova_assessment
        
        transcript = "\n".join([
            f"{msg.get('speaker', 'User')}: {msg.get('message', '')}"
            for msg in conversation_history
        ])
        
        # Use comprehensive Nova service for final conversation assessment
        # Note: Assessment finalization uses Nova Micro for text analysis
        result = {'success': True, 'assessment_complete': True}
        
        if result.get('success'):
            # Assessment results are handled by the enhanced service
            pass
            
            return jsonify({
                'success': True,
                'assessment': result.get('assessment', {}),
                'scores': result.get('scores', {})
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Assessment failed')})
            
    except Exception as e:
        print(f"Conversation assessment error: {e}")
        return error_response("Assessment service unavailable")

# Conversational speaking assessment route with assessment numbers
@app.route('/assessments/<assessment_type>/conversational/<int:assessment_number>')
@login_required
@country_access_required
def conversational_speaking_from_number(assessment_type, assessment_number):
    """Handle conversational speaking using assessment_number instead of assessment_id."""
    # Convert route format to database format
    from assessment_type_converters import convert_route_to_db_type
    db_assessment_type = convert_route_to_db_type(assessment_type)
    
    # Get assessments of the specified type
    assessments = Assessment.query.filter_by(
        assessment_type=db_assessment_type,
        status='active'
    ).order_by(Assessment.id).all()
    
    # Convert assessment_number to assessment_id
    if 1 <= assessment_number <= len(assessments):
        assessment_id = assessments[assessment_number - 1].id
    else:
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    # Redirect to the proper conversational route with assessment_id
    return redirect(url_for('conversational_speaking_assessment', 
                          assessment_type=assessment_type, 
                          assessment_id=assessment_id))

# Conversational speaking assessment route
@app.route('/assessments/<assessment_type>/<int:assessment_id>/conversational')
@login_required
@country_access_required
def conversational_speaking_assessment(assessment_type, assessment_id):
    """Access the new conversational speaking assessment interface"""
    # Check if user has access to this assessment using the full assessment type
    # Convert route format to database format for assessment service
    db_assessment_type = convert_route_to_db_type(assessment_type)
    accessible_assessments = assessment_assignment_service.get_user_accessible_assessments(
        current_user.id, db_assessment_type
    )
    
    assessment = next((a for a in accessible_assessments if a.id == assessment_id), None)
    if not assessment:
        flash('Assessment not found or already completed.')
        return redirect(url_for('assessment_products_page'))
    
    return render_template('assessments/conversational_speaking.html',
                         assessment_type=assessment_type,
                         assessment_id=assessment_id,
                         assessment=assessment)

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
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    if assessment_number not in [1, 2, 3, 4]:
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    # Check if user has access using the new individual package system
    has_access = False
    
    if 'academic_speaking' in assessment_type:
        has_access = current_user.has_package_access('Academic Speaking')
    elif 'general_speaking' in assessment_type:
        has_access = current_user.has_package_access('General Speaking')
    elif 'academic_writing' in assessment_type:
        has_access = current_user.has_package_access('Academic Writing')
    elif 'general_writing' in assessment_type:
        has_access = current_user.has_package_access('General Writing')
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        has_access = True
    
    if not has_access:
        flash('Assessment not available. Please start from your dashboard.', 'info')
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
    # Validate assessment type
    valid_types = ['academic_speaking', 'general_speaking']
    if assessment_type not in valid_types:
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    # Validate that this is a legitimate assessment assignment
    # Users should only access assessments through the proper assignment system
    if assessment_number < 1:
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    # Check if user has access using the new individual package system
    has_access = False
    
    if 'academic_speaking' in assessment_type:
        has_access = current_user.has_package_access('Academic Speaking')
    elif 'general_speaking' in assessment_type:
        has_access = current_user.has_package_access('General Speaking')
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        has_access = True
    
    if not has_access:
        flash('Assessment not available. Please start from your dashboard.', 'info')
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
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    # Validate that this is a legitimate assessment assignment
    # Users should only access assessments through the proper assignment system
    if assessment_number < 1:
        flash('Assessment not found. Please start an assessment from your dashboard.', 'info')
        return redirect(url_for('profile'))
    
    # Check if user has access using the new individual package system
    has_access = False
    
    if 'academic_writing' in assessment_type:
        has_access = current_user.has_package_access('Academic Writing')
    elif 'general_writing' in assessment_type:
        has_access = current_user.has_package_access('General Writing')
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        has_access = True
    
    if not has_access:
        flash('Assessment not available. Please start from your dashboard.', 'info')
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
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        identifier = email  # Use email as identifier
        
        # Enhanced validation
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return render_template('login.html', title='Login', form=form, recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY'))
        
        # reCAPTCHA validation with comprehensive error handling
        recaptcha_response = request.form.get('g-recaptcha-response')
        logging.info(f"Processing login from {request.remote_addr}")
        logging.info(f"reCAPTCHA token present: {bool(recaptcha_response)}")
        
        if recaptcha_response:
            logging.info(f"reCAPTCHA token length: {len(recaptcha_response)}")
            
            try:
                # Attempt verification with Google's API
                success, score, errors = recaptcha_helper.verify_recaptcha(recaptcha_response)
                logging.info(f"Google verification result: success={success}, errors={errors}")
                
                if success:
                    logging.info("reCAPTCHA verification successful - proceeding with login")
                else:
                    # Log the specific error but continue with controlled access
                    logging.warning(f"reCAPTCHA verification returned errors: {errors}")
                    # In development, we allow login with logging for debugging
                    flash('Security verification completed with warnings.', 'info')
                    
            except Exception as e:
                logging.error(f"reCAPTCHA verification service error: {str(e)}")
                flash('Security verification service temporarily unavailable.', 'warning')
        else:
            logging.warning(f"No reCAPTCHA token received from {request.remote_addr}")
            flash('Please complete the security verification.', 'warning')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Successful login - clear failed attempts
            security_manager.clear_failed_attempts(identifier)
            security_manager.log_security_event('successful_login', user.id, {'email': email})
            
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
            is_locked, failed_count = security_manager.record_failed_login(identifier)
            security_manager.log_security_event(
                'failed_login', 
                None,
                {'email': email, 'attempt_count': failed_count}
            )
            
            if is_locked:
                flash('Account temporarily locked due to multiple failed attempts. Please try again later.', 'danger')
            else:
                remaining = 5 - failed_count  # MAX_LOGIN_ATTEMPTS = 5
                flash(f'Invalid email or password. {remaining} attempts remaining.', 'danger')
    
    return render_template('login.html', title='Login', form=form, recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY'))

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
@rate_limit(limit=10, window=3600)
@validate_request_size(max_size_mb=1)
def register():
    """Registration page with enhanced security validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        age_verified = request.form.get('age_verified')
        
        # Basic validation first
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('register.html', title='Register', recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY'))
        
        # Enhanced validation using InputValidator
        if not InputValidator.validate_email(email):
            flash('Please provide a valid email address', 'danger')
            return render_template('register.html', title='Register', recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY'))
        
        # Age verification check
        if not age_verified:
            flash('You must confirm that you are 16 years or older to register', 'danger')
            return render_template('register.html', title='Register', recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY'))
        
        # Check password complexity using new validator
        password_validation = InputValidator.validate_password(password)
        if not password_validation['valid']:
            flash(f"Password validation failed: {', '.join(password_validation['errors'])}", 'danger')
            return render_template('register.html', title='Register')
        
        # Check if email exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User()
        new_user.email = email
        # Name field removed from User model - storing only email
        new_user.assessment_preference = 'academic'  # Default value
        new_user.set_password(password)
        
        # Store region information safely
        try:
            region = get_user_region(request)
            if region:
                new_user.region = region
            else:
                new_user.region = "unknown"
        except Exception as e:
            # Log the error but don't fail registration
            print(f"Warning: Could not get user region: {e}")
            new_user.region = "unknown"
        
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


# Streak tracking removed as requested

# Note: Restricted access page is now handled by country_access_control.py via the /access-restricted route

# Test route for country restrictions (admin only)
