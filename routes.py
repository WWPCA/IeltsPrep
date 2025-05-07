import os
import json
import time
import uuid
import base64
import urllib
import logging
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session, abort, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import app, db
from models import User, TestStructure, PracticeTest, UserTestAttempt, SpeakingPrompt, SpeakingResponse, CompletePracticeTest, CompleteTestProgress, UserTestAssignment
from utils import get_user_region, get_translation, compress_audio
from payment_services import create_stripe_checkout_session, create_payment_record, verify_stripe_payment, create_stripe_checkout_speaking
import test_assignment_service
from openai_writing_assessment import assess_writing_task1, assess_writing_task2, assess_complete_writing_test
from aws_services import analyze_speaking_response, analyze_pronunciation, transcribe_audio, generate_polly_speech
from geoip_services import get_country_from_ip, get_pricing_for_country

# Import the test details route
try:
    from add_test_details_route import test_details_route
except ImportError:
    # Define it directly if the import fails
    def test_details_route(test_type, test_id):
        """Show details about a test before starting it"""
        if test_type not in ['listening', 'reading', 'writing', 'speaking']:
            abort(404)
        
        test = PracticeTest.query.get_or_404(test_id)
        
        # All tests require subscription
        if not current_user.is_subscribed():
            flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
            return redirect(url_for('assessment_products_page'))
        
        # Check if user has already taken this test during current subscription period
        if current_user.has_taken_test(test_id, test_type):
            flash('You have already taken this test during your current subscription period. Each test can only be taken once per subscription.', 'warning')
            return redirect(url_for('practice_test_list', test_type=test_type))
        
        return render_template('practice/test_details.html', 
                              title=f'IELTS {test_type.capitalize()} Practice',
                              test=test,
                              test_type=test_type)

# Add the test details route
app.add_url_rule('/practice/<test_type>/<int:test_id>/details', 
                 'test_details', 
                 test_details_route, 
                 methods=['GET'])

# Custom cache buster to force browsers to reload CSS, JS on new deployments
@app.context_processor
def inject_cache_buster():
    """Add cache_buster variable to all templates to prevent browser caching"""
    cache_buster = int(time.time())
    return dict(cache_buster=cache_buster)

def subscription_required(f):
    """Decorator to check if user has an active subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('login'))
            
        if not current_user.is_subscribed():
            flash('This feature requires a subscription. Please subscribe to access all features.', 'warning')
            return redirect(url_for('assessment_products_page'))
            
        return f(*args, **kwargs)
    return decorated_function

# Streak tracking removed as requested

# Home route
@app.route('/')
def index():
    return render_template('index.html', title='IELTS AI Prep')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html', title='Login')
            
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    class RegistrationForm:
        # Simple form class to enable CSRF protection
        def __init__(self):
            pass

    form = RegistrationForm()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        region = request.form.get('region', get_user_region())
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html', title='Register', form=form)
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return render_template('register.html', title='Register', form=form)
        
        test_preference = request.form.get('test_preference', 'academic')
        
        new_user = User(
            username=username,
            email=email,
            region=region,
            test_preference=test_preference
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

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
            
        # Check password length
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
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
            
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # For simplicity and security, we'll just show a success message
            # In a production app, you'd generate a token and send a reset email
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
            # TODO: Implement email sending functionality with reset token
        else:
            # Same message for security (don't reveal if email exists)
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
            
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # For simplicity and security, we'll just show a success message
            # In a production app, you'd send an email with the username
            flash('If an account exists with that email, your username has been sent.', 'info')
            # TODO: Implement email sending functionality
        else:
            # Same message for security (don't reveal if email exists)
            flash('If an account exists with that email, your username has been sent.', 'info')
            
        return redirect(url_for('login'))
        
    return render_template('forgot_username.html', title='Forgot Username')

# Test Structure Routes
@app.route('/test-structure')
def test_structure():
    return render_template('test_structure/index.html', title='IELTS Test Structure')

@app.route('/test-structure/<test_type>')
def test_structure_detail(test_type):
    test_info = TestStructure.query.filter_by(test_type=test_type).first_or_404()
    return render_template(f'test_structure/{test_type}.html', 
                          title=f'IELTS {test_type.replace("_", " ").title()}',
                          test_info=test_info)

@app.route('/test-day')
@login_required
def test_day():
    # Check if user has purchased a value pack (4 tests package)
    if not current_user.is_authenticated:
        flash('Please log in to access the Test Day Guide.', 'warning')
        return redirect(url_for('login'))
    
    # Check if user has Value Pack subscription
    if current_user.subscription_status != 'Value Pack':
        flash('The Test Day Guide is only available with the Value Pack (4 tests) subscription.', 'warning')
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
        user_test_preference = current_user.test_preference
        
        # Use the test assignment service to get the tests the user has access to
        if current_user.is_subscribed():
            # First check if user has any assigned tests
            assigned_tests = test_assignment_service.get_user_accessible_tests(
                user_id=current_user.id,
                test_type=user_test_preference
            )
            
            if assigned_tests:
                # User has assigned tests from the new system
                complete_tests = assigned_tests
            else:
                # Fallback to the old system for users with legacy subscriptions
                # Determine number of tests to show based on user's subscription
                num_tests_to_show = 1  # Default for single test package
                
                if current_user.subscription_status == 'Value Pack':
                    num_tests_to_show = 4
                elif current_user.subscription_status == 'Double Package':
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
                
                # Limit the number of tests based on subscription
                complete_tests = all_tests[:num_tests_to_show]
        else:
            # For non-subscribers, only show free tests (also avoid duplicates)
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
    
    # Determine how many tests to show based on subscription
    if current_user.is_subscribed():
        # Determine number of tests to show based on user's subscription
        num_tests_to_show = 1  # Default for single test package
            
        if current_user.subscription_status == 'Value Pack':
            num_tests_to_show = 4
        elif current_user.subscription_status == 'Double Package':
            num_tests_to_show = 2
            
        # Limit tests based on subscription level
        tests = tests[:num_tests_to_show] if tests else []
    else:
        # For non-subscribers, only show the first test
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
    elif not current_user.is_subscribed():
        # Regular subscription check for other test types
        flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already taken this test during current subscription period
    if current_user.has_taken_test(test_id, test_type):
        flash('You have already taken this test during your current subscription period. Each test can only be taken once per subscription.', 'warning')
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
        
    elif not current_user.is_subscribed():
        # Regular subscription check for other test types
        flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already taken this test during current subscription period
    if current_user.has_taken_test(test_id, test_type):
        flash('You have already taken this test during your current subscription period. Each test can only be taken once per subscription.', 'warning')
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
        flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Verify that this test should be accessible based on the user's package
    # Get all tests for this user's preference
    from sqlalchemy import func
    
    # Determine number of tests to show based on user's subscription
    num_tests_to_show = 1  # Default for single test package
    if current_user.subscription_status == 'Value Pack':
        num_tests_to_show = 4
    elif current_user.subscription_status == 'Double Package':
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
        flash(f'This test is not available with your current {current_user.subscription_status} package.', 'warning')
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
        
        # Determine number of tests allowed based on user's subscription
        num_tests_allowed = 1  # Default for single test package
        if current_user.subscription_status == 'Value Pack':
            num_tests_allowed = 4
        elif current_user.subscription_status == 'Double Package':
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
            flash(f'This test is not available with your current {current_user.subscription_status} package.', 'warning')
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
        
        # Determine number of tests allowed based on user's subscription
        num_tests_allowed = 1  # Default for single test package
        if current_user.subscription_status == 'Value Pack':
            num_tests_allowed = 4
        elif current_user.subscription_status == 'Double Package':
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
            flash(f'This test is not available with your current {current_user.subscription_status} package.', 'warning')
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
        
        # Determine number of tests allowed based on user's subscription
        num_tests_allowed = 1  # Default for single test package
        if current_user.subscription_status == 'Value Pack':
            num_tests_allowed = 4
        elif current_user.subscription_status == 'Double Package':
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
            flash(f'This incomplete test is not available with your current {current_user.subscription_status} package.', 'warning')
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
        # Mark this test as completed so it can't be retaken during current subscription period
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
        # Mark this test as completed so it can't be retaken during current subscription period
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
        # Mark this test as completed so it can't be retaken during current subscription period
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

@app.route('/api/submit-speaking', methods=['POST'])
@login_required
def submit_speaking():
    prompt_id = request.form.get('prompt_id')
    audio_file = request.files.get('audio')
    
    if not prompt_id or not audio_file:
        return jsonify({'error': 'Missing required data'}), 400
    
    # Process the audio file
    filename = f"user_{current_user.id}_prompt_{prompt_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.mp3"
    audio_path = os.path.join('static', 'uploads', 'audio', filename)
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    # Save and compress the audio
    audio_file.save(audio_path)
    compressed_path = compress_audio(audio_path)
    
    # Transcribe using AWS Transcribe
    try:
        transcription = transcribe_audio(compressed_path)
        
        # Get the prompt
        prompt = SpeakingPrompt.query.get_or_404(prompt_id)
        
        # Analyze the transcription against IELTS speaking criteria
        scores, feedback = analyze_speaking_response(transcription)
        
        # Create a new speaking response
        response = SpeakingResponse(
            user_id=current_user.id,
            prompt_id=prompt_id,
            audio_url=url_for('static', filename=f'uploads/audio/{filename}'),
            transcription=transcription,
            scores=scores  # Stored as JSON
        )
        
        db.session.add(response)
        
        # Update the user's speaking scores
        speaking_scores = current_user.speaking_scores
        speaking_scores.append({
            'date': datetime.utcnow().isoformat(),
            'prompt_id': prompt_id,
            'band_score': scores.get('overall_band', 0),
            'fluency': scores.get('fluency', 0),
            'pronunciation': scores.get('pronunciation', 0),
            'grammar': scores.get('grammar', 0),
            'vocabulary': scores.get('vocabulary', 0)
        })
        current_user.speaking_scores = speaking_scores
        
        # Generate audio feedback using Polly
        try:
            feedback_filename = f"feedback_user_{current_user.id}_prompt_{prompt_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.mp3"
            feedback_path = os.path.join('static', 'uploads', 'audio', feedback_filename)
            generate_polly_speech(feedback, feedback_path)
            response.feedback_audio_url = url_for('static', filename=f'uploads/audio/{feedback_filename}')
        except Exception as e:
            app.logger.error(f"Error generating feedback audio: {str(e)}")
            
        db.session.commit()
        
        # Return the assessment results
        result = {
            'success': True,
            'transcription': transcription,
            'scores': scores,
            'audio_url': response.audio_url,
            'feedback_audio_url': response.feedback_audio_url if hasattr(response, 'feedback_audio_url') else None,
            'feedback': feedback
        }
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error in speaking submission: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/subscribe')
def subscribe():
    """Redirect to assessment products page since we now use one-time purchases instead of subscriptions"""
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
            # For new subscription format
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
        # For new subscription format
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
    if current_user.is_authenticated and current_user.subscription_status == 'Value Pack' and current_user.is_subscribed():
        error_message = 'You already have an active Value Pack subscription. You cannot purchase additional test packages while your Value Pack is active.'
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
    package = request.args.get('package')
    test_preference = request.args.get('test_preference', 'academic')
    session_id = request.args.get('session_id') or session.get('checkout_session_id')
    
    if not current_user.is_authenticated:
        # Store details in session and redirect to login
        session['pending_payment'] = {
            'session_id': session_id,
            'package': package,
            'test_preference': test_preference
        }
        flash('Please log in or register to complete your purchase.', 'info')
        return redirect(url_for('login'))
    
    # Package duration and details
    package_details = {
        'single': {'days': 15, 'tests': 1, 'name': 'Single Test'},
        'double': {'days': 15, 'tests': 2, 'name': 'Double Package'},
        'pack': {'days': 30, 'tests': 4, 'name': 'Value Pack'}
    }
    
    # Verify the session_id with Stripe if available
    if session_id:
        try:
            # Verify payment with Stripe
            payment_verified = verify_stripe_payment(session_id)
            
            if not payment_verified:
                flash('Payment verification failed. Please contact support.', 'danger')
                return redirect(url_for('assessment_products_page'))
                
            # Create a payment record
            payment_record = create_payment_record(
                user_id=current_user.id,
                amount=package_details[package].get('price', 0),
                package=package,
                session_id=session_id
            )
            
        except Exception as e:
            app.logger.error(f"Error verifying payment: {str(e)}")
            flash('Error processing payment. Please contact support.', 'danger')
            return redirect(url_for('assessment_products_page'))
    
    # Update user's subscription
    if package in package_details:
        # Calculate expiry date
        subscription_days = package_details[package]['days']
        expiry_date = datetime.utcnow() + timedelta(days=subscription_days)
        
        # Update user's subscription status
        current_user.subscription_status = package_details[package]['name']
        current_user.subscription_expiry = expiry_date
        current_user.test_preference = test_preference
        
        # Add to user's test history
        test_history = current_user.test_history
        test_history.append({
            'date': datetime.utcnow().isoformat(),
            'action': 'subscription',
            'test_purchase': {
                'package': package,
                'test_preference': test_preference,
                'num_tests': package_details[package]['tests'],
                'purchase_date': datetime.utcnow().isoformat(),
                'expiry_date': expiry_date.isoformat()
            }
        })
        current_user.test_history = test_history
        
        # Assign unique tests to the user using our test assignment service
        num_tests = package_details[package]['tests']
        try:
            # Assign tests from the repository
            assigned_numbers, success = test_assignment_service.assign_tests_to_user(
                user_id=current_user.id,
                test_type=test_preference,  # academic or general
                num_tests=num_tests,
                subscription_days=subscription_days
            )
            
            if success:
                app.logger.info(f"Successfully assigned {len(assigned_numbers)} tests to user {current_user.id}")
                
                # Add the assigned test numbers to the test history
                test_history[-1]['test_purchase']['assigned_tests'] = assigned_numbers
                current_user.test_history = test_history
            else:
                app.logger.warning(f"Could not assign {num_tests} unique tests to user {current_user.id}")
                flash('Warning: You have already been assigned all available tests. Some tests may be repeats.', 'warning')
        except Exception as e:
            app.logger.error(f"Error assigning tests: {str(e)}")
            # Continue with subscription, even if test assignment fails
        
        db.session.commit()
        
        flash(f'Thank you for your purchase! Your {package_details[package]["name"]} is now active.', 'success')
    else:
        flash('Invalid package selected.', 'danger')
    
    # Clean up session variables
    if 'checkout_session_id' in session:
        session.pop('checkout_session_id')
    if 'checkout_package' in session:
        session.pop('checkout_package')
    if 'checkout_test_preference' in session:
        session.pop('checkout_test_preference')
    if 'pending_payment' in session:
        session.pop('pending_payment')
    
    return render_template('payment_success.html', 
                          title='Payment Successful',
                          package=package,
                          package_details=package_details.get(package, {}),
                          test_preference=test_preference)

@app.route('/payment-cancel')
def payment_cancel():
    """Handle cancelled Stripe checkout sessions"""
    flash('Payment was cancelled. Your subscription has not been processed.', 'info')
    
    # Clean up session variables
    if 'checkout_session_id' in session:
        session.pop('checkout_session_id')
    if 'checkout_package' in session:
        session.pop('checkout_package')
    if 'checkout_test_preference' in session:
        session.pop('checkout_test_preference')
    
    return redirect(url_for('assessment_products_page'))

@app.route('/device-specs')
def device_specs():
    """Display device specifications and test capabilities"""
    return render_template('device_specs.html', title='Device Specifications')

@app.route('/terms-and-payment')
def terms_and_payment():
    """Show terms and payment information"""
    return render_template('terms_and_payment.html', title='Terms and Payment')

@app.route('/api/sync-data', methods=['POST'])
@login_required
def sync_data():
    """Synchronize user data for mobile apps"""
    # Get the user's data
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'subscription_status': current_user.subscription_status,
        'subscription_expiry': current_user.subscription_expiry.isoformat() if current_user.subscription_expiry else None,
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

# Speaking-only routes
@app.route('/speaking-only')
def speaking_only():
    """Landing page for speaking-only users"""
    # Check if user is already logged in
    if current_user.is_authenticated:
        if current_user.is_speaking_only_user():
            # Already a speaking-only user, go to speaking tests
            return redirect(url_for('practice_test_list', test_type='speaking'))
        else:
            # Regular user, show them speaking tests
            return redirect(url_for('practice_test_list', test_type='speaking'))
    
    # Show landing page for unregistered speaking-only users
    return render_template('speaking_only.html', 
                          title='IELTS Speaking Assessment')

@app.route('/speaking-only-checkout/<package>')
def speaking_only_checkout(package):
    """Checkout page for speaking-only packages"""
    if package not in ['basic', 'pro']:
        flash('Invalid package selected.', 'danger')
        return redirect(url_for('speaking_only'))
    
    # Get user's country for localized payment options
    user_country = get_country_from_ip(request.remote_addr) or 'US'
    
    try:
        # Create checkout session
        checkout_data = create_stripe_checkout_speaking(package, user_country)
        
        # Store checkout data in session
        session['speaking_checkout'] = {
            'session_id': checkout_data['session_id'],
            'package': package,
            'processed': False
        }
        
        # Redirect to Stripe checkout
        return redirect(checkout_data['checkout_url'])
    
    except Exception as e:
        app.logger.error(f"Error creating speaking checkout: {str(e)}")
        flash('There was an error processing your request. Please try again later.', 'danger')
        return redirect(url_for('speaking_only'))

@app.route('/speaking-payment-success')
def speaking_payment_success():
    """Handle successful speaking package payments from Stripe"""
    # Get session ID from URL param
    session_id = request.args.get('session_id')
    
    try:
        # If this is a new order we're processing
        if session_id and 'speaking_checkout' not in session:
            # We don't have checkout data, create a basic record
            session['speaking_checkout'] = {
                'session_id': session_id,
                'package': 'basic',  # Default to basic if we don't know
                'processed': False
            }
        
        # Process the payment if it hasn't been processed already
        if session_id and 'speaking_checkout' in session and not session['speaking_checkout'].get('processed', False):
            package = session['speaking_checkout'].get('package', 'basic')
            
            try:
                # Verify payment with Stripe
                payment_verified = verify_stripe_payment(session_id)
                
                if not payment_verified:
                    flash('Payment verification failed. Please contact support with your order details.', 'danger')
                    return redirect(url_for('speaking_only'))
                
                # If user is not logged in, create a new speaking-only user account
                if not current_user.is_authenticated:
                    # Generate a random username and password
                    random_id = uuid.uuid4().hex[:8]
                    username = f"speaking_user_{random_id}"
                    password = uuid.uuid4().hex[:12]
                    email = f"speaking_{random_id}@example.com"  # Placeholder email
                    
                    # Create a new user
                    new_user = User(
                        username=username,
                        email=email,
                        region=get_country_from_ip(request.remote_addr) or 'US',
                        test_preference='academic',  # Default
                        subscription_status=f"Speaking Only {package.title()}"
                    )
                    new_user.set_password(password)
                    # No expiry date for speaking-only users
                    new_user.subscription_expiry = None
                    
                    # Add speaking purchase to history
                    total_assessments = 4 if package == 'basic' else 10
                    amount = 15.0 if package == 'basic' else 20.0
                    
                    test_history = []
                    speaking_purchase = {
                        "speaking_purchase": {
                            "purchase_date": datetime.utcnow().isoformat(),
                            "expiry_date": None,  # No expiry date
                            "package": f"Speaking Only {package.title()}",
                            "total_assessments": total_assessments,
                            "used_assessments": 0,
                            "amount": amount
                        }
                    }
                    test_history.append(speaking_purchase)
                    new_user.test_history = test_history
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    # Log in the new user
                    login_user(new_user)
                    
                    # Display credentials to user (only once)
                    flash(f'Your speaking assessment account has been created! Username: {username} | Password: {password} - Please save these credentials for future logins.', 'success')
                
                else:
                    # Update existing user
                    current_user.subscription_status = f"Speaking Only {package.title()}"
                    # No expiry date for speaking-only users
                    current_user.subscription_expiry = None
                    
                    # Add speaking purchase to history
                    total_assessments = 4 if package == 'basic' else 10
                    amount = 15.0 if package == 'basic' else 20.0
                    
                    test_history = current_user.test_history
                    speaking_purchase = {
                        "speaking_purchase": {
                            "purchase_date": datetime.utcnow().isoformat(),
                            "expiry_date": None,  # No expiry date
                            "package": f"Speaking Only {package.title()}",
                            "total_assessments": total_assessments,
                            "used_assessments": 0,
                            "amount": amount
                        }
                    }
                    test_history.append(speaking_purchase)
                    current_user.test_history = test_history
                    
                    db.session.commit()
                    
                    flash(f'Thank you for your purchase! Your Speaking Only {package.title()} package is now active.', 'success')
                
                # Mark payment as processed to prevent duplicates
                speaking_data = session['speaking_checkout']
                speaking_data['processed'] = True
                session['speaking_checkout'] = speaking_data
                
                return redirect(url_for('practice_test_list', test_type='speaking'))
                
            except Exception as e:
                app.logger.error(f"Error verifying speaking payment: {str(e)}")
                flash('There was an error processing your payment. Please contact support.', 'danger')
                return redirect(url_for('speaking_only'))
                
        elif 'speaking_checkout' in session and session['speaking_checkout'].get('processed', False):
            # Payment was already processed, just redirect
            flash('Your payment has already been processed.', 'info')
            return redirect(url_for('practice_test_list', test_type='speaking'))
            
        else:
            # No session ID or pending payment
            flash('No payment information found.', 'warning')
            return redirect(url_for('speaking_only'))
            
    except Exception as e:
        app.logger.error(f"Error in speaking_payment_success: {str(e)}")
        flash('An unexpected error occurred. Please contact support.', 'danger')
        return redirect(url_for('speaking_only'))

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
