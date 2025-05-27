"""
Comprehensive Assessment Recovery System

This module provides robust recovery capabilities for speaking assessments,
allowing users to resume or restart assessments after technical interruptions
with minimal cost impact and maximum user experience.
"""

import json
import uuid
from datetime import datetime, timedelta
from flask import session, request, jsonify, current_app
from app import db
import logging

logger = logging.getLogger(__name__)

class AssessmentRecoveryManager:
    """Manages assessment recovery operations with user-friendly options."""
    
    @staticmethod
    def save_assessment_state(user_id, assessment_id, conversation_state):
        """
        Save current assessment state for potential recovery.
        
        Args:
            user_id (int): User's ID
            assessment_id (str): Unique assessment identifier
            conversation_state (dict): Current conversation state including:
                - current_part: Which IELTS part (1, 2, or 3)
                - conversation_history: Full dialogue history
                - questions_asked: Questions already presented
                - responses_given: User responses received
                - start_time: When assessment began
                - tokens_used: Tokens consumed so far
        """
        try:
            recovery_data = {
                'user_id': user_id,
                'assessment_id': assessment_id,
                'conversation_state': conversation_state,
                'saved_at': datetime.utcnow().isoformat(),
                'recovery_token': str(uuid.uuid4()),
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            # Store in session for immediate access
            session[f'recovery_{assessment_id}'] = recovery_data
            
            # Also store in database for persistence
            recovery_record = UserTestAttempt.query.filter_by(
                user_id=user_id,
                assessment_id=assessment_id,
                status='in_progress'
            ).first()
            
            if recovery_record:
                recovery_record.recovery_data = json.dumps(recovery_data)
                recovery_record.last_activity = datetime.utcnow()
                db.session.commit()
                
            logger.info(f"Assessment state saved for user {user_id}, assessment {assessment_id}")
            return recovery_data['recovery_token']
            
        except Exception as e:
            logger.error(f"Failed to save assessment state: {e}")
            return None
    
    @staticmethod
    def get_recovery_options(user_id, assessment_id):
        """
        Get available recovery options for an interrupted assessment.
        
        Returns:
            dict: Recovery options with costs and recommendations
        """
        try:
            # Check session first
            recovery_key = f'recovery_{assessment_id}'
            recovery_data = session.get(recovery_key)
            
            # Fallback to database
            if not recovery_data:
                recovery_record = UserTestAttempt.query.filter_by(
                    user_id=user_id,
                    assessment_id=assessment_id,
                    status='in_progress'
                ).first()
                
                if recovery_record and recovery_record.recovery_data:
                    recovery_data = json.loads(recovery_record.recovery_data)
            
            if not recovery_data:
                return {'available': False, 'reason': 'No recovery data found'}
            
            # Check if recovery period has expired
            expires_at = datetime.fromisoformat(recovery_data['expires_at'])
            if datetime.utcnow() > expires_at:
                return {'available': False, 'reason': 'Recovery period expired (24 hours)'}
            
            # Analyze conversation state to determine progress
            conversation_state = recovery_data['conversation_state']
            current_part = conversation_state.get('current_part', 1)
            progress_percent = AssessmentRecoveryManager._calculate_progress(conversation_state)
            
            # Determine recovery recommendation based on progress
            if progress_percent < 20:
                recommendation = 'restart'
                impact = 'minimal'
            elif progress_percent < 60:
                recommendation = 'resume'
                impact = 'low'
            else:
                recommendation = 'resume'
                impact = 'medium'
            
            return {
                'available': True,
                'recovery_token': recovery_data['recovery_token'],
                'progress': {
                    'current_part': current_part,
                    'percent_complete': progress_percent,
                    'questions_completed': len(conversation_state.get('responses_given', [])),
                    'time_elapsed': AssessmentRecoveryManager._calculate_time_elapsed(recovery_data)
                },
                'options': {
                    'resume': {
                        'available': True,
                        'description': f'Continue from Part {current_part} where you left off',
                        'cost_impact': impact,
                        'recommended': recommendation == 'resume'
                    },
                    'restart': {
                        'available': True,
                        'description': 'Start a completely fresh assessment',
                        'cost_impact': 'none',
                        'recommended': recommendation == 'restart'
                    }
                },
                'saved_at': recovery_data['saved_at'],
                'expires_at': recovery_data['expires_at']
            }
            
        except Exception as e:
            logger.error(f"Failed to get recovery options: {e}")
            return {'available': False, 'reason': 'Recovery system error'}
    
    @staticmethod
    def resume_assessment(user_id, assessment_id, recovery_token):
        """
        Resume an assessment from saved state.
        
        Returns:
            dict: Resumed conversation state or error
        """
        try:
            recovery_data = session.get(f'recovery_{assessment_id}')
            
            if not recovery_data or recovery_data['recovery_token'] != recovery_token:
                return {'success': False, 'error': 'Invalid recovery token'}
            
            # Verify recovery is still valid
            expires_at = datetime.fromisoformat(recovery_data['expires_at'])
            if datetime.utcnow() > expires_at:
                return {'success': False, 'error': 'Recovery period expired'}
            
            conversation_state = recovery_data['conversation_state']
            
            # Update assessment record
            assessment_record = UserTestAttempt.query.filter_by(
                user_id=user_id,
                assessment_id=assessment_id,
                status='in_progress'
            ).first()
            
            if assessment_record:
                assessment_record.resumed_at = datetime.utcnow()
                assessment_record.recovery_used = True
                db.session.commit()
            
            logger.info(f"Assessment resumed for user {user_id}, assessment {assessment_id}")
            
            return {
                'success': True,
                'conversation_state': conversation_state,
                'message': f"Welcome back! Continuing from Part {conversation_state.get('current_part', 1)}"
            }
            
        except Exception as e:
            logger.error(f"Failed to resume assessment: {e}")
            return {'success': False, 'error': 'Resume operation failed'}
    
    @staticmethod
    def restart_assessment(user_id, assessment_id, recovery_token):
        """
        Start a fresh assessment, clearing previous state.
        
        Returns:
            dict: New assessment state or error
        """
        try:
            recovery_data = session.get(f'recovery_{assessment_id}')
            
            if not recovery_data or recovery_data['recovery_token'] != recovery_token:
                return {'success': False, 'error': 'Invalid recovery token'}
            
            # Clear previous state
            session.pop(f'recovery_{assessment_id}', None)
            
            # Update database record
            assessment_record = UserTestAttempt.query.filter_by(
                user_id=user_id,
                assessment_id=assessment_id,
                status='in_progress'
            ).first()
            
            if assessment_record:
                assessment_record.restarted_at = datetime.utcnow()
                assessment_record.recovery_used = True
                assessment_record.recovery_data = None
                db.session.commit()
            
            # Create fresh conversation state
            fresh_state = {
                'current_part': 1,
                'conversation_history': [],
                'questions_asked': [],
                'responses_given': [],
                'start_time': datetime.utcnow().isoformat(),
                'tokens_used': 0,
                'assessment_id': assessment_id
            }
            
            logger.info(f"Assessment restarted for user {user_id}, assessment {assessment_id}")
            
            return {
                'success': True,
                'conversation_state': fresh_state,
                'message': "Starting fresh assessment. Good luck!"
            }
            
        except Exception as e:
            logger.error(f"Failed to restart assessment: {e}")
            return {'success': False, 'error': 'Restart operation failed'}
    
    @staticmethod
    def cleanup_expired_recoveries():
        """Remove expired recovery data to keep system clean."""
        try:
            # Clean session data
            expired_keys = []
            for key in session.keys():
                if key.startswith('recovery_'):
                    recovery_data = session[key]
                    if isinstance(recovery_data, dict) and 'expires_at' in recovery_data:
                        expires_at = datetime.fromisoformat(recovery_data['expires_at'])
                        if datetime.utcnow() > expires_at:
                            expired_keys.append(key)
            
            for key in expired_keys:
                session.pop(key, None)
            
            # Clean database records
            expired_attempts = UserTestAttempt.query.filter(
                UserTestAttempt.recovery_data.isnot(None),
                UserTestAttempt.last_activity < datetime.utcnow() - timedelta(hours=24)
            ).all()
            
            for attempt in expired_attempts:
                attempt.recovery_data = None
                attempt.status = 'expired'
            
            db.session.commit()
            logger.info(f"Cleaned up {len(expired_keys)} session recoveries and {len(expired_attempts)} database recoveries")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired recoveries: {e}")
    
    @staticmethod
    def _calculate_progress(conversation_state):
        """Calculate assessment completion percentage."""
        current_part = conversation_state.get('current_part', 1)
        responses_given = len(conversation_state.get('responses_given', []))
        
        # Rough estimates based on typical IELTS structure
        if current_part == 1:
            return min(responses_given * 8, 25)  # Part 1 is about 25% of total
        elif current_part == 2:
            return 25 + min(responses_given * 15, 25)  # Part 2 is about 25%
        else:  # Part 3
            return 50 + min(responses_given * 10, 50)  # Part 3 is about 50%
    
    @staticmethod
    def _calculate_time_elapsed(recovery_data):
        """Calculate time elapsed since assessment start."""
        try:
            saved_at = datetime.fromisoformat(recovery_data['saved_at'])
            conversation_state = recovery_data['conversation_state']
            start_time = datetime.fromisoformat(conversation_state['start_time'])
            return str(saved_at - start_time)
        except:
            return "Unknown"

# Utility functions for Flask routes
def handle_connection_interruption():
    """Handle sudden connection loss during assessment."""
    try:
        user_id = session.get('user_id')
        assessment_id = session.get('current_assessment_id')
        conversation_state = session.get('conversation_state')
        
        if user_id and assessment_id and conversation_state:
            recovery_token = AssessmentRecoveryManager.save_assessment_state(
                user_id, assessment_id, conversation_state
            )
            return recovery_token
        return None
    except Exception as e:
        logger.error(f"Failed to handle connection interruption: {e}")
        return None

def get_recovery_status():
    """Get current recovery status for the user."""
    try:
        user_id = session.get('user_id')
        assessment_id = session.get('current_assessment_id')
        
        if user_id and assessment_id:
            return AssessmentRecoveryManager.get_recovery_options(user_id, assessment_id)
        return {'available': False, 'reason': 'No active assessment'}
    except Exception as e:
        logger.error(f"Failed to get recovery status: {e}")
        return {'available': False, 'reason': 'System error'}