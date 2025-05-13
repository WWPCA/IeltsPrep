"""
Speaking Assessment Routes Module

This module provides routes specifically for IELTS speaking assessments:
- Part 1 (Introduction and interview)
- Part 2 (Individual long turn)
- Part 3 (Two-way discussion)

All speaking responses are GenAI-assessed using Elaris® technology for accurate band scoring.
"""

from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, session, abort, jsonify
from flask_login import login_required, current_user
import os
import json

from main import app
from models import db, Assessment, UserAssessmentAttempt, SpeakingResponse
from account_activation import authenticated_user_required

# Taking a speaking assessment
@app.route('/assessments/speaking/<int:assessment_id>/attempt/<int:attempt_id>')
@login_required
@authenticated_user_required
def take_speaking_assessment(assessment_id, attempt_id):
    """Take a speaking assessment"""
    # Get the assessment
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Get the assessment attempt
    attempt = UserAssessmentAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You do not have permission to access this assessment attempt.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Check if the assessment type matches
    if 'speaking' not in assessment.assessment_type:
        flash('Invalid assessment type for this route.', 'danger')
        return redirect(url_for('assessment_index'))
    
    # Get existing responses
    part1_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=1
    ).first()
    
    part2_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=2
    ).first()
    
    part3_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=3
    ).first()
    
    # Check if assessment is already completed
    if attempt.status == 'completed':
        return redirect(url_for('assessment_results', assessment_type='speaking', attempt_id=attempt_id))
    
    # Determine if this is an Academic or General Training assessment
    is_academic = 'academic' in assessment.assessment_type
    
    # Render the speaking assessment template
    return render_template('assessments/speaking.html',
                          title='IELTS Speaking Assessment',
                          assessment=assessment,
                          attempt=attempt,
                          is_academic=is_academic,
                          part1_response=part1_response,
                          part2_response=part2_response,
                          part3_response=part3_response)

# Submit speaking response for Part 1
@app.route('/assessments/speaking/<int:assessment_id>/attempt/<int:attempt_id>/part1', methods=['POST'])
@login_required
@authenticated_user_required
def submit_speaking_part1(assessment_id, attempt_id):
    """Submit a response for speaking Part 1"""
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
        return redirect(url_for('assessment_results', assessment_type='speaking', attempt_id=attempt_id))
    
    # Get the audio file
    if 'audio_file' not in request.files:
        flash('No audio file provided.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        flash('No audio file selected.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Save the audio file
    upload_folder = os.path.join('static', 'uploads', 'speaking')
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = f'user_{current_user.id}_assessment_{assessment_id}_attempt_{attempt_id}_part1_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.webm'
    filepath = os.path.join(upload_folder, filename)
    
    audio_file.save(filepath)
    
    # Check for existing response
    existing_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=1
    ).first()
    
    if existing_response:
        # Update existing response
        existing_response.audio_filename = filename
        existing_response.submission_time = datetime.utcnow()
    else:
        # Create new response
        new_response = SpeakingResponse()
        new_response.attempt_id = attempt_id
        new_response.part_number = 1
        new_response.audio_filename = filename
        new_response.submission_time = datetime.utcnow()
        db.session.add(new_response)
    
    db.session.commit()
    
    flash('Part 1 response submitted successfully!', 'success')
    return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))

# Submit speaking response for Part 2
@app.route('/assessments/speaking/<int:assessment_id>/attempt/<int:attempt_id>/part2', methods=['POST'])
@login_required
@authenticated_user_required
def submit_speaking_part2(assessment_id, attempt_id):
    """Submit a response for speaking Part 2"""
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
        return redirect(url_for('assessment_results', assessment_type='speaking', attempt_id=attempt_id))
    
    # Get the audio file
    if 'audio_file' not in request.files:
        flash('No audio file provided.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        flash('No audio file selected.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Save the audio file
    upload_folder = os.path.join('static', 'uploads', 'speaking')
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = f'user_{current_user.id}_assessment_{assessment_id}_attempt_{attempt_id}_part2_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.webm'
    filepath = os.path.join(upload_folder, filename)
    
    audio_file.save(filepath)
    
    # Check for existing response
    existing_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=2
    ).first()
    
    if existing_response:
        # Update existing response
        existing_response.audio_filename = filename
        existing_response.submission_time = datetime.utcnow()
    else:
        # Create new response
        new_response = SpeakingResponse()
        new_response.attempt_id = attempt_id
        new_response.part_number = 2
        new_response.audio_filename = filename
        new_response.submission_time = datetime.utcnow()
        db.session.add(new_response)
    
    db.session.commit()
    
    flash('Part 2 response submitted successfully!', 'success')
    return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))

# Submit speaking response for Part 3
@app.route('/assessments/speaking/<int:assessment_id>/attempt/<int:attempt_id>/part3', methods=['POST'])
@login_required
@authenticated_user_required
def submit_speaking_part3(assessment_id, attempt_id):
    """Submit a response for speaking Part 3"""
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
        return redirect(url_for('assessment_results', assessment_type='speaking', attempt_id=attempt_id))
    
    # Get the audio file
    if 'audio_file' not in request.files:
        flash('No audio file provided.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        flash('No audio file selected.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Save the audio file
    upload_folder = os.path.join('static', 'uploads', 'speaking')
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = f'user_{current_user.id}_assessment_{assessment_id}_attempt_{attempt_id}_part3_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.webm'
    filepath = os.path.join(upload_folder, filename)
    
    audio_file.save(filepath)
    
    # Check for existing response
    existing_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=3
    ).first()
    
    if existing_response:
        # Update existing response
        existing_response.audio_filename = filename
        existing_response.submission_time = datetime.utcnow()
    else:
        # Create new response
        new_response = SpeakingResponse(
            attempt_id=attempt_id,
            part_number=3,
            audio_filename=filename,
            submission_time=datetime.utcnow()
        )
        db.session.add(new_response)
    
    db.session.commit()
    
    flash('Part 3 response submitted successfully!', 'success')
    return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))

# Submit entire speaking assessment (all three parts)
@app.route('/assessments/speaking/<int:assessment_id>/attempt/<int:attempt_id>/complete', methods=['POST'])
@login_required
@authenticated_user_required
def complete_speaking_assessment(assessment_id, attempt_id):
    """Complete a speaking assessment and submit for GenAI scoring"""
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
        return redirect(url_for('assessment_results', assessment_type='speaking', attempt_id=attempt_id))
    
    # Check if all parts have responses
    part1_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=1
    ).first()
    
    part2_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=2
    ).first()
    
    part3_response = SpeakingResponse.query.filter_by(
        attempt_id=attempt_id,
        part_number=3
    ).first()
    
    if not part1_response or not part2_response or not part3_response:
        flash('You must complete all three parts before submitting.', 'danger')
        return redirect(url_for('take_speaking_assessment', assessment_id=assessment_id, attempt_id=attempt_id))
    
    # Mark the attempt as completed
    attempt.status = 'completed'
    attempt.end_time = datetime.utcnow()
    
    # Mark assessment as taken by this user during current package period
    current_user.mark_assessment_completed(assessment_id, 'speaking')
    
    # Update streak info
    current_user.update_streak()
    
    # If this is a speaking-only package, log the usage
    if current_user.is_speaking_only_user():
        current_user.use_speaking_assessment()
    
    db.session.commit()
    
    # Queue the assessment for GenAI scoring (background process)
    # This would be implemented with a task queue in a production environment
    
    flash('Your speaking assessment has been submitted for GenAI evaluation with Elaris® technology. Results will be available shortly.', 'success')
    return redirect(url_for('assessment_results', assessment_type='speaking', attempt_id=attempt_id))

print("Speaking assessment routes added successfully.")