#!/usr/bin/env python3
"""
Assign assessments to test user for testing purposes
"""
import os
import sys
from datetime import datetime, timedelta

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, UserAssessmentAssignment
from assessment_assignment_service import assign_assessments_to_user

def assign_test_assessments():
    with app.app_context():
        user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        if not user:
            print("Test user not found!")
            return
        
        print(f"Assigning assessments to user {user.id} ({user.email})")
        
        # Assign 4 assessments for each type
        assessment_types = ['academic', 'general']
        
        for assessment_type in assessment_types:
            print(f"Assigning {assessment_type} assessments...")
            try:
                assigned_ids, success = assign_assessments_to_user(user.id, assessment_type, 4)
                if success:
                    print(f"Successfully assigned {len(assigned_ids)} {assessment_type} assessments: {assigned_ids}")
                else:
                    print(f"Failed to assign {assessment_type} assessments")
            except Exception as e:
                print(f"Error assigning {assessment_type}: {e}")
        
        # Verify assignments
        assignments = UserAssessmentAssignment.query.filter_by(user_id=user.id).all()
        print(f"\nTotal assignments: {len(assignments)}")
        for assignment in assignments:
            print(f"- {assignment.assessment_type}: Assessments {assignment.assessment_ids}")

if __name__ == "__main__":
    assign_test_assessments()