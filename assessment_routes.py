"""
Assessment Routes Module

This module provides the main routes for handling IELTS GenAI Assessments.
It defines the index, listings, and common functionality for all assessment types.
"""

from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, flash, session, abort, jsonify
from flask_login import login_required, current_user
import json
import logging

from app import app
from models import db, Assessment, UserAssessmentAttempt
from account_activation import authenticated_user_required


@app.route('/assessments')
@login_required
def assessment_index():
    """Display the main assessment landing page."""
    # Check if user has an active assessment package
    has_package = current_user.has_active_assessment_package()
    
    # Get user's assessment preference (academic or general)
    assessment_type = current_user.assessment_preference
    
    return render_template('assessments/index.html',
                          title='IELTS GenAI Assessments',
                          has_package=has_package,
                          assessment_type=assessment_type)


@app.route('/assessments/<assessment_type>')
@login_required
@authenticated_user_required
def assessment_list(assessment_type):
    """Display a list of assessments for a specific type."""
    valid_types = ['listening', 'reading', 'writing', 'speaking']
    
    if assessment_type not in valid_types:
        flash(f'Invalid assessment type: {assessment_type}', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Get user's assessment preference (academic or general)
    user_preference = current_user.assessment_preference
    
    # Determine the full assessment type based on user preference and requested type
    full_assessment_type = f'{user_preference}_{assessment_type}'
    
    # Get all active assessments of the requested type
    assessments = Assessment.query.filter_by(
        assessment_type=full_assessment_type,
        status='active'
    ).all()
    
    # Get list of assessments user has already completed
    completed_assessments = current_user.completed_assessments
    
    return render_template('assessments/list.html',
                          title=f'{assessment_type.capitalize()} Assessments',
                          assessment_type=assessment_type,
                          assessments=assessments,
                          has_package=True,
                          completed_assessments=completed_assessments)


@app.route('/assessments/<assessment_type>/<int:assessment_id>', endpoint='assessment_details_new')
@login_required
@authenticated_user_required
def assessment_details_new(assessment_type, assessment_id):
    """Show details about an assessment before starting it."""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Check if the assessment type matches
    if assessment_type not in assessment.assessment_type:
        flash('Invalid assessment type for this assessment.', 'danger')
        return redirect(url_for('assessment_list', assessment_type=assessment_type))
    
    # Check if user has already completed this assessment
    already_completed = current_user.has_taken_assessment(assessment_id, assessment_type)
    
    # If this is a speaking-only package, check available attempts
    is_speaking_only = current_user.is_speaking_only_user()
    remaining_speaking = current_user.get_remaining_speaking_assessments() if is_speaking_only else None
    
    return render_template('assessment_details.html',
                          title=assessment.title,
                          assessment=assessment,
                          assessment_type=assessment_type,
                          already_completed=already_completed,
                          is_speaking_only=is_speaking_only,
                          remaining_speaking=remaining_speaking)


@app.route('/assessments/<assessment_type>/<int:assessment_id>/start', methods=['POST'])
@login_required
@authenticated_user_required
def start_assessment(assessment_type, assessment_id):
    """Start a new assessment attempt."""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Check if the assessment type matches
    if assessment_type not in assessment.assessment_type:
        flash('Invalid assessment type for this assessment.', 'danger')
        return redirect(url_for('assessment_list', assessment_type=assessment_type))
    
    # If this is a speaking-only package and the assessment is speaking,
    # check if they have any attempts remaining
    if assessment_type == 'speaking' and current_user.is_speaking_only_user():
        remaining = current_user.get_remaining_speaking_assessments()
        if remaining <= 0:
            flash('You have used all your available speaking assessments. Purchase a new package to continue.', 'danger')
            return redirect(url_for('assessment_details_new', assessment_type=assessment_type, assessment_id=assessment_id))
    
    # Create a new assessment attempt
    new_attempt = UserAssessmentAttempt()
    new_attempt.user_id = current_user.id
    new_attempt.assessment_id = assessment_id
    new_attempt.assessment_type = assessment_type
    new_attempt.status = 'in_progress'
    new_attempt.start_time = datetime.utcnow()
    
    db.session.add(new_attempt)
    db.session.commit()
    
    # Redirect to the appropriate assessment route based on type
    if assessment_type == 'writing':
        return redirect(url_for('take_writing_assessment', assessment_id=assessment_id, attempt_id=new_attempt.id))
    elif assessment_type == 'speaking':
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=new_attempt.id))
    elif assessment_type == 'reading':
        return redirect(url_for('take_reading_assessment', assessment_id=assessment_id, attempt_id=new_attempt.id))
    elif assessment_type == 'listening':
        return redirect(url_for('take_listening_assessment', assessment_id=assessment_id, attempt_id=new_attempt.id))
    else:
        flash('Invalid assessment type', 'danger')
        return redirect(url_for('assessment_index'))


@app.route('/assessments/results/<assessment_type>/<int:attempt_id>')
@login_required
def assessment_results(assessment_type, attempt_id):
    """Show results for a completed assessment attempt."""
    # Get the assessment attempt
    attempt = UserAssessmentAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You do not have permission to view these results.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Ensure the attempt is completed
    if attempt.status != 'completed':
        flash('This assessment has not been completed yet.', 'info')
        
        # Redirect based on assessment type
        if assessment_type == 'writing':
            return redirect(url_for('take_writing_assessment', assessment_id=attempt.assessment_id, attempt_id=attempt.id))
        elif assessment_type == 'speaking':
            return redirect(url_for('take_speaking_assessment', assessment_id=attempt.assessment_id, attempt_id=attempt.id))
        else:
            return redirect(url_for('assessment_index'))
    
    # Get the assessment
    assessment = Assessment.query.get_or_404(attempt.assessment_id)
    
    # Render the appropriate results template based on assessment type
    return render_template(f'assessments/{assessment_type}_results.html',
                          title='Assessment Results',
                          attempt=attempt,
                          assessment=assessment,
                          assessment_type=assessment_type)


@app.route('/assessments/history')
@login_required
@authenticated_user_required
def assessment_history():
    """Display a user's assessment history."""
    # Get all completed assessment attempts for this user
    attempts = UserAssessmentAttempt.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(UserAssessmentAttempt.end_time.desc()).all()
    
    # Group attempts by assessment type
    grouped_attempts = {
        'writing': [],
        'speaking': [],
        'reading': [],
        'listening': []
    }
    
    for attempt in attempts:
        if attempt.assessment_type in grouped_attempts:
            grouped_attempts[attempt.assessment_type].append(attempt)
    
    return render_template('assessment_history.html',
                          title='Assessment History',
                          grouped_attempts=grouped_attempts)


@app.route('/assessments/update-preference', methods=['POST'])
@login_required
def update_assessment_preference():
    """Update a user's assessment preference (academic or general)."""
    preference = request.form.get('assessment_preference')
    
    if preference not in ['academic', 'general']:
        flash('Invalid assessment preference.', 'danger')
        return redirect(url_for('assessment_index'))
    
    current_user.assessment_preference = preference
    db.session.commit()
    
    flash(f'Your assessment preference has been updated to {preference.capitalize()}.', 'success')
    return redirect(url_for('assessment_index'))

print("Assessment routes added successfully.")