"""
IELTS Writing Assessment Routes
Flask routes for the writing assessment feature using OpenAI GPT-4o.
"""

from flask import Blueprint, request, jsonify, render_template, current_app, session, flash, redirect, url_for, abort
from flask_login import login_required, current_user
import json
import os
import time
import logging
from werkzeug.utils import secure_filename
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

# Import our OpenAI assessment module
from openai_writing_assessment import assess_writing, format_assessment_for_display

# Import database models
from models import db, User, PracticeTest, UserTestAttempt

# Create a blueprint for the writing assessment routes
writing_assessment_bp = Blueprint('writing_assessment', __name__, url_prefix='/writing-assessment')

# Decorator to check if user has subscription access to the advanced assessment
def subscription_required_for_ai_assessment(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access AI writing assessment.', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_subscribed():
            flash('This feature requires an active subscription.', 'warning')
            return redirect(url_for('subscribe'))
        
        # Check if user has already taken this specific test
        test_id = kwargs.get('test_id')
        if test_id and current_user.has_taken_test(test_id, 'writing'):
            flash('You have already completed this writing test. Each test can only be taken once per subscription period.', 'info')
            return redirect(url_for('practice_test_list', test_type='writing'))
            
        return f(*args, **kwargs)
    return decorated_function

# Routes for the writing assessment feature
@writing_assessment_bp.route('/tests')
@login_required
def writing_tests():
    """Display available writing tests."""
    writing_tests = PracticeTest.query.filter_by(test_type='writing').all()
    
    # Mark tests the user has already taken
    for test in writing_tests:
        test.taken = current_user.has_taken_test(test.id, 'writing')
    
    return render_template(
        'practice/writing_tests.html', 
        tests=writing_tests,
        title='IELTS Writing Practice'
    )

@writing_assessment_bp.route('/take/<int:test_id>')
@login_required
@subscription_required_for_ai_assessment
def take_writing_test(test_id):
    """Display the writing test interface."""
    test = PracticeTest.query.get_or_404(test_id)
    
    # Get the first question as the writing prompt
    questions = test.questions
    prompt = questions[0] if questions else "No prompt available."
    
    return render_template(
        'practice/writing_test.html',
        test=test,
        prompt=prompt,
        title=f'IELTS Writing: {test.title}'
    )

@writing_assessment_bp.route('/submit/<int:test_id>', methods=['POST'])
@login_required
@subscription_required_for_ai_assessment
def submit_writing(test_id):
    """Handle writing submission and trigger AI assessment."""
    test = PracticeTest.query.get_or_404(test_id)
    
    # Get the essay text from the form
    essay_text = request.form.get('essay_text', '')
    
    if not essay_text:
        flash('Please provide your essay text.', 'danger')
        return redirect(url_for('writing_assessment.take_writing_test', test_id=test_id))
    
    # Get the writing prompt
    questions = test.questions
    prompt = questions[0] if questions else "No prompt available."
    
    # Determine the task type based on the test data
    task_type = None
    if "Task 1" in test.title and "Academic" in test.title:
        task_type = "Academic Task 1"
    elif "Task 1" in test.title and "General" in test.title:
        task_type = "General Training Task 1"
    elif "Task 2" in test.title:
        task_type = "Task 2"
    
    try:
        # Call the OpenAI assessment function
        assessment_result = assess_writing(essay_text, prompt, task_type)
        
        # Save the assessment results to the database
        try:
            user_test_attempt = UserTestAttempt(
                user_id=current_user.id,
                test_id=test_id,
                user_answers=json.dumps({'essay_text': essay_text}),
                score=assessment_result['scores']['overall'] if 'scores' in assessment_result else 0
            )
            
            # Store the full assessment in the database
            user_test_attempt.assessment = json.dumps(assessment_result)
            
            db.session.add(user_test_attempt)
            db.session.commit()
            
            # Mark the test as completed for this user in a separate transaction
            try:
                current_user.mark_test_completed(test_id, 'writing')
                db.session.commit()
            except SQLAlchemyError as e:
                current_app.logger.error(f"Error marking test as completed: {str(e)}")
                db.session.rollback()
                # We continue since the assessment was already saved
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error saving assessment: {str(e)}")
            db.session.rollback()
            flash("There was a problem saving your assessment results. Please try again.", "danger")
            return redirect(url_for('writing_assessment.take_writing_test', test_id=test_id))
        
        # Store the assessment ID in the session for the results page
        session['last_assessment_id'] = user_test_attempt.id
        
        return redirect(url_for('writing_assessment.show_results', attempt_id=user_test_attempt.id))
        
    except Exception as e:
        current_app.logger.error(f"Assessment error: {str(e)}")
        flash(f"Sorry, there was a problem with the assessment: {str(e)}", 'danger')
        return redirect(url_for('writing_assessment.take_writing_test', test_id=test_id))

@writing_assessment_bp.route('/results/<int:attempt_id>')
@login_required
def show_results(attempt_id):
    """Display the assessment results."""
    try:
        attempt = UserTestAttempt.query.get_or_404(attempt_id)
        
        # Ensure the user can only see their own results
        if attempt.user_id != current_user.id:
            flash('You do not have permission to view these results.', 'danger')
            return redirect(url_for('writing_assessment.writing_tests'))
        
        # Get the test details
        try:
            test = PracticeTest.query.get(attempt.test_id)
            if not test:
                current_app.logger.error(f"Test ID {attempt.test_id} not found")
                flash('The associated test could not be found.', 'warning')
                return redirect(url_for('writing_assessment.writing_tests'))
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error retrieving test: {str(e)}")
            db.session.rollback()
            flash('Error retrieving test information.', 'danger')
            return redirect(url_for('writing_assessment.writing_tests'))
        
        # Get the saved assessment
        try:
            assessment = json.loads(attempt.assessment) if attempt.assessment else None
            
            if not assessment:
                flash('Assessment results are not available.', 'warning')
                return redirect(url_for('writing_assessment.writing_tests'))
            
            # Format the assessment for display
            formatted_assessment = format_assessment_for_display(assessment)
            
            # Get the essay text
            user_answers = json.loads(attempt.user_answers)
            essay_text = user_answers.get('essay_text', '')
            
            return render_template(
                'practice/writing_results.html',
                assessment=formatted_assessment,
                test=test,
                essay_text=essay_text,
                title='IELTS Writing Assessment Results'
            )
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON decode error: {str(e)}")
            flash('The assessment data is corrupted.', 'danger')
            return redirect(url_for('writing_assessment.writing_tests'))
        except Exception as e:
            current_app.logger.error(f"Error displaying results: {str(e)}")
            flash('Sorry, there was a problem displaying the results.', 'danger')
            return redirect(url_for('writing_assessment.writing_tests'))
            
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error loading attempt: {str(e)}")
        db.session.rollback()
        flash('Error loading assessment data.', 'danger')
        return redirect(url_for('writing_assessment.writing_tests'))

# Add route for history/previous assessments
@writing_assessment_bp.route('/history')
@login_required
def assessment_history():
    """Show user's writing assessment history."""
    try:
        # Get all writing test attempts by this user
        attempts = UserTestAttempt.query.join(
            PracticeTest, UserTestAttempt.test_id == PracticeTest.id
        ).filter(
            UserTestAttempt.user_id == current_user.id,
            PracticeTest.test_type == 'writing'
        ).order_by(
            UserTestAttempt.attempt_date.desc()
        ).all()
        
        return render_template(
            'practice/writing_history.html',
            attempts=attempts,
            title='My Writing Assessment History'
        )
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in assessment history: {str(e)}")
        db.session.rollback()
        flash('Error loading your assessment history.', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        current_app.logger.error(f"Error in assessment history: {str(e)}")
        flash('An error occurred while loading your assessment history.', 'danger')
        return redirect(url_for('index'))