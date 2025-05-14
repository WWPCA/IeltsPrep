"""
Check Academic Writing tests.
"""
from main import app
from models import PracticeTest, db

def check_academic_writing_tests():
    """Check the Academic Writing tests in the database."""
    with app.app_context():
        tests = PracticeTest.query.filter_by(
            ielts_test_type='academic', 
            test_type='writing'
        ).order_by(PracticeTest.id).all()
        
        print(f"Found {len(tests)} Academic Writing tests")
        print("\nAcademic Writing Tests:")
        for i, test in enumerate(tests):
            print(f"{i+1}. {test.title} (Section {test.section})")
            
        # Count by section
        task1_count = PracticeTest.query.filter_by(
            ielts_test_type='academic', 
            test_type='writing',
            section=1
        ).count()
        
        task2_count = PracticeTest.query.filter_by(
            ielts_test_type='academic', 
            test_type='writing',
            section=2
        ).count()
        
        print(f"\nTask 1 (Charts/Graphs): {task1_count}")
        print(f"Task 2 (Essays): {task2_count}")

if __name__ == "__main__":
    check_academic_writing_tests()
