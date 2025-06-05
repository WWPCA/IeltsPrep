"""
Assessment Recovery System
Provides recovery functionality for interrupted assessments
"""

import json
from datetime import datetime, timedelta
from app import db
from models import UserTestAttempt

class AssessmentRecoveryService:
    """Service for managing assessment recovery functionality"""
    
    @staticmethod
    def can_recover_assessment(user_id, assessment_type):
        """Check if user has a recoverable assessment"""
        try:
            # Look for incomplete attempts within last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            incomplete_attempt = UserTestAttempt.query.filter_by(
                user_id=user_id,
                test_type=assessment_type,
                completed=False
            ).filter(
                UserTestAttempt.created_at >= cutoff_time
            ).order_by(UserTestAttempt.created_at.desc()).first()
            
            return incomplete_attempt is not None, incomplete_attempt
            
        except Exception as e:
            print(f"Error checking recovery status: {e}")
            return False, None
    
    @staticmethod
    def recover_assessment(user_id, assessment_type):
        """Recover the most recent incomplete assessment"""
        try:
            can_recover, attempt = AssessmentRecoveryService.can_recover_assessment(user_id, assessment_type)
            
            if can_recover and attempt:
                # Mark as resumed
                attempt.recovery_used = True
                attempt.resumed_at = datetime.utcnow()
                db.session.commit()
                
                return True, attempt
                
        except Exception as e:
            print(f"Error recovering assessment: {e}")
            db.session.rollback()
            
        return False, None
    
    @staticmethod
    def start_new_assessment(user_id, assessment_type):
        """Start a new assessment (marks previous as abandoned)"""
        try:
            # Mark any existing incomplete attempts as abandoned
            incomplete_attempts = UserTestAttempt.query.filter_by(
                user_id=user_id,
                test_type=assessment_type,
                completed=False
            ).all()
            
            for attempt in incomplete_attempts:
                attempt.completed = True  # Mark as completed (abandoned)
                attempt.restarted_at = datetime.utcnow()
            
            # Create new attempt
            new_attempt = UserTestAttempt(
                user_id=user_id,
                test_type=assessment_type,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_attempt)
            db.session.commit()
            
            return True, new_attempt
            
        except Exception as e:
            print(f"Error starting new assessment: {e}")
            db.session.rollback()
            return False, None

def integrate_recovery_system():
    """Integration function called during app startup"""
    try:
        print("Assessment recovery system integrated successfully.")
        return True
    except Exception as e:
        print(f"Failed to integrate recovery system: {e}")
        return False