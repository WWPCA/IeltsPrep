"""
Assessment Assignment Service
This module manages the assignment of assessments to users, ensuring they don't receive
the same assessment twice when purchasing new packages.
"""
import json
import random
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_

from models import db, UserAssessmentAssignment, User, Assessment

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
    Assign a specific number of assessments to a user, ensuring they don't receive 
    assessments they've already seen. Access never expires unless user deletes account.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Either 'academic' or 'general'
        num_assessments (int): Number of assessments to assign (1, 2 or 4)
        
    Returns:
        list: The assigned assessment IDs
        bool: True if successful, False if not enough unique assessments available
    """
    # Validate parameters
    if num_assessments not in [1, 2, 4]:
        raise ValueError("Number of assessments must be 1, 2, or 4")
    if assessment_type not in ['academic', 'general']:
        raise ValueError("Assessment type must be 'academic' or 'general'")
    
    # Get available assessment IDs
    available_ids = get_available_assessment_ids(user_id, assessment_type)
    
    # Check if we have enough unique assessments
    if len(available_ids) < num_assessments:
        return [], False
    
    # Randomly select assessments from available IDs
    assigned_ids = random.sample(available_ids, num_assessments)
    
    # Create new assignment record
    assignment = UserAssessmentAssignment()
    assignment.user_id = user_id
    assignment.assessment_type = assessment_type
    assignment.assigned_assessment_ids = json.dumps(assigned_ids)
    assignment.purchase_date = datetime.utcnow()
    assignment.expiry_date = None  # Never expires unless user deletes account
    
    db.session.add(assignment)
    db.session.commit()
    
    # Return the assigned assessment IDs
    return assigned_ids, True

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
    Get Assessment objects that the user currently has access to.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Assessment type like 'academic_writing' or 'general_speaking'
        
    Returns:
        list: Assessment objects the user can access
    """
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
    
    if user.assessment_package_status != assessment_mapping.get(assessment_type):
        return []
    
    # Get the base assessment type (academic or general)
    base_type = 'academic' if assessment_type.startswith('academic') else 'general'
    
    # Get the user's assigned assessment IDs
    assigned_ids = get_current_assessment_assignments(user_id, base_type)
    
    if not assigned_ids:
        return []
    
    # Get assessment objects for this type and assigned IDs
    assessments = Assessment.query.filter(
        Assessment.id.in_(assigned_ids),
        Assessment.assessment_type == assessment_type,
        Assessment.status == 'active'
    ).all()
    
    return assessments