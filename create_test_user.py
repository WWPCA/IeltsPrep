"""
Create a test user for development and testing purposes.
"""
import datetime
import logging
from app import app, db
from models import User, SpeakingPrompt
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user():
    """Create a test user for development purposes."""
    
    # Check if the test user already exists
    existing_user = User.query.filter_by(username='testuser').first()
    if existing_user:
        logger.info("Test user already exists! Username: testuser, Password: testpassword")
        return
    
    # Create a new test user
    test_user = User(
        username='testuser',
        email='testuser@example.com',
        region='global',
        subscription_status='premium',  # Premium account for full feature access
        subscription_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
        preferred_language='en'
    )
    test_user.set_password('testpassword')
    
    # Add test user to database
    db.session.add(test_user)
    
    # Ensure we have at least one speaking prompt for testing
    if SpeakingPrompt.query.count() == 0:
        # Create sample speaking prompts for testing
        speaking_prompts = [
            SpeakingPrompt(part=1, prompt_text="Tell me about your favorite hobby and why you enjoy it."),
            SpeakingPrompt(part=2, prompt_text="Describe a place you have visited that had a significant impact on you. You should say: where the place is, when you went there, what you did there, and explain why this place had such an impact on you."),
            SpeakingPrompt(part=3, prompt_text="Do you think travel is an important part of education? Why or why not?")
        ]
        
        for prompt in speaking_prompts:
            db.session.add(prompt)
    
    # Commit changes
    db.session.commit()
    
    logger.info("Successfully created test user!")
    logger.info("Username: testuser")
    logger.info("Password: testpassword")
    logger.info("This user has premium subscription status for full feature testing.")

if __name__ == "__main__":
    with app.app_context():
        create_test_user()