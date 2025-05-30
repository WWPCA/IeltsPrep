#!/usr/bin/env python3
"""
Test password verification for the test user
"""
import os
import sys
from werkzeug.security import check_password_hash

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def test_password():
    with app.app_context():
        user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        if not user:
            print("User not found!")
            return
        
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Password hash: {user.password_hash[:50]}...")
        
        # Test password
        test_password = "TestPass123!"
        print(f"Testing password: {test_password}")
        
        # Test using werkzeug directly
        result1 = check_password_hash(user.password_hash, test_password)
        print(f"Direct werkzeug check: {result1}")
        
        # Test using user method
        result2 = user.check_password(test_password)
        print(f"User method check: {result2}")
        
        # Test account status
        print(f"Account activated: {user.account_activated}")
        print(f"Email verified: {user.email_verified}")
        print(f"Is active: {user.is_active}")

if __name__ == "__main__":
    test_password()