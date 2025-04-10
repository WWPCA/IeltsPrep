from app import app, db
from models import PracticeTest

with app.app_context():
    test = PracticeTest.query.filter_by(test_type='listening').first()
    if test:
        test.audio_url = 'uploads/audio/listening_test_section1_1744256262.mp3'
        db.session.commit()
        print(f'Updated audio URL to: {test.audio_url}')
    else:
        print('No listening test found in database')