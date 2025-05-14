import os
import json
import time
import uuid
import base64
import urllib
import logging
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session, abort, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import app, db, recaptcha_v3
from models import User, TestStructure, SpeakingPrompt, Assessment, UserAssessmentAssignment, PaymentRecord
from utils import get_user_region, get_translation, compress_audio
from payment_services import create_stripe_checkout_session, create_payment_record, verify_stripe_payment, create_stripe_checkout_speaking
import assessment_assignment_service
from openai_writing_assessment import assess_writing_task1, assess_writing_task2, assess_complete_writing_test
from aws_services import analyze_speaking_response, analyze_pronunciation, transcribe_audio, generate_polly_speech
# Note: get_pricing_for_country is deprecated as we've moved to fixed pricing 
# Kept for backward compatibility
from geoip_services import get_country_from_ip, get_pricing_for_country
from country_restrictions import country_access_required, is_country_restricted, RESTRICTION_MESSAGE

# Import the assessment details route
try:
    from add_assessment_details_route import assessment_details_route
except ImportError:
    # Define it directly if the import fails
    def assessment_details_route(assessment_type, assessment_id):
        """Show details about an assessment before starting it"""
        if assessment_type not in ['listening', 'reading', 'writing', 'speaking']:
            abort(404)
        
        assessment = Assessment.query.get_or_404(assessment_id)
        
        # All assessments require an assessment package
        if not current_user.has_active_assessment_package():
            flash('This assessment requires an assessment package. Please purchase an assessment package to access GenAI-powered skill evaluations.', 'warning')
            return redirect(url_for('assessment_products_page'))
        
        # Check if user has already used this assessment during current assessment package period
        if current_user.has_taken_assessment(assessment_id, assessment_type):
            flash('You have already used this assessment during your current assessment package period. Each assessment can only be used once per assessment package.', 'warning')
            return redirect(url_for('assessment_products_page'))
        
        return render_template('assessment_details.html', 
                              title=f'IELTS {assessment_type.capitalize()} Assessment',
                              assessment=assessment,
                              assessment_type=assessment_type)

# Add the assessment details route
app.add_url_rule('/assessment/<assessment_type>/<int:assessment_id>/details', 
                 'assessment_details', 
                 assessment_details_route, 
                 methods=['GET'])

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
@app.route('/test-country-restriction/<country_code>')
@login_required
def test_country_restriction(country_code):
    """Test route to check if a specific country is restricted."""
    if not current_user.is_admin:
        flash("Admin access required for this function.", "danger")
        return redirect(url_for('index'))
        
    from country_restrictions import is_country_restricted, is_country_allowed, RESTRICTED_COUNTRIES, get_allowed_countries
    from payment_country_check import check_country_restriction
    
    # Test if the payment service check works correctly
    payment_test_result = None
    try:
        # Try to run the check_country_restriction function
        check_country_restriction(country_code, is_country_restricted)
        # If we get here, the country was allowed
        payment_test_result = {
            'success': True,
            'message': 'Country allowed for payments'
        }
    except ValueError as e:
        # If we get a ValueError, it means the country was restricted as expected
        payment_test_result = {
            'success': country_code.upper() in RESTRICTED_COUNTRIES,  # Success if restricted and caught
            'message': str(e)
        }
    except Exception as e:
        # If we get any other exception, it's an unexpected error
        payment_test_result = {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }
    
    # Get the allowed countries list to check if this country is in it
    allowed_countries = get_allowed_countries()
    
    country_info = {
        'code': country_code.upper(),
        'is_restricted': is_country_restricted(country_code),
        'is_allowed': is_country_allowed(country_code),
        'all_restricted': RESTRICTED_COUNTRIES,
        'checkout_allowed': country_code.upper() in allowed_countries,
        'payment_test_result': payment_test_result
    }
    
    return render_template('admin/test_country.html', country_info=country_info, title='Test Country Restriction')

# Simulate access from a restricted country (admin only)
@app.route('/simulate-country-access/<country_code>')
@login_required
def simulate_country_access(country_code):
    """Simulate accessing the site from a specific country code."""
    if not current_user.is_admin:
        flash("Admin access required for this function.", "danger")
        return redirect(url_for('index'))
    
    from country_restrictions import is_country_restricted, RESTRICTED_COUNTRIES
    
    # Store the simulated country in session
    session['country_code'] = country_code.upper()
    session['simulated_country'] = True
    is_restricted = is_country_restricted(country_code)
    
    if is_restricted:
        flash(f"Simulating access from restricted country: {country_code.upper()}", "warning")
        return redirect(url_for('restricted_access'))
    else:
        flash(f"Simulating access from allowed country: {country_code.upper()}", "success")
        return redirect(url_for('index'))

# Reset simulated country (admin only)
@app.route('/reset-country-simulation')
@login_required
def reset_country_simulation():
    """Reset any simulated country code in the session."""
    if not current_user.is_admin:
        flash("Admin access required for this function.", "danger")
        return redirect(url_for('index'))
    
    # Remove simulated country from session
    if 'country_code' in session:
        session.pop('country_code')
    if 'simulated_country' in session:
        session.pop('simulated_country')
    
    flash("Country simulation has been reset. Your actual location will now be used.", "success")
    return redirect(url_for('index'))

# Home route with country access check
@app.route('/')
@country_access_required
def index():
    return render_template('index.html', title='IELTS GenAI Prep')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
@country_access_required
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Verify reCAPTCHA
        recaptcha_token = request.form.get('g-recaptcha-response')
        if not recaptcha_token:
            flash('Please verify that you are not a robot.', 'danger')
            return render_template('login.html', title='Login')
            
        # Verify the token with Google
        recaptcha_result = recaptcha_v3.verify(response=recaptcha_token, action='login')
        if not recaptcha_result['success']:
            # For security, don't reveal specific failure reason
            flash('Security verification failed. Please try again.', 'danger')
            logging.warning(f"reCAPTCHA verification failed during login: {recaptcha_result.get('error', 'unknown reason')}")
            return render_template('login.html', title='Login')
        
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html', title='Login')
            
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            
            # Check if user came from checkout or has pending payment
            next_page = request.args.get('next')
            if next_page == 'checkout':
                flash('Login successful! Please complete your purchase.', 'success')
                return redirect(url_for('cart.checkout'))
            elif 'pending_checkout' in session and session['pending_checkout']:
                # Clear the pending checkout flag
                session.pop('pending_checkout')
                flash('Login successful! Please complete your purchase.', 'success')
                return redirect(url_for('cart.checkout'))
            elif 'pending_payment' in session:
                # User has a pending payment to process
                flash('Login successful! Processing your previous purchase...', 'success')
                return redirect(url_for('payment_success'))
                
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
@country_access_required
def register():
    if current_user.is_authenticated:
        # If user is coming from checkout, redirect back there
        next_page = request.args.get('next')
        if next_page == 'checkout':
            return redirect(url_for('cart.checkout'))
        return redirect(url_for('index'))
    
    class RegistrationForm:
        # Simple form class to enable CSRF protection
        def __init__(self):
            pass

    form = RegistrationForm()
    
    # Get pre-filled email from session if available
    pre_filled_email = None
    if 'registration_email' in session:
        pre_filled_email = session.pop('registration_email')
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Country selection has been removed, so we'll set a default value
        region = "Unknown"
        
        # Verify reCAPTCHA
        recaptcha_token = request.form.get('g-recaptcha-response')
        if not recaptcha_token:
            flash('Please verify that you are not a robot.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # Verify the token with Google
        recaptcha_result = recaptcha_v3.verify(response=recaptcha_token, action='register')
        if not recaptcha_result['success']:
            # For security, don't reveal specific failure reason
            flash('Security verification failed. Please try again.', 'danger')
            logging.warning(f"reCAPTCHA verification failed: {recaptcha_result.get('error', 'unknown reason')}")
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # If successful but score is too low, show a more specific message
        if recaptcha_result.get('score', 0) < 0.3:  # Very low scores likely indicate bots
            flash('Your verification score was too low. Please try again later or contact support if this persists.', 'danger')
            logging.warning(f"Low reCAPTCHA score for registration: {recaptcha_result.get('score', 0)}")
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
        
        # Check if age verification was confirmed
        if not request.form.get('age_verification'):
            flash('You must confirm that you are at least 16 years of age to register.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # Check if terms were agreed to
        if not request.form.get('agree_terms'):
            flash('You must agree to the Terms of Service and Privacy Policy to register.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # Validate password length and complexity
        import re
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
        
        # Check for uppercase letters
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # Check for lowercase letters
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # Check for numbers
        if not re.search(r'\d', password):
            flash('Password must contain at least one number.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
            
        # Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one special character.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
        
        try:
            # Use safer query approach with only needed columns
            existing_user = db.session.query(User.id).filter_by(email=email).first()
            if existing_user:
                flash('Email already exists! Please login or use a different email address.', 'danger')
                return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
        except Exception as e:
            # Log the error
            print(f"Error checking email in registration: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)
        
        # Determine initial test preference from cart products
        test_preference = 'academic'  # Default value
        
        # If user has items in cart, determine test preference from those
        if 'cart' in session and session['cart']:
            from cart import determine_test_preference, get_product_ids
            product_ids = get_product_ids()
            cart_preference = determine_test_preference(product_ids)
            if cart_preference:
                test_preference = cart_preference
        
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # If user exists, redirect to login
            flash('An account with this email already exists. Please log in.', 'info')
            return redirect(url_for('login'))
            
        # Store registration data in session (don't create account yet)
        session['registration_data'] = {
            'username': email,  # Use email as the username
            'email': email,
            'password': password,  # We'll hash this when creating the user
            'region': region,
            'test_preference': test_preference  # From cart products or default
        }
        
        # Check if the user has items in their cart
        if 'cart' in session and session['cart']:
            flash('Please complete your purchase to create your account.', 'info')
            return redirect(url_for('cart.checkout'))
        
        # Check if the user came from checkout (legacy flow)
        next_page = request.args.get('next')
        if next_page == 'checkout':
            flash('Please complete your purchase to create your account.', 'info')
            return redirect(url_for('cart.checkout'))
        
        flash('Please purchase an assessment product to create your account.', 'info')
        return redirect(url_for('assessment_products_page'))
    
    return render_template('register.html', title='Register', form=form, pre_filled_email=pre_filled_email)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Profile page is now simplified, no streak data needed
    return render_template('profile.html', title='My Profile')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow users to change their password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check if current password is correct
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Validate password length and complexity
        import re
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check for uppercase letters
        if not re.search(r'[A-Z]', new_password):
            flash('Password must contain at least one uppercase letter.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check for lowercase letters
        if not re.search(r'[a-z]', new_password):
            flash('Password must contain at least one lowercase letter.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check for numbers
        if not re.search(r'\d', new_password):
            flash('Password must contain at least one number.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            flash('Password must contain at least one special character.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Check if new password is the same as any previous passwords
        if current_user.is_password_reused(new_password):
            flash('You cannot reuse a previous password. Please choose a different password.', 'danger')
            return render_template('change_password.html', title='Change Password')
            
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Your password has been updated successfully.', 'success')
        return redirect(url_for('profile'))
        
    return render_template('change_password.html', title='Change Password')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('forgot_password.html', title='Forgot Password')
            
        try:
            # Check if user exists using safer query approach
            user = db.session.query(User.id).filter_by(email=email).first()
            
            # For simplicity and security, always show the same success message
            # regardless of whether the email exists
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
            # TODO: Implement email sending functionality with reset token
        except Exception as e:
            # Log the error
            print(f"Error checking email in forgot password: {str(e)}")
            # Same message for security (don't reveal database error)
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
            
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html', title='Forgot Password')

@app.route('/forgot-username', methods=['GET', 'POST'])
def forgot_username():
    """Handle forgot username requests"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('forgot_username.html', title='Forgot Username')
            
        try:
            # Check if user exists using safer query approach
            user = db.session.query(User.id).filter_by(email=email).first()
            
            # For simplicity and security, always show the same success message
            # regardless of whether the email exists
            flash('If an account exists with that email, your username has been sent.', 'info')
            # TODO: Implement email sending functionality
        except Exception as e:
            # Log the error
            print(f"Error checking email in forgot username: {str(e)}")
            # Same message for security (don't reveal database error)
            flash('If an account exists with that email, your username has been sent.', 'info')
            
        return redirect(url_for('login'))
        
    return render_template('forgot_username.html', title='Forgot Username')

# Test Structure Routes
@app.route('/test-structure')
def test_structure():
    ielts_info = "The International English Language Testing System (IELTS) assesses the English language proficiency of people who want to study or work in environments where English is used as the language of communication."
    return render_template('test_structure/index.html', 
                          title='IELTS Test Structure',
                          ielts_info=ielts_info)

@app.route('/test-structure/<test_type>')
def test_structure_detail(test_type):
    ielts_info = "The International English Language Testing System (IELTS) assesses the English language proficiency of people who want to study or work in environments where English is used as the language of communication."
    test_info = TestStructure.query.filter_by(test_type=test_type).first_or_404()
    return render_template(f'test_structure/{test_type}.html', 
                          title=f'IELTS {test_type.replace("_", " ").title()}',
                          test_info=test_info,
                          ielts_info=ielts_info)

@app.route('/test-day')
@login_required
def test_day():
    # Check if user has purchased a value pack (4 tests package)
    if not current_user.is_authenticated:
        flash('Please log in to access the Test Day Guide.', 'warning')
        return redirect(url_for('login'))
    
    # Check if user has Value Pack assessment package
    if current_user.assessment_package_status != 'Value Pack':
        flash('The Test Day Guide is only available with the Value Pack (4 tests) assessment package.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    return render_template('test_day.html', title='IELTS Test Day Preparation')

# Practice Test Routes
@app.route('/practice')
def practice_index():
    test_types = ['listening', 'reading', 'writing']
    sample_tests = {}
    
    for test_type in test_types:
        sample_tests[test_type] = PracticeTest.query.filter_by(test_type=test_type).first()
    
    # Get complete tests based on user's test preference
    complete_tests = []
    test_progress = {}
    
    if current_user.is_authenticated:
        # Filter tests by user's test preference
        # Map user preference to assessment type
        preference_to_assessment = {
            'academic': 'academic_writing',
            'general': 'general_writing' 
        }
        user_assessment_type = preference_to_assessment.get(current_user.test_preference, 'academic_writing')
        
        # Use the test assignment service to get the tests the user has access to
        if current_user.has_active_assessment_package():
            # First check if user has any assigned tests
            assigned_tests = test_assignment_service.get_user_accessible_assessments(
                user_id=current_user.id,
                assessment_type=user_test_preference
            )
            
            if assigned_tests:
                # User has assigned tests from the new system
                complete_tests = assigned_tests
            else:
                # Fallback to the old system for users with legacy assessment packages
                # Determine number of tests to show based on user's assessment package
                num_tests_to_show = 1  # Default for single test package
                
                if current_user.assessment_package_status == 'Value Pack':
                    num_tests_to_show = 4
                elif current_user.assessment_package_status == 'Double Package':
                    num_tests_to_show = 2
                
                # Use sqlalchemy to get tests
                from sqlalchemy import func
                
                # First get the latest ID for each test number
                subquery = db.session.query(
                    CompletePracticeTest.test_number,
                    func.max(CompletePracticeTest.id).label('max_id')
                ).filter(
                    CompletePracticeTest.ielts_test_type == user_test_preference
                ).group_by(CompletePracticeTest.test_number).subquery()
                
                # Then join to get the complete test records
                all_tests = CompletePracticeTest.query.join(
                    subquery,
                    db.and_(
                        CompletePracticeTest.id == subquery.c.max_id,
                        CompletePracticeTest.test_number == subquery.c.test_number
                    )
                ).order_by(CompletePracticeTest.test_number).all()
                
                # Limit the number of tests based on assessment package
                complete_tests = all_tests[:num_tests_to_show]
        else:
            # For users without an assessment package, only show free tests (also avoid duplicates)
            subquery = db.session.query(
                CompletePracticeTest.test_number,
                func.max(CompletePracticeTest.id).label('max_id')
            ).filter(
                CompletePracticeTest.ielts_test_type == user_test_preference,
                CompletePracticeTest.is_free == True
            ).group_by(CompletePracticeTest.test_number).subquery()
            
            complete_tests = CompletePracticeTest.query.join(
                subquery,
                db.and_(
                    CompletePracticeTest.id == subquery.c.max_id,
                    CompletePracticeTest.test_number == subquery.c.test_number
                )
            ).order_by(CompletePracticeTest.test_number).all()
            
        # Get progress for each test
        if complete_tests:
            user_progress = CompleteTestProgress.query.filter_by(user_id=current_user.id).all()
            for progress in user_progress:
                # Calculate percentage complete
                if progress.section_progress:
                    num_sections = len(progress.section_progress)
                    num_completed = sum(1 for section in progress.section_progress.values() 
                                      if section.get('completed', False))
                    progress_percent = int((num_completed / max(1, num_sections)) * 100)
                    
                    test_progress[progress.complete_test_id] = {
                        'progress_percent': progress_percent,
                        'is_completed': progress.is_test_completed(),
                        'score': progress.get_overall_score() if progress.is_test_completed() else None,
                        'status': 'Completed' if progress.is_test_completed() 
                                else f'{num_completed} of {num_sections} sections completed'
                    }
    else:
        # For anonymous users, just show a sample of free tests (avoiding duplicates)
        from sqlalchemy import func
        
        # First get the latest ID for each test number
        subquery = db.session.query(
            CompletePracticeTest.test_number,
            CompletePracticeTest.ielts_test_type,
            func.max(CompletePracticeTest.id).label('max_id')
        ).filter(
            CompletePracticeTest.is_free == True
        ).group_by(CompletePracticeTest.test_number, CompletePracticeTest.ielts_test_type).subquery()
        
        # Then get the complete test records using those IDs
        complete_tests = CompletePracticeTest.query.join(
            subquery,
            db.and_(
                CompletePracticeTest.id == subquery.c.max_id,
                CompletePracticeTest.test_number == subquery.c.test_number,
                CompletePracticeTest.ielts_test_type == subquery.c.ielts_test_type
            )
        ).limit(4).all()
    
    return render_template('practice/index.html', title='Practice Tests', 
                          sample_tests=sample_tests,
                          complete_tests=complete_tests,
                          test_progress=test_progress)

@app.route('/practice/<test_type>')
@login_required
def practice_test_list(test_type):
    # Add speaking to the list of valid test types
    if test_type not in ['listening', 'reading', 'writing', 'speaking']:
        abort(404)
        
    # Check access rights - speaking-only users can only access speaking tests
    if current_user.is_speaking_only_user() and test_type != 'speaking':
        flash('Your speaking-only access allows you to access speaking tests only. Please upgrade to access all test types.', 'warning')
        return redirect(url_for('practice_test_list', test_type='speaking'))
    
    # Handle speaking tests separately for speaking-only users
    if test_type == 'speaking':
        # Get all tests of this type, but filter to just show ones with complete questions and answers
        tests = PracticeTest.query.filter_by(test_type=test_type).all()
        
        # Get a list of test IDs the user has already completed
        completed_test_ids = [test['test_id'] for test in current_user.completed_tests 
                             if test['test_type'] == test_type]
                             
        # For speaking-only users, add remaining attempts count to the template
        remaining_attempts = 0
        is_speaking_only = False
        if current_user.is_speaking_only_user():
            is_speaking_only = True
            remaining_attempts = current_user.get_remaining_speaking_assessments()
            
        return render_template(f'practice/{test_type}.html', 
                              title=f'IELTS {test_type.capitalize()} Practice',
                              tests=tests,
                              completed_test_ids=completed_test_ids,
                              is_speaking_only=is_speaking_only,
                              remaining_attempts=remaining_attempts)
    
    # For other test types (reading, writing, listening)
    # Get all tests of this type, but filter to just show ones with complete questions and answers
    tests = PracticeTest.query.filter_by(test_type=test_type).all()
    
    # Determine how many tests to show based on assessment package
    if current_user.has_active_assessment_package():
        # Determine number of tests to show based on user's assessment package
        num_tests_to_show = 1  # Default for single test package
            
        if current_user.assessment_package_status == 'Value Pack':
            num_tests_to_show = 4
        elif current_user.assessment_package_status == 'Double Package':
            num_tests_to_show = 2
            
        # Limit tests based on assessment package level
        tests = tests[:num_tests_to_show] if tests else []
    else:
        # For users without an assessment package, only show the first test
        tests = tests[:1] if tests else []
    
    # Get a list of test IDs the user has already completed
    completed_test_ids = [test['test_id'] for test in current_user.completed_tests 
                         if test['test_type'] == test_type]
    
    return render_template(f'practice/{test_type}.html', 
                          title=f'IELTS {test_type.capitalize()} Practice',
                          tests=tests,
                          completed_test_ids=completed_test_ids)

@app.route('/practice/<test_type>/<int:test_id>')
@login_required
def take_practice_test(test_type, test_id):
    if test_type not in ['listening', 'reading', 'writing', 'speaking']:
        abort(404)
    
    # Check access rights - speaking-only users can only access speaking tests
    if current_user.is_speaking_only_user() and test_type != 'speaking':
        flash('Your speaking-only access allows you to access speaking tests only. Please upgrade to access all test types.', 'warning')
        return redirect(url_for('practice_test_list', test_type='speaking'))
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # Check if user has sufficient access
    if test_type == 'speaking' and current_user.is_speaking_only_user():
        # Special handling for speaking-only users
        remaining_attempts = current_user.get_remaining_speaking_assessments()
        if remaining_attempts <= 0:
            flash('You have used all your speaking assessments. Please purchase more to continue.', 'warning')
            return redirect(url_for('speaking_only'))
    elif not current_user.has_active_assessment_package():
        # Check for assessment package access for other test types
        flash('This test requires an assessment package. Please purchase an assessment package to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already taken this test during current assessment package period
    if current_user.has_taken_test(test_id, test_type):
        flash('You have already taken this test during your current assessment package period. Each test can only be taken once per assessment package.', 'warning')
        return redirect(url_for('practice_test_list', test_type=test_type))
    
    # For all tests, use the empty templates instead of actual content to prevent popup errors
    if test_type == 'listening':
        return render_template('practice/listening_empty.html',
                              title='IELTS Listening Practice',
                              test=test,
                              taking_test=True)
    elif test_type == 'reading':
        return render_template('practice/reading_empty.html',
                              title='IELTS Reading Practice',
                              test=test,
                              taking_test=True)
    elif test_type == 'writing':
        return render_template('practice/writing_empty.html',
                              title='IELTS Writing Practice',
                              test=test,
                              taking_test=True)
    elif test_type == 'speaking':
        # For speaking tests, add speaking-only user info to the template
        is_speaking_only = current_user.is_speaking_only_user()
        remaining_attempts = current_user.get_remaining_speaking_assessments() if is_speaking_only else 0
        
        return render_template('practice/speaking_empty.html',
                              title='IELTS Speaking Practice',
                              test=test,
                              taking_test=True,
                              is_speaking_only=is_speaking_only,
                              remaining_attempts=remaining_attempts)

@app.route('/practice/<test_type>/<int:test_id>/start')
@login_required
def start_practice_test(test_type, test_id):
    """Start a practice test after viewing the test details page"""
    if test_type not in ['listening', 'reading', 'writing', 'speaking']:
        abort(404)
        
    # Check access rights - speaking-only users can only access speaking tests
    if current_user.is_speaking_only_user() and test_type != 'speaking':
        flash('Your speaking-only access allows you to access speaking tests only. Please upgrade to access all test types.', 'warning')
        return redirect(url_for('practice_test_list', test_type='speaking'))
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # Check if user has sufficient access
    if test_type == 'speaking' and current_user.is_speaking_only_user():
        # Special handling for speaking-only users
        remaining_attempts = current_user.get_remaining_speaking_assessments()
        if remaining_attempts <= 0:
            flash('You have used all your speaking assessments. Please purchase more to continue.', 'warning')
            return redirect(url_for('speaking_only'))
            
        # Decrement the user's remaining speaking attempts
        use_result = current_user.use_speaking_assessment()
        if not use_result:
            flash('There was an error processing your request. Please try again.', 'danger')
            return redirect(url_for('practice_test_list', test_type='speaking'))
            
        # Update remaining count for display
        remaining_attempts -= 1
        
    elif not current_user.has_active_assessment_package():
        # Check for assessment package access for other test types
        flash('This test requires an assessment package. Please purchase an assessment package to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already taken this test during current assessment package period
    if current_user.has_taken_test(test_id, test_type):
        flash('You have already taken this test during your current assessment package period. Each test can only be taken once per assessment package.', 'warning')
        return redirect(url_for('practice_test_list', test_type=test_type))
    
    # Initialize test record for tracking user's progress
    attempt = UserTestAttempt(
        user_id=current_user.id,
        test_id=test_id,
        test_type=test_type,
        start_time=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Redirect to the appropriate template based on test type
    if test_type == 'listening':
        return render_template('practice/listening_empty.html',
                              title='IELTS Listening Practice',
                              test=test,
                              taking_test=True)
    elif test_type == 'reading':
        return render_template('practice/reading_empty.html',
                              title='IELTS Reading Practice',
                              test=test,
                              taking_test=True)
    elif test_type == 'writing':
        return render_template('practice/writing_empty.html',
                              title='IELTS Writing Practice',
                              test=test,
                              taking_test=True)
    elif test_type == 'speaking':
        # For speaking tests, add speaking-only user info to the template
        is_speaking_only = current_user.is_speaking_only_user()
        remaining_attempts = current_user.get_remaining_speaking_assessments() if is_speaking_only else 0
        
        return render_template('practice/speaking_empty.html',
                              title='IELTS Speaking Practice',
                              test=test,
                              taking_test=True,
                              is_speaking_only=is_speaking_only,
                              remaining_attempts=remaining_attempts)

# Complete Test Routes
@app.route('/practice/complete-test/<int:test_id>/start')
@login_required
def start_complete_test(test_id):
    """Start a new complete IELTS practice test"""
    complete_test = CompletePracticeTest.query.get_or_404(test_id)
    
    # Check if user has access to this test
    if not current_user.is_subscribed():
        flash('This test requires an assessment package. Please purchase an assessment package to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Verify that this test should be accessible based on the user's package
    # Get all tests for this user's preference
    from sqlalchemy import func
    
    # Determine number of tests to show based on user's assessment package
    num_tests_to_show = 1  # Default for single test package
    if current_user.assessment_package_status == 'Value Pack':
        num_tests_to_show = 4
    elif current_user.assessment_package_status == 'Double Package':
        num_tests_to_show = 2
    
    # Get the latest version of each test number
    subquery = db.session.query(
        CompletePracticeTest.test_number,
        func.max(CompletePracticeTest.id).label('max_id')
    ).filter(
        CompletePracticeTest.ielts_test_type == current_user.test_preference
    ).group_by(CompletePracticeTest.test_number).subquery()
    
    # Get all tests the user should have access to
    allowed_tests = CompletePracticeTest.query.join(
        subquery,
        db.and_(
            CompletePracticeTest.id == subquery.c.max_id,
            CompletePracticeTest.test_number == subquery.c.test_number
        )
    ).order_by(CompletePracticeTest.test_number).limit(num_tests_to_show).all()
    
    # Check if the requested test is in the allowed tests list
    if complete_test not in allowed_tests:
        flash(f'This test is not available with your current {current_user.assessment_package_status} package.', 'warning')
        return redirect(url_for('practice_index'))
    
    # Check if user already has an in-progress attempt
    existing_progress = CompleteTestProgress.query.filter_by(
        user_id=current_user.id,
        complete_test_id=test_id
    ).first()
    
    if existing_progress:
        if existing_progress.is_test_completed():
            flash('You have already completed this test.', 'info')
            return redirect(url_for('practice_index'))
        
        # Continue existing progress
        return redirect(url_for('continue_complete_test', test_id=test_id))
    
    # Start a new test progress
    progress = CompleteTestProgress(
        user_id=current_user.id,
        complete_test_id=test_id,
        start_date=datetime.utcnow()
    )
    
    # All IELTS tests start with the listening section
    progress.current_section = 'listening'
    
    db.session.add(progress)
    db.session.commit()
    
    # Redirect to the first section
    return redirect(url_for('take_complete_test_section', 
                            test_id=test_id, 
                            section=progress.current_section))

@app.route('/practice/complete-test/<int:test_id>/continue')
@login_required
def continue_complete_test(test_id):
    """Continue an in-progress complete test"""
    # Get user's progress for this test
    progress = CompleteTestProgress.query.filter_by(
        user_id=current_user.id,
        complete_test_id=test_id
    ).first_or_404()
    
    # Get the complete test
    complete_test = CompletePracticeTest.query.get_or_404(test_id)
    
    # Verify this test should be available to this user (only check if test not already completed)
    # This allows users to see their results even if their package has been downgraded
    if not progress.is_test_completed():
        # Verify the user has the appropriate package for this test
        from sqlalchemy import func
        
        # Determine number of tests allowed based on user's assessment package
        num_tests_allowed = 1  # Default for single test package
        if current_user.assessment_package_status == 'Value Pack':
            num_tests_allowed = 4
        elif current_user.assessment_package_status == 'Double Package':
            num_tests_allowed = 2
        
        # Get the latest version of each test number
        subquery = db.session.query(
            CompletePracticeTest.test_number,
            func.max(CompletePracticeTest.id).label('max_id')
        ).filter(
            CompletePracticeTest.ielts_test_type == current_user.test_preference
        ).group_by(CompletePracticeTest.test_number).subquery()
        
        # Get all tests the user should have access to
        allowed_tests = CompletePracticeTest.query.join(
            subquery,
            db.and_(
                CompletePracticeTest.id == subquery.c.max_id,
                CompletePracticeTest.test_number == subquery.c.test_number
            )
        ).order_by(CompletePracticeTest.test_number).limit(num_tests_allowed).all()
        
        # Check if the requested test is in the allowed tests list
        if complete_test not in allowed_tests:
            flash(f'This test is not available with your current {current_user.assessment_package_status} package.', 'warning')
            return redirect(url_for('practice_index'))
    
    # If the test is already completed, show results
    if progress.is_test_completed():
        return redirect(url_for('complete_test_results', test_id=test_id))
    
    # Get the next section to complete
    next_section = progress.get_next_section()
    if not next_section:
        # Test is completed
        progress.completed_date = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('complete_test_results', test_id=test_id))
    
    # Update current section
    progress.current_section = next_section
    db.session.commit()
    
    # Redirect to that section
    return redirect(url_for('take_complete_test_section', 
                            test_id=test_id, 
                            section=next_section))

@app.route('/practice/complete-test/<int:test_id>/<section>')
@login_required
def take_complete_test_section(test_id, section):
    """Take a specific section of a complete test"""
    if section not in ['listening', 'reading', 'writing', 'speaking']:
        abort(404)
    
    # Verify user has an in-progress test
    progress = CompleteTestProgress.query.filter_by(
        user_id=current_user.id,
        complete_test_id=test_id
    ).first_or_404()
    
    # Get the complete test
    complete_test = CompletePracticeTest.query.get_or_404(test_id)
    
    # Verify the user can access this test based on their current package (if not already completed)
    if not progress.is_test_completed():
        # Verify the user has the appropriate package for this test
        from sqlalchemy import func
        
        # Determine number of tests allowed based on user's assessment package
        num_tests_allowed = 1  # Default for single test package
        if current_user.assessment_package_status == 'Value Pack':
            num_tests_allowed = 4
        elif current_user.assessment_package_status == 'Double Package':
            num_tests_allowed = 2
        
        # Get the latest version of each test number
        subquery = db.session.query(
            CompletePracticeTest.test_number,
            func.max(CompletePracticeTest.id).label('max_id')
        ).filter(
            CompletePracticeTest.ielts_test_type == current_user.test_preference
        ).group_by(CompletePracticeTest.test_number).subquery()
        
        # Get all tests the user should have access to
        allowed_tests = CompletePracticeTest.query.join(
            subquery,
            db.and_(
                CompletePracticeTest.id == subquery.c.max_id,
                CompletePracticeTest.test_number == subquery.c.test_number
            )
        ).order_by(CompletePracticeTest.test_number).limit(num_tests_allowed).all()
        
        # Check if the requested test is in the allowed tests list
        if complete_test not in allowed_tests:
            flash(f'This test is not available with your current {current_user.assessment_package_status} package.', 'warning')
            return redirect(url_for('practice_index'))
    
    # Ensure the user is on the correct section
    if progress.current_section != section:
        flash(f'Please complete the {progress.current_section} section first.', 'warning')
        return redirect(url_for('continue_complete_test', test_id=test_id))
    
    # Get the section test
    section_test = PracticeTest.query.filter_by(
        complete_test_id=test_id,
        test_type=section,
        ielts_test_type=complete_test.ielts_test_type
    ).first_or_404()
    
    # For all test types, use the empty templates to prevent popup errors
    if section == 'listening':
        return render_template('practice/listening_empty.html',
                              title=f'IELTS {section.capitalize()} Test',
                              test=section_test,
                              taking_test=True,
                              complete_test_id=test_id,
                              test_progress=progress)
    elif section == 'reading':
        return render_template('practice/reading_empty.html',
                              title=f'IELTS {section.capitalize()} Test',
                              test=section_test,
                              taking_test=True,
                              complete_test_id=test_id,
                              test_progress=progress)
    elif section == 'writing':
        return render_template('practice/writing_empty.html',
                              title=f'IELTS {section.capitalize()} Test',
                              test=section_test,
                              taking_test=True,
                              complete_test_id=test_id,
                              test_progress=progress)
    elif section == 'speaking':
        return render_template('practice/speaking_empty.html',
                              title=f'IELTS {section.capitalize()} Test',
                              test=section_test,
                              taking_test=True,
                              complete_test_id=test_id,
                              test_progress=progress)

@app.route('/practice/complete-test/<int:test_id>/results')
@login_required
def complete_test_results(test_id):
    """View results of a completed test"""
    # Get the user's progress for this test
    progress = CompleteTestProgress.query.filter_by(
        user_id=current_user.id,
        complete_test_id=test_id
    ).first_or_404()
    
    # If test is not completed, check if user has access to continue it and redirect to continue
    if not progress.is_test_completed():
        # Verify the user has the appropriate package for this test
        from sqlalchemy import func
        
        # Determine number of tests allowed based on user's assessment package
        num_tests_allowed = 1  # Default for single test package
        if current_user.assessment_package_status == 'Value Pack':
            num_tests_allowed = 4
        elif current_user.assessment_package_status == 'Double Package':
            num_tests_allowed = 2
        
        # Get the complete test
        complete_test = CompletePracticeTest.query.get_or_404(test_id)
        
        # Get the latest version of each test number
        subquery = db.session.query(
            CompletePracticeTest.test_number,
            func.max(CompletePracticeTest.id).label('max_id')
        ).filter(
            CompletePracticeTest.ielts_test_type == current_user.test_preference
        ).group_by(CompletePracticeTest.test_number).subquery()
        
        # Get all tests the user should have access to
        allowed_tests = CompletePracticeTest.query.join(
            subquery,
            db.and_(
                CompletePracticeTest.id == subquery.c.max_id,
                CompletePracticeTest.test_number == subquery.c.test_number
            )
        ).order_by(CompletePracticeTest.test_number).limit(num_tests_allowed).all()
        
        # Check if the requested test is in the allowed tests list
        if complete_test not in allowed_tests:
            flash(f'This incomplete test is not available with your current {current_user.assessment_package_status} package.', 'warning')
            return redirect(url_for('practice_index'))
            
        # If they have access but haven't completed it, send them to continue
        flash('Please complete all sections of the test first.', 'warning')
        return redirect(url_for('continue_complete_test', test_id=test_id))
    
    # For completed tests, always show results regardless of current package
    complete_test = CompletePracticeTest.query.get_or_404(test_id)
    
    # Get all attempts for this test
    section_attempts = []
    for section_type in ['listening', 'reading', 'writing', 'speaking']:
            
        section_test = PracticeTest.query.filter_by(
            complete_test_id=test_id,
            test_type=section_type
        ).first()
        
        if section_test:
            attempt = UserTestAttempt.query.filter_by(
                user_id=current_user.id,
                test_id=section_test.id,
                complete_test_progress_id=progress.id
            ).first()
            
            section_attempts.append({
                'section_type': section_type,
                'test': section_test,
                'attempt': attempt,
                'score': progress.section_progress.get(section_type, {}).get('score', 0) if progress.section_progress else 0
            })
    
    return render_template('practice/complete_test_results.html',
                          title='Test Results',
                          complete_test=complete_test,
                          progress=progress,
                          section_attempts=section_attempts,
                          overall_score=progress.get_overall_score())

@app.route('/api/submit-test', methods=['POST'])
@login_required
def submit_test():
    data = request.json
    test_id = data.get('test_id')
    user_answers = data.get('answers')
    complete_test_id = data.get('complete_test_id')  # May be None for individual section practice
    
    if not test_id or not user_answers:
        return jsonify({'error': 'Missing required data'}), 400
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # Parse answers from JSON string
    import json
    correct_answers = json.loads(test.answers)
    
    # Calculate score
    score = 0
    total_questions = len(correct_answers)
    
    for q_id, user_answer in user_answers.items():
        if q_id in correct_answers and user_answer.lower() == correct_answers[q_id].lower():
            score += 1
    
    score_percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Convert to band score for IELTS (0-9 scale)
    band_score = (score_percentage / 100) * 9
    
    # Get complete test progress if this is part of a complete test
    complete_test_progress = None
    if complete_test_id:
        complete_test_progress = CompleteTestProgress.query.filter_by(
            user_id=current_user.id,
            complete_test_id=complete_test_id
        ).first()
        
        if complete_test_progress:
            # Mark this section as completed
            complete_test_progress.mark_section_completed(test.test_type, band_score)
    
    # Save the attempt
    attempt = UserTestAttempt(
        user_id=current_user.id,
        test_id=test_id,
        complete_test_progress_id=complete_test_progress.id if complete_test_progress else None,
        user_answers=user_answers,
        score=score_percentage
    )
    
    db.session.add(attempt)
    
    # Update user's test history
    test_history = current_user.test_history
    test_history.append({
        'test_id': test_id,
        'test_type': test.test_type,
        'title': test.title,
        'date': datetime.utcnow().isoformat(),
        'score': score_percentage,
        'complete_test_id': complete_test_id
    })
    current_user.test_history = test_history
    
    # For individual section practice (not part of complete test)
    if not complete_test_id:
        # Mark this test as completed so it can't be retaken during current assessment package period
        current_user.mark_test_completed(test_id, test.test_type)
    
    db.session.commit()
    
    response_data = {
        'score': score_percentage,
        'band_score': round(band_score, 1),
        'correct': score,
        'total': total_questions
    }
    
    # Check if complete test is now completed
    if complete_test_progress and complete_test_progress.is_test_completed():
        response_data['complete_test_finished'] = True
        response_data['results_url'] = url_for('complete_test_results', test_id=complete_test_id)
    elif complete_test_progress:
        response_data['next_section'] = complete_test_progress.get_next_section()
        response_data['next_section_url'] = url_for(
            'take_complete_test_section', 
            test_id=complete_test_id, 
            section=complete_test_progress.get_next_section()
        )
    
    return jsonify(response_data)

@app.route('/api/submit-writing', methods=['POST'])
@login_required
def submit_writing():
    data = request.json
    test_id = data.get('test_id')
    essay_text = data.get('essay_text')
    complete_test_id = data.get('complete_test_id')  # May be None for individual section practice
    
    if not test_id or not essay_text:
        return jsonify({'error': 'Missing required data'}), 400
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # Save the user's writing response
    user_answers = {'essay': essay_text}
    
    # Check for OpenAI API key for AI assessment
    if 'OPENAI_API_KEY' in os.environ:
        # Assess the writing using OpenAI
        try:
            # Determine if this is Task 1 or Task 2 based on the test section
            task_number = 1 if test.section == 1 else 2
            
            # Get the task prompt
            task_prompt = test.questions[0]['question'] if test.questions else ''
            
            # Process based on task type
            if task_number == 1:
                evaluation = assess_writing_task1(essay_text, task_prompt, test.ielts_test_type)
            else:
                evaluation = assess_writing_task2(essay_text, task_prompt, test.ielts_test_type)
                
            # For backward compatibility, extract band score
            if "overall_band_for_task" in evaluation:
                evaluation["band_score"] = evaluation["overall_band_for_task"]
            
            # Calculate band score (0-9 scale)
            band_score = evaluation.get('band_score', 0)
            
            # Convert band score to percentage for consistency with other tests (0-100%)
            score_percentage = (band_score / 9) * 100
            
            # Add feedback to user_answers
            user_answers['assessment'] = evaluation
        except Exception as e:
            app.logger.error(f"Error in OpenAI writing assessment: {str(e)}")
            score_percentage = 0  # Default if assessment fails
            band_score = 0
            user_answers['assessment_error'] = str(e)
    else:
        # No OpenAI API key, use placeholder score
        score_percentage = 70  # Default score
        band_score = 6.0
        user_answers['assessment'] = {
            'band_score': band_score,
            'feedback': 'AI assessment not available. Please contact support.'
        }
    
    # Get complete test progress if this is part of a complete test
    complete_test_progress = None
    if complete_test_id:
        complete_test_progress = CompleteTestProgress.query.filter_by(
            user_id=current_user.id,
            complete_test_id=complete_test_id
        ).first()
        
        if complete_test_progress:
            # Mark this section as completed
            complete_test_progress.mark_section_completed(test.test_type, band_score)
    
    # Save the attempt
    attempt = UserTestAttempt(
        user_id=current_user.id,
        test_id=test_id,
        complete_test_progress_id=complete_test_progress.id if complete_test_progress else None,
        user_answers=user_answers,
        score=score_percentage,
        assessment=json.dumps(user_answers.get('assessment', {}))
    )
    
    db.session.add(attempt)
    
    # Update user's test history
    test_history = current_user.test_history
    test_history.append({
        'test_id': test_id,
        'test_type': test.test_type,
        'title': test.title,
        'date': datetime.utcnow().isoformat(),
        'score': score_percentage,
        'complete_test_id': complete_test_id
    })
    current_user.test_history = test_history
    
    # For individual section practice (not part of complete test)
    if not complete_test_id:
        # Mark this test as completed so it can't be retaken during current assessment package period
        current_user.mark_test_completed(test_id, test.test_type)
    
    db.session.commit()
    
    response_data = {
        'score': score_percentage,
        'band_score': band_score,
        'assessment': user_answers.get('assessment', {})
    }
    
    # Check if complete test is now completed
    if complete_test_progress and complete_test_progress.is_test_completed():
        response_data['complete_test_finished'] = True
        response_data['results_url'] = url_for('complete_test_results', test_id=complete_test_id)
    elif complete_test_progress:
        response_data['next_section'] = complete_test_progress.get_next_section()
        response_data['next_section_url'] = url_for(
            'take_complete_test_section', 
            test_id=complete_test_id, 
            section=complete_test_progress.get_next_section()
        )
    
    return jsonify(response_data)

# Speaking routes
@app.route('/api/submit-speaking-response', methods=['POST'])
@login_required
def submit_speaking_response(test_id=None):
    """Submit a speaking response for a complete test section"""
    audio_blob = request.form.get('audio_blob')
    complete_test_id = request.form.get('complete_test_id')
    
    if not audio_blob:
        flash('No audio recording was provided.', 'danger')
        if complete_test_id:
            return redirect(url_for('take_complete_test_section', 
                                   test_id=complete_test_id, 
                                   section='speaking'))
        return redirect(url_for('practice_index'))
    
    # Process the audio file from the blob data
    import base64
    audio_data = base64.b64decode(audio_blob.split(',')[1])
    
    # Save the audio file
    filename = f"user_{current_user.id}_test_{test_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.mp3"
    audio_path = os.path.join('static', 'uploads', 'audio', filename)
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    with open(audio_path, 'wb') as f:
        f.save(audio_data)
    
    # Compress the audio file
    compressed_path = compress_audio(audio_path)
    
    # Get the test
    test = PracticeTest.query.get_or_404(test_id)
    
    # Transcribe using AWS Transcribe
    transcription = None
    try:
        transcription = transcribe_audio(compressed_path)
    except Exception as e:
        app.logger.error(f"Error transcribing audio: {str(e)}")
        transcription = "Transcription failed. Please try again."
    
    # Analyze the speaking response
    assessment = {}
    band_score = 0
    try:
        assessment, feedback = analyze_speaking_response(transcription)
        band_score = assessment.get('overall_band', 0)
    except Exception as e:
        app.logger.error(f"Error analyzing speaking response: {str(e)}")
        assessment = {"error": str(e)}
        band_score = 5.0  # Default band score
    
    # Convert band score to percentage for consistency
    score_percentage = (band_score / 9) * 100
    
    # Get complete test progress if this is part of a complete test
    complete_test_progress = None
    if complete_test_id:
        complete_test_progress = CompleteTestProgress.query.filter_by(
            user_id=current_user.id,
            complete_test_id=complete_test_id
        ).first()
        
        if complete_test_progress:
            # Mark this section as completed
            complete_test_progress.mark_section_completed('speaking', band_score)
    
    # Save the user's response
    user_answers = {
        'audio_url': url_for('static', filename=f'uploads/audio/{filename}'),
        'transcription': transcription,
        'assessment': assessment
    }
    
    # Save the attempt
    attempt = UserTestAttempt(
        user_id=current_user.id,
        test_id=test_id,
        complete_test_progress_id=complete_test_progress.id if complete_test_progress else None,
        user_answers=user_answers,
        score=score_percentage,
        assessment=json.dumps(assessment)
    )
    
    db.session.add(attempt)
    
    # Update the user's speaking scores
    speaking_scores = current_user.speaking_scores
    speaking_scores.append({
        'date': datetime.utcnow().isoformat(),
        'band_score': band_score,
        'fluency': assessment.get('fluency', 0),
        'pronunciation': assessment.get('pronunciation', 0),
        'grammar': assessment.get('grammar', 0),
        'vocabulary': assessment.get('vocabulary', 0)
    })
    current_user.speaking_scores = speaking_scores
    
    # Update test history
    test_history = current_user.test_history
    test_history.append({
        'test_id': test_id,
        'test_type': 'speaking',
        'title': test.title,
        'date': datetime.utcnow().isoformat(),
        'score': score_percentage,
        'complete_test_id': complete_test_id
    })
    current_user.test_history = test_history
    
    # For individual section practice (not part of complete test)
    if not complete_test_id:
        # Mark this test as completed so it can't be retaken during current assessment package period
        current_user.mark_test_completed(test_id, 'speaking')
    
    db.session.commit()
    
    response_data = {
        'score': score_percentage,
        'band_score': band_score,
        'transcription': transcription,
        'assessment': assessment
    }
    
    # Check if complete test is now completed
    if complete_test_progress and complete_test_progress.is_test_completed():
        response_data['complete_test_finished'] = True
        response_data['results_url'] = url_for('complete_test_results', test_id=complete_test_id)
    
    return jsonify(response_data)

# This route has been replaced by assessment-specific routes in speaking_assessment_routes.py
# Keeping as a commented reference for backward compatibility
"""
@app.route('/api/submit-speaking', methods=['POST'])
@login_required
def submit_speaking():
    # This route has been deprecated as part of the move to assessment-based system
    # All speaking functionality is now handled through the AssessmentSpeakingResponse model
    # and related routes in speaking_assessment_routes.py
    return jsonify({'error': 'This API endpoint has been deprecated'}), 410
"""

# @login_required
# def speaking_assessment(prompt_id):
#     """Get a speaking assessment for a specific prompt."""
#     prompt = SpeakingPrompt.query.get_or_404(prompt_id)
#     
#     # Get previous responses for this prompt by this user
#     previous_responses = SpeakingResponse.query.filter_by(
#         user_id=current_user.id,
#         prompt_id=prompt_id
#     ).order_by(SpeakingResponse.response_date.desc()).all()
#     
#     return render_template('speaking_assessment.html',
#                           title='Speaking Assessment',
#                           prompt=prompt,
#                           previous_responses=previous_responses)

@app.route('/purchase-assessment')
def purchase_assessment_package():
    """Redirect to assessment products page for purchasing assessment packages"""
    return redirect(url_for('assessment_products_page'))

@app.route('/checkout-review', methods=['POST'])
def checkout_review():
    """Review page before finalizing payment"""
    # Handle both form data and JSON requests
    try:
        if request.is_json:
            data = request.json
        else:
            data = request.form
        
        plan = data.get('plan')
        test_type = data.get('test_type', 'academic')
        test_package = data.get('test_package')
        
        # Check if we're using new plan format
        if plan == 'purchase' and test_type and test_package:
            # For assessment package format
            package = test_package
        else:
            # For old format
            package = data.get('package')
            if not package and test_package:
                package = test_package
        
        # Validate required fields
        if not package:
            if request.is_json:
                return jsonify({'error': 'No package selected'}), 400
            else:
                flash('No package selected', 'danger')
                return redirect(url_for('assessment_products_page'))
        
        # Free test doesn't need payment
        if package == 'free':
            if request.is_json:
                return jsonify({'url': url_for('practice_index')}), 200
            else:
                return redirect(url_for('practice_index'))
        
        # Package pricing and details
        package_details = {
            'single': {
                'name': f'IELTS {test_type.capitalize()} - Single Test Package',
                'description': f'1 IELTS {test_type.capitalize()} Practice Test with AI Assessment (15-day access)',
                'price': 2500,  # in cents
                'discount': 0,  # No discount by default
                'tests': 1,
                'days': 15
            },
            'double': {
                'name': f'IELTS {test_type.capitalize()} - Double Test Package',
                'description': f'2 IELTS {test_type.capitalize()} Practice Tests with AI Assessment (15-day access)',
                'price': 3500,  # in cents
                'discount': 0,  # No discount by default
                'tests': 2,
                'days': 15
            },
            'pack': {
                'name': f'IELTS {test_type.capitalize()} - Value Pack',
                'description': f'4 IELTS {test_type.capitalize()} Practice Tests with AI Assessment (30-day access)',
                'price': 5000,  # in cents
                'discount': 0,  # No discount by default
                'tests': 4,
                'days': 30
            }
        }
        
        if package not in package_details:
            if request.is_json:
                return jsonify({'error': 'Invalid package selected'}), 400
            else:
                flash('Invalid package selected', 'danger')
                return redirect(url_for('assessment_products_page'))
        
        # Format the test type for display (academic -> Academic, general -> General Training)
        if test_type.lower() == 'general':
            test_type_formatted = 'General Training'
        else:
            test_type_formatted = test_type.capitalize()
        
        # Store package data in session
        session['checkout_package'] = package
        session['checkout_test_type'] = test_type
        
        # Get Stripe publishable key from environment
        stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        
        if not stripe_publishable_key:
            logging.error("STRIPE_PUBLISHABLE_KEY not found in environment variables")
            flash('Payment service is currently unavailable. Please try again later.', 'danger')
            return redirect(url_for('assessment_products_page'))
        
        # Render the checkout review page
        return render_template('checkout_review.html',
                              title='Review Your Purchase',
                              stripe_publishable_key=stripe_publishable_key,
                              plan=plan or 'purchase',
                              test_type=test_type,
                              test_type_formatted=test_type_formatted,
                              test_package=package,
                              package_name=package_details[package]['name'],
                              description=package_details[package]['description'],
                              price=package_details[package]['price'],
                              discount=package_details[package]['discount'],
                              tests=package_details[package]['tests'],
                              days=package_details[package]['days'])
    except Exception as e:
        logging.error(f"Error in checkout_review: {str(e)}")
        flash('An error occurred while processing your request. Please try again later.', 'danger')
        return redirect(url_for('assessment_products_page'))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    # Handle both form data and JSON requests
    if request.is_json:
        data = request.json
        plan = data.get('plan')
        test_type = data.get('test_type')
        test_package = data.get('test_package')
        package = data.get('package')
    else:
        data = request.form
        plan = data.get('plan')
        test_type = data.get('test_type')
        test_package = data.get('test_package')
        package = data.get('package')
    
    # Check if we're using new plan format
    if plan == 'purchase' and test_type and test_package:
        # For assessment package format
        package = test_package
        test_preference = test_type
    else:
        # For old format
        test_preference = data.get('test_preference', 'academic')
    
    # Validate required fields
    if not package and not test_package:
        if request.is_json:
            return jsonify({'error': 'No package selected'}), 400
        else:
            flash('No package selected', 'danger')
            return redirect(url_for('assessment_products_page'))
    
    # Free test doesn't need payment
    if package == 'free':
        if request.is_json:
            return jsonify({'url': url_for('practice_index')}), 200
        else:
            return redirect(url_for('practice_index'))
    
    # Check if user already has a Value Pack (cannot purchase additional packages)
    if current_user.is_authenticated and current_user.assessment_package_status == 'Value Pack' and current_user.has_active_assessment_package():
        error_message = 'You already have an active Value Pack assessment package. You cannot purchase additional test packages while your Value Pack is active.'
        if request.is_json:
            return jsonify({'error': error_message}), 400
        else:
            flash(error_message, 'info')
            return redirect(url_for('assessment_products_page'))
    
    # Create a Stripe checkout session
    success_url = url_for('payment_success', package=package, test_preference=test_preference, _external=True)
    cancel_url = url_for('payment_cancel', _external=True)
    
    # Package pricing and details
    package_details = {
        'single': {
            'name': f'IELTS {test_preference.capitalize()} - Single Test Package',
            'description': f'1 IELTS {test_preference.capitalize()} Practice Test with AI Assessment (15-day access)',
            'price': 25.00,  # in USD
            'duration_days': 15
        },
        'double': {
            'name': f'IELTS {test_preference.capitalize()} - Double Test Package',
            'description': f'2 IELTS {test_preference.capitalize()} Practice Tests with AI Assessment (15-day access)',
            'price': 35.00,  # in USD
            'duration_days': 15
        },
        'pack': {
            'name': f'IELTS {test_preference.capitalize()} - Value Pack',
            'description': f'4 IELTS {test_preference.capitalize()} Practice Tests with AI Assessment (30-day access)',
            'price': 50.00,  # in USD
            'duration_days': 30
        }
    }
    
    if package not in package_details:
        if request.is_json:
            return jsonify({'error': 'Invalid package selected'}), 400
        else:
            flash('Invalid package selected', 'danger')
            return redirect(url_for('assessment_products_page'))
    
    # Create Stripe checkout session
    try:
        checkout_session = create_stripe_checkout_session(
            package_details[package]['name'],
            package_details[package]['description'],
            package_details[package]['price'],
            success_url,
            cancel_url
        )
        
        # Store session_id for later verification
        if current_user.is_authenticated:
            # Save in session for authenticated users
            session['checkout_session_id'] = checkout_session.id
            session['checkout_package'] = package
            session['checkout_test_preference'] = test_preference
        else:
            # For non-logged in users, include in success URL
            success_url = f"{success_url}?session_id={checkout_session.id}"
        
        # Return appropriate response based on request type
        if request.is_json:
            return jsonify({'url': checkout_session.url})
        else:
            return redirect(checkout_session.url)
    
    except Exception as e:
        app.logger.error(f"Error creating checkout session: {str(e)}")
        # Check for common Stripe errors and provide user-friendly messages
        error_message = str(e)
        if "RetryError" in error_message or "InvalidRequestError" in error_message:
            error_message = "There was an issue processing your payment request. Please try again later or contact support if the problem persists."
        
        if request.is_json:
            return jsonify({'error': error_message}), 500
        else:
            flash(error_message, 'danger')
            return redirect(url_for('assessment_products_page'))

@app.route('/stripe-checkout', methods=['POST'])
def stripe_checkout():
    """Alternative route for payment that uses server-side redirect"""
    package = request.form.get('package')
    test_preference = request.form.get('test_preference', 'academic')
    
    if not package or package == 'free':
        return redirect(url_for('practice_index'))
    
    # Create a Stripe checkout session
    success_url = url_for('payment_success', package=package, test_preference=test_preference, _external=True)
    cancel_url = url_for('payment_cancel', _external=True)
    
    # Package pricing and details
    package_details = {
        'single': {
            'name': 'Single Test Package',
            'description': '1 IELTS Practice Test with AI Assessment (15-day access)',
            'price': 25.00,  # in USD
            'duration_days': 15
        },
        'double': {
            'name': 'Double Test Package',
            'description': '2 IELTS Practice Tests with AI Assessment (15-day access)',
            'price': 35.00,  # in USD
            'duration_days': 15
        },
        'pack': {
            'name': 'Value Pack',
            'description': '4 IELTS Practice Tests with AI Assessment (30-day access)',
            'price': 50.00,  # in USD
            'duration_days': 30
        }
    }
    
    if package not in package_details:
        flash('Invalid package selected.', 'danger')
        return redirect(url_for('assessment_products_page'))
    
    # Create Stripe checkout session
    try:
        checkout_session = create_stripe_checkout_session(
            package_details[package]['name'],
            package_details[package]['description'],
            package_details[package]['price'],
            success_url,
            cancel_url
        )
        
        # Store session_id for later verification
        if current_user.is_authenticated:
            # Save in session for authenticated users
            session['checkout_session_id'] = checkout_session.id
            session['checkout_package'] = package
            session['checkout_test_preference'] = test_preference
        
        # Redirect to Stripe
        return redirect(checkout_session.url)
    
    except Exception as e:
        app.logger.error(f"Error creating checkout session: {str(e)}")
        flash(f'Payment error: {str(e)}', 'danger')
        return redirect(url_for('assessment_products_page'))

@app.route('/payment-success')
def payment_success():
    """Handle successful payments from Stripe"""
    session_id = request.args.get('session_id') or session.get('checkout_session_id')
    package = request.args.get('package')
    test_preference = request.args.get('test_preference', 'academic')
    
    # Check if this is a cart checkout
    is_cart_checkout = 'checkout' in session and session['checkout'].get('product_ids')
    
    # For cart checkout, get the test preference from cart contents
    if is_cart_checkout:
        from cart import determine_test_preference
        product_ids = session['checkout'].get('product_ids', [])
        cart_preference = determine_test_preference(product_ids)
        if cart_preference:
            test_preference = cart_preference
    
    # Package details
    package_details = {
        'single': {'name': 'Single Test', 'price': 25.00},
        'double': {'name': 'Double Package', 'price': 35.00},
        'pack': {'name': 'Value Pack', 'price': 50.00}
    }
    
    # For regular package checkout, validate package
    if not is_cart_checkout and package not in package_details:
        flash('Invalid package selected.', 'danger')
        return redirect(url_for('assessment_products_page'))
    
    # Redirect if user is not authenticated
    if not current_user.is_authenticated:
        session['pending_payment'] = {
            'session_id': session_id,
            'package': package,
            'test_preference': test_preference
        }
        flash('Please log in or register to complete your purchase.', 'info')
        return redirect(url_for('login'))
    
    # Process cart checkout
    if is_cart_checkout and session.get('checkout', {}).get('product_ids') and not session.get('checkout', {}).get('processed', False):
        try:
            # Import here to avoid circular imports
            from add_assessment_routes import handle_assessment_product_payment
            
            # Process each product in the cart
            product_ids = session['checkout']['product_ids']
            for product_id in product_ids:
                handle_assessment_product_payment(current_user, product_id)
                app.logger.info(f"Processed cart product: {product_id} for user {current_user.id}")
            
            # Mark checkout as processed
            session['checkout']['processed'] = True
            
            # Clear the cart after successful checkout
            from cart import clear_cart
            clear_cart()
            
            flash('Your assessment products have been added to your account.', 'success')
        except Exception as e:
            app.logger.error(f"Error processing cart checkout: {str(e)}")
            flash('Error processing your purchase. Please contact support.', 'danger')
    
    # Clean up session variables
    for key in ['checkout_session_id', 'checkout_package', 'checkout_test_preference', 
                'pending_payment', 'checkout']:
        if key in session:
            session.pop(key, None)
    
    # Return success page
    return render_template('payment_success.html',
                          title='Payment Successful',
                          user=current_user)

@app.route('/payment-cancel')
def payment_cancel():
    """Handle cancelled Stripe checkout sessions"""
    flash('Payment was cancelled. Your purchase has not been processed.', 'info')
    
    # Clean up session variables
    if 'checkout_session_id' in session:
        session.pop('checkout_session_id')
    if 'checkout_package' in session:
        session.pop('checkout_package')
    if 'checkout_test_preference' in session:
        session.pop('checkout_test_preference')
    if 'checkout' in session:
        session.pop('checkout')
    
    # Clean up registration data if payment was cancelled during registration flow
    if 'registration_data' in session:
        app.logger.info(f"Cleaning up registration data for cancelled payment: {session['registration_data'].get('email')}")
        session.pop('registration_data')
        flash('Registration process has been cancelled. Please try again when you are ready to complete your purchase.', 'info')
    
    # Check if this was a cart checkout
    if 'cart' in session and session['cart']:
        return redirect(url_for('cart.view_cart'))
    else:
        return redirect(url_for('assessment_products_page'))

@app.route('/device-specs')
def device_specs():
    """Display device specifications and test capabilities"""
    return render_template('device_specs.html', title='Device Specifications')

@app.route('/terms-and-payment')
def terms_and_payment():
    """Show terms and payment information"""
    return render_template('terms_and_payment.html', title='Terms and Payment')
    
@app.route('/privacy')
def privacy_policy():
    """Show privacy policy information"""
    return render_template('privacy.html', title='Privacy Policy')

@app.route('/address-usage-policy')
def address_usage_policy():
    """Show address usage policy information"""
    return render_template('gdpr/address_usage_policy.html', title='Address Usage Policy')

@app.route('/api/sync-data', methods=['POST'])
@login_required
def sync_data():
    """Synchronize user data for mobile apps"""
    # Get the user's data
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'assessment_package_status': current_user.assessment_package_status,
        'assessment_package_expiry': current_user.assessment_package_expiry.isoformat() if current_user.assessment_package_expiry else None,
        'test_preference': current_user.test_preference,
        'test_history': current_user.test_history,
        'speaking_scores': current_user.speaking_scores,
    }
    
    return jsonify(user_data)

# Audio file serving route to avoid embedded page issues
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """
    Serve audio files as a direct download to avoid Replit embedded page issues.
    This route handles both static/audio/ and static/uploads/audio/ directories.
    """
    app.logger.info(f"Serving audio file: {filename}")
    
    # Sanitize filename to prevent directory traversal attacks
    filename = os.path.basename(filename)
    
    # Search for the file in possible locations
    possible_paths = [
        os.path.join("static", "audio", filename),
        os.path.join("static", "uploads", "audio", filename)
    ]
    
    for path in possible_paths:
        try:
            if os.path.isfile(path) and os.access(path, os.R_OK):
                app.logger.info(f"Found audio file at: {path}")
                
                # Force download to avoid Replit embedded page detection
                return send_file(
                    path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='audio/mpeg'
                )
                
        except Exception as e:
            app.logger.error(f"Error serving audio from {path}: {str(e)}")
    
    # If we get here, the file wasn't found
    app.logger.warning(f"Audio file not found: {filename}")
    abort(404)

# Error handlers

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', title='Page Not Found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', title='Server Error'), 500

# Database initialization command
@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    app.logger.info('Initialized the database.')
