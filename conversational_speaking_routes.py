"""
Conversational Speaking Assessment Routes
This module provides routes for interactive speaking practice with AI examiner
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from account_activation import authenticated_user_required
from models import db, SpeakingPrompt
from intelligent_speaking_assessment import intelligent_speaking_service
from azure_speech_services import azure_speech_service

logger = logging.getLogger(__name__)

conversational_bp = Blueprint('conversational', __name__)

@conversational_bp.route('/speaking/conversational/<int:assessment_id>')
@login_required
@authenticated_user_required
def start_conversational_assessment(assessment_id):
    """Start a conversational speaking assessment"""
    try:
        # Determine test type based on user preference
        test_type = current_user.assessment_preference or 'academic'
        
        # Initialize the conversational assessment
        result = intelligent_speaking_service.start_assessment_conversation(
            assessment_id, test_type
        )
        
        if not result.get('success'):
            return render_template('error.html', 
                                 error=f"Could not start assessment: {result.get('error', 'Unknown error')}")
        
        # Store conversation context in session
        session['conversation_context'] = result.get('context', {})
        session['conversation_active'] = True
        
        return render_template('assessments/conversational_speaking.html',
                             assessment_info=result.get('assessment_info', {}),
                             first_question=result.get('specific_question', {}),
                             conversation_id=result.get('conversation_id', ''))
        
    except Exception as e:
        logger.error(f"Error starting conversational assessment: {e}")
        return render_template('error.html', error="Could not start conversational assessment")

@conversational_bp.route('/api/conversation/continue', methods=['POST'])
@login_required
@authenticated_user_required
def continue_conversation():
    """Continue the conversational assessment"""
    try:
        data = request.get_json()
        user_response = data.get('user_response', '')
        
        if not user_response.strip():
            return jsonify({"success": False, "error": "No response provided"})
        
        # Get conversation context from session
        conversation_context = session.get('conversation_context', {})
        if not conversation_context:
            return jsonify({"success": False, "error": "No active conversation"})
        
        # Continue the conversation
        result = intelligent_speaking_service.continue_contextual_conversation(
            conversation_context, user_response
        )
        
        if result.get('success'):
            # Update session with new context
            session['conversation_context'] = result.get('conversation_context', {})
            
            # Generate British female voice for examiner response
            examiner_text = result.get('examiner_response', '')
            if examiner_text and azure_speech_service:
                try:
                    audio_result = azure_speech_service.synthesize_speech(
                        examiner_text,
                        voice_name="en-GB-SoniaNeural",  # British female voice
                        output_format="audio-16khz-32kbitrate-mono-mp3"
                    )
                    
                    if audio_result.get('success'):
                        result['examiner_audio_url'] = audio_result.get('audio_url')
                        result['has_audio'] = True
                    else:
                        result['has_audio'] = False
                        logger.warning(f"Could not generate audio: {audio_result.get('error')}")
                except Exception as audio_error:
                    logger.error(f"Audio generation error: {audio_error}")
                    result['has_audio'] = False
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error continuing conversation: {e}")
        return jsonify({"success": False, "error": "Could not continue conversation"})

@conversational_bp.route('/api/conversation/finalize', methods=['POST'])
@login_required
@authenticated_user_required
def finalize_conversation():
    """Finalize the conversational assessment and get scores"""
    try:
        # Get conversation context from session
        conversation_context = session.get('conversation_context', {})
        if not conversation_context:
            return jsonify({"success": False, "error": "No active conversation"})
        
        # Generate final assessment
        result = intelligent_speaking_service.finalize_intelligent_assessment(
            conversation_context
        )
        
        if result.get('success'):
            # Clear conversation from session
            session.pop('conversation_context', None)
            session.pop('conversation_active', None)
            
            # Generate British female voice for final feedback
            feedback_text = result.get('detailed_feedback', '')
            if feedback_text and azure_speech_service:
                try:
                    # Create a summary feedback for audio
                    audio_feedback = f"Thank you for completing your IELTS speaking assessment. Your overall band score is {result.get('overall_score', 'not available')}. {feedback_text[:200]}..."
                    
                    audio_result = azure_speech_service.synthesize_speech(
                        audio_feedback,
                        voice_name="en-GB-SoniaNeural",  # British female voice
                        output_format="audio-16khz-32kbitrate-mono-mp3"
                    )
                    
                    if audio_result.get('success'):
                        result['feedback_audio_url'] = audio_result.get('audio_url')
                        result['has_feedback_audio'] = True
                except Exception as audio_error:
                    logger.error(f"Feedback audio generation error: {audio_error}")
                    result['has_feedback_audio'] = False
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error finalizing conversation: {e}")
        return jsonify({"success": False, "error": "Could not finalize assessment"})

@conversational_bp.route('/api/speech/transcribe', methods=['POST'])
@login_required
@authenticated_user_required
def transcribe_speech():
    """Transcribe user's speech input"""
    try:
        if 'audio' not in request.files:
            return jsonify({"success": False, "error": "No audio file provided"})
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"success": False, "error": "No audio file selected"})
        
        # Use Azure Speech Services for transcription
        if azure_speech_service:
            # Save temporary audio file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_file.save(temp_file.name)
                
                # Transcribe with Azure
                result = azure_speech_service.transcribe_audio(temp_file.name)
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                if result.get('success'):
                    return jsonify({
                        "success": True,
                        "transcription": result.get('transcription', ''),
                        "confidence": result.get('confidence', 0)
                    })
                else:
                    return jsonify({"success": False, "error": result.get('error', 'Transcription failed')})
        else:
            return jsonify({"success": False, "error": "Speech service not available"})
            
    except Exception as e:
        logger.error(f"Error transcribing speech: {e}")
        return jsonify({"success": False, "error": "Could not transcribe audio"})

def register_conversational_routes(app):
    """Register conversational speaking routes with the app"""
    app.register_blueprint(conversational_bp)
    logger.info("Conversational speaking routes registered")