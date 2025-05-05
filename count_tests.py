"""
Count tests of different types in the database.
"""
from app import app, db
from models import PracticeTest

def count_tests():
    """Count tests of different types in the database."""
    with app.app_context():
        # Count all tests by type and IELTS test type
        test_types = ['reading', 'writing', 'listening', 'speaking']
        ielts_types = ['academic', 'general']
        
        for ielts_type in ielts_types:
            print(f"\n{ielts_type.capitalize()} IELTS Test Counts:")
            for test_type in test_types:
                count = PracticeTest.query.filter_by(
                    test_type=test_type,
                    ielts_test_type=ielts_type
                ).count()
                print(f"  {test_type.capitalize()}: {count}")

if __name__ == "__main__":
    count_tests()