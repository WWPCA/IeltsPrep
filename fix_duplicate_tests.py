"""
Fix duplicate IELTS practice tests in the database.
"""

import json
from app import app, db
from sqlalchemy import text
from models import CompletePracticeTest, PracticeTest

def fix_duplicate_tests():
    """Remove duplicate practice tests while preserving the complete test structure."""
    
    print("Cleaning up duplicate tests...")
    
    with app.app_context():
        # Get Academic test duplicates - keep the most recent ones (higher IDs)
        # First, identify duplicates by test_number
        test_numbers_query = text("""
            SELECT test_number, ielts_test_type, COUNT(*) as count
            FROM complete_practice_test
            GROUP BY test_number, ielts_test_type
            HAVING COUNT(*) > 1
            ORDER BY test_number
        """)
        duplicates = db.session.execute(test_numbers_query).fetchall()
        
        if not duplicates:
            print("No duplicate tests found.")
            return
            
        print(f"Found {len(duplicates)} duplicate test sets.")
        
        # For each duplicate set, keep only the test with the highest ID
        for duplicate in duplicates:
            test_number = duplicate[0]
            test_type = duplicate[1]
            count = duplicate[2]
            
            # Get all IDs for this test number and type
            test_ids_query = text("""
                SELECT id 
                FROM complete_practice_test 
                WHERE test_number = :test_number AND ielts_test_type = :test_type
                ORDER BY id
            """)
            test_ids = db.session.execute(
                test_ids_query, 
                {"test_number": test_number, "test_type": test_type}
            ).fetchall()
            
            # Keep the highest ID, delete the rest
            ids_to_delete = [row[0] for row in test_ids[:-1]]  # All but the last one
            
            if ids_to_delete:
                print(f"Deleting {len(ids_to_delete)} duplicate(s) of {test_type} test #{test_number}")
                
                # First, delete any related practice test sections
                for test_id in ids_to_delete:
                    # Find all related practice tests
                    related_practice_tests = db.session.query(PracticeTest).filter_by(complete_test_id=test_id).all()
                    for pt in related_practice_tests:
                        print(f"Deleting practice test section ID {pt.id} (from complete test {test_id})")
                        db.session.delete(pt)
                
                # Now it's safe to delete the complete tests
                for test_id in ids_to_delete:
                    delete_query = text("DELETE FROM complete_practice_test WHERE id = :id")
                    db.session.execute(delete_query, {"id": test_id})
                    print(f"Deleted complete test ID {test_id}")
        
        # Commit changes
        db.session.commit()
        print("Duplicate test cleanup completed.")

if __name__ == "__main__":
    fix_duplicate_tests()