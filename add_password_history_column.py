"""
Add _password_history column to User table
This script adds the missing _password_history column to fix registration errors.
"""

from app import app, db
from sqlalchemy import Column, Text, text

def add_password_history_column():
    """Add the _password_history column to the User table"""
    print("Adding _password_history column to User table...")
    
    # Connect to database
    with app.app_context():
        # Check if column already exists
        try:
            # Use raw SQL to check if column exists with text() wrapper
            sql_check = text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='_password_history'")
            result = db.session.execute(sql_check)
            column_exists = result.scalar() is not None
            
            if column_exists:
                print("Column _password_history already exists. No changes needed.")
                return
                
            # Add the column using text() wrapper
            sql_add_column = text("ALTER TABLE \"user\" ADD COLUMN _password_history TEXT DEFAULT '[]'")
            db.session.execute(sql_add_column)
            db.session.commit()
            print("Successfully added _password_history column to User table")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding column: {str(e)}")
            raise

if __name__ == "__main__":
    add_password_history_column()