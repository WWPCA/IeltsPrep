"""
Check the content of the first General Training Reading Multiple Choice test.
"""
from app import app, db
from models import PracticeTest
import json

def check_multiple_choice_content():
    """Check the content of the first General Training Reading Multiple Choice test."""
    with app.app_context():
        # Get all Multiple Choice tests
        tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=1  # Section 1 is for Multiple Choice
        ).all()
        
        print(f"Found {len(tests)} Multiple Choice tests")
        
        if tests:
            # Get the first test
            test = tests[0]
            print(f"\nTest ID: {test.id}")
            print(f"Title: {test.title}")
            print(f"Description: {test.description}")
            print(f"\nContent:")
            print(test._content[:500] + "..." if len(test._content) > 500 else test._content)
            
            print(f"\nQuestions:")
            questions = json.loads(test._questions)
            for i, q in enumerate(questions, 1):
                print(f"{i}. {q}")
            
            print(f"\nAnswers:")
            answers = json.loads(test._answers)
            for q_num, answer in answers.items():
                print(f"Question {q_num}: {answer}")

if __name__ == "__main__":
    check_multiple_choice_content()