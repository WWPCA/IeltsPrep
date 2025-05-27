"""
Comprehensive Assessment Recovery System
Protects users from losing assessments due to network issues or accidental browser closure.
"""

from datetime import datetime, timedelta
from flask import session, request, jsonify
from models import db, UserTestAttempt
import json

class AssessmentRecoveryManager:
    """
    Manages assessment recovery for interrupted sessions.
    Ensures users don't lose their one assessment opportunity due to technical issues.
    """
    
    @staticmethod
    def start_assessment_session(user_id, assessment_id, assessment_type):
        """
        Start a new assessment session with recovery protection.
        
        Args:
            user_id (int): User ID
            assessment_id (int): Assessment ID
            assessment_type (str): Type of assessment (speaking, writing, etc.)
            
        Returns:
            dict: Session data with recovery token
        """
        session_data = {
            'user_id': user_id,
            'assessment_id': assessment_id,
            'assessment_type': assessment_type,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'in_progress',
            'recovery_attempts': 0,
            'progress_checkpoint': {},
            'last_activity': datetime.utcnow().isoformat()
        }
        
        # Store in session for immediate access
        session['assessment_session'] = session_data
        
        # Also store in database for persistence across browser sessions
        recovery_record = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress'
        ).first()
        
        if not recovery_record:
            recovery_record = UserTestAttempt(
                user_id=user_id,
                assessment_id=assessment_id,
                assessment_type=assessment_type,
                status='in_progress',
                started_at=datetime.utcnow(),
                recovery_data=json.dumps(session_data)
            )
            db.session.add(recovery_record)
            db.session.commit()
        
        return session_data
    
    @staticmethod
    def check_for_interrupted_session(user_id, assessment_id):
        """
        Check if user has an interrupted assessment session.
        
        Args:
            user_id (int): User ID
            assessment_id (int): Assessment ID
            
        Returns:
            dict: Recovery information or None
        """
        # Check database for interrupted sessions
        interrupted_session = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress'
        ).first()
        
        if interrupted_session:
            # Check if session is still valid (within 24 hours)
            time_limit = datetime.utcnow() - timedelta(hours=24)
            
            if interrupted_session.started_at > time_limit:
                try:
                    recovery_data = json.loads(interrupted_session.recovery_data or '{}')
                    return {
                        'has_interrupted_session': True,
                        'started_at': interrupted_session.started_at.isoformat(),
                        'time_elapsed': str(datetime.utcnow() - interrupted_session.started_at),
                        'recovery_attempts': recovery_data.get('recovery_attempts', 0),
                        'progress': recovery_data.get('progress_checkpoint', {}),
                        'can_resume': recovery_data.get('recovery_attempts', 0) < 3
                    }
                except:
                    pass
        
        return {'has_interrupted_session': False}
    
    @staticmethod
    def save_progress_checkpoint(user_id, assessment_id, progress_data):
        """
        Save user's progress during assessment for recovery purposes.
        
        Args:
            user_id (int): User ID
            assessment_id (int): Assessment ID
            progress_data (dict): Current progress data
        """
        # Update session data
        if 'assessment_session' in session:
            session['assessment_session']['progress_checkpoint'] = progress_data
            session['assessment_session']['last_activity'] = datetime.utcnow().isoformat()
        
        # Update database record
        recovery_record = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress'
        ).first()
        
        if recovery_record:
            try:
                recovery_data = json.loads(recovery_record.recovery_data or '{}')
                recovery_data['progress_checkpoint'] = progress_data
                recovery_data['last_activity'] = datetime.utcnow().isoformat()
                
                recovery_record.recovery_data = json.dumps(recovery_data)
                db.session.commit()
            except Exception as e:
                print(f"Error saving progress checkpoint: {e}")
    
    @staticmethod
    def resume_assessment(user_id, assessment_id):
        """
        Resume an interrupted assessment session.
        
        Args:
            user_id (int): User ID
            assessment_id (int): Assessment ID
            
        Returns:
            dict: Resumed session data
        """
        recovery_record = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress'
        ).first()
        
        if recovery_record:
            try:
                recovery_data = json.loads(recovery_record.recovery_data or '{}')
                
                # Increment recovery attempts
                recovery_data['recovery_attempts'] = recovery_data.get('recovery_attempts', 0) + 1
                recovery_data['resumed_at'] = datetime.utcnow().isoformat()
                
                # Update database
                recovery_record.recovery_data = json.dumps(recovery_data)
                db.session.commit()
                
                # Restore session
                session['assessment_session'] = recovery_data
                
                return {
                    'success': True,
                    'session_data': recovery_data,
                    'message': 'Assessment session resumed successfully'
                }
            except Exception as e:
                print(f"Error resuming assessment: {e}")
        
        return {
            'success': False,
            'message': 'Unable to resume assessment session'
        }
    
    @staticmethod
    def complete_assessment(user_id, assessment_id, final_data):
        """
        Mark assessment as completed and clean up recovery data.
        
        Args:
            user_id (int): User ID
            assessment_id (int): Assessment ID
            final_data (dict): Final assessment results
        """
        # Update the recovery record to completed
        recovery_record = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress'
        ).first()
        
        if recovery_record:
            recovery_record.status = 'completed'
            recovery_record.completed_at = datetime.utcnow()
            recovery_record.final_results = json.dumps(final_data)
            db.session.commit()
        
        # Clear session data
        if 'assessment_session' in session:
            del session['assessment_session']
    
    @staticmethod
    def restart_assessment(user_id, assessment_id, reason='user_requested'):
        """
        Allow user to restart an interrupted assessment.
        
        Args:
            user_id (int): User ID
            assessment_id (int): Assessment ID
            reason (str): Reason for restart
            
        Returns:
            dict: Restart confirmation
        """
        # Remove the interrupted session
        recovery_record = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress'
        ).first()
        
        if recovery_record:
            # Log the restart for tracking
            try:
                recovery_data = json.loads(recovery_record.recovery_data or '{}')
                recovery_data['restart_reason'] = reason
                recovery_data['restart_time'] = datetime.utcnow().isoformat()
                
                recovery_record.recovery_data = json.dumps(recovery_data)
                recovery_record.status = 'restarted'
                db.session.commit()
            except:
                pass
        
        # Clear session
        if 'assessment_session' in session:
            del session['assessment_session']
        
        return {
            'success': True,
            'message': 'Assessment restarted successfully. You can begin again.'
        }
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up recovery sessions older than 24 hours.
        Should be run periodically as a maintenance task.
        """
        expiry_time = datetime.utcnow() - timedelta(hours=24)
        
        expired_sessions = UserTestAttempt.query.filter(
            UserTestAttempt.status == 'in_progress',
            UserTestAttempt.started_at < expiry_time
        ).all()
        
        for session_record in expired_sessions:
            session_record.status = 'expired'
            
        db.session.commit()
        
        return len(expired_sessions)

def init_recovery_routes(app):
    """Initialize recovery routes for the Flask app."""
    
    @app.route('/assessment/recovery/check/<int:assessment_id>')
    def check_recovery(assessment_id):
        """Check for interrupted assessment sessions."""
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        recovery_info = AssessmentRecoveryManager.check_for_interrupted_session(
            current_user.id, assessment_id
        )
        return jsonify(recovery_info)
    
    @app.route('/assessment/recovery/resume/<int:assessment_id>', methods=['POST'])
    def resume_recovery(assessment_id):
        """Resume an interrupted assessment."""
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        result = AssessmentRecoveryManager.resume_assessment(
            current_user.id, assessment_id
        )
        return jsonify(result)
    
    @app.route('/assessment/recovery/restart/<int:assessment_id>', methods=['POST'])
    def restart_recovery(assessment_id):
        """Restart an interrupted assessment."""
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json() or {}
        reason = data.get('reason', 'user_requested')
        
        result = AssessmentRecoveryManager.restart_assessment(
            current_user.id, assessment_id, reason
        )
        return jsonify(result)
    
    @app.route('/assessment/recovery/checkpoint/<int:assessment_id>', methods=['POST'])
    def save_checkpoint(assessment_id):
        """Save progress checkpoint during assessment."""
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        progress_data = request.get_json() or {}
        
        AssessmentRecoveryManager.save_progress_checkpoint(
            current_user.id, assessment_id, progress_data
        )
        
        return jsonify({'success': True, 'message': 'Progress saved'})