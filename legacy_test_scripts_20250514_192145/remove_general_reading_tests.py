"""
Remove all General Training Reading tests from the database.
"""
from app import app, db
from models import PracticeTest, CompletePracticeTest
from sqlalchemy import text

def remove_general_reading_tests():
    """Remove all General Training Reading tests from the database."""
    with app.app_context():
        # Get all General Training reading test IDs
        general_reading_tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).all()
        
        test_ids = [test.id for test in general_reading_tests]
        
        print(f"Found {len(test_ids)} General Training Reading tests to remove")
        
        if not test_ids:
            print("No General Training Reading tests found. Nothing to remove.")
            return
        
        # Delete the tests
        try:
            for test_id in test_ids:
                test = PracticeTest.query.get(test_id)
                if test:
                    db.session.delete(test)
                    print(f"Deleted test: {test.title} (ID: {test_id})")
            
            db.session.commit()
            print("Successfully removed all General Training Reading tests")
        except Exception as e:
            db.session.rollback()
            print(f"Error removing tests: {str(e)}")

if __name__ == "__main__":
    remove_general_reading_tests()