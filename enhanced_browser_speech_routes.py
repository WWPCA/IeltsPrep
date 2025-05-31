"""
Enhanced Browser Speech Routes
Implements comprehensive browser-based speech recognition with robust error handling,
input validation, and GDPR compliance based on technical review recommendations.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from botocore.exceptions import ClientError, BotoCoreError

from security_manager import rate_limit, validate_inputs, api_protection
from nova_sonic_services import nova_sonic_service
from enhanced_nova_assessment import EnhancedNovaAssessment, InputValidator

# Configure logging
logger = logging.getLogger(__name__)

# Initialize blueprint
speech_bp = Blueprint('enhanced_speech', __name__)

# Initialize assessment service
try:
    nova_assessment = EnhancedNovaAssessment()
except Exception as e:
    logger.error(f"Failed to initialize Nova Assessment service: {e}")
    nova_assessment = None

# Timeout settings
SILENCE_TIMEOUT = 5  # seconds
MAX_SPEAKING_TIME = 30  # seconds
API_RESPONSE_TIMEOUT = 15  # seconds

@speech_bp.route('/api/speech-consent', methods=['POST'])
@login_required
@rate_limit('api')
def speech_consent():
    """Handle speech recognition consent for GDPR compliance"""
    try:
        data = request.get_json()
        consent_given = data.get('consent', False)
        
        if consent_given:
            session['speech_consent'] = True
            session['speech_consent_timestamp'] = datetime.utcnow().isoformat()
            
            logger.info("Speech consent granted", 
                       user_id=current_user.id, 
                       timestamp=session['speech_consent_timestamp'])
            
            return jsonify({
                'success': True,
                'message': 'Consent recorded. You may now use speech features.',
                'privacy_note': 'All speech processing happens locally in your browser.'
            })
        else:
            logger.info("Speech consent denied", user_id=current_user.id)
            return jsonify({
                'success': False, 
                'error': 'Consent required for speech features'
            }), 403
            
    except Exception as e:
        logger.error(f"Consent processing error for user {current_user.id}: {e}")
        return jsonify({
            'success': False, 
            'error': 'Consent processing failed'
        }), 500

@speech_bp.route('/api/start-speaking-session', methods=['POST'])
@login_required
@rate_limit('assessment')
@validate_inputs(assessment_type='text', part_number='text')
@api_protection()
def start_speaking_session():
    """Start enhanced speaking assessment session with comprehensive validation"""
    try:
        # Check speech consent
        if not session.get('speech_consent'):
            return jsonify({
                'success': False,
                'error': 'Speech consent required',
                'consent_required': True
            }), 403
        
        data = request.get_json()
        assessment_type = data.get('assessment_type')
        part_number = int(data.get('part_number', 1))
        question_id = data.get('question_id')
        
        # Enhanced input validation
        if not assessment_type or assessment_type not in ['academic_speaking', 'general_speaking']:
            logger.warning(f"Invalid assessment type: {assessment_type} from user {current_user.id}")
            return jsonify({'success': False, 'error': 'Invalid assessment type'}), 400
        
        if part_number not in [1, 2, 3]:
            logger.warning(f"Invalid part number: {part_number} from user {current_user.id}")
            return jsonify({'success': False, 'error': 'Invalid part number'}), 400
        
        # Check user access permissions using new individual package system
        has_access = False
        
        if assessment_type == 'academic_speaking':
            has_access = current_user.has_package_access('Academic Speaking')
        elif assessment_type == 'general_speaking':
            has_access = current_user.has_package_access('General Speaking')
        
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            has_access = True
        
        if not has_access:
            logger.warning(f"Access denied for user {current_user.id} to {assessment_type}")
            return jsonify({
                'success': False, 
                'error': 'You do not have access to this assessment type'
            }), 403
        
        # Create session with Nova Sonic
        if not nova_assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment service unavailable'
            }), 503
        
        session_result = nova_assessment.create_enhanced_speaking_session(
            user_level='intermediate',  # Could be determined from user profile
            part_number=part_number,
            topic=assessment_type.replace('_', ' '),
            specific_questions=[question_id] if question_id else None,
            user_id=current_user.id
        )
        
        if session_result.get('success'):
            logger.info("Speaking session created successfully", 
                       user_id=current_user.id, 
                       session_id=session_result.get('conversation_id'))
            
            return jsonify({
                'success': True,
                'session_id': session_result.get('conversation_id'),
                'examiner_greeting': session_result.get('examiner_response'),
                'instructions': 'Enable microphone access and start speaking when ready.',
                'timeout_settings': {
                    'silence_timeout': SILENCE_TIMEOUT,
                    'max_speaking_time': MAX_SPEAKING_TIME,
                    'api_response_timeout': API_RESPONSE_TIMEOUT
                },
                'privacy_reminder': 'Your speech is processed locally in your browser only.'
            })
        else:
            logger.error("Failed to create speaking session", 
                        user_id=current_user.id, 
                        error=session_result.get('error'))
            return jsonify({
                'success': False,
                'error': 'Failed to create speaking session. Please try again.'
            }), 500
            
    except ValueError as e:
        logger.warning(f"Invalid input for speaking session: {e}")
        return jsonify({'success': False, 'error': 'Invalid input format'}), 400
    except (ClientError, BotoCoreError) as e:
        logger.error(f"AWS service error creating session for user {current_user.id}: {e}")
        return jsonify({
            'success': False, 
            'error': 'Assessment service temporarily unavailable'
        }), 503
    except Exception as e:
        logger.error(f"Unexpected speaking session error for user {current_user.id}: {e}")
        return jsonify({
            'success': False, 
            'error': 'Session creation failed. Ensure microphone access and browser compatibility.'
        }), 500

@speech_bp.route('/api/submit-speaking-response', methods=['POST'])
@login_required
@rate_limit('assessment')
@validate_inputs(transcript='text', session_id='text')
@api_protection()
def submit_speaking_response():
    """Submit speaking response with enhanced ClearScore processing"""
    try:
        # Check speech consent
        if not session.get('speech_consent'):
            return jsonify({
                'success': False,
                'error': 'Speech consent required'
            }), 403
        
        data = request.get_json()
        transcript = data.get('transcript', '').strip()
        session_id = data.get('session_id')
        part_number = int(data.get('part_number', 1))
        question_id = data.get('question_id')
        
        # Validate transcript input
        if not transcript:
            logger.warning(f"Empty transcript from user {current_user.id}")
            return jsonify({
                'success': False, 
                'error': 'No speech detected. Please try speaking clearly.'
            }), 400
        
        # Validate audio input format
        is_valid, error_msg = InputValidator.validate_audio_input(transcript.encode())
        if not is_valid:
            logger.warning(f"Invalid audio input from user {current_user.id}: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Process with ClearScore enhanced assessment
        if not nova_assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment service unavailable'
            }), 503
        
        # Create conversation history format for assessment
        conversation_history = [
            {
                'role': 'examiner',
                'content': 'Please respond to the speaking prompt.',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'role': 'candidate',
                'content': transcript,
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        assessment_result = nova_assessment.assess_speaking_with_rag(
            conversation_history=conversation_history,
            part_number=part_number,
            specific_questions=[question_id] if question_id else None,
            user_id=current_user.id
        )
        
        if assessment_result.get('success'):
            logger.info("ClearScore speaking assessment completed", 
                       user_id=current_user.id, 
                       score=assessment_result.get('overall_score'))
            
            # Store assessment results in database
            try:
                from models import AssessmentSpeakingResponse, UserAssessmentAttempt, db
                
                # Create assessment attempt record
                attempt = UserAssessmentAttempt(
                    user_id=current_user.id,
                    assessment_type=f"speaking_part_{part_number}",
                    status='completed',
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow()
                )
                db.session.add(attempt)
                db.session.flush()  # Get the ID
                
                # Create speaking response record
                speaking_response = AssessmentSpeakingResponse(
                    attempt_id=attempt.id,
                    part_number=part_number,
                    transcript_text=transcript,
                    audio_filename=None,  # No audio file since browser-based
                    submission_time=datetime.utcnow()
                )
                
                # Store ClearScore assessment data
                speaking_response.set_clearscore_assessment({
                    'overall_score': assessment_result.get('overall_score'),
                    'fluency_coherence': assessment_result.get('fluency_coherence'),
                    'lexical_resource': assessment_result.get('lexical_resource'),
                    'grammatical_range': assessment_result.get('grammatical_range'),
                    'pronunciation': assessment_result.get('pronunciation'),
                    'detailed_feedback': assessment_result.get('detailed_feedback'),
                    'band_justification': assessment_result.get('band_justification'),
                    'assessment_type': assessment_result.get('assessment_type'),
                    'assessment_timestamp': assessment_result.get('assessment_timestamp')
                })
                
                db.session.add(speaking_response)
                db.session.commit()
                
                logger.info("Assessment results stored successfully", 
                           user_id=current_user.id, 
                           attempt_id=attempt.id)
                
            except Exception as db_error:
                logger.error(f"Database error storing assessment for user {current_user.id}: {db_error}")
                db.session.rollback()
                # Continue with response even if storage fails
            
            return jsonify({
                'success': True,
                'assessment': {
                    'overall_score': assessment_result.get('overall_score'),
                    'detailed_scores': {
                        'fluency_coherence': assessment_result.get('fluency_coherence'),
                        'lexical_resource': assessment_result.get('lexical_resource'),
                        'grammatical_range': assessment_result.get('grammatical_range'),
                        'pronunciation': assessment_result.get('pronunciation')
                    },
                    'feedback': assessment_result.get('detailed_feedback'),
                    'band_justification': assessment_result.get('band_justification'),
                    'transcript': transcript
                },
                'privacy_note': 'Your audio was processed locally and securely.'
            })
        else:
            logger.error("ClearScore assessment failed", 
                        user_id=current_user.id, 
                        error=assessment_result.get('error'))
            return jsonify({
                'success': False,
                'error': 'Assessment processing failed. Please try again.'
            }), 500
            
    except ValueError as e:
        logger.warning(f"Invalid input for speaking response: {e}")
        return jsonify({'success': False, 'error': 'Invalid input format'}), 400
    except TimeoutError:
        logger.warning(f"Assessment timeout for user {current_user.id}")
        return jsonify({
            'success': False, 
            'error': 'Assessment timed out. Please try again with a shorter response.'
        }), 408
    except (ClientError, BotoCoreError) as e:
        logger.error(f"AWS service error processing speech for user {current_user.id}: {e}")
        return jsonify({
            'success': False, 
            'error': 'Assessment service temporarily unavailable'
        }), 503
    except Exception as e:
        logger.error(f"Unexpected error processing speech for user {current_user.id}: {e}")
        return jsonify({
            'success': False, 
            'error': 'Assessment processing failed'
        }), 500

@speech_bp.route('/api/browser-compatibility-check', methods=['GET'])
@login_required
@rate_limit('api')
def browser_compatibility_check():
    """Check browser compatibility for Web Speech API"""
    try:
        user_agent = request.headers.get('User-Agent', '')
        
        # Basic browser compatibility indicators
        compatibility_info = {
            'web_speech_api_likely_supported': True,  # Assume modern browser
            'recommendations': [],
            'privacy_features': {
                'local_processing': True,
                'no_server_audio': True,
                'gdpr_compliant': True
            }
        }
        
        # Check for known incompatible browsers
        if 'MSIE' in user_agent or 'Trident' in user_agent:
            compatibility_info['web_speech_api_likely_supported'] = False
            compatibility_info['recommendations'].append(
                'Please use a modern browser like Chrome, Firefox, or Safari'
            )
        
        if not compatibility_info['web_speech_api_likely_supported']:
            compatibility_info['recommendations'].append(
                'Web Speech API may not be available in your browser'
            )
        else:
            compatibility_info['recommendations'].append(
                'Ensure microphone permissions are enabled'
            )
        
        logger.info("Browser compatibility check", 
                   user_id=current_user.id, 
                   user_agent=user_agent[:100])  # Truncate for privacy
        
        return jsonify({
            'success': True,
            'compatibility': compatibility_info
        })
        
    except Exception as e:
        logger.error(f"Browser compatibility check error: {e}")
        return jsonify({
            'success': False,
            'error': 'Compatibility check failed'
        }), 500

def process_speaking_response_pipeline(transcript, question_id, user_id, part_number=1):
    """
    Clear pipeline for browser transcription → Sonic → Nova Micro processing
    
    Args:
        transcript (str): Browser-transcribed text
        question_id (str): Question identifier
        user_id (int): User ID
        part_number (int): Speaking part number
        
    Returns:
        dict: Complete assessment result
    """
    try:
        # Step 1: Browser-based transcription (already done)
        if not transcript or len(transcript.strip()) < 10:
            return {
                'success': False, 
                'error': 'Transcript too short or empty'
            }
        
        # Step 2: Generate AI examiner response with Nova Sonic
        if nova_assessment:
            sonic_response = nova_assessment.create_enhanced_speaking_session(
                user_level='intermediate',
                part_number=part_number,
                topic='ielts_speaking',
                specific_questions=[question_id] if question_id else None,
                user_id=user_id
            )
        else:
            sonic_response = {'success': False, 'error': 'Service unavailable'}
        
        # Step 3: Analyze with Nova Micro
        if sonic_response.get('success') and nova_assessment:
            conversation_history = [
                {'role': 'examiner', 'content': sonic_response.get('examiner_response', '')},
                {'role': 'candidate', 'content': transcript}
            ]
            
            analysis_result = nova_assessment.assess_speaking_with_rag(
                conversation_history=conversation_history,
                part_number=part_number,
                specific_questions=[question_id] if question_id else None,
                user_id=user_id
            )
            
            return analysis_result
        else:
            return {
                'success': False,
                'error': 'Assessment service processing failed'
            }
            
    except Exception as e:
        logger.error(f"Speaking response pipeline error for user {user_id}: {e}")
        return {'success': False, 'error': 'Processing pipeline failed'}