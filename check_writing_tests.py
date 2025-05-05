"""
Check the number of writing tests in the database.
"""
from app import app, db
from models import PracticeTest

def check_writing_tests():
    """Check the number of writing tests in the database."""
    with app.app_context():
        total_writing_tests = PracticeTest.query.filter_by(test_type='writing').count()
        academic_writing_tests = PracticeTest.query.filter_by(
            test_type='writing', 
            ielts_test_type='academic'
        ).count()
        general_writing_tests = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='general'
        ).count()
        
        print(f"Total writing tests: {total_writing_tests}")
        print(f"Academic writing tests: {academic_writing_tests}")
        print(f"General writing tests: {general_writing_tests}")
        
        # List academic writing tests
        print("\nAcademic Writing Tests:")
        academic_tests = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='academic'
        ).all()
        
        for i, test in enumerate(academic_tests, 1):
            print(f"{i}. {test.title}")

if __name__ == "__main__":
    check_writing_tests()