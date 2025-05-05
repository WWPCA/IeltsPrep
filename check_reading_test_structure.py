"""
Check the structure of reading tests in the database.
"""
from app import app, db
from models import PracticeTest
import json

def check_reading_test_structure():
    """Check the structure of reading tests."""
    with app.app_context():
        # Get one Academic and one General Training reading test
        academic_test = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='academic'
        ).first()
        
        general_test = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).first()
        
        # Check the structure of the academic test
        print("ACADEMIC READING TEST STRUCTURE:")
        if academic_test:
            print(f"Title: {academic_test.title}")
            print(f"ID: {academic_test.id}")
            print(f"Test Type: {academic_test.test_type}")
            print(f"IELTS Test Type: {academic_test.ielts_test_type}")
            
            # Check questions structure
            try:
                questions = json.loads(academic_test._questions)
                print(f"\nNumber of Questions: {len(questions)}")
                print("Question Structure Sample:")
                for key in questions[0].keys():
                    print(f"- {key}")
                
                # Print a sample question
                print("\nSample Question:")
                print(json.dumps(questions[0], indent=2))
            except Exception as e:
                print(f"Error parsing questions: {str(e)}")
        else:
            print("No academic reading tests found.")
        
        # Check the structure of the general test
        print("\n\nGENERAL TRAINING READING TEST STRUCTURE:")
        if general_test:
            print(f"Title: {general_test.title}")
            print(f"ID: {general_test.id}")
            print(f"Test Type: {general_test.test_type}")
            print(f"IELTS Test Type: {general_test.ielts_test_type}")
            
            # Check questions structure
            try:
                questions = json.loads(general_test._questions)
                print(f"\nNumber of Questions: {len(questions)}")
                print("Question Structure Sample:")
                for key in questions[0].keys():
                    print(f"- {key}")
                
                # Print a sample question
                print("\nSample Question:")
                print(json.dumps(questions[0], indent=2))
            except Exception as e:
                print(f"Error parsing questions: {str(e)}")
        else:
            print("No general training reading tests found.")

if __name__ == "__main__":
    check_reading_test_structure()