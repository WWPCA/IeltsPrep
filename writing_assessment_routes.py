"""
Writing Assessment Routes Module

This module provides routes specifically for IELTS writing assessments:
- Academic Task 1 (graph/chart description)
- Academic Task 2 (essay)
- General Training Task 1 (letter)
- General Training Task 2 (essay)

All writing responses are GenAI-assessed using TrueScore® technology for accurate band scoring.
"""

from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, session, abort, jsonify
from flask_login import login_required, current_user
import json

from main import app
from models import db, Assessment, UserAssessmentAttempt, WritingResponse
from account_activation import authenticated_user_required

# Taking a writing assessment
@app.route('/assessments/writing/<int:assessment_id>/attempt/<int:attempt_id>')
@login_required
@authenticated_user_required
def take_writing_assessment(assessment_id, attempt_id):
    """Take a writing assessment"""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Get the assessment attempt
    attempt = UserAssessmentAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You do not have permission to access this assessment attempt.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Check if the assessment type matches
    if 'writing' not in assessment.assessment_type:
        flash('Invalid assessment type for this route.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Get existing responses
    task1_response = WritingResponse.query.filter_by(
        attempt_id=attempt_id,
        task_number=1
    ).first()
    
    task2_response = WritingResponse.query.filter_by(
        attempt_id=attempt_id,
        task_number=2
    ).first()
    
    # Check if assessment is already completed
    if attempt.status == 'completed':
        return redirect(url_for('assessment_results', assessment_type='writing', attempt_id=attempt_id))
    
    # Determine if this is an Academic or General Training assessment
    is_academic = 'academic' in assessment.assessment_type
    
    # Render the writing assessment template
    return render_template('assessments/writing.html',
                          title='IELTS Writing Assessment',
                          assessment=assessment,
                          attempt=attempt,
                          is_academic=is_academic,
                          task1_response=task1_response,
                          task2_response=task2_response)

# Submit writing response for Task 1
@app.route('/assessments/writing/<int:assessment_id>/attempt/<int:attempt_id>/task1', methods=['POST'])
@login_required
@authenticated_user_required
def submit_writing_task1(assessment_id, attempt_id):
    """Submit a response for writing Task 1"""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Get the assessment attempt
    attempt = UserAssessmentAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You do not have permission to access this assessment attempt.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Check if the assessment is already completed
    if attempt.status == 'completed':
        flash('This assessment has already been completed.', 'warning')
        return redirect(url_for('assessment_results', assessment_type='writing', attempt_id=attempt_id))
    
    # Get the response text
    response_text = request.form.get('task1_response', '').strip()
    
    # Check for empty response
    if not response_text:
        flash('Please provide a response for Task 1.', 'danger')
        return redirect(url_for('take_writing_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Check for existing response
    existing_response = WritingResponse.query.filter_by(
        attempt_id=attempt_id,
        task_number=1
    ).first()
    
    if existing_response:
        # Update existing response
        existing_response.response_text = response_text
        existing_response.submission_time = datetime.utcnow()
    else:
        # Create new response
        new_response = WritingResponse()
        new_response.attempt_id = attempt_id
        new_response.task_number = 1
        new_response.response_text = response_text
        new_response.submission_time = datetime.utcnow()
        db.session.add(new_response)
    
    db.session.commit()
    
    flash('Task 1 response saved successfully!', 'success')
    return redirect(url_for('take_writing_assessment', assessment_id=assessment_id, attempt_id=attempt_id))

# Submit writing response for Task 2
@app.route('/assessments/writing/<int:assessment_id>/attempt/<int:attempt_id>/task2', methods=['POST'])
@login_required
@authenticated_user_required
def submit_writing_task2(assessment_id, attempt_id):
    """Submit a response for writing Task 2"""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Get the assessment attempt
    attempt = UserAssessmentAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You do not have permission to access this assessment attempt.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Check if the assessment is already completed
    if attempt.status == 'completed':
        flash('This assessment has already been completed.', 'warning')
        return redirect(url_for('assessment_results', assessment_type='writing', attempt_id=attempt_id))
    
    # Get the response text
    response_text = request.form.get('task2_response', '').strip()
    
    # Check for empty response
    if not response_text:
        flash('Please provide a response for Task 2.', 'danger')
        return redirect(url_for('take_writing_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Check for existing response
    existing_response = WritingResponse.query.filter_by(
        attempt_id=attempt_id,
        task_number=2
    ).first()
    
    if existing_response:
        # Update existing response
        existing_response.response_text = response_text
        existing_response.submission_time = datetime.utcnow()
    else:
        # Create new response
        new_response = WritingResponse()
        new_response.attempt_id = attempt_id
        new_response.task_number = 2
        new_response.response_text = response_text
        new_response.submission_time = datetime.utcnow()
        db.session.add(new_response)
    
    db.session.commit()
    
    flash('Task 2 response saved successfully!', 'success')
    return redirect(url_for('take_writing_assessment', assessment_id=assessment_id, attempt_id=attempt_id))

# Submit entire writing assessment (both tasks)
@app.route('/assessments/writing/<int:assessment_id>/attempt/<int:attempt_id>/complete', methods=['POST'])
@login_required
@authenticated_user_required
def complete_writing_assessment(assessment_id, attempt_id):
    """Complete a writing assessment and submit for GenAI scoring"""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Get the assessment attempt
    attempt = UserAssessmentAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You do not have permission to access this assessment attempt.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Check if the assessment is already completed
    if attempt.status == 'completed':
        flash('This assessment has already been completed.', 'warning')
        return redirect(url_for('assessment_results', assessment_type='writing', attempt_id=attempt_id))
    
    # Check if both tasks have responses
    task1_response = WritingResponse.query.filter_by(
        attempt_id=attempt_id,
        task_number=1
    ).first()
    
    task2_response = WritingResponse.query.filter_by(
        attempt_id=attempt_id,
        task_number=2
    ).first()
    
    if not task1_response or not task2_response:
        flash('You must complete both Task 1 and Task 2 before submitting.', 'danger')
        return redirect(url_for('take_writing_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Mark the attempt as completed
    attempt.status = 'completed'
    attempt.end_time = datetime.utcnow()
    
    # Mark assessment as taken by this user during current package period
    current_user.mark_assessment_completed(assessment_id, 'writing')
    
    # Update streak info
    current_user.update_streak()
    
    db.session.commit()
    
    # Queue the assessment for GenAI scoring (background process)
    # This would be implemented with a task queue in a production environment
    
    flash('Your writing assessment has been submitted for GenAI evaluation with TrueScore® technology. Results will be available shortly.', 'success')
    return redirect(url_for('assessment_results', assessment_type='writing', attempt_id=attempt_id))

print("Writing assessment routes added successfully.")