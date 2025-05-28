"""
Create a test user account for platform testing.
This script creates a test user with access to all assessment types.
"""

import sys
sys.path.append('.')

from app import app, db
from models import User
from datetime import datetime, timedelta

def create_test_user():
    """Create a test user account with full access."""
    
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        
        if test_user:
            print("Test user already exists!")
            print("Email: test@ieltsaiprep.com")
            print("Password: TestPass123!")
            return
        
        # Create new test user
        test_user = User()
        test_user.email = 'test@ieltsaiprep.com'
        test_user.name = 'Test User'
        test_user.assessment_preference = 'academic'
        test_user.set_password('TestPass123!')
        
        # Set user as fully activated
        test_user.account_activated = True
        test_user.email_verified = True
        test_user.is_active = True
        
        # Give user access to all assessment types
        test_user.assessment_package_status = 'All Products'
        test_user.assessment_package_expiry = datetime.now() + timedelta(days=365)
        
        # Set region and other fields
        test_user.region = 'North America'
        test_user.current_streak = 0
        test_user.longest_streak = 0
        test_user.last_activity_date = datetime.now()
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test user created successfully!")
        print("Email: test@ieltsaiprep.com")
        print("Password: TestPass123!")
        print("Access: All assessment types (Speaking & Writing)")
        print("Status: Fully activated and verified")

if __name__ == "__main__":
    create_test_user()