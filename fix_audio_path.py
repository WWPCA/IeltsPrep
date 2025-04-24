from main import app
from models import PracticeTest
from app import db

with app.app_context():
    # Find the first listening test
    test = PracticeTest.query.filter_by(
        test_type='listening',
        section=1
    ).first()
    
    if not test:
        print("No listening test found to update.")
        exit()
    
    # Use an existing audio file that works
    new_audio_path = 'uploads/audio/ielts_listening_section1_1744256646.mp3'
    
    print(f"Updating audio URL from {test.audio_url} to {new_audio_path}")
    test.audio_url = new_audio_path
    
    # Save changes
    db.session.commit()
    
    print(f"Successfully updated listening test audio path for: {test.title}")