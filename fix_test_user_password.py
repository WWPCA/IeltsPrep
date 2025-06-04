"""
Fix Test User Password Hash
This script fixes the password hash for the test user to resolve login issues.
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def fix_test_user_password():
    """Fix the test user's password hash"""
    with app.app_context():
        try:
            # Find the test user
            test_user = User.query.filter_by(email='test@ieltsaiprep.com').first()
            
            if not test_user:
                print("Test user not found. Creating new test user...")
                # Create new test user with proper password hash
                test_user = User(
                    username='testuser',
                    email='test@ieltsaiprep.com',
                    password_hash=generate_password_hash('TestPass123!'),
                    account_activated=True,
                    email_verified=True,
                    is_admin=False
                )
                db.session.add(test_user)
                db.session.commit()
                print("New test user created successfully!")
            else:
                print("Found test user. Updating password hash...")
                # Update the password hash properly
                test_user.password_hash = generate_password_hash('TestPass123!')
                test_user.account_activated = True
                test_user.email_verified = True
                db.session.commit()
                print("Test user password hash updated successfully!")
            
            print(f"Test user ID: {test_user.id}")
            print(f"Email: {test_user.email}")
            print(f"Account activated: {test_user.account_activated}")
            print(f"Email verified: {test_user.email_verified}")
            print("Password hash format is now valid")
            
        except Exception as e:
            print(f"Error fixing test user password: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_test_user_password()