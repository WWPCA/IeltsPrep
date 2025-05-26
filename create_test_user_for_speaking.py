"""
Create a test user for speaking assessment testing
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_test_user():
    """Create a test user with known credentials for testing speaking assessments"""
    
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='speaking@test.com').first()
        if existing_user:
            print(f"Test user already exists: speaking@test.com")
            print(f"Username: speaking_test")
            print(f"Password: testpass123")
            return
        
        # Create new test user
        test_user = User(
            username='speaking_test',
            email='speaking@test.com',
            password_hash=generate_password_hash('testpass123'),
            account_activated=True,
            email_verified=True,
            assessment_package_status='active'
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test user created successfully!")
        print("Email: speaking@test.com")
        print("Username: speaking_test") 
        print("Password: testpass123")
        print("Account is activated and ready for speaking assessments")

if __name__ == '__main__':
    create_test_user()