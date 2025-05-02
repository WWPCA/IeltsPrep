"""
Test Assignment Service
This module manages the assignment of tests to users, ensuring they don't receive
the same test twice when purchasing new packages.
"""
import json
import random
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_

from models import db, UserTestAssignment, CompletePracticeTest, User

# Total number of unique tests for each test type
TOTAL_ACADEMIC_TESTS = 16
TOTAL_GENERAL_TESTS = 16

def get_available_test_numbers(user_id, test_type):
    """
    Get a list of test numbers that haven't been assigned to this user.
    
    Args:
        user_id (int): The user's ID
        test_type (str): Either 'academic' or 'general'
        
    Returns:
        list: Available test numbers (1-16) not previously assigned to this user
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

def assign_tests_to_user(user_id, test_type, num_tests, subscription_days=15):
    """
    Assign a specific number of tests to a user, ensuring they don't receive 
    tests they've already seen.
    
    Args:
        user_id (int): The user's ID
        test_type (str): Either 'academic' or 'general'
        num_tests (int): Number of tests to assign (1, 2 or 4)
        subscription_days (int): Number of days the subscription is valid (15 or 30)
        
    Returns:
        list: The assigned test numbers
        bool: True if successful, False if not enough unique tests available
    """
    # Validate parameters
    if num_tests not in [1, 2, 4]:
        raise ValueError("Number of tests must be 1, 2, or 4")
    if test_type not in ['academic', 'general']:
        raise ValueError("Test type must be 'academic' or 'general'")
    
    # Get available test numbers
    available_numbers = get_available_test_numbers(user_id, test_type)
    
    # Check if we have enough unique tests
    if len(available_numbers) < num_tests:
        return [], False
    
    # Randomly select tests from available numbers
    assigned_numbers = random.sample(available_numbers, num_tests)
    
    # Create expiry date
    expiry_date = datetime.utcnow() + timedelta(days=subscription_days)
    
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

def get_user_accessible_tests(user_id, test_type):
    """
    Get CompletePracticeTest objects that the user currently has access to.
    
    Args:
        user_id (int): The user's ID
        test_type (str): Either 'academic' or 'general'
        
    Returns:
        list: CompletePracticeTest objects the user can access
    """
    # Get the user's current assigned test numbers
    assigned_numbers = get_current_test_assignments(user_id, test_type)
    
    if not assigned_numbers:
        # No tests assigned or all assignments expired
        return []
    
    # Get one test object for each assigned test number (latest version)
    test_objects = []
    
    for test_number in assigned_numbers:
        # Get the latest version of this test number
        latest_test = CompletePracticeTest.query.filter_by(
            ielts_test_type=test_type,
            test_number=test_number
        ).order_by(CompletePracticeTest.creation_date.desc()).first()
        
        if latest_test:
            test_objects.append(latest_test)
    
    return test_objects