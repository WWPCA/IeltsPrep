"""
Debug and Fix Reading Questions
This script debugs and fixes the duplicate questions issue in reading tests.
"""
import json
import sys
from datetime import datetime

from app import app, db
from models import PracticeTest

def debug_and_fix_questions():
    """Debug and fix reading questions."""
    with app.app_context():
        try:
            test_id = 211  # Use test_id 211 as our example
            
            # Get the test
            test = PracticeTest.query.filter_by(id=test_id).first()
            if not test or test.test_type != 'reading':
                print(f"Test {test_id} not found or is not a reading test")
                return
            
            print(f"Original questions data type: {type(test.questions)}")
            print(f"Original questions count: {len(test.questions.get('questions', []))}")
            
            # Display duplicate counts
            questions_by_number = {}
            for q in test.questions.get('questions', []):
                q_num = q.get('number')
                if q_num not in questions_by_number:
                    questions_by_number[q_num] = []
                questions_by_number[q_num].append(q)
            
            print(f"Question numbers with duplicates:")
            for q_num, qs in sorted(questions_by_number.items()):
                if len(qs) > 1:
                    print(f"  Question {q_num}: {len(qs)} duplicates")
            
            # Create a completely new questions object
            passage_text = test.questions.get('passage', '')
            
            # Extract unique questions
            unique_questions = []
            for q_num, qs in sorted(questions_by_number.items()):
                unique_questions.append(qs[0])
            
            # Create completely new questions object
            new_questions = {
                'passage': passage_text,
                'questions': unique_questions
            }
            
            print(f"New questions count: {len(new_questions['questions'])}")
            print(f"Unique question numbers: {len(questions_by_number)}")
            
            # Check question types
            question_types = {}
            for q in new_questions['questions']:
                q_type = q.get('type', 'unknown')
                if q_type not in question_types:
                    question_types[q_type] = 0
                question_types[q_type] += 1
            print(f"Question types: {question_types}")
            
            # Update test.questions with the new object
            test.questions = new_questions
            db.session.commit()
            
            # Verify after commit
            test = PracticeTest.query.filter_by(id=test_id).first()
            print(f"After commit: {len(test.questions.get('questions', []))} questions")
            
            # Check if it worked for other tests
            for test_id in [19, 67, 163, 211, 259]:
                test = PracticeTest.query.filter_by(id=test_id).first()
                if test and isinstance(test.questions, dict) and 'questions' in test.questions:
                    # Group questions by number
                    questions_by_number = {}
                    for q in test.questions.get('questions', []):
                        q_num = q.get('number')
                        if q_num not in questions_by_number:
                            questions_by_number[q_num] = []
                        questions_by_number[q_num].append(q)
                    
                    # Create unique questions list
                    unique_questions = []
                    for q_num, qs in sorted(questions_by_number.items()):
                        unique_questions.append(qs[0])
                    
                    # Create new questions object
                    test.questions = {
                        'passage': test.questions.get('passage', ''),
                        'questions': unique_questions
                    }
                    
                    print(f"Fixed test {test_id}: now has {len(unique_questions)} questions")
            
            # Commit all changes
            db.session.commit()
            print("All changes committed")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    debug_and_fix_questions()