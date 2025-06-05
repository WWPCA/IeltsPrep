"""
Assessment Assignment Service
Handles assignment and validation of assessment packages for users
"""

import json
from datetime import datetime, timedelta
from app import db
from models import User, UserAssessmentAssignment

class AssessmentAssignmentService:
    """Service for managing assessment assignments"""
    
    @staticmethod
    def assign_assessment_package(user_id, package_type, assessment_count=4):
        """Assign assessment package to user"""
        try:
            # Create assessment assignment record
            assignment = UserAssessmentAssignment(
                user_id=user_id,
                assessment_type=package_type,
                assigned_assessment_ids=json.dumps(list(range(1, assessment_count + 1))),
                purchase_date=datetime.utcnow(),
                expiry_date=datetime.utcnow() + timedelta(days=365)  # 1 year access
            )
            
            db.session.add(assignment)
            
            # Update user's package status
            user = User.query.get(user_id)
            if user:
                user.assessment_package_status = package_type
                user.assessment_package_expiry = assignment.expiry_date
            
            db.session.commit()
            return True, assignment
            
        except Exception as e:
            db.session.rollback()
            print(f"Error assigning assessment package: {e}")
            return False, None
    
    @staticmethod
    def has_package_access(user_id, package_type):
        """Check if user has access to specific assessment package"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Check if user has active package
            if user.assessment_package_status == package_type:
                if user.assessment_package_expiry and user.assessment_package_expiry > datetime.utcnow():
                    return True
            
            # Check assignment records
            assignment = UserAssessmentAssignment.query.filter_by(
                user_id=user_id,
                assessment_type=package_type
            ).filter(
                UserAssessmentAssignment.expiry_date > datetime.utcnow()
            ).first()
            
            return assignment is not None
            
        except Exception as e:
            print(f"Error checking package access: {e}")
            return False
    
    @staticmethod
    def get_user_assignments(user_id):
        """Get all assessment assignments for a user"""
        try:
            assignments = UserAssessmentAssignment.query.filter_by(
                user_id=user_id
            ).filter(
                UserAssessmentAssignment.expiry_date > datetime.utcnow()
            ).all()
            
            return assignments
            
        except Exception as e:
            print(f"Error getting user assignments: {e}")
            return []
    
    @staticmethod
    def get_available_assessments(user_id, package_type):
        """Get list of available assessment IDs for user's package"""
        try:
            assignment = UserAssessmentAssignment.query.filter_by(
                user_id=user_id,
                assessment_type=package_type
            ).filter(
                UserAssessmentAssignment.expiry_date > datetime.utcnow()
            ).first()
            
            if assignment:
                return assignment.assessment_ids
            
            return []
            
        except Exception as e:
            print(f"Error getting available assessments: {e}")
            return []

def has_package_access(user_id, package_type):
    """Convenience function for package access checking"""
    return AssessmentAssignmentService.has_package_access(user_id, package_type)

def assign_assessment_package(user_id, package_type, assessment_count=4):
    """Convenience function for package assignment"""
    return AssessmentAssignmentService.assign_assessment_package(
        user_id, package_type, assessment_count
    )