"""
Check the new General Training Reading test structure.
"""
from app import app, db
from models import PracticeTest, CompletePracticeTest

def check_new_structure():
    """Check the newly created General Training Reading test structure."""
    with app.app_context():
        # Get all General Training reading tests
        tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).order_by(PracticeTest.section).all()
        
        print(f"Found {len(tests)} General Training Reading tests")
        
        # Check each test
        for test in tests:
            print(f"\nTest: {test.title} (ID: {test.id})")
            print(f"  Section: {test.section}")
            print(f"  Description: {test.description}")
            print(f"  Time Limit: {test.time_limit} minutes")
            print(f"  Complete Test ID: {test.complete_test_id}")
        
        # Check the complete test
        if tests and tests[0].complete_test_id:
            complete_test = CompletePracticeTest.query.get(tests[0].complete_test_id)
            if complete_test:
                print(f"\nComplete Test: {complete_test.title} (ID: {complete_test.id})")
                print(f"  IELTS Test Type: {complete_test.ielts_test_type}")
                print(f"  Test Number: {complete_test.test_number}")
                print(f"  Description: {complete_test.description}")
                print(f"  Is Free: {complete_test.is_free}")
                print(f"  Subscription Level: {complete_test.subscription_level}")

if __name__ == "__main__":
    check_new_structure()