"""
Check for True/False/Not Given questions in existing General Reading tests.
"""
from app import app, db
from models import PracticeTest
import json

def check_question_types():
    """Check for specific question types in General Reading tests."""
    with app.app_context():
        # Get all General Training reading tests
        tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).all()
        
        print(f"Found {len(tests)} General Training Reading tests")
        
        # Check each test for True/False/Not Given questions
        tfng_tests = []
        for test in tests:
            try:
                questions = json.loads(test._questions)
                if not questions:
                    continue
                
                # Look for any indicators of True/False/Not Given questions
                for q in questions:
                    if 'type' in q and q['type'] in ['true_false_not_given', 'tfng', 'true/false/not given']:
                        tfng_tests.append(test)
                        break
                    
                    # Check options for True/False/Not Given
                    if 'options' in q:
                        options = q['options']
                        if isinstance(options, list) and set(['True', 'False', 'Not Given']).issubset(set(options)):
                            tfng_tests.append(test)
                            break
                            
                    # Check question text for True/False/Not Given indicators
                    q_text = q.get('text', '').lower()
                    if 'true, false or not given' in q_text or 'true/false/not given' in q_text:
                        tfng_tests.append(test)
                        break
            except Exception as e:
                print(f"Error checking test {test.id}: {str(e)}")
                continue
        
        print(f"Found {len(tfng_tests)} tests with True/False/Not Given questions")
        
        # Show details of tests with TFNG questions
        for test in tfng_tests:
            print(f"\nTest: {test.title} (ID: {test.id})")
            
            try:
                questions = json.loads(test._questions)
                for i, q in enumerate(questions):
                    if ('type' in q and q['type'] in ['true_false_not_given', 'tfng', 'true/false/not given']) or \
                       ('options' in q and isinstance(q['options'], list) and 
                        set(['True', 'False', 'Not Given']).issubset(set(q['options']))):
                        print(f"  Question {i+1}: {q.get('text', '')[:100]}...")
                        if 'options' in q:
                            print(f"    Options: {q['options']}")
                        if 'answer' in q:
                            print(f"    Answer: {q['answer']}")
            except Exception as e:
                print(f"  Error parsing questions: {str(e)}")

if __name__ == "__main__":
    check_question_types()