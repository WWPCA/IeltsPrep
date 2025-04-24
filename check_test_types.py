"""
Check and update test types in the database.
This script ensures all tests are using only 'academic' or 'general' types.
"""

from app import app, db
from models import CompletePracticeTest, PracticeTest
from datetime import datetime

def check_test_types():
    """Check and display test types in the database."""
    with app.app_context():
        # Check complete tests
        print("Checking complete practice tests...")
        complete_tests = CompletePracticeTest.query.all()
        for test in complete_tests:
            if test.ielts_test_type not in ['academic', 'general']:
                print(f"Found test with type '{test.ielts_test_type}': {test.title} (ID: {test.id})")
                # Update to the closest appropriate type
                if test.ielts_test_type in ['ukvi', 'ielts_online']:
                    # These are similar to academic
                    test.ielts_test_type = 'academic'
                    print(f"  Updated to 'academic'")
                elif test.ielts_test_type == 'life_skills':
                    # Life skills is closer to general
                    test.ielts_test_type = 'general'
                    print(f"  Updated to 'general'")
        
        # Check individual practice tests
        print("\nChecking individual practice tests...")
        practice_tests = PracticeTest.query.all()
        for test in practice_tests:
            if test.ielts_test_type not in ['academic', 'general']:
                print(f"Found test with type '{test.ielts_test_type}': {test.title} (ID: {test.id})")
                # Update to the closest appropriate type
                if test.ielts_test_type in ['ukvi', 'ielts_online']:
                    # These are similar to academic
                    test.ielts_test_type = 'academic'
                    print(f"  Updated to 'academic'")
                elif test.ielts_test_type == 'life_skills':
                    # Life skills is closer to general
                    test.ielts_test_type = 'general'
                    print(f"  Updated to 'general'")
        
        # Commit changes
        db.session.commit()
        print("All test types have been checked and updated!")

if __name__ == "__main__":
    check_test_types()