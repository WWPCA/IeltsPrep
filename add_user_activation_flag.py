"""
Add is_active flag to User table.
This script adds the is_active flag to track if a user has completed payment.
"""
import sys
from sqlalchemy import Column, Boolean
from sqlalchemy.sql import text
from app import db
from models import User

def add_user_activation_flag():
    """Add is_active column to User table and set existing users as active."""
    try:
        # Check if the column already exists
        result = db.session.execute(text("SELECT * FROM information_schema.columns WHERE table_name='user' AND column_name='is_active'"))
        column_exists = result.rowcount > 0
        
        if not column_exists:
            # Add the column to the User table
            print("Adding is_active column to User table...")
            db.engine.execute('ALTER TABLE "user" ADD COLUMN is_active BOOLEAN DEFAULT false')
            
            # Set all existing users as active
            print("Setting existing users as active...")
            db.engine.execute('UPDATE "user" SET is_active = true')
            
            print("is_active column added successfully.")
        else:
            print("is_active column already exists.")
            
        return True
    except Exception as e:
        print(f"Error adding is_active column: {str(e)}")
        return False

if __name__ == "__main__":
    add_user_activation_flag()