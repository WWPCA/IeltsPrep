"""
Add email verification columns to User table.
This script adds the email_verified, email_verification_token, and 
email_verification_sent_at columns to the User table.
"""
import sys
from sqlalchemy.sql import text
from app import db, app

def add_email_verification_columns():
    """Add email verification columns to User table."""
    try:
        with app.app_context():
            # Check if the email_verified column already exists
            result = db.session.execute(text(
                "SELECT * FROM information_schema.columns WHERE table_name='user' AND column_name='email_verified'"
            ))
            column_exists = result.rowcount > 0
            
            if not column_exists:
                # Add the columns to the User table
                print("Adding email verification columns to User table...")
                
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN email_verified BOOLEAN DEFAULT false'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN email_verification_token VARCHAR(100)'))
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN email_verification_sent_at TIMESTAMP'))
                
                # Commit the changes
                db.session.commit()
                
                print("Email verification columns added successfully.")
            else:
                print("Email verification columns already exist.")
                
            return True
    except Exception as e:
        print(f"Error adding email verification columns: {str(e)}")
        return False

if __name__ == "__main__":
    add_email_verification_columns()