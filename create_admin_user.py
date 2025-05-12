#!/usr/bin/env python3
"""
Create Admin User Script

This script creates an admin user with the appropriate subscription status to access
the admin dashboard.
"""

import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Set up path to include app directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import app and models
from app import app, db
from models import User

def create_admin_user(email, password):
    """Create an admin user with the necessary permissions."""
    with app.app_context():
        # Extract username from email
        username = email.split('@')[0]
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            # Update to admin status
            existing_user.subscription_status = "Value Pack"
            existing_user.is_active = True
            existing_user.email_verified = True
            db.session.commit()
            print(f"Updated {email} to admin status.")
            return

        # Create new admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            join_date=datetime.utcnow(),
            preferred_language="en",
            test_preference="academic",
            is_active=True,
            email_verified=True,
            subscription_status="Value Pack",  # This is used to identify admins
            current_streak=0,
            longest_streak=0,
            last_activity_date=datetime.utcnow(),
            _activity_history="{}",
            _test_history="{}",
            _speaking_scores="{}",
            _completed_tests="[]",
            _password_history="[]"
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user {email} created successfully.")

if __name__ == "__main__":
    # Create admin user with default credentials
    create_admin_user("admin@ieltsaiprep.com", "AdminPass123!")
    
    # If command line arguments are provided, use them
    if len(sys.argv) >= 3:
        create_admin_user(sys.argv[1], sys.argv[2])