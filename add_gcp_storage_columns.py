"""
Add GCP storage columns to UserTestAttempt model.
This script adds columns to store Google Cloud Storage references for transcripts and assessments.
"""

import os
from app import app, db
from sqlalchemy import text

def add_gcp_storage_columns():
    """Add GCP storage reference columns to UserTestAttempt table."""
    try:
        with app.app_context():
            conn = db.engine.connect()
            
            # Check if the columns already exist
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user_test_attempt' AND column_name='gcp_transcript_path'"
            )
            result = conn.execute(check_column_query)
            transcript_column_exists = result.scalar() is not None
            
            if not transcript_column_exists:
                # Add transcript path column
                alter_table_query = text(
                    "ALTER TABLE user_test_attempt ADD COLUMN gcp_transcript_path VARCHAR(255)"
                )
                conn.execute(alter_table_query)
                print("Added gcp_transcript_path column to user_test_attempt table.")
            else:
                print("Column gcp_transcript_path already exists in user_test_attempt table.")
            
            # Check for assessment path column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user_test_attempt' AND column_name='gcp_assessment_path'"
            )
            result = conn.execute(check_column_query)
            assessment_column_exists = result.scalar() is not None
            
            if not assessment_column_exists:
                # Add assessment path column
                alter_table_query = text(
                    "ALTER TABLE user_test_attempt ADD COLUMN gcp_assessment_path VARCHAR(255)"
                )
                conn.execute(alter_table_query)
                print("Added gcp_assessment_path column to user_test_attempt table.")
            else:
                print("Column gcp_assessment_path already exists in user_test_attempt table.")
            
            # Check for expiry date column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user_test_attempt' AND column_name='transcript_expiry_date'"
            )
            result = conn.execute(check_column_query)
            expiry_column_exists = result.scalar() is not None
            
            if not expiry_column_exists:
                # Add transcript expiry date column
                alter_table_query = text(
                    "ALTER TABLE user_test_attempt ADD COLUMN transcript_expiry_date TIMESTAMP WITH TIME ZONE"
                )
                conn.execute(alter_table_query)
                print("Added transcript_expiry_date column to user_test_attempt table.")
            else:
                print("Column transcript_expiry_date already exists in user_test_attempt table.")
            
            conn.commit()
            conn.close()
            print("Successfully updated user_test_attempt table for GCP storage.")
    except Exception as e:
        print(f"Error updating user_test_attempt table: {str(e)}")
        
if __name__ == "__main__":
    add_gcp_storage_columns()