"""
Integrate GCP Storage with Speaking Assessment

This script updates the speaking assessment process to store assessment
and transcript data in GCP Storage for improved scalability and privacy.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from flask import current_app
from app import app, db
from models import UserTestAttempt
import gcp_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_speaking_assessment_routes():
    """
    Updates the speaking_assessment_routes.py file to integrate GCP storage.
    """
    # Path to the files
    routes_file = 'speaking_assessment_routes.py'
    
    try:
        # Read the original file
        with open(routes_file, 'r') as f:
            content = f.read()
            
        # Create a backup
        backup_file = f'{routes_file}.bak'
        with open(backup_file, 'w') as f:
            f.write(content)
        logger.info(f"Created backup at {backup_file}")
        
        # Make necessary imports
        if "import gcp_storage" not in content:
            # Find the imports section
            import_section = content.split("\n\n")[0]
            # Add gcp_storage import
            updated_imports = import_section + "\nimport gcp_storage\n"
            content = content.replace(import_section, updated_imports)
            
        # Update handle_speaking_post - this is the function where assessment happens
        if "process_speaking_response" in content and "gcp_storage" not in content:
            # Find the section after assessment is generated
            pattern = "assessment = process_speaking_response(compressed_path, prompt_text, part_number)"
            
            # Add GCP storage logic after assessment is processed
            gcp_integration = """
                assessment = process_speaking_response(compressed_path, prompt_text, part_number)
                
                # Store transcript and assessment in GCP storage if available
                if gcp_storage.is_available():
                    try:
                        # Store transcript data
                        transcript_data = {
                            'test_id': test.id,
                            'prompt': prompt_text,
                            'transcription': assessment.get('transcription', '')
                        }
                        
                        # Calculate transcript expiry date (6 months from now)
                        expiry_date = datetime.utcnow() + timedelta(days=180)  # 6 months retention
                        
                        # Store in GCP with appropriate metadata
                        transcript_success, transcript_path = gcp_storage.store_transcript(
                            user_id=current_user.id,
                            assessment_id=assessment_id,  # Will be stored in user_test_attempt after creation
                            transcript_data=transcript_data,
                            metadata={
                                'test_type': 'speaking',
                                'expiry_date': expiry_date.isoformat()
                            }
                        )
                        
                        # Store assessment data
                        assessment_data = {key: value for key, value in assessment.items() if key != 'transcription'}
                        assessment_success, assessment_path = gcp_storage.store_assessment(
                            user_id=current_user.id,
                            assessment_id=assessment_id,  # Will be stored in user_test_attempt after creation
                            assessment_data=assessment_data
                        )
                        
                        # Add paths to user_answers for storage in UserTestAttempt
                        if transcript_success:
                            user_answers['gcp_transcript_path'] = transcript_path
                        
                        if assessment_success:
                            user_answers['gcp_assessment_path'] = assessment_path
                    
                    except Exception as gcp_error:
                        print(f"Warning: Failed to store in GCP: {str(gcp_error)}")
                        # Continue with process - local storage is used as fallback
                
                # Get the overall band score"""
                
            content = content.replace(pattern, gcp_integration)
            
        # Update speaking_assessment_results to retrieve from GCP if available
        if "speaking_assessment_results" in content and "gcp_storage" not in content:
            pattern = """    # Get the assessment data
    assessment = json.loads(attempt.assessment) if attempt.assessment else {}
    
    # Get the user answers
    user_answers = json.loads(attempt.user_answers) if attempt.user_answers else {}"""
            
            gcp_results = """    # Get the assessment data from GCP if available
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
        transcription = user_answers.get('transcription', '')"""
            
            content = content.replace(pattern, gcp_results)
            
            # Also update the data dictionary to use our retrieved transcription
            data_pattern = """    # Prepare data for the template
    data = {
        'attempt': attempt,
        'test': test,
        'assessment': assessment,
        'audio_url': user_answers.get('audio_url', ''),
        'transcription': user_answers.get('transcription', ''),"""
            
            data_replacement = """    # Prepare data for the template
    data = {
        'attempt': attempt,
        'test': test,
        'assessment': assessment,
        'audio_url': user_answers.get('audio_url', ''),
        'transcription': transcription,"""
            
            content = content.replace(data_pattern, data_replacement)
            
        # Update UserTestAttempt creation to include GCP storage references
        if "attempt = UserTestAttempt(" in content and "gcp_transcript_path" not in content:
            pattern = """        # Save the attempt
        attempt = UserTestAttempt(
            user_id=current_user.id,
            test_id=test_id,
            complete_test_progress_id=complete_test_progress.id if complete_test_progress else None,
            user_answers=user_answers,"""
            
            replacement = """        # Get assessment_id for GCP storage (will be attempt.id)
        # Create a placeholder in user_answers to remember we need to update this
        user_answers['needs_gcp_update'] = True
        
        # Save the attempt
        attempt = UserTestAttempt(
            user_id=current_user.id,
            test_id=test_id,
            complete_test_progress_id=complete_test_progress.id if complete_test_progress else None,
            user_answers=user_answers,"""
            
            content = content.replace(pattern, replacement)
            
            # Add post-commit update to set GCP paths
            pattern = """        # Commit all changes
        db.session.commit()"""
            
            replacement = """        # Commit all changes
        db.session.commit()
        
        # Now that we have attempt.id, update GCP paths if needed
        if user_answers.get('needs_gcp_update') and gcp_storage.is_available():
            try:
                # If paths are in user_answers, move them to proper columns
                if 'gcp_transcript_path' in user_answers:
                    attempt.gcp_transcript_path = user_answers['gcp_transcript_path']
                    attempt.transcript_expiry_date = datetime.utcnow() + timedelta(days=180)
                    
                if 'gcp_assessment_path' in user_answers:
                    attempt.gcp_assessment_path = user_answers['gcp_assessment_path']
                
                # Remove temporary fields from user_answers
                user_answers.pop('needs_gcp_update', None)
                user_answers.pop('gcp_transcript_path', None)
                user_answers.pop('gcp_assessment_path', None)
                attempt.user_answers = user_answers
                
                # Commit the updates
                db.session.commit()
            except Exception as e:
                print(f"Warning: Failed to update GCP paths: {str(e)}")
                # Don't block the process if this fails"""
                
            content = content.replace(pattern, replacement)
        
        # Write the updated file
        with open(routes_file, 'w') as f:
            f.write(content)
        
        logger.info("Successfully updated speaking_assessment_routes.py with GCP integration")
        return True
    
    except Exception as e:
        logger.error(f"Error updating speaking_assessment_routes.py: {str(e)}")
        return False

def run_database_upgrades():
    """
    Run the database upgrade to add GCP storage columns
    """
    try:
        from add_gcp_storage_columns import add_gcp_storage_columns
        
        logger.info("Running database upgrade for GCP storage...")
        add_gcp_storage_columns()
        logger.info("Database upgrade completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running database upgrades: {str(e)}")
        return False

def update_templates_for_privacy():
    """
    Updates the speaking templates to include privacy notices about audio storage
    """
    try:
        # Update the speaking test template
        template_file = 'templates/practice/speaking_test_template.html'
        
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Check if we need to add the privacy notice
        if "privacy-notice" not in content:
            # Find a good place to insert the notice - right before the recording UI
            pattern = '<div class="row mb-3">\n                <div class="col-md-12">\n                    <div class="speaking-recorder">'
            
            privacy_notice = """<div class="row mb-3">
                <div class="col-md-12">
                    <div class="alert alert-info privacy-notice">
                        <h5><i class="fas fa-shield-alt"></i> Privacy Notice</h5>
                        <p>Your audio recording is only used for immediate assessment and is not permanently stored. 
                        Only your written assessment and transcript will be saved to your account.</p>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="privacyConsent" required>
                            <label class="form-check-label" for="privacyConsent">
                                I understand and consent to the temporary processing of my audio for assessment purposes.
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-12">
                    <div class="speaking-recorder">"""
            
            content = content.replace(pattern, privacy_notice)
            
            # Add JavaScript validation for the consent checkbox
            js_pattern = '$("#recordButton").click(function() {'
            
            js_addition = """// Check privacy consent
            if (!$("#privacyConsent").prop("checked")) {
                showAlert("Please agree to the privacy consent before recording.", "warning");
                return;
            }
            
            $("#recordButton").click(function() {"""
            
            content = content.replace(js_pattern, js_addition)
            
            # Write back the updated file
            with open(template_file, 'w') as f:
                f.write(content)
                
            logger.info(f"Updated {template_file} with privacy notice")
        
        # Update the speaking results template
        results_file = 'templates/practice/speaking_results.html'
        
        with open(results_file, 'r') as f:
            results_content = f.read()
        
        # Check for audio playback section and add a note
        if "Audio recording is not stored" not in results_content and "audio-player" in results_content:
            pattern = '<div class="card-body">\n                        <div class="audio-player mb-3">'
            
            replacement = '<div class="card-body">\n                        <p class="text-muted"><i class="fas fa-info-circle"></i> Audio recording is not stored for privacy protection. Only your transcript and assessment are saved.</p>\n                        <div class="audio-player mb-3">'
            
            results_content = results_content.replace(pattern, replacement)
            
            # Write back the updated file
            with open(results_file, 'w') as f:
                f.write(results_content)
                
            logger.info(f"Updated {results_file} with privacy note")
        
        return True
    except Exception as e:
        logger.error(f"Error updating templates: {str(e)}")
        return False

if __name__ == "__main__":
    success = True
    
    # Run database upgrades first
    if not run_database_upgrades():
        logger.error("Failed to run database upgrades. Aborting.")
        sys.exit(1)
    
    # Update speaking assessment routes
    if not update_speaking_assessment_routes():
        logger.error("Failed to update speaking assessment routes. Aborting.")
        sys.exit(1)
    
    # Update templates for privacy notices
    if not update_templates_for_privacy():
        logger.error("Failed to update templates. Aborting.")
        sys.exit(1)
    
    logger.info("Successfully integrated GCP storage with speaking assessment!")