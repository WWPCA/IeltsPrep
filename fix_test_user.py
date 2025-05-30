#!/usr/bin/env python3
"""
Fix test user account and assign direct assessment access
"""
import os
import sys
import json

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, UserAssessmentAssignment

def fix_test_user():
    with app.app_context():
        user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        if not user:
            print("Test user not found!")
            return
        
        print(f"Fixing user {user.id} ({user.email})")
        
        # Clear any existing broken assignments
        UserAssessmentAssignment.query.filter_by(user_id=user.id).delete()
        
        # Create new valid assignments with proper JSON
        assignments = [
            {'user_id': user.id, 'assessment_type': 'academic', 'assigned_assessment_ids': '[1, 2, 3, 4]'},
            {'user_id': user.id, 'assessment_type': 'general', 'assigned_assessment_ids': '[1, 2]'}
        ]
        
        for assignment_data in assignments:
            assignment = UserAssessmentAssignment(**assignment_data)
            db.session.add(assignment)
        
        db.session.commit()
        print("Test user fixed with valid assessment assignments")
        
        # Verify the fix
        assignments = UserAssessmentAssignment.query.filter_by(user_id=user.id).all()
        for assignment in assignments:
            try:
                ids = json.loads(assignment.assigned_assessment_ids)
                print(f"✓ {assignment.assessment_type}: {ids}")
            except json.JSONDecodeError as e:
                print(f"✗ {assignment.assessment_type}: JSON error - {e}")

if __name__ == "__main__":
    fix_test_user()