"""
Create a General Training test user for development and testing purposes.
"""

from app import app, db
from models import User
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def create_general_test_user():
    """Create a test user with General Training preference."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='generaluser').first()
        if existing_user:
            print("General Training test user already exists.")
            
            # Update to premium subscription
            existing_user.subscription_status = 'premium'
            existing_user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
            existing_user.test_preference = 'general'
            db.session.commit()
            print("General Training test user updated to premium subscription.")
            return
        
        # Create new test user
        new_user = User(
            username='generaluser',
            email='general@example.com',
            password_hash=generate_password_hash('ielts123'),
            subscription_status='premium',
            subscription_expiry=datetime.utcnow() + timedelta(days=30),
            test_preference='general',
            region='UK',
            join_date=datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        print("Created new General Training test user with premium subscription.")
        print("Username: generaluser")
        print("Password: ielts123")

if __name__ == '__main__':
    create_general_test_user()