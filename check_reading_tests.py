"""
Check Reading tests count in the database.
"""
from app import app
from models import PracticeTest

def check_reading_tests():
    """Check the Reading tests in the database."""
    with app.app_context():
        # Count all reading tests
        all_reading = PracticeTest.query.filter_by(test_type='reading').count()
        
        # Count academic reading tests
        academic_reading = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='academic'
        ).count()
        
        # Count general reading tests
        general_reading = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).count()
        
        print(f"Total Reading tests: {all_reading}")
        print(f"Academic Reading tests: {academic_reading}")
        print(f"General Training Reading tests: {general_reading}")
        
        # List all reading tests with their titles
        print("\nReading Tests:")
        tests = PracticeTest.query.filter_by(test_type='reading').order_by(
            PracticeTest.ielts_test_type, PracticeTest.id
        ).all()
        
        for i, test in enumerate(tests):
            print(f"{i+1}. [{test.ielts_test_type.capitalize()}] {test.title}")

if __name__ == "__main__":
    check_reading_tests()