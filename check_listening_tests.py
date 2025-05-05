"""
Check Listening tests count in the database.
"""
from app import app
from models import PracticeTest

def check_listening_tests():
    """Check the Listening tests in the database."""
    with app.app_context():
        # Count all listening tests
        all_listening = PracticeTest.query.filter_by(test_type='listening').count()
        
        # List all listening tests with their titles
        print(f"Total Listening tests: {all_listening}")
        print("\nListening Tests:")
        tests = PracticeTest.query.filter_by(test_type='listening').order_by(
            PracticeTest.id
        ).all()
        
        for i, test in enumerate(tests):
            has_audio = "✓" if test.audio_url else "✗"
            print(f"{i+1}. {test.title} [Audio: {has_audio}]")

if __name__ == "__main__":
    check_listening_tests()