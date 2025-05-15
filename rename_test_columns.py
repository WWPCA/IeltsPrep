"""
Update column names from test_id to assessment_id.
This script updates column names that were changed in models.py to maintain database consistency.
"""
import os
import sys
from sqlalchemy import text
from app import app, db

def rename_test_to_assessment_columns():
    """Rename test_id columns to assessment_id for affected tables."""
    try:
        with app.app_context():
            # Update ConnectionIssueLog table
            db.session.execute(text(
                "ALTER TABLE connection_issue_log RENAME COLUMN test_id TO assessment_id"
            ))
            
            # Update AssessmentSession table
            db.session.execute(text(
                "ALTER TABLE assessment_session RENAME COLUMN test_id TO assessment_id"
            ))
            
            db.session.commit()
            print("Column names successfully updated from test_id to assessment_id")
            return True
    except Exception as e:
        print(f"Error updating column names: {str(e)}")
        return False

if __name__ == "__main__":
    success = rename_test_to_assessment_columns()
    sys.exit(0 if success else 1)