"""
Maya Assessment Handler
Integrates Maya conversation engine with IELTS band scoring for complete assessment flow
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from lambda_security import apply_security
from assessment_access_control import get_assessment_controller
from question_bank_dal import get_question_bank_dal
from maya_conversation_engine import get_maya_engine
from ielts_band_scoring import get_band_scorer

logger = logging.getLogger(__name__)

@apply_security(
    rate_limit_per_ip=20,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_start_maya_conversation(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Start Maya conversation for speaking assessment
    
    Expected payload:
    {
        "session_id": "session_123456789",
        "assessment_type": "academic_speaking"
    }
    """
    try:
        # Get user email from authenticated session
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id', '').strip()
        assessment_type = body.get('assessment_type', '').strip().lower()
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'session_id is required'
                })
            }
        
        # Get assessment session details
        question_dal = get_question_bank_dal()
        session_result = question_dal.get_assessment_session(session_id)
        
        if not session_result['success']:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Assessment session not found'
                })
            }
        
        session_details = session_result['session']
        
        # Verify session belongs to user
        if session_details.get('user_email') != user_email:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Access denied - session belongs to different user'
                })
            }
        
        # Initialize Maya conversation
        maya_engine = get_maya_engine()
        conversation_result = maya_engine.initialize_session({
            'session_id': session_id,
            'assessment_type': assessment_type,
            'questions': session_details.get('question_ids_by_category', {})
        })
        
        if conversation_result['success']:
            logger.info(f"Maya conversation started for session: {session_id}")
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Maya conversation started successfully',
                    'maya_response': conversation_result,
                    'session_id': session_id
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': conversation_result.get('error', 'Failed to start Maya conversation')
                })
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Invalid JSON payload'
            })
        }
    
    except Exception as e:
        logger.error(f"Start Maya conversation error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=50,  # Higher limit for conversation flow
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_maya_conversation_turn(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process user response in Maya conversation
    
    Expected payload:
    {
        "session_id": "session_123456789",
        "user_response": "transcribed text from user",
        "audio_duration": 15.2,
        "conversation_stage": "part1_questions"
    }
    """
    try:
        # Get user email from authenticated session
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id', '').strip()
        user_response = body.get('user_response', '').strip()
        audio_duration = body.get('audio_duration', 0.0)
        
        if not session_id or not user_response:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'session_id and user_response are required'
                })
            }
        
        # Verify session access
        question_dal = get_question_bank_dal()
        session_result = question_dal.get_assessment_session(session_id)
        
        if not session_result['success']:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Assessment session not found'
                })
            }
        
        session_details = session_result['session']
        if session_details.get('user_email') != user_email:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Access denied'
                })
            }
        
        # Process conversation turn
        maya_engine = get_maya_engine()
        conversation_turn = maya_engine.process_user_response(user_response, audio_duration)
        
        if conversation_turn['success']:
            # Check if assessment is complete
            is_complete = conversation_turn.get('assessment_complete', False)
            
            response_data = {
                'success': True,
                'maya_response': conversation_turn,
                'assessment_complete': is_complete
            }
            
            # If complete, generate band score report
            if is_complete:
                conversation_summary = maya_engine.get_conversation_summary()
                band_scorer = get_band_scorer()
                
                # Generate comprehensive evaluation
                evaluation_result = band_scorer.evaluate_speaking_assessment(conversation_summary)
                
                if evaluation_result['success']:
                    response_data['band_score_report'] = evaluation_result
                    logger.info(f"Assessment completed for session {session_id} - Band score: {evaluation_result.get('overall_band_score')}")
                else:
                    logger.warning(f"Failed to generate band score for session {session_id}")
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(response_data)
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': conversation_turn.get('error', 'Failed to process conversation turn')
                })
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Invalid JSON payload'
            })
        }
    
    except Exception as e:
        logger.error(f"Maya conversation turn error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=10,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_get_conversation_summary(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get conversation summary and current state
    
    Query parameters:
    ?session_id=session_123456789
    """
    try:
        # Get user email from authenticated session
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        query_params = event.get('queryStringParameters', {}) or {}
        session_id = query_params.get('session_id', '').strip()
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'session_id parameter required'
                })
            }
        
        # Verify session access
        question_dal = get_question_bank_dal()
        session_result = question_dal.get_assessment_session(session_id)
        
        if not session_result['success']:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Assessment session not found'
                })
            }
        
        session_details = session_result['session']
        if session_details.get('user_email') != user_email:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Access denied'
                })
            }
        
        # Get conversation summary
        maya_engine = get_maya_engine()
        conversation_summary = maya_engine.get_conversation_summary()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'data': conversation_summary
            })
        }
    
    except Exception as e:
        logger.error(f"Get conversation summary error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=15,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_generate_band_score_report(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Generate detailed IELTS band score report for completed assessment
    
    Expected payload:
    {
        "session_id": "session_123456789",
        "include_detailed_feedback": true
    }
    """
    try:
        # Get user email from authenticated session
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id', '').strip()
        include_detailed = body.get('include_detailed_feedback', True)
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'session_id is required'
                })
            }
        
        # Verify session access and completion
        question_dal = get_question_bank_dal()
        session_result = question_dal.get_assessment_session(session_id)
        
        if not session_result['success']:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Assessment session not found'
                })
            }
        
        session_details = session_result['session']
        if session_details.get('user_email') != user_email:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Access denied'
                })
            }
        
        # Check if assessment is complete
        if session_details.get('status') != 'completed':
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Assessment must be completed before generating band score report'
                })
            }
        
        # Get conversation data
        maya_engine = get_maya_engine()
        conversation_summary = maya_engine.get_conversation_summary()
        
        # Generate band score report
        band_scorer = get_band_scorer()
        evaluation_result = band_scorer.evaluate_speaking_assessment(conversation_summary)
        
        if evaluation_result['success']:
            # Optionally filter detailed feedback
            if not include_detailed:
                evaluation_result = {
                    'success': True,
                    'overall_band_score': evaluation_result['overall_band_score'],
                    'criterion_scores': evaluation_result['criterion_scores'],
                    'assessment_date': evaluation_result['assessment_date'],
                    'session_id': evaluation_result['session_id']
                }
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Band score report generated successfully',
                    'report': evaluation_result
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': evaluation_result.get('error', 'Failed to generate band score report')
                })
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Invalid JSON payload'
            })
        }
    
    except Exception as e:
        logger.error(f"Generate band score report error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=30,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_get_user_assessment_history(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user's assessment history with band scores
    
    Query parameters:
    ?assessment_type=academic_speaking&limit=10
    """
    try:
        # Get user email from authenticated session
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        query_params = event.get('queryStringParameters', {}) or {}
        assessment_type = query_params.get('assessment_type', '').strip().lower()
        limit = min(int(query_params.get('limit', '10')), 50)  # Max 50 results
        
        # Get user's question usage stats (proxy for assessment history)
        question_dal = get_question_bank_dal()
        
        if assessment_type:
            stats_result = question_dal.get_user_question_stats(user_email, assessment_type)
        else:
            # Get stats for all assessment types
            assessment_types = ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing']
            all_stats = []
            
            for a_type in assessment_types:
                stats = question_dal.get_user_question_stats(user_email, a_type)
                if stats.get('success') and stats.get('total_questions_used', 0) > 0:
                    all_stats.append({
                        'assessment_type': a_type,
                        'stats': stats
                    })
            
            stats_result = {
                'success': True,
                'assessment_history': all_stats
            }
        
        if stats_result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'data': stats_result,
                    'user_email': user_email
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': stats_result.get('error', 'Failed to get assessment history')
                })
            }
    
    except Exception as e:
        logger.error(f"Get user assessment history error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

# Export handlers
__all__ = [
    'handle_start_maya_conversation',
    'handle_maya_conversation_turn',
    'handle_get_conversation_summary',
    'handle_generate_band_score_report',
    'handle_get_user_assessment_history'
]