"""
Check Speaking tests count in the database.
"""
from app import app
from models import PracticeTest

def check_speaking_tests():
    """Check the Speaking tests in the database."""
    with app.app_context():
        # Count all speaking tests
        all_speaking = PracticeTest.query.filter_by(test_type='speaking').count()
        
        # List all speaking tests with their titles
        print(f"Total Speaking tests: {all_speaking}")
        print("\nSpeaking Tests:")
        tests = PracticeTest.query.filter_by(test_type='speaking').order_by(
            PracticeTest.id
        ).all()
        
        for i, test in enumerate(tests):
            print(f"{i+1}. {test.title}")

if __name__ == "__main__":
    check_speaking_tests()