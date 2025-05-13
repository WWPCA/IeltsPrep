"""
IELTS Speaking Assessment Routes
This module provides routes for assessing IELTS speaking responses using AssemblyAI and GPT-4o.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import db, Assessment, User, SpeakingPrompt, SpeakingResponse, AssessmentSession
from assemblyai_services import process_speaking_response, assess_existing_transcription
import json
import os
import base64
import tempfile
from datetime import datetime, timedelta
from utils import compress_audio
from aws_services import generate_polly_speech
import gcp_storage

speaking_assessment = Blueprint('speaking_assessment', __name__)

@speaking_assessment.route('/speaking/recovery_check/<int:test_id>', methods=['GET'])
@login_required
def check_for_unfinished_session(test_id):
    """
    Check if a user has an unfinished speaking assessment session
    """
    test = Assessment.query.get_or_404(test_id)
    
    # Determine the product ID based on the test type
    product_id = None
    if test.test_type == "speaking":
        if test.ielts_test_type == "academic":
            product_id = "academic_speaking"
        else:
            product_id = "general_speaking"
    
    if not product_id:
        return jsonify({"has_unfinished_session": False})
    
    # Check for unfinished session
    unfinished_session = AssessmentSession.get_active_session(current_user.id, product_id)
    
    if unfinished_session:
        # Check if the session is less than 24 hours old - only allow recovery for recent sessions
        session_age = datetime.utcnow() - unfinished_session.started_at
        if session_age < timedelta(hours=24):
            return jsonify({
                "has_unfinished_session": True,
                "session_id": unfinished_session.id,
                "started_at": unfinished_session.started_at.isoformat()
            })
    
    return jsonify({"has_unfinished_session": False})

@speaking_assessment.route('/speaking/submit_response/<int:test_id>', methods=['POST'])
@login_required
def submit_speaking_response(test_id):
    """
    Submit a speaking response for assessment
    """
    try:
        # Get the test
        test = Assessment.query.get_or_404(test_id)
        
        # Verify user has access to this test
        if not test.is_free and not current_user.has_active_assessment_package():
            flash("You must be subscribed to submit this test.", "danger")
            return redirect(url_for('practice.test_details', test_type='speaking', test_id=test_id))
        
        # Check if user has already taken this test without having an unfinished session
        if current_user.has_taken_test(test_id, 'speaking'):
            # Determine the product ID based on the test type
            product_id = None
            if test.ielts_test_type == "academic":
                product_id = "academic_speaking"
            else:
                product_id = "general_speaking"
            
            # Check if there's an unfinished session that would allow retaking
            unfinished_session = None
            if product_id:
                unfinished_session = AssessmentSession.get_active_session(current_user.id, product_id)
            
            # If there's no unfinished session, don't allow retaking
            if not unfinished_session:
                flash("You have already taken this test. Each assessment can only be taken once to keep costs manageable.", "warning")
                
                # Find their previous attempt to display results
                previous_attempt = UserTestAttempt.query.filter_by(
                    user_id=current_user.id,
                    test_id=test_id
                ).order_by(UserTestAttempt.attempt_date.desc()).first()
                
                if previous_attempt:
                    return redirect(url_for('speaking_assessment.speaking_assessment_results', attempt_id=previous_attempt.id))
                else:
                    return redirect(url_for('practice.test_details', test_type='speaking', test_id=test_id))
            else:
                # If there's an unfinished session, mark it as complete before continuing
                unfinished_session.mark_complete()
        
        # Determine the product ID based on the test type for creating a new session
        product_id = None
        if test.ielts_test_type == "academic":
            product_id = "academic_speaking"
        else:
            product_id = "general_speaking"
        
        # Create a new session
        if product_id:
            # Create or update the session
            session_record = AssessmentSession.create_session(current_user.id, product_id, test_id)
        
        # Get the audio file from the request
        audio_blob = request.form.get('audio_blob')
        
        # Initialize user_answers variable to ensure it's always defined
        user_answers = {
            'transcription': '',
            'audio_url': ''  # Explicitly empty for privacy
        }
        
        if not audio_blob:
            flash("No audio recording was provided.", "danger")
            return redirect(url_for('practice.take_test', test_type='speaking', test_id=test_id))
        
        # Decode the audio data
        audio_data = base64.b64decode(audio_blob.split(',')[1])
        
        # Create a temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_audio_path = temp_file.name
        
        # Compress the audio file
        compressed_path = compress_audio(temp_audio_path)
        
        # Get the test data
        test_questions = test.questions
        
        # Determine speaking part number (1, 2, or 3) based on test section
        part_number = min(3, max(1, test.section))
        
        # Get the speaking prompt
        prompt_text = test_questions[0]['question'] if test_questions else ''
        
        try:
            # Check if we have both ASSEMBLY_API_KEY and OPENAI_API_KEY
            if 'ASSEMBLY_API_KEY' in os.environ and 'OPENAI_API_KEY' in os.environ:
                # Process the speaking response using AssemblyAI + GPT-4o
                assessment = process_speaking_response(compressed_path, prompt_text, part_number)
                
                # The following will be our assessment_id after the record is created
                assessment_id = None  
                
                # Store transcript and assessment in GCP storage if available
                if gcp_storage.is_available():
                    try:
                        # Store transcript data - we'll update the paths after attempt is created
                        transcript_data = {
                            'test_id': test.id,
                            'prompt': prompt_text,
                            'transcription': assessment.get('transcription', '')
                        }
                        
                        # We'll set these fields in user_answers and move them to DB columns later
                        user_answers = {
                            'transcription': assessment.get('transcription', ''),
                            'audio_url': '',  # Explicitly empty for privacy
                            'needs_gcp_update': True  # Flag to update after we have attempt.id
                        }
                    except Exception as gcp_error:
                        print(f"Warning: Failed to prepare GCP data: {str(gcp_error)}")
                        # Continue with process - local storage is used as fallback
                        user_answers = {
                            'transcription': assessment.get('transcription', ''),
                            'audio_url': ''  # Explicitly empty for privacy
                        }
                else:
                    user_answers = {
                        'transcription': assessment.get('transcription', ''),
                        'audio_url': ''  # Explicitly empty for privacy
                    }
                
                # Get the overall band score
                overall_band_score = assessment.get('overall_band', 0)
            else:
                # Missing API key(s)
                transcription = "Transcription service unavailable. Please ask administrator to set up ASSEMBLY_API_KEY and OPENAI_API_KEY."
                assessment = {
                    "error": "Assessment service unavailable.",
                    "transcription": transcription,
                    "scores": {
                        "Fluency and Coherence": 5,
                        "Lexical Resource": 5,
                        "Grammatical Range and Accuracy": 5,
                        "Pronunciation": 5
                    },
                    "overall_band": 5,
                    "overall_feedback": "Assessment service unavailable. Please contact support."
                }
                overall_band_score = 5.0
                
                # Initialize user_answers for the fallback case
                user_answers = {
                    'transcription': transcription,
                    'audio_url': ''  # Explicitly empty for privacy
                }
        finally:
            # Delete temporary audio files regardless of assessment outcome
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(compressed_path) and compressed_path != temp_audio_path:
                    os.remove(compressed_path)
            except Exception as e:
                print(f"Error deleting temporary audio files: {str(e)}")
        
        # Create a new attempt record - audio not saved, only the transcription and assessment
        attempt = UserTestAttempt()
        attempt.user_id = current_user.id
        attempt.test_id = test_id
        attempt._user_answers = json.dumps(user_answers)
        attempt.score = overall_band_score
        attempt.assessment = json.dumps(assessment)
        
        # If this is part of a complete test, link it to the test progress
        complete_test_progress_id = session.get('complete_test_progress_id')
        if complete_test_progress_id:
            attempt.complete_test_progress_id = complete_test_progress_id
            test_progress = CompleteTestProgress.query.get(complete_test_progress_id)
            if test_progress:
                # Mark this section as completed
                test_progress.mark_section_completed('speaking', overall_band_score)
                
                # Update progress current section
                if test_progress.is_test_completed():
                    test_progress.current_section = None
                else:
                    test_progress.current_section = test_progress.get_next_section()
                    
                db.session.add(test_progress)
        
        db.session.add(attempt)
        
        # Update the user's speaking scores
        speaking_scores = current_user.speaking_scores
        speaking_scores.append({
            'date': datetime.utcnow().isoformat(),
            'test_id': test_id,
            'band_score': overall_band_score,
            'fluency': assessment.get('scores', {}).get('Fluency and Coherence', 0),
            'vocabulary': assessment.get('scores', {}).get('Lexical Resource', 0),
            'grammar': assessment.get('scores', {}).get('Grammatical Range and Accuracy', 0),
            'pronunciation': assessment.get('scores', {}).get('Pronunciation', 0)
        })
        current_user.speaking_scores = speaking_scores
        
        # Mark test as completed for this user
        current_user.mark_test_completed(test_id, 'speaking')
        
        # Update the user's streak
        current_user.update_streak()
        
        # Mark any active session as completed successfully
        if product_id:
            session_record = AssessmentSession.get_active_session(current_user.id, product_id)
            if session_record:
                session_record.mark_complete()
                session_record.mark_submitted()
        
        # Commit the changes to get an ID for our new attempt
        db.session.commit()
        
        # Now that we have attempt.id, update GCP paths if needed
        if user_answers.get('needs_gcp_update', False) and gcp_storage.is_available():
            try:
                # Store transcript in GCP with the attempt ID
                transcript_data = {
                    'test_id': test.id,
                    'prompt': prompt_text,
                    'transcription': assessment.get('transcription', '')
                }
                
                # Calculate transcript expiry date (6 months from now)
                expiry_date = datetime.utcnow() + timedelta(days=180)
                
                # Store in GCP with appropriate metadata
                transcript_success, transcript_path = gcp_storage.store_transcript(
                    user_id=current_user.id,
                    assessment_id=attempt.id,
                    transcript_data=transcript_data,
                    metadata={
                        'test_type': 'speaking',
                        'expiry_date': expiry_date.isoformat()
                    }
                )
                
                # Store assessment data separately (kept indefinitely)
                assessment_data = {key: value for key, value in assessment.items() if key != 'transcription'}
                assessment_success, assessment_path = gcp_storage.store_assessment(
                    user_id=current_user.id,
                    assessment_id=attempt.id,
                    assessment_data=assessment_data
                )
                
                # Update attempt with GCP storage paths
                if transcript_success:
                    attempt.gcp_transcript_path = transcript_path
                    attempt.transcript_expiry_date = expiry_date
                
                if assessment_success:
                    attempt.gcp_assessment_path = assessment_path
                
                # Remove temporary flags from user_answers
                updated_user_answers = attempt.user_answers
                updated_user_answers.pop('needs_gcp_update', None)
                attempt.user_answers = updated_user_answers
                
                # Commit the updates
                db.session.commit()
                print(f"Successfully stored assessment data in GCP for attempt {attempt.id}")
            except Exception as e:
                print(f"Warning: Failed to update GCP paths: {str(e)}")
                # Don't block the process if this fails
        
        # Redirect to the results page
        return redirect(url_for('speaking_assessment.speaking_assessment_results', attempt_id=attempt.id))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing speaking submission: {str(e)}")
        
        # Mark any active session as failed
        product_id = None
        test = Assessment.query.get(test_id)
        if test and test.assessment_product_id:
            product_id = test.assessment_product_id
            
        if product_id:
            session_record = AssessmentSession.get_active_session(current_user.id, product_id)
            if session_record:
                session_record.mark_failed(reason=str(e)[:255])  # Limit reason length
        
        flash(f"An error occurred while processing your submission. Please try again.", "danger")
        return redirect(url_for('practice.take_test', test_type='speaking', test_id=test_id))

@speaking_assessment.route('/speaking/results/<int:attempt_id>')
@login_required
def speaking_assessment_results(attempt_id):
    """
    Display the results of a speaking assessment
    """
    # Get the attempt
    attempt = UserTestAttempt.query.get_or_404(attempt_id)
    
    # Verify this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash("You are not authorized to view these results.", "danger")
        return redirect(url_for('practice.index'))
    
    # Get the test
    test = PracticeTest.query.get_or_404(attempt.test_id)
    
    # Get the assessment data from GCP if available
    assessment = {}
    if attempt.gcp_assessment_path and gcp_storage.is_available():
        success, gcp_assessment = gcp_storage.retrieve_assessment(
            attempt.gcp_assessment_path, 
            user_id=current_user.id
        )
        if success:
            assessment = gcp_assessment
        else:
            # Fall back to database storage
            assessment = json.loads(attempt.assessment) if attempt.assessment else {}
    else:
        # Use database storage
        assessment = json.loads(attempt.assessment) if attempt.assessment else {}
    
    # Get the user answers
    user_answers = json.loads(attempt.user_answers) if attempt.user_answers else {}
    
    # Get transcript from GCP if available
    transcription = ""
    if attempt.gcp_transcript_path and gcp_storage.is_available() and not attempt.is_transcript_expired():
        success, gcp_transcript = gcp_storage.retrieve_transcript(
            attempt.gcp_transcript_path, 
            user_id=current_user.id
        )
        if success:
            transcription = gcp_transcript.get('transcription', '')
        else:
            transcription = user_answers.get('transcription', '')
    else:
        transcription = user_answers.get('transcription', '')
    
    # Determine if this is part of a complete test
    is_part_of_complete_test = attempt.complete_test_progress_id is not None
    
    # Prepare data for the template
    data = {
        'attempt': attempt,
        'test': test,
        'assessment': assessment,
        'audio_url': user_answers.get('audio_url', ''),
        'transcription': transcription,
        'band_score': round(float(attempt.score or 0), 1),
        'part_number': min(3, max(1, test.section)),
        'is_part_of_complete_test': is_part_of_complete_test,
        'using_gcp_storage': bool(attempt.gcp_transcript_path or attempt.gcp_assessment_path),
        'transcript_expiry_date': attempt.transcript_expiry_date
    }
    
    # Render the results template
    return render_template('practice/speaking_results.html', **data)

@speaking_assessment.route('/api/speaking/assess', methods=['POST'])
@login_required
def api_assess_speaking():
    """
    API endpoint to assess a speaking response
    """
    try:
        # Check if the request has the audio file
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        prompt_text = request.form.get('prompt_text', '')
        part_number = int(request.form.get('part_number', 1))
        
        if not audio_file or not prompt_text:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Create a temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            audio_file.save(temp_file)
            temp_path = temp_file.name
        
        try:
            # Check if we have both ASSEMBLY_API_KEY and OPENAI_API_KEY
            if 'ASSEMBLY_API_KEY' in os.environ and 'OPENAI_API_KEY' in os.environ:
                # Process the speaking response using AssemblyAI + GPT-4o
                assessment = process_speaking_response(temp_path, prompt_text, part_number)
            else:
                # Missing API key(s)
                return jsonify({
                    'error': 'Assessment service unavailable. Please configure ASSEMBLY_API_KEY and OPENAI_API_KEY.'
                }), 500
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Error removing temporary file: {str(e)}")
            
        return jsonify(assessment)
        
    except Exception as e:
        print(f"Error assessing speaking response: {str(e)}")
        return jsonify({'error': str(e)}), 500

@speaking_assessment.route('/api/speaking/generate-audio/<int:prompt_id>', methods=['GET'])
def generate_prompt_audio(prompt_id):
    """
    Generate audio for a speaking prompt using Amazon Polly
    """
    try:
        # Get the speaking prompt
        prompt = SpeakingPrompt.query.get_or_404(prompt_id)
        
        # Check if we already have an audio file for this prompt
        audio_filename = f"prompt_{prompt_id}.mp3"
        audio_path = os.path.join('static', 'audio', 'prompts', audio_filename)
        audio_url = url_for('static', filename=f'audio/prompts/{audio_filename}')
        
        # If the audio file already exists, return it
        if os.path.exists(audio_path):
            return jsonify({
                'success': True,
                'audio_url': audio_url
            })
        
        # Create the directory for storing prompt audio files
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        # Generate the audio using Amazon Polly
        prompt_text = prompt.prompt_text
        
        # Add a gentle introduction to make it sound more like an examiner
        if prompt.part == 1:
            polly_text = f"Let's move on to part one. {prompt_text}"
        elif prompt.part == 2:
            polly_text = f"Now, I'm going to give you a topic. {prompt_text} You have one minute to prepare. You can make notes if you wish."
        elif prompt.part == 3:
            polly_text = f"Let's consider {prompt_text}"
        else:
            polly_text = prompt_text
        
        # Check if AWS credentials are available
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if not aws_access_key or not aws_secret_key:
            return jsonify({
                'success': False,
                'error': 'AWS credentials not available. Contact administrator to configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.'
            }), 403
        
        # Generate the audio file
        success = generate_polly_speech(polly_text, audio_path)
        
        if success:
            return jsonify({
                'success': True,
                'audio_url': audio_url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate audio with Amazon Polly. Please check AWS credentials and permissions.'
            }), 500
            
    except Exception as e:
        print(f"Error generating prompt audio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@speaking_assessment.route('/api/speaking/assess-transcription', methods=['POST'])
@login_required
def api_assess_transcription():
    """
    API endpoint to assess a speaking transcription
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        transcription_text = data.get('transcription')
        prompt_text = data.get('prompt_text')
        part_number = int(data.get('part_number', 1))
        
        if not transcription_text or not prompt_text:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Check if we have OPENAI_API_KEY
        if 'OPENAI_API_KEY' in os.environ:
            # Assess the transcription using GPT-4o
            assessment = assess_existing_transcription(transcription_text, prompt_text, part_number)
        else:
            # Missing API key
            return jsonify({
                'error': 'Assessment service unavailable. Please configure OPENAI_API_KEY.'
            }), 500
            
        return jsonify(assessment)
        
    except Exception as e:
        print(f"Error assessing transcription: {str(e)}")
        return jsonify({'error': str(e)}), 500