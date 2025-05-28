"""
Add password reset columns to User table.
This script adds the password_reset_token and password_reset_expires columns.
"""

from app import app, db
from models import User
from sqlalchemy import text

def add_password_reset_columns():
    """Add password reset columns to User table."""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            # Add password_reset_token column if it doesn't exist
            if 'password_reset_token' not in columns:
                db.session.execute(text(
                    'ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255)'
                ))
                print("Added password_reset_token column")
            else:
                print("password_reset_token column already exists")
            
            # Add password_reset_expires column if it doesn't exist
            if 'password_reset_expires' not in columns:
                db.session.execute(text(
                    'ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP'
                ))
                print("Added password_reset_expires column")
            else:
                print("password_reset_expires column already exists")
            
            db.session.commit()
            print("Password reset columns added successfully!")
            
        except Exception as e:
            print(f"Error adding password reset columns: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_password_reset_columns()