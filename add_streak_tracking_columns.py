"""
Add streak tracking columns to User table.
This script adds the current_streak, longest_streak, last_activity_date,
_activity_history, _test_history, _speaking_scores, _completed_tests, and
_password_history columns to the User table.
"""
import sys
from sqlalchemy.sql import text
from app import db, app

def add_streak_tracking_columns():
    """Add streak tracking columns to User table."""
    try:
        with app.app_context():
            # Check if the current_streak column already exists
            result = db.session.execute(text(
                "SELECT * FROM information_schema.columns WHERE table_name='user' AND column_name='current_streak'"
            ))
            column_exists = result.rowcount > 0
            
            if not column_exists:
                # Add the columns to the User table
                print("Adding streak tracking columns to User table...")
                
                # Basic streak tracking
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN current_streak INTEGER DEFAULT 0'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN longest_streak INTEGER DEFAULT 0'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN last_activity_date TIMESTAMP'))
                
                # JSON history fields
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN _activity_history TEXT DEFAULT \'[]\' NOT NULL'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN _test_history TEXT DEFAULT \'[]\' NOT NULL'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN _speaking_scores TEXT DEFAULT \'[]\' NOT NULL'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN _completed_tests TEXT DEFAULT \'[]\' NOT NULL'))
                
                # Password history for security
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN _password_history TEXT DEFAULT \'[]\' NOT NULL'))
                
                # Commit the changes
                db.session.commit()
                
                print("Streak tracking columns added successfully.")
            else:
                print("Streak tracking columns already exist.")
                
            return True
    except Exception as e:
        print(f"Error adding streak tracking columns: {str(e)}")
        return False

if __name__ == "__main__":
    add_streak_tracking_columns()