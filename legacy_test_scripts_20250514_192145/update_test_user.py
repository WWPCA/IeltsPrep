"""
Update test user with proper subscription details for testing.
"""
import os
import sys
from datetime import datetime, timedelta

# Add the current directory to the path to allow importing from app
sys.path.append('.')

from models import User, db
from app import app

def update_test_user():
    """Update test user with proper subscription details."""
    with app.app_context():
        # Find the test user
        test_user = User.query.filter_by(username="premium_user").first()
        if not test_user:
            print("Test user not found. Creating a new one...")
            # Create the test user if not exists
            from werkzeug.security import generate_password_hash
            test_user = User(
                username="premium_user",
                email="premium@example.com",
                password_hash=generate_password_hash("test1234"),
                region="United States",
                join_date=datetime.utcnow(),
                subscription_status="Value Pack",
                subscription_expiry=datetime.utcnow() + timedelta(days=30),
                preferred_language="en",
                test_preference="academic"
            )
            db.session.add(test_user)
        else:
            print(f"Found test user: {test_user.username}")
            # Update the existing user's subscription details
            test_user.subscription_status = "Value Pack"
            test_user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
        
        # Find the standard test user
        standard_user = User.query.filter_by(username="testuser").first()
        if standard_user:
            print(f"Updating standard user: {standard_user.username}")
            standard_user.subscription_status = "Value Pack"
            standard_user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
        
        # Find the general training test user
        general_user = User.query.filter_by(username="generaluser").first()
        if general_user:
            print(f"Updating general user: {general_user.username}")
            general_user.subscription_status = "Value Pack"
            general_user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        print("Test users updated successfully!")

if __name__ == "__main__":
    update_test_user()