import os
import json
import uuid
import logging
from functools import wraps
from datetime import datetime, timedelta

from flask import render_template, url_for, flash, redirect, request, jsonify, session, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import (User, TestStructure, PracticeTest, UserTestAttempt, 
                   SpeakingPrompt, SpeakingResponse, PaymentMethod, Translation, CountryPricing,
                   CompletePracticeTest, CompleteTestProgress)
from utils import get_user_region, get_translation, compress_audio
from aws_services import (transcribe_audio, generate_polly_speech, analyze_speaking_response, 
                      analyze_pronunciation, generate_pronunciation_exercises)
from payment_services import create_stripe_checkout, verify_payment
from geoip_services import get_country_from_ip, get_pricing_for_country

# Helper functions
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_subscribed():
            flash('This feature requires a subscription. Please subscribe to continue.', 'warning')
            return redirect(url_for('subscribe'))
        return f(*args, **kwargs)
    return decorated_function

def update_user_streak(f):
    """Decorator to update a user's study streak when they perform activities"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First execute the route function
        response = f(*args, **kwargs)
        
        # Then update the user's streak if they're logged in
        if current_user.is_authenticated:
            try:
                current_user.update_streak()
                db.session.commit()
            except Exception as e:
                app.logger.error(f"Error updating user streak: {str(e)}")
                db.session.rollback()
                
        return response
    return decorated_function

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
@update_user_streak
def profile():
    # Get streak data for visualization
    streak_data = current_user.get_streak_data()
    return render_template('profile.html', title='My Profile', streak_data=streak_data)

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
    
    # Check if user has the 4-test value pack
    has_value_pack = False
    test_history = current_user.test_history
    
    for entry in test_history:
        # Check for test purchases with the "pack" package (4 tests)
        if 'test_purchase' in entry and entry['test_purchase'].get('test_package') == 'pack':
            # Check if the purchase is still valid (not expired)
            purchase_expiry = datetime.fromisoformat(entry['test_purchase'].get('expiry_date'))
            if purchase_expiry > datetime.utcnow():
                has_value_pack = True
                break
    
    if not has_value_pack:
        flash('The Test Day Guide is only available with the Value Pack (4 tests) subscription.', 'warning')
        return redirect(url_for('subscribe'))
    
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
        
        # Get tests (free ones and those matching user's subscription level)
        # Use subquery to get only the latest version of each test number (to avoid duplicates)
        from sqlalchemy import func
        
        # For each test number, get the maximum ID (latest version)
        if current_user.is_subscribed():
            # First get the latest ID for each test number - show academic tests for premium users
            subquery = db.session.query(
                CompletePracticeTest.test_number,
                func.max(CompletePracticeTest.id).label('max_id')
            ).filter(
                CompletePracticeTest.ielts_test_type == 'academic'  # Always show academic tests 
            ).group_by(CompletePracticeTest.test_number).subquery()
            
            # Then join to get the complete test records
            complete_tests = CompletePracticeTest.query.join(
                subquery,
                db.and_(
                    CompletePracticeTest.id == subquery.c.max_id,
                    CompletePracticeTest.test_number == subquery.c.test_number
                )
            ).order_by(CompletePracticeTest.test_number).all()
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
@update_user_streak
def practice_test_list(test_type):
    if test_type not in ['listening', 'reading', 'writing']:
        abort(404)
        
    # Get all tests of this type, but filter to just show ones with complete questions and answers
    tests = PracticeTest.query.filter_by(test_type=test_type).all()
    
    # If we have premium users, show all tests
    if not current_user.is_subscribed():
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
@update_user_streak
def take_practice_test(test_type, test_id):
    if test_type not in ['listening', 'reading', 'writing']:
        abort(404)
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # All tests require subscription
    if not current_user.is_subscribed():
        flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
        return redirect(url_for('subscribe'))
    
    # Check if user has already taken this test during current subscription period
    if current_user.has_taken_test(test_id, test_type):
        flash('You have already taken this test during your current subscription period. Each test can only be taken once per subscription.', 'warning')
        return redirect(url_for('practice_test_list', test_type=test_type))
    
    # Handle new question format for listening tests
    if test_type == 'listening':
        # Convert questions from JSON string to Python list/dict
        import json
        if isinstance(test.questions, str):
            test.questions = json.loads(test.questions)
    
    return render_template(f'practice/{test_type}.html', 
                          title=f'IELTS {test_type.capitalize()} Practice',
                          test=test,
                          taking_test=True)

# Complete Test Routes
@app.route('/practice/complete-test/<int:test_id>/start')
@login_required
@update_user_streak
def start_complete_test(test_id):
    """Start a new complete IELTS practice test"""
    complete_test = CompletePracticeTest.query.get_or_404(test_id)
    
    # Check if user has access to this test
    if not current_user.is_subscribed():
        flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
        return redirect(url_for('subscribe'))
    
    # We now allow users to access all test types regardless of preference
    # Keep a comment explaining the change for future reference
    # Previously, we were restricting users to only take tests that matched their preference
    
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
@update_user_streak
def continue_complete_test(test_id):
    """Continue an in-progress complete test"""
    # Get user's progress for this test
    progress = CompleteTestProgress.query.filter_by(
        user_id=current_user.id,
        complete_test_id=test_id
    ).first_or_404()
    
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
@update_user_streak
def take_complete_test_section(test_id, section):
    """Take a specific section of a complete test"""
    if section not in ['listening', 'reading', 'writing', 'speaking']:
        abort(404)
    
    # Verify user has an in-progress test
    progress = CompleteTestProgress.query.filter_by(
        user_id=current_user.id,
        complete_test_id=test_id
    ).first_or_404()
    
    # Ensure the user is on the correct section
    if progress.current_section != section:
        flash(f'Please complete the {progress.current_section} section first.', 'warning')
        return redirect(url_for('continue_complete_test', test_id=test_id))
    
    complete_test = CompletePracticeTest.query.get_or_404(test_id)
    
    # Get the section test
    section_test = PracticeTest.query.filter_by(
        complete_test_id=test_id,
        test_type=section,
        ielts_test_type=complete_test.ielts_test_type
    ).first_or_404()
    
    # Handle question format for different test types
    if section == 'listening':
        # Convert questions from JSON string to Python list/dict if not already parsed
        import json
        if isinstance(section_test.questions, str):
            section_test.questions = json.loads(section_test.questions)
    
    return render_template(f'practice/{section}.html', 
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
    
    if not progress.is_test_completed():
        flash('Please complete all sections of the test first.', 'warning')
        return redirect(url_for('continue_complete_test', test_id=test_id))
    
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
@update_user_streak
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
        response_data['next_section_url'] = url_for('continue_complete_test', test_id=complete_test_id)
        
    return jsonify(response_data)

# Speaking Assessment Routes
# Speaking routes removed as requested
# @app.route('/speaking')
# def speaking_index():
#     # Redirect to the practice test list page for complete tests
#     flash('Speaking assessments are now available as part of complete IELTS practice tests.', 'info')
#     return redirect(url_for('practice_index'))
# 
# @app.route('/speaking/<int:prompt_id>')
# @login_required
# def speaking_assessment(prompt_id):
#     # Redirect to the practice test list page for complete tests
#     flash('Speaking assessments are now available as part of complete IELTS practice tests.', 'info')
#     return redirect(url_for('practice_index'))

@app.route('/practice/submit-speaking/<int:test_id>', methods=['POST'])
@login_required
@update_user_streak
def submit_speaking_response(test_id):
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
        f.write(audio_data)
    
    # Compress the audio
    compressed_path = compress_audio(audio_path)
    
    try:
        # Get the test
        test = PracticeTest.query.get_or_404(test_id)
        
        # Transcribe and analyze the response
        transcription = transcribe_audio(compressed_path)
        scores, feedback = analyze_speaking_response(transcription)
        
        # Generate audio feedback
        feedback_audio_filename = f"feedback_{os.path.basename(compressed_path)}"
        feedback_audio_path = os.path.join('static', 'uploads', 'feedback', feedback_audio_filename)
        os.makedirs(os.path.dirname(feedback_audio_path), exist_ok=True)
        
        polly_result = generate_polly_speech(feedback, feedback_audio_path)
        
        # Create a speaking response record
        response = SpeakingResponse(
            user_id=current_user.id,
            prompt_id=test_id,  # Using the test ID as the prompt ID
            audio_url=compressed_path.replace('static/', ''),
            transcription=transcription,
            scores=scores,
            feedback_audio_url=feedback_audio_path.replace('static/', '') if polly_result else None
        )
        
        db.session.add(response)
        
        # Create a test attempt record
        new_attempt = UserTestAttempt(
            user_id=current_user.id,
            test_id=test_id,
            user_answers={'transcription': transcription},
            score=scores.get('overall', 0) if isinstance(scores, dict) else 0,
            assessment=json.dumps({
                'transcription': transcription,
                'scores': scores,
                'feedback': feedback
            })
        )
        
        if complete_test_id:
            # Get the user's progress for this complete test
            progress = CompleteTestProgress.query.filter_by(
                user_id=current_user.id,
                complete_test_id=complete_test_id
            ).first()
            
            if progress:
                new_attempt.complete_test_progress_id = progress.id
                
                # Mark speaking section as completed
                progress.mark_section_completed('speaking', scores.get('overall', 0))
                
                # Check if all sections are completed
                if progress.is_test_completed():
                    progress.completed_date = datetime.utcnow()
        
        db.session.add(new_attempt)
        
        # Update user's speaking scores
        speaking_scores = current_user.speaking_scores
        speaking_scores.append({
            'prompt_id': test_id,
            'date': datetime.utcnow().isoformat(),
            'scores': scores
        })
        current_user.speaking_scores = speaking_scores
        
        # Mark this test as completed
        current_user.mark_test_completed(test_id, 'speaking')
        
        db.session.commit()
        
        flash('Your speaking response has been submitted and assessed.', 'success')
        
        if complete_test_id:
            # Check if this was the last section
            if progress.is_test_completed():
                return redirect(url_for('complete_test_results', test_id=complete_test_id))
            else:
                return redirect(url_for('continue_complete_test', test_id=complete_test_id))
        else:
            return redirect(url_for('practice_index'))
            
    except Exception as e:
        app.logger.error(f"Error processing speaking assessment: {str(e)}")
        flash(f'An error occurred while processing your speaking response: {str(e)}', 'danger')
        
        if complete_test_id:
            return redirect(url_for('continue_complete_test', test_id=complete_test_id))
        else:
            return redirect(url_for('practice_index'))

@app.route('/api/speaking/submit', methods=['POST'])
@login_required
@update_user_streak
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
        
        # Analyze the response using IELTS criteria
        scores, feedback = analyze_speaking_response(transcription)
        
        # Generate audio feedback using Amazon Polly
        feedback_audio_filename = f"feedback_{os.path.basename(compressed_path)}"
        feedback_audio_path = os.path.join('static', 'uploads', 'feedback', feedback_audio_filename)
        os.makedirs(os.path.dirname(feedback_audio_path), exist_ok=True)
        
        polly_result = generate_polly_speech(feedback, feedback_audio_path)
        
        # Save the response
        response = SpeakingResponse(
            user_id=current_user.id,
            prompt_id=prompt_id,
            audio_url=compressed_path.replace('static/', ''),
            transcription=transcription,
            scores=scores,
            feedback_audio_url=feedback_audio_path.replace('static/', '') if polly_result else None
        )
        
        db.session.add(response)
        
        # Update user's speaking scores
        speaking_scores = current_user.speaking_scores
        speaking_scores.append({
            'prompt_id': prompt_id,
            'date': datetime.utcnow().isoformat(),
            'scores': scores
        })
        current_user.speaking_scores = speaking_scores
        
        # Mark this speaking prompt as completed so it can't be retaken during current subscription period
        current_user.mark_test_completed(int(prompt_id), 'speaking')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transcription': transcription,
            'scores': scores,
            'feedback': feedback,
            'feedback_audio_url': url_for('static', filename=feedback_audio_path.replace('static/', '')) if polly_result else None
        })
        
    except Exception as e:
        logging.error(f"Error processing speaking assessment: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Subscription Routes
@app.route('/subscribe')
def subscribe():
    # Get payment methods based on user's region
    region = get_user_region() if not current_user.is_authenticated else current_user.region
    
    # Get regional payment methods
    regional_methods = PaymentMethod.query.filter_by(region=region).order_by(PaymentMethod.display_order).all()
    
    # Get global payment methods
    global_methods = PaymentMethod.query.filter_by(region=None).order_by(PaymentMethod.display_order).all()
    
    # Combine and sort
    payment_methods = sorted(regional_methods + global_methods, key=lambda x: x.display_order)
    
    # Get country-specific pricing based on user's location
    country_code = None
    if current_user.is_authenticated and current_user.region:
        # Try to get country code from user's stored region
        # This is a simplified approach - in production you would have a proper mapping
        country_code = current_user.region[:2].upper() if len(current_user.region) >= 2 else None
    
    # If no country code from user profile, detect from IP
    if not country_code:
        country_code, _ = get_country_from_ip()
    
    # Get pricing for the detected country
    pricing = get_pricing_for_country(country_code)
    
    return render_template('subscribe.html', title='Subscribe',
                          payment_methods=payment_methods,
                          pricing=pricing)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    payment_method = request.form.get('payment_method', 'stripe')
    plan = request.form.get('plan', 'base')
    terms_accepted = request.form.get('terms_accepted')
    
    # Get test-specific parameters for the new pricing structure
    test_type = request.form.get('test_type')  # 'academic' or 'general'
    test_package = request.form.get('test_package')  # 'single', 'double', or 'pack'
    
    # For forms that don't directly include terms_accepted (like the card buttons)
    # Allow them to bypass if they've previously accepted terms
    if not terms_accepted and not session.get('terms_accepted'):
        flash('You must accept the Terms and Conditions to proceed with payment.', 'warning')
        return redirect(url_for('subscribe'))
    
    # For now, we only implement Stripe checkout
    if payment_method == 'stripe':
        try:
            # Detect user's country for region-specific payment methods
            from geoip_services import get_country_from_ip
            country_code, _ = get_country_from_ip()
            
            # Create checkout session based on whether it's a subscription or test purchase
            if plan == 'purchase' and test_type and test_package:
                # New test purchase flow
                checkout_data = create_stripe_checkout(
                    plan_info='purchase',
                    country_code=country_code,
                    test_type=test_type,
                    test_package=test_package
                )
            else:
                # Legacy subscription flow
                checkout_data = create_stripe_checkout(
                    plan_info=plan,
                    country_code=country_code
                )
            
            # Store checkout information in session
            session['checkout_session_id'] = checkout_data['session_id']
            session['checkout_url'] = checkout_data['checkout_url']
            
            # Store test purchase details if applicable
            if plan == 'purchase':
                session['test_purchase'] = {
                    'test_type': test_type,
                    'test_package': test_package
                }
            
            # Store acceptance of terms in the session
            session['terms_accepted'] = True
            session['terms_accepted_time'] = datetime.utcnow().isoformat()
            
            # Redirect to our new checkout page route
            return redirect(url_for('stripe_checkout'))
        except Exception as e:
            flash(f'Error creating checkout session: {str(e)}', 'danger')
            return redirect(url_for('subscribe'))
    else:
        flash('This payment method is not yet implemented', 'warning')
        return redirect(url_for('subscribe'))

@app.route('/stripe-checkout')
def stripe_checkout():
    # Get checkout URL from session
    checkout_url = session.get('checkout_url')
    
    if not checkout_url:
        flash('Checkout session not found', 'danger')
        return redirect(url_for('subscribe'))
    
    return render_template('stripe_checkout.html', 
                          checkout_url=checkout_url,
                          title='Stripe Checkout')

@app.route('/payment-success')
def payment_success():
    # Verify payment and update subscription status
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session', 'danger')
        return redirect(url_for('subscribe'))
    
    try:
        # Verify the payment with Stripe
        payment_info = verify_payment(session_id)
        
        if payment_info and payment_info.get('paid') and current_user.is_authenticated:
            plan = payment_info.get('plan', 'base')
            tests = int(payment_info.get('tests', 3))  # Default to 3 tests if not specified
            days = int(payment_info.get('days', 15))   # Default to 15 days if not specified
            
            # Check if this is a test purchase or a legacy subscription
            is_test_purchase = 'test_type' in payment_info and 'test_package' in payment_info
            
            if is_test_purchase:
                # Test purchase flow
                test_type = payment_info.get('test_type')
                test_package = payment_info.get('test_package')
                
                # Set the expiry date
                expiry_date = datetime.utcnow() + timedelta(days=days)
                
                # Update user's test preferences based on purchase if not already set
                if not current_user.test_preference:
                    current_user.test_preference = test_type
                
                # Create purchase record
                purchase_data = {
                    'plan': f"{test_type}_{test_package}",
                    'test_type': test_type,
                    'total_tests': tests,
                    'tests_remaining': tests,
                    'purchase_date': datetime.utcnow().isoformat(),
                    'expiry_date': expiry_date.isoformat()
                }
                
                # Update user's test_history to include purchase data
                test_history = current_user.test_history
                test_history.append({"test_purchase": purchase_data})
                current_user.test_history = test_history
                
                db.session.commit()
                
                flash(f'Thank you for purchasing {tests} {test_type.capitalize()} practice tests! You have access for {days} days.', 'success')
            else:
                # Legacy subscription flow
                expiry_date = datetime.utcnow() + timedelta(days=days)
                
                current_user.subscription_status = plan  # Use actual plan level (base, intermediate, pro)
                current_user.subscription_expiry = expiry_date
                
                # Save the number of tests the user has access to
                user_subscription_data = {
                    'plan': plan,
                    'total_tests': tests,
                    'tests_remaining': tests,
                    'purchase_date': datetime.utcnow().isoformat()
                }
                
                # Update user's test_history to include subscription data
                test_history = current_user.test_history
                test_history.append({"subscription_data": user_subscription_data})
                current_user.test_history = test_history
                
                db.session.commit()
                
                flash(f'Thank you for purchasing the {plan} plan!', 'success')
        else:
            flash('Payment verification failed', 'danger')
            
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'danger')
    
    return render_template('payment_success.html', title='Payment Successful')

@app.route('/payment-cancel')
def payment_cancel():
    flash('Payment was cancelled', 'info')
    return render_template('payment_cancel.html', title='Payment Cancelled')

# Device Specs Route
@app.route('/device-specs')
def device_specs():
    return render_template('device_specs.html', title='Device Requirements')

# API Routes for data sync
@app.route('/api/sync', methods=['POST'])
@login_required
def sync_data():
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data to sync'}), 400
    
    test_attempts = data.get('test_attempts', [])
    
    for attempt in test_attempts:
        test_id = attempt.get('test_id')
        user_answers = attempt.get('answers')
        
        if not test_id or not user_answers:
            continue
        
        # Check if this attempt already exists
        existing_attempt = UserTestAttempt.query.filter_by(
            user_id=current_user.id,
            test_id=test_id,
            _user_answers=json.dumps(user_answers)
        ).first()
        
        if existing_attempt:
            continue
        
        # Process new attempt
        test = PracticeTest.query.get(test_id)
        if not test:
            continue
            
        # Calculate score
        score = 0
        total_questions = len(test.answers)
        
        for q_id, user_answer in user_answers.items():
            if q_id in test.answers and user_answer.lower() == test.answers[q_id].lower():
                score += 1
        
        score_percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        
        # Save the attempt
        new_attempt = UserTestAttempt(
            user_id=current_user.id,
            test_id=test_id,
            user_answers=user_answers,
            score=score_percentage,
            attempt_date=datetime.fromisoformat(attempt.get('date', datetime.utcnow().isoformat()))
        )
        
        db.session.add(new_attempt)
        
        # Update user's test history
        test_history = current_user.test_history
        test_history.append({
            'test_id': test_id,
            'test_type': test.test_type,
            'title': test.title,
            'date': new_attempt.attempt_date.isoformat(),
            'score': score_percentage
        })
        current_user.test_history = test_history
        
        # Mark this test as completed so it can't be retaken during current subscription period
        current_user.mark_test_completed(test_id, test.test_type)
    
    db.session.commit()
    
    return jsonify({'success': True})

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Initialize database with sample data
@app.cli.command('init-db')
def init_db_command():
    # Add sample data for test structure
    if TestStructure.query.count() == 0:
        test_structures = [
            TestStructure(
                test_type='academic',
                description='IELTS Academic is designed for those applying to study at undergraduate or postgraduate levels, and for those seeking professional registration.',
                format_details=json.dumps({
                    'listening': 'Listening: 30 minutes + 10 minutes transfer time, 4 sections, 40 questions',
                    'reading': 'Reading: 60 minutes, 3 passages, 40 questions',
                    'writing': 'Writing: 60 minutes, Task 1 (150 words describing visual data), Task 2 (250 word essay)',
                    'speaking': 'Speaking: 11-14 minutes, face-to-face interview with examiner, 3 parts'
                }),
                sample_image_url='https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_1x1/public/ielts_academic_0.jpg'
            ),
            TestStructure(
                test_type='general_training',
                description='IELTS General Training is for those migrating to Australia, Canada, New Zealand and the UK, or applying for secondary education, training programmes or work experience in an English-speaking environment.',
                format_details=json.dumps({
                    'listening': 'Listening: 30 minutes + 10 minutes transfer time, 4 sections, 40 questions',
                    'reading': 'Reading: 60 minutes, 3 sections, 40 questions',
                    'writing': 'Writing: 60 minutes, Task 1 (150 words letter), Task 2 (250 word essay)',
                    'speaking': 'Speaking: 11-14 minutes, face-to-face interview with examiner, 3 parts'
                }),
                sample_image_url='https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_1x1/public/ielts_general_training.jpg'
            )
        ]
        
        for structure in test_structures:
            db.session.add(structure)
        
        # Add sample practice tests
        sample_listening_test = PracticeTest(
            test_type='listening',
            section=1,
            title='Booking a holiday',
            description='A conversation between a customer and a travel agent',
            questions=json.dumps({
                '1': 'When does the customer want to travel?',
                '2': 'What is the customer\'s budget?',
                '3': 'How many people are traveling?'
            }),
            answers=json.dumps({
                '1': 'June',
                '2': '£1000',
                '3': '2'
            }),
            audio_url='https://example.com/sample-listening.mp3'
        )
        
        sample_reading_test = PracticeTest(
            test_type='reading',
            section=1,
            title='Global Warming',
            description='An article about climate change and its effects',
            questions=json.dumps({
                '1': 'What is the main cause of global warming according to the passage?',
                '2': 'Which country has the highest carbon emissions?',
                '3': 'What year did the Kyoto Protocol come into effect?'
            }),
            answers=json.dumps({
                '1': 'Greenhouse gases',
                '2': 'China',
                '3': '2005'
            })
        )
        
        sample_writing_test = PracticeTest(
            test_type='writing',
            section=1,
            title='Task 1: Bar Chart',
            description='The chart below shows the percentage of households with internet access in four different countries between 2000 and 2020.',
            questions=json.dumps({
                'task': 'Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.'
            }),
            answers=json.dumps({
                'sample_answer': 'The bar chart illustrates the proportion of homes with internet access in four nations over a twenty-year period from 2000 to 2020...'
            })
        )
        
        db.session.add(sample_listening_test)
        db.session.add(sample_reading_test)
        db.session.add(sample_writing_test)
        
        # Add sample speaking prompts
        sample_prompts = [
            SpeakingPrompt(
                part=1,
                prompt_text='Tell me about your hometown.'
            ),
            SpeakingPrompt(
                part=2,
                prompt_text='Describe a time when you helped someone. You should say: who you helped, what you did to help, why the person needed help, and explain how you felt about helping them.'
            )
        ]
        
        for prompt in sample_prompts:
            db.session.add(prompt)
        
        # Add payment methods
        payment_methods = [
            # Regional methods
            PaymentMethod(name='Razorpay', region='India', display_order=1),
            PaymentMethod(name='JazzCash', region='Pakistan', display_order=1),
            PaymentMethod(name='bKash', region='Bangladesh', display_order=1),
            PaymentMethod(name='STC Pay', region='Saudi Arabia', display_order=1),
            PaymentMethod(name='LINE Pay', region='Japan', display_order=1),
            PaymentMethod(name='KakaoPay', region='South Korea', display_order=1),
            PaymentMethod(name='BLIK', region='Poland', display_order=1),
            PaymentMethod(name='iDEAL', region='Netherlands', display_order=1),
            PaymentMethod(name='Sofort', region='Germany', display_order=1),
            
            # Global methods
            PaymentMethod(name='Stripe', region=None, display_order=2),
            PaymentMethod(name='PayPal', region=None, display_order=2),
            PaymentMethod(name='Google Pay', region=None, display_order=2),
            PaymentMethod(name='Apple Pay', region=None, display_order=2)
        ]
        
        for method in payment_methods:
            db.session.add(method)
        
        db.session.commit()
        print('Database initialized with sample data')
