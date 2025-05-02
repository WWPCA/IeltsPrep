"""
Fix Reading Tests Questions
This script removes duplicate questions from reading tests.
"""
import json
import sys
from datetime import datetime

from app import app, db
from models import PracticeTest, CompletePracticeTest

def fix_duplicate_reading_questions():
    """Remove duplicate questions from reading tests."""
    with app.app_context():
        try:
            # Get reading tests
            reading_tests = PracticeTest.query.filter_by(test_type='reading').all()
            print(f"Found {len(reading_tests)} reading tests")
            
            fixed_count = 0
            
            for test in reading_tests:
                if isinstance(test.questions, dict) and 'questions' in test.questions:
                    original_count = len(test.questions['questions'])
                    
                    # Group questions by number
                    questions_by_number = {}
                    for q in test.questions['questions']:
                        q_num = q.get('number')
                        if q_num not in questions_by_number:
                            questions_by_number[q_num] = []
                        questions_by_number[q_num].append(q)
                    
                    # Keep only the first question for each number
                    unique_questions = []
                    for q_num, q_list in sorted(questions_by_number.items()):
                        unique_questions.append(q_list[0])
                    
                    if len(unique_questions) < original_count:
                        # Update test with unique questions
                        test.questions['questions'] = unique_questions
                        fixed_count += 1
                        print(f"Test {test.id}: reduced from {original_count} to {len(unique_questions)} questions")
            
            # Commit the changes
            db.session.commit()
            print(f"Fixed {fixed_count} tests with duplicate questions")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    fix_duplicate_reading_questions()