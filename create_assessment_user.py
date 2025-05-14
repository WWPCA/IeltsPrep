"""
Create a development user for assessment access and testing purposes.
"""
import datetime
import logging
from app import app, db
from models import User, SpeakingPrompt
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_assessment_user():
    """Create a development user for assessment access."""
    
    # Check if the development user already exists
    existing_user = User.query.filter_by(username='assessmentuser').first()
    if existing_user:
        logger.info("Assessment user already exists! Username: assessmentuser, Password: assessmentpassword")
        return
    
    # Create a new assessment user
    assessment_user = User(
        username='assessmentuser',
        email='assessmentuser@example.com',
        region='global',
        assessment_package_status='active',  # Active package for full access
        assessment_package_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
        preferred_language='en',
        account_activated=True,
        email_verified=True
    )
    assessment_user.set_password('assessmentpassword')
    
    # Add assessment user to database
    db.session.add(assessment_user)
    
    # Ensure we have at least one speaking prompt for assessment
    if SpeakingPrompt.query.count() == 0:
        # Create sample speaking prompts for assessment
        speaking_prompts = [
            SpeakingPrompt(part=1, prompt_text="Tell me about your favorite hobby and why you enjoy it."),
            SpeakingPrompt(part=2, prompt_text="Describe a place you have visited that had a significant impact on you. You should say: where the place is, when you went there, what you did there, and explain why this place had such an impact on you."),
            SpeakingPrompt(part=3, prompt_text="Do you think travel is an important part of education? Why or why not?")
        ]
        
        for prompt in speaking_prompts:
            db.session.add(prompt)
    
    # Commit changes
    db.session.commit()
    
    logger.info("Successfully created assessment user!")
    logger.info("Username: assessmentuser")
    logger.info("Password: assessmentpassword")
    logger.info("This user has an active assessment package for full feature access.")

if __name__ == "__main__":
    with app.app_context():
        create_assessment_user()