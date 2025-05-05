"""
Check General Training Writing tests.
"""
from app import app
from models import PracticeTest

def check_general_writing_tests():
    """Check the General Training Writing tests in the database."""
    with app.app_context():
        tests = PracticeTest.query.filter_by(
            ielts_test_type='general', 
            test_type='writing'
        ).order_by(PracticeTest.id).all()
        
        print(f"Found {len(tests)} General Training Writing tests")
        print("\nGeneral Training Writing Tests:")
        for i, test in enumerate(tests):
            print(f"{i+1}. {test.title} (Section {test.section})")
            
        # Count by section
        task1_count = PracticeTest.query.filter_by(
            ielts_test_type='general', 
            test_type='writing',
            section=1
        ).count()
        
        task2_count = PracticeTest.query.filter_by(
            ielts_test_type='general', 
            test_type='writing',
            section=2
        ).count()
        
        print(f"\nTask 1 (Letters): {task1_count}")
        print(f"Task 2 (Essays): {task2_count}")

if __name__ == "__main__":
    check_general_writing_tests()