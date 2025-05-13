"""
Assessment Assignment Service
This module manages the assignment of assessments to users, ensuring they don't receive
the same assessment twice when purchasing new packages.

Note: This file was previously named for test assignments but now manages assessment assignments
as part of the transition to the assessment-only model.
"""
import json
import random
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_

from models import db, UserTestAssignment, User, Assessment

# Total number of unique assessments for each assessment type
# Variable names retained for backward compatibility
TOTAL_ACADEMIC_TESTS = 16
TOTAL_GENERAL_TESTS = 16

def get_available_test_numbers(user_id, test_type):
    """
    Get a list of assessment numbers that haven't been assigned to this user.
    
    Args:
        user_id (int): The user's ID
        test_type (str): Either 'academic' or 'general'
        
    Returns:
        list: Available assessment numbers (1-16) not previously assigned to this user
        
    Note: Function name retains "test_numbers" for backward compatibility
    """
    # Get all test numbers previously assigned to this user
    previous_assignments = UserTestAssignment.query.filter_by(
        user_id=user_id,
        test_type=test_type
    ).all()
    
    # Create a set of all previously assigned test numbers
    assigned_numbers = set()
    for assignment in previous_assignments:
        assigned_numbers.update(assignment.test_numbers)
    
    # Determine the total number of tests for this type
    total_tests = TOTAL_ACADEMIC_TESTS if test_type == 'academic' else TOTAL_GENERAL_TESTS
    
    # Calculate which test numbers are still available (1-indexed)
    available_numbers = [n for n in range(1, total_tests + 1) if n not in assigned_numbers]
    
    return available_numbers

def assign_tests_to_user(user_id, test_type, num_tests, access_days=15):
    """
    Assign a specific number of assessments to a user, ensuring they don't receive 
    assessments they've already seen.
    
    Args:
        user_id (int): The user's ID
        test_type (str): Either 'academic' or 'general'
        num_tests (int): Number of assessments to assign (1, 2 or 4)
        access_days (int): Number of days the assessment package is valid (15 or 30)
        
    Returns:
        list: The assigned assessment numbers
        bool: True if successful, False if not enough unique assessments available
        
    Note: Function name retains "tests" terminology for backward compatibility
    """
    # Validate parameters
    if num_tests not in [1, 2, 4]:
        raise ValueError("Number of assessments must be 1, 2, or 4")
    if test_type not in ['academic', 'general']:
        raise ValueError("Assessment type must be 'academic' or 'general'")
    
    # Get available test numbers
    available_numbers = get_available_test_numbers(user_id, test_type)
    
    # Check if we have enough unique tests
    if len(available_numbers) < num_tests:
        return [], False
    
    # Randomly select tests from available numbers
    assigned_numbers = random.sample(available_numbers, num_tests)
    
    # Create expiry date
    expiry_date = datetime.utcnow() + timedelta(days=access_days)
    
    # Create new assignment record
    assignment = UserTestAssignment(
        user_id=user_id,
        test_type=test_type,
        assigned_test_numbers=json.dumps(assigned_numbers),
        purchase_date=datetime.utcnow(),
        expiry_date=expiry_date
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    # Return the assigned test numbers
    return assigned_numbers, True

def get_current_test_assignments(user_id, test_type):
    """
    Get the currently assigned tests for a user that haven't expired.
    
    Args:
        user_id (int): The user's ID
        test_type (str): Either 'academic' or 'general'
        
    Returns:
        list: Currently assigned test numbers
    """
    # Get most recent assignment that hasn't expired
    assignment = UserTestAssignment.query.filter(
        UserTestAssignment.user_id == user_id,
        UserTestAssignment.test_type == test_type,
        UserTestAssignment.expiry_date > datetime.utcnow()
    ).order_by(UserTestAssignment.purchase_date.desc()).first()
    
    if assignment:
        return assignment.test_numbers
    
    return []

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
    
    # Get assessment objects for this type
    assessments = Assessment.query.filter_by(
        assessment_type=assessment_type,
        status='active'
    ).order_by(Assessment.creation_date.desc()).limit(4).all()
    
    return assessments