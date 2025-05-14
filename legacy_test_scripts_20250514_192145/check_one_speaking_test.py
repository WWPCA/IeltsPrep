"""
Check one speaking test from the database.
"""
from app import app
from models import PracticeTest
import json

def check_one_speaking_test():
    """Check a single speaking test to see its structure and source."""
    with app.app_context():
        # Get a sample speaking test
        test = PracticeTest.query.filter_by(
            test_type='speaking', 
            ielts_test_type='academic'
        ).first()
        
        if not test:
            print("No speaking tests found in the database.")
            return
            
        print(f"Test: {test.title} (ID: {test.id})")
        print(f"Test Type: {test.test_type}")
        print(f"IELTS Test Type: {test.ielts_test_type}")
        
        # Check for questions
        try:
            questions = json.loads(test._questions)
            print(f"\nNumber of Questions: {len(questions)}")
            for i, q in enumerate(questions):
                print(f"\nQuestion {i+1}:")
                print(f"Task: {q.get('task', 'N/A')}")
                print(f"Description: {q.get('description', 'N/A')}")
                if 'instructions' in q:
                    print(f"Instructions: {q.get('instructions', 'N/A')}")
                if 'topics' in q:
                    print(f"Topics: {', '.join(q.get('topics', []))}")
        except Exception as e:
            print(f"Error parsing questions: {str(e)}")

if __name__ == "__main__":
    check_one_speaking_test()