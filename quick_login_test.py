"""
Quick Login Test for Maya Testing
This script creates a direct login session for testing purposes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from flask_login import login_user
from werkzeug.security import check_password_hash

def create_test_session():
    """Create a test session for Maya testing."""
    with app.app_context():
        try:
            # Find the test user
            test_user = User.query.filter_by(email='test@ieltsaiprep.com').first()
            
            if not test_user:
                print("Test user not found. Creating test user...")
                test_user = User(
                    email='test@ieltsaiprep.com',
                    region='Canada',
                    assessment_preference='academic',
                    account_activated=True,
                    email_verified=True,
                    assessment_package_status='All Access',
                    assessment_package_expiry=None
                )
                test_user.set_password('TestPass123!')
                db.session.add(test_user)
                db.session.commit()
                print("Test user created successfully!")
            
            # Verify password
            if check_password_hash(test_user.password_hash, 'TestPass123!'):
                print("✓ Test user credentials verified")
                print(f"✓ User has access to: {test_user.assessment_package_status}")
                print(f"✓ Account activated: {test_user.account_activated}")
                print(f"✓ Email verified: {test_user.email_verified}")
                
                # Check assessment access
                print("\n=== Assessment Access ===")
                assessments = ['Academic Speaking', 'Academic Writing', 'General Speaking', 'General Writing']
                for assessment in assessments:
                    has_access = test_user.has_package_access(assessment) or test_user.is_admin
                    print(f"✓ {assessment}: {'Available' if has_access else 'Not Available'}")
                
                return True
            else:
                print("✗ Password verification failed")
                return False
                
        except Exception as e:
            print(f"✗ Error creating test session: {str(e)}")
            return False

if __name__ == "__main__":
    success = create_test_session()
    if success:
        print("\n✓ Test user is ready for Maya testing!")
        print("You can now access speaking assessments to test Maya.")
    else:
        print("\n✗ Test user setup failed.")