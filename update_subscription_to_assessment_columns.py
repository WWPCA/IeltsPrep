"""
Update subscription columns to assessment package columns.
This script renames subscription_status to assessment_package_status and 
subscription_expiry to assessment_package_expiry to align the database with the new terminology.
"""

from app import app, db
from sqlalchemy import text
import logging

def update_subscription_to_assessment_columns():
    """Update subscription columns to assessment package columns."""
    
    with app.app_context():
        logging.info("Starting database column migration...")
        
        try:
            # Check if the columns already exist to avoid errors
            column_check = db.session.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'assessment_package_status'")
            ).fetchone()
            
            if not column_check:
                # Rename the subscription_status column to assessment_package_status
                db.session.execute(
                    text("ALTER TABLE \"user\" RENAME COLUMN subscription_status TO assessment_package_status")
                )
                
                # Rename the subscription_expiry column to assessment_package_expiry
                db.session.execute(
                    text("ALTER TABLE \"user\" RENAME COLUMN subscription_expiry TO assessment_package_expiry")
                )
                
                # Rename the test_preference column to assessment_preference
                db.session.execute(
                    text("ALTER TABLE \"user\" RENAME COLUMN test_preference TO assessment_preference")
                )
                
                # Rename the _test_history column to _assessment_history
                db.session.execute(
                    text("ALTER TABLE \"user\" RENAME COLUMN _test_history TO _assessment_history")
                )
                
                # Rename the _completed_tests column to _completed_assessments
                db.session.execute(
                    text("ALTER TABLE \"user\" RENAME COLUMN _completed_tests TO _completed_assessments")
                )
                
                # Commit the changes
                db.session.commit()
                logging.info("Successfully migrated database columns")
                print("Database columns have been successfully migrated")
            else:
                logging.info("Columns already migrated, skipping")
                print("Columns already migrated, skipping")
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating database columns: {e}")
            print(f"Error: {e}")
        
        finally:
            db.session.close()
            db.engine.dispose()

if __name__ == "__main__":
    update_subscription_to_assessment_columns()