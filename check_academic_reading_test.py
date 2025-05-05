"""
Check the content of Academic Reading tests.
"""
from app import app, db
from models import PracticeTest
import json

def check_academic_reading_tests():
    """Check the content of Academic Reading tests."""
    with app.app_context():
        # Get all Academic reading tests
        tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='academic'
        ).all()
        
        print(f"Found {len(tests)} Academic Reading tests")
        
        # Try to find a test with questions
        test_with_questions = None
        for test in tests:
            try:
                questions = json.loads(test._questions)
                if questions and len(questions) > 0:
                    test_with_questions = test
                    break
            except:
                continue
        
        if test_with_questions:
            test = test_with_questions
            print(f"\nTest with questions: {test.title} (ID: {test.id})")
            print(f"Test Type: {test.test_type}")
            print(f"IELTS Test Type: {test.ielts_test_type}")
            print(f"Section: {test.section}")
            print(f"Time Limit: {test.time_limit} minutes")
            
            # Check questions and answers
            try:
                questions = json.loads(test._questions)
                print(f"\nNumber of Questions: {len(questions)}")
                
                if questions:
                    print("\nQuestion Structure:")
                    print(json.dumps(questions[0], indent=2))
                
                answers = json.loads(test._answers)
                print(f"\nNumber of Answers: {len(answers)}")
                
                if answers:
                    print("\nAnswer Structure:")
                    print(json.dumps(answers[0], indent=2))
            except Exception as e:
                print(f"Error parsing questions/answers: {str(e)}")
        else:
            print("No Academic Reading test with questions found.")

if __name__ == "__main__":
    check_academic_reading_tests()