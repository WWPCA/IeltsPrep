"""
Check the content of General Training Reading tests.
"""
from app import app, db
from models import PracticeTest
import json

def check_general_reading_tests():
    """Check the content of General Training Reading tests."""
    with app.app_context():
        # Get all General Training reading tests
        tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).all()
        
        print(f"Found {len(tests)} General Training Reading tests")
        
        # Check the first test in detail
        if tests:
            test = tests[0]
            print(f"\nTest: {test.title} (ID: {test.id})")
            print(f"Test Type: {test.test_type}")
            print(f"IELTS Test Type: {test.ielts_test_type}")
            print(f"Section: {test.section}")
            print(f"Time Limit: {test.time_limit} minutes")
            
            # Check questions and answers
            try:
                raw_questions = test._questions
                raw_answers = test._answers
                
                print("\nRaw Questions Format:")
                print(raw_questions[:500] + "..." if len(raw_questions) > 500 else raw_questions)
                
                print("\nRaw Answers Format:")
                print(raw_answers[:500] + "..." if len(raw_answers) > 500 else raw_answers)
                
                questions = json.loads(test._questions)
                print(f"\nNumber of Questions: {len(questions)}")
                
                if questions:
                    print("\nQuestion Keys:")
                    for key in questions[0].keys():
                        print(f"- {key}")
                
                answers = json.loads(test._answers)
                print(f"\nNumber of Answers: {len(answers)}")
                
                if answers:
                    print("\nSample Answer Format:")
                    print(json.dumps(answers[0], indent=2))
            except Exception as e:
                print(f"Error parsing questions/answers: {str(e)}")
        else:
            print("No General Training Reading tests found.")

if __name__ == "__main__":
    check_general_reading_tests()