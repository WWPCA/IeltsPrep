"""
Add assessment package columns to User model.
This script adds the assessment_package_status and assessment_package_expiry
columns to the User table to support the move from subscriptions to assessment packages.
"""

from app import app, db
from models import User
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timedelta
import logging

def add_assessment_package_columns():
    """Add assessment package columns to User table."""
    
    with app.app_context():
        logging.info("Checking if assessment_package_status column exists...")
        
        # Check if the column already exists
        columns = [column.name for column in User.__table__.columns]
        
        # Add assessment_package_status column if it doesn't exist
        if 'assessment_package_status' not in columns:
            logging.info("Adding assessment_package_status column to User table...")
            
            # Add the column to the User table
            db.engine.execute('ALTER TABLE "user" ADD COLUMN assessment_package_status VARCHAR(20) DEFAULT \'none\'')
            logging.info("assessment_package_status column added successfully")
        else:
            logging.info("assessment_package_status column already exists")
            
        # Add assessment_package_expiry column if it doesn't exist
        if 'assessment_package_expiry' not in columns:
            logging.info("Adding assessment_package_expiry column to User table...")
            
            # Add the column to the User table
            db.engine.execute('ALTER TABLE "user" ADD COLUMN assessment_package_expiry TIMESTAMP')
            logging.info("assessment_package_expiry column added successfully")
        else:
            logging.info("assessment_package_expiry column already exists")
        
        # Commit the changes
        db.session.commit()
        logging.info("Database changes committed successfully")
        
        print("Assessment package columns added to User table")

if __name__ == "__main__":
    add_assessment_package_columns()