"""
Check the structure of speaking tests in the database.
"""
from main import app
from models import PracticeTest
import json

def check_speaking_test_structure():
    """Check the structure of speaking tests in the database."""
    with app.app_context():
        # Get a sample speaking test
        speaking_test = PracticeTest.query.filter_by(test_type='speaking').first()
        
        if speaking_test:
            print(f"Sample Speaking Test ID: {speaking_test.id}")
            print(f"Title: {speaking_test.title}")
            print(f"Test Type: {speaking_test.test_type}")
            print(f"IELTS Test Type: {speaking_test.ielts_test_type}")
            print(f"Section: {speaking_test.section}")
            
            print("\nQuestions Structure:")
            try:
                print(speaking_test._questions)
                questions = json.loads(speaking_test._questions)
                print("\nParsed Questions Structure:")
                print(json.dumps(questions, indent=2))
            except Exception as e:
                print(f"Error parsing questions: {str(e)}")
            
            print("\nAnswers Structure:")
            try:
                print(speaking_test._answers)
                answers = json.loads(speaking_test._answers)
                print("\nParsed Answers Structure:")
                print(json.dumps(answers, indent=2))
            except Exception as e:
                print(f"Error parsing answers: {str(e)}")

if __name__ == "__main__":
    check_speaking_test_structure()
