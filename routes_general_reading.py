"""
Routes for General Training Reading tests.
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime
from app import app, db
from models import PracticeTest, CompletePracticeTest, UserTestAttempt
import json

@app.route('/practice/general-reading/<int:test_id>')
@login_required
def general_reading_test(test_id):
    """
    Display a General Training Reading test.
    This route will select the appropriate template based on the question type.
    """
    # Get the test details
    test = PracticeTest.query.get_or_404(test_id)
    
    # Verify that this is a General Training Reading test
    if test.test_type != 'reading' or test.ielts_test_type != 'general':
        flash('Invalid test type', 'danger')
        return redirect(url_for('practice_tests'))
    
    # Determine which template to use based on the section number
    template_map = {
        1: 'general_reading_multiple_choice.html',
        2: 'general_reading_true_false_not_given.html',
        3: 'general_reading_matching_information.html',
        4: 'general_reading_matching_features.html',
        5: 'general_reading_summary_completion.html',
        6: 'general_reading_note_completion.html',
        7: 'general_reading_sentence_completion.html'
    }
    
    template = template_map.get(test.section, 'general_reading_multiple_choice.html')
    
    # Parse questions and answers
    questions = test.questions
    
    # Record the test attempt
    attempt = UserTestAttempt(
        user_id=current_user.id,
        test_id=test.id,
        _user_answers=json.dumps({})  # Empty user answers initially
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Store the attempt ID in the session
    session['current_attempt_id'] = attempt.id
    
    return render_template(
        f'practice/{template}', 
        test=test, 
        attempt_id=attempt.id,
        passage=test._content,
        questions=questions
    )

@app.route('/practice/general-reading/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_general_reading_test(test_id):
    """Submit a General Training Reading test."""
    test = PracticeTest.query.get_or_404(test_id)
    
    # Get the user's answers from the form
    answers = {}
    form_data = request.form.to_dict(flat=False)  # Get all form data including multiple values
    
    # Handle different question types
    if test.section == 1:  # Multiple Choice (two answers per question)
        for i in range(1, 6):  # Multiple Choice typically has 5 questions
            question_key = f'q{i}'
            if question_key in form_data:
                # Convert list of answers to sorted string (e.g., ['B', 'D'] -> 'BD')
                answers[str(i)] = ''.join(sorted(form_data[question_key]))
    else:  # Other question types (one answer per question)
        for key in request.form:
            if key.startswith('q'):
                question_number = key[1:]  # Extract the question number
                answers[question_number] = request.form[key]
    
    # Calculate the score
    correct_answers = json.loads(test._answers)
    total_questions = len(correct_answers)
    correct_count = 0
    
    # Check answers based on question type
    if test.section == 1:  # Multiple Choice (two answers)
        for question_number, correct_answer in correct_answers.items():
            # For multiple choice, both answers must be correct
            # Convert to sorted string for comparison (e.g., 'BD' == 'BD')
            user_answer = answers.get(question_number, '')
            expected_answer = ''.join(sorted([correct_answers.get(question_number, ''), correct_answers.get(f"{question_number}_2", '')]))
            if user_answer == expected_answer:
                correct_count += 1
    else:  # Other question types
        for question_number, user_answer in answers.items():
            if question_number in correct_answers and user_answer == correct_answers[question_number]:
                correct_count += 1
    
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Update the attempt as complete
    attempt_id = session.get('current_attempt_id')
    if attempt_id:
        attempt = UserTestAttempt.query.get(attempt_id)
        if attempt and attempt.user_id == current_user.id:
            attempt.score = score
            attempt._user_answers = json.dumps(answers)
            db.session.commit()
    
    # Mark the test as completed for this user
    current_user.mark_test_completed(test_id, 'reading')
    db.session.commit()
    
    # Redirect to results page
    return redirect(url_for('reading_test_results', test_id=test_id, attempt_id=attempt_id))

@app.route('/practice/general-reading/<int:test_id>/results/<int:attempt_id>')
@login_required
def reading_test_results(test_id, attempt_id):
    """Display results for a General Training Reading test."""
    test = PracticeTest.query.get_or_404(test_id)
    attempt = UserTestAttempt.query.get_or_404(attempt_id)
    
    # Verify that this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You are not authorized to view these results', 'danger')
        return redirect(url_for('practice_tests'))
    
    # Get the user's answers and the correct answers
    user_answers = json.loads(attempt._user_answers) if attempt._user_answers else {}
    correct_answers = json.loads(test._answers) if test._answers else {}
    
    # Calculate score details
    total_questions = len(correct_answers)
    correct_count = 0
    
    # Check answers based on question type
    if test.section == 1:  # Multiple Choice (two answers)
        for question_number, correct_answer in correct_answers.items():
            # For multiple choice, both answers must be correct
            user_answer = user_answers.get(question_number, '')
            expected_answer = ''.join(sorted([correct_answers.get(question_number, ''), correct_answers.get(f"{question_number}_2", '')]))
            if user_answer == expected_answer:
                correct_count += 1
    else:  # Other question types
        for question_number, correct_answer in correct_answers.items():
            if question_number in user_answers and user_answers[question_number] == correct_answer:
                correct_count += 1
    
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    return render_template('practice/reading_test_results.html', 
                          test=test, 
                          attempt=attempt,
                          user_answers=user_answers,
                          correct_answers=correct_answers,
                          score=score,
                          correct_count=correct_count,
                          total_questions=total_questions)