from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_premium_user():
    """Create a premium test user."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email='premium@example.com').first()
        if existing_user:
            print(f"User already exists with ID {existing_user.id}")
            # Update subscription status just to be sure
            existing_user.subscription_status = 'premium'
            db.session.commit()
            return
            
        # Create new user
        user = User(
            username='premium_user',
            email='premium@example.com',
            password_hash=generate_password_hash('test1234'),
            subscription_status='premium',
            test_preference='academic'
        )
        
        db.session.add(user)
        db.session.commit()
        print(f"User created with ID {user.id}")

if __name__ == '__main__':
    create_premium_user()