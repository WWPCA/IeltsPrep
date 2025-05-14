"""
Ensure there are 12 practice tests for each IELTS test type (Academic and General).
This script checks the current count and adds more tests if needed.
"""

from app import app, db
from models import CompletePracticeTest, PracticeTest
from datetime import datetime

def ensure_twelve_tests():
    """Check and ensure 12 tests per category."""
    with app.app_context():
        # Check academic tests
        print("Checking academic tests...")
        academic_tests = CompletePracticeTest.query.filter_by(ielts_test_type='academic').all()
        academic_count = len(academic_tests)
        print(f"Found {academic_count} academic tests")
        
        # Check general tests
        print("\nChecking general training tests...")
        general_tests = CompletePracticeTest.query.filter_by(ielts_test_type='general').all()
        general_count = len(general_tests)
        print(f"Found {general_count} general training tests")
        
        # Print recommendation if tests are less than 12
        if academic_count < 12:
            print(f"\nNeed to add {12 - academic_count} more academic tests")
            print("Run add_more_tests.py to add more tests")
        
        if general_count < 12:
            print(f"\nNeed to add {12 - general_count} more general training tests")
            print("Run add_more_tests.py to add more tests")
            
        if academic_count >= 12 and general_count >= 12:
            print("\nBoth academic and general training have at least 12 tests each!")

if __name__ == "__main__":
    ensure_twelve_tests()