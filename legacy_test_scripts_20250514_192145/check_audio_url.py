from main import app
from models import PracticeTest

with app.app_context():
    test = PracticeTest.query.filter_by(test_type='listening', section=1).first()
    if test:
        print(f"Test ID: {test.id}")
        print(f"Title: {test.title}")
        print(f"Audio URL: {test.audio_url}")
    else:
        print("No listening test found")