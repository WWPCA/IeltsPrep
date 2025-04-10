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
                   SpeakingPrompt, SpeakingResponse, PaymentMethod, Translation)
from utils import get_user_region, get_translation, compress_audio
from aws_services import (transcribe_audio, generate_polly_speech, analyze_speaking_response, 
                      analyze_pronunciation, generate_pronunciation_exercises)
from payment_services import create_stripe_checkout, verify_payment

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
    
    class LoginForm:
        # Simple form class to enable CSRF protection
        def __init__(self):
            pass
    
    form = LoginForm()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            
    return render_template('login.html', title='Login', form=form)

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
        
        new_user = User(
            username=username,
            email=email,
            region=region
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
def test_day():
    return render_template('test_day.html', title='IELTS Test Day Preparation')

# Practice Test Routes
@app.route('/practice')
def practice_index():
    test_types = ['listening', 'reading', 'writing']
    sample_tests = {}
    
    for test_type in test_types:
        sample_tests[test_type] = PracticeTest.query.filter_by(test_type=test_type).first()
    
    return render_template('practice/index.html', title='Practice Tests', 
                          sample_tests=sample_tests)

@app.route('/practice/<test_type>')
@login_required
def practice_test_list(test_type):
    if test_type not in ['listening', 'reading', 'writing']:
        abort(404)
        
    tests = PracticeTest.query.filter_by(test_type=test_type).all()
    
    if not current_user.is_subscribed():
        # For non-subscribers, only show the first test
        tests = tests[:1] if tests else []
    
    return render_template(f'practice/{test_type}.html', 
                          title=f'IELTS {test_type.capitalize()} Practice',
                          tests=tests)

@app.route('/practice/<test_type>/<int:test_id>')
@login_required
@update_user_streak
def take_practice_test(test_type, test_id):
    if test_type not in ['listening', 'reading', 'writing']:
        abort(404)
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # Check if this is the free sample or if user is subscribed
    is_free_sample = (PracticeTest.query.filter_by(test_type=test_type).first().id == test_id)
    
    if not is_free_sample and not current_user.is_subscribed():
        flash('This test requires a subscription. Please subscribe to access all practice tests.', 'warning')
        return redirect(url_for('subscribe'))
    
    # Handle new question format for listening tests
    if test_type == 'listening':
        # Convert questions from JSON string to Python list/dict
        import json
        test.questions = json.loads(test.questions)
    
    return render_template(f'practice/{test_type}.html', 
                          title=f'IELTS {test_type.capitalize()} Practice',
                          test=test,
                          taking_test=True)

@app.route('/api/submit-test', methods=['POST'])
@login_required
@update_user_streak
def submit_test():
    data = request.json
    test_id = data.get('test_id')
    user_answers = data.get('answers')
    
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
    
    # Save the attempt
    attempt = UserTestAttempt(
        user_id=current_user.id,
        test_id=test_id,
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
        'score': score_percentage
    })
    current_user.test_history = test_history
    
    db.session.commit()
    
    return jsonify({
        'score': score_percentage,
        'correct': score,
        'total': total_questions
    })

# Speaking Assessment Routes
@app.route('/speaking')
def speaking_index():
    try:
        prompts = SpeakingPrompt.query.all()
        sample_prompt = prompts[0] if prompts else None
        
        # Flag to indicate if this is a sample view (not subscribed)
        is_sample = not (current_user.is_authenticated and current_user.is_subscribed())
        
        # Set assessment to False for the index page, only set to True for specific prompt pages
        return render_template('speaking/index.html', title='Speaking Assessment',
                            prompts=prompts, sample_prompt=sample_prompt, 
                            is_sample=is_sample, assessment=False)
    except Exception as e:
        app.logger.error(f"Error in speaking_index: {str(e)}")
        flash('An error occurred while loading the speaking assessment page. Please try again.', 'danger')
        return redirect(url_for('index'))

@app.route('/speaking/<int:prompt_id>')
@login_required
@update_user_streak
def speaking_assessment(prompt_id):
    prompt = SpeakingPrompt.query.get_or_404(prompt_id)
    
    # Get all prompts to display in the information section
    prompts = SpeakingPrompt.query.all()
    sample_prompt = prompts[0] if prompts else None
    
    # Don't allow non-subscribers to access any speaking prompt
    if not current_user.is_subscribed():
        flash('Speaking assessment requires a subscription. Please subscribe to access this feature.', 'warning')
        return redirect(url_for('subscribe'))
    
    return render_template('speaking/index.html', title='Speaking Assessment',
                          prompt=prompt, assessment=True, prompts=prompts, sample_prompt=sample_prompt, is_sample=False)

@app.route('/api/speaking/submit', methods=['POST'])
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
    
    return render_template('subscribe.html', title='Subscribe',
                          payment_methods=payment_methods)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    payment_method = request.form.get('payment_method', 'stripe')
    plan = request.form.get('plan', 'base')
    
    # For now, we only implement Stripe checkout
    if payment_method == 'stripe':
        try:
            # Create checkout session and store in session
            checkout_data = create_stripe_checkout(plan)
            session['checkout_session_id'] = checkout_data['session_id']
            session['checkout_url'] = checkout_data['checkout_url']
            
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
            # Update user subscription
            plan = payment_info.get('plan', 'base')
            tests = payment_info.get('tests', 3)  # Default to 3 tests if not specified
            days = payment_info.get('days', 30)   # Default to 30 days if not specified
            
            expiry_date = datetime.utcnow() + timedelta(days=days)
            
            current_user.subscription_status = 'active'
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
            
            flash(f'Thank you for purchasing the {plan.capitalize()} plan!', 'success')
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

# API Routes for offline sync
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
