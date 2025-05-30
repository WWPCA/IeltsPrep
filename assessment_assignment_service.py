"""
Enhanced Assessment Assignment Service
This module manages the assignment of assessments to users with robust error handling,
performance optimization, and comprehensive monitoring.
"""
import json
import random
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_
from sqlalchemy.exc import SQLAlchemyError

from models import db, UserAssessmentAssignment, User, Assessment

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
MAX_ACTIVE_ASSESSMENTS = 100  # Soft limit for monitoring

# Total number of unique assessments for each assessment type
TOTAL_ACADEMIC_ASSESSMENTS = 16
TOTAL_GENERAL_ASSESSMENTS = 16

def get_available_assessment_ids(user_id, assessment_type):
    """
    Get a list of assessment IDs that haven't been assigned to this user.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Either 'academic' or 'general'
        
    Returns:
        list: Available assessment IDs not previously assigned to this user
    """
    # Get the assessment category prefix based on assessment_type
    assessment_category_map = {
        'academic': ['academic_writing', 'academic_speaking'],
        'general': ['general_writing', 'general_speaking']
    }
    
    assessment_categories = assessment_category_map.get(assessment_type, [])
    
    # Get all assessments of this type
    all_assessments = Assessment.query.filter(
        Assessment.assessment_type.in_(assessment_categories),
        Assessment.status == 'active'
    ).all()
    
    # Get all assessment IDs previously assigned to this user
    previous_assignments = UserAssessmentAssignment.query.filter_by(
        user_id=user_id,
        assessment_type=assessment_type
    ).all()
    
    # Create a set of all previously assigned assessment IDs
    assigned_ids = set()
    for assignment in previous_assignments:
        assigned_ids.update(assignment.assessment_ids)
    
    # Calculate which assessment IDs are still available
    available_ids = [assessment.id for assessment in all_assessments if assessment.id not in assigned_ids]
    
    return available_ids

def assign_assessments_to_user(user_id, assessment_type, num_assessments):
    """
    Assign a specific number of assessments to a user with enhanced error handling and monitoring.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Either 'academic' or 'general'
        num_assessments (int): Number of assessments to assign (1, 2 or 4)
        
    Returns:
        tuple: (assigned_ids, success) where assigned_ids is list and success is boolean
    """
    try:
        # Validate parameters
        if num_assessments not in [1, 2, 4]:
            logger.error(f"Invalid assessment count: {num_assessments} for user {user_id}")
            raise ValueError("Number of assessments must be 1, 2, or 4")
        if assessment_type not in ['academic', 'general']:
            logger.error(f"Invalid assessment type: {assessment_type} for user {user_id}")
            raise ValueError("Assessment type must be 'academic' or 'general'")
        
        # Check soft limit for active assessments
        active_assignments = UserAssessmentAssignment.query.filter_by(
            user_id=user_id, assessment_type=assessment_type
        ).count()
        
        if active_assignments > MAX_ACTIVE_ASSESSMENTS:
            logger.warning(f"User {user_id} exceeds active assessment limit: {active_assignments}")
            return [], False
        
        # Get used assessment IDs with optimized query
        used_ids = db.session.query(UserAssessmentAssignment.assigned_assessment_ids).filter_by(
            user_id=user_id, assessment_type=assessment_type
        ).all()
        
        # Flatten the list of used assessment IDs
        used_ids_set = set()
        for assignment_ids in used_ids:
            if assignment_ids[0]:  # Check if not None
                try:
                    ids = json.loads(assignment_ids[0]) if isinstance(assignment_ids[0], str) else assignment_ids[0]
                    used_ids_set.update(ids)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Invalid assignment data for user {user_id}: {e}")
        
        # Get available assessments with optimized query
        assessment_category_map = {
            'academic': ['academic_writing', 'academic_speaking'],
            'general': ['general_writing', 'general_speaking']
        }
        
        assessment_categories = assessment_category_map.get(assessment_type, [])
        available_assessments = db.session.query(Assessment.id).filter(
            Assessment.assessment_type.in_(assessment_categories),
            Assessment.status == 'active',
            ~Assessment.id.in_(used_ids_set)
        ).limit(num_assessments * 2).all()  # Get extra to have selection flexibility
        
        available_ids = [aid[0] for aid in available_assessments]
        
        # Check if we have enough unique assessments
        if len(available_ids) < num_assessments:
            logger.warning(f"Not enough unique assessments for user {user_id}: {len(available_ids)}/{num_assessments}")
            return [], False
        
        # Randomly select assessments from available IDs
        assigned_ids = random.sample(available_ids, num_assessments)
        
        # Create new assignment record with transaction management
        assignment = UserAssessmentAssignment(
            user_id=user_id,
            assessment_type=assessment_type,
            assigned_assessment_ids=assigned_ids,
            purchase_date=datetime.utcnow(),
            expiry_date=None  # Never expires unless user deletes account
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Log successful assignment
        logger.info(f"Assigned {num_assessments} {assessment_type} assessments to user {user_id}", 
                   extra={'user_id': user_id, 'assessment_type': assessment_type, 
                          'count': num_assessments, 'assigned_ids': assigned_ids})
        
        return assigned_ids, True
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in assignment for user {user_id}: {e}")
        return [], False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in assignment for user {user_id}: {e}")
        return [], False

def get_current_assessment_assignments(user_id, assessment_type):
    """
    Get the currently assigned assessments for a user (never expires unless account deleted).
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Either 'academic' or 'general'
        
    Returns:
        list: Currently assigned assessment IDs
    """
    # Get all assignments for this user and type (no expiry check)
    assignments = UserAssessmentAssignment.query.filter(
        UserAssessmentAssignment.user_id == user_id,
        UserAssessmentAssignment.assessment_type == assessment_type
    ).order_by(UserAssessmentAssignment.purchase_date.desc()).all()
    
    # Combine all assigned IDs from all purchases
    all_assigned_ids = []
    for assignment in assignments:
        all_assigned_ids.extend(assignment.assessment_ids)
    
    return list(set(all_assigned_ids))  # Remove duplicates

def get_user_accessible_assessments(user_id, assessment_type):
    """
    Get Assessment objects that the user currently has access to take (unused assessments only).
    Once an assessment is used, it becomes inaccessible but feedback remains available.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Assessment type like 'academic_writing' or 'general_speaking'
        
    Returns:
        list: Assessment objects the user can still take (unused only)
    """
    from models import UserAssessmentAttempt
    
    # Get the user
    user = User.query.get(user_id)
    if not user or not user.has_active_assessment_package():
        return []
    
    # Check if user has the right assessment package type
    assessment_mapping = {
        'academic_writing': 'Academic Writing',
        'academic_speaking': 'Academic Speaking',
        'general_writing': 'General Writing',
        'general_speaking': 'General Speaking'
    }
    
    required_package = assessment_mapping.get(assessment_type)
    if required_package and not user.has_package_access(required_package):
        return []
    
    # Get the base assessment type (academic or general)
    base_type = 'academic' if assessment_type.startswith('academic') else 'general'
    
    # Get the user's assigned assessment IDs
    assigned_ids = get_current_assessment_assignments(user_id, base_type)
    
    if not assigned_ids:
        return []
    
    # Get IDs of assessments the user has already completed
    completed_attempts = UserAssessmentAttempt.query.filter(
        UserAssessmentAttempt.user_id == user_id,
        UserAssessmentAttempt.assessment_type == assessment_type,
        UserAssessmentAttempt.status == 'completed'
    ).all()
    
    completed_assessment_ids = {attempt.assessment_id for attempt in completed_attempts}
    
    # Only return unused assessments (assigned but not completed)
    unused_assessment_ids = [aid for aid in assigned_ids if aid not in completed_assessment_ids]
    
    # Get assessment objects for unused assessments only
    assessments = Assessment.query.filter(
        Assessment.id.in_(unused_assessment_ids),
        Assessment.assessment_type == assessment_type,
        Assessment.status == 'active'
    ).all()
    
    return assessments

def get_user_completed_assessments_with_feedback(user_id, assessment_type):
    """
    Get completed assessments with their GenAI feedback for permanent review.
    Once an assessment is used, the assessment itself becomes inaccessible but 
    feedback remains permanently available.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Assessment type like 'academic_writing' or 'general_speaking'
        
    Returns:
        list: UserAssessmentAttempt objects with completed assessments and feedback
    """
    from models import UserAssessmentAttempt
    
    # Get all completed assessment attempts with feedback
    completed_attempts = UserAssessmentAttempt.query.filter(
        UserAssessmentAttempt.user_id == user_id,
        UserAssessmentAttempt.assessment_type == assessment_type,
        UserAssessmentAttempt.status == 'completed'
    ).order_by(UserAssessmentAttempt.end_time.desc()).all()
    
    return completed_attempts