"""
Initialize Test Repository
This script initializes the test repository with 16 unique academic and 16 unique general tests.
Content is sourced from the IELTS Reading Context File and other attached resources.
"""
import json
import sys
from datetime import datetime

from flask import Flask
from sqlalchemy import func
from app import db
from models import CompletePracticeTest, PracticeTest

def init_reading_tests():
    """
    Initialize reading tests in the database.
    
    This uses the IELTS Reading Context File to create:
    - 16 unique academic reading tests
    - 16 unique general reading tests
    """
    print("Initializing reading tests...")
    
    # Check if tests already exist
    existing_tests = CompletePracticeTest.query.filter_by(test_type='reading').count()
    if existing_tests > 0:
        print(f"Found {existing_tests} existing reading tests. Skipping initialization.")
        return
    
    # First, read the content file
    try:
        with open('attached_assets/IELTS Reading Context File.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: IELTS Reading Context File not found. Please ensure it's in the attached_assets directory.")
        return
    
    # Split content into tests
    raw_tests = content.split("Part ")
    
    # Skip the first element as it's just the header
    if raw_tests and "IELTS Reading Context File" in raw_tests[0]:
        raw_tests = raw_tests[1:]
    
    print(f"Found {len(raw_tests)} raw test sections in the file.")
    
    # Process each test
    academic_tests = []
    general_tests = []
    
    for i, test_content in enumerate(raw_tests[:32]):  # Process only the first 32 tests (16 academic + 16 general)
        # First 16 are academic, next 16 are general
        is_academic = i < 16
        test_type = 'academic' if is_academic else 'general'
        test_number = (i % 16) + 1  # 1-16 for each type
        
        # Create test title
        title = f"{'Academic' if is_academic else 'General Training'} Reading Test {test_number}"
        
        # Create test object
        test = {
            'test_number': test_number,
            'ielts_test_type': test_type,
            'title': title,
            'content': test_content.strip(),
            'is_free': test_number == 1,  # First test of each type is free
        }
        
        if is_academic:
            academic_tests.append(test)
        else:
            general_tests.append(test)
    
    print(f"Processed {len(academic_tests)} academic tests and {len(general_tests)} general tests.")
    
    # Now insert the complete tests
    for test_type, tests in [('academic', academic_tests), ('general', general_tests)]:
        for test in tests:
            # Create a complete practice test entry
            complete_test = CompletePracticeTest(
                ielts_test_type=test['ielts_test_type'],
                test_number=test['test_number'],
                title=test['title'],
                description=f"Complete IELTS {test['ielts_test_type'].title()} Test {test['test_number']}",
                is_free=test['is_free'],
                subscription_level="basic",
                creation_date=datetime.utcnow()
            )
            db.session.add(complete_test)
            db.session.flush()  # Get the ID
            
            # Create a reading practice test entry linked to the complete test
            questions = []
            answers = []
            
            # Extract questions/answers from the content
            lines = test['content'].split('\n')
            reading_passage = []
            questions_section = []
            
            question_mode = False
            for line in lines:
                if "** Questions for Passage" in line or "Questions for Reading Passage" in line:
                    question_mode = True
                    continue
                    
                if question_mode:
                    questions_section.append(line)
                else:
                    reading_passage.append(line)
            
            reading_text = '\n'.join(reading_passage)
            
            # Parse questions and answers
            current_question = None
            for line in questions_section:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this is a question (starts with a number)
                if line[0].isdigit() and '.' in line[:5]:
                    # New question
                    question_number = line.split('.')[0].strip()
                    question_text = line.split('.', 1)[1].strip()
                    
                    current_question = {
                        'number': int(question_number),
                        'text': question_text,
                        'options': []
                    }
                    questions.append(current_question)
                elif current_question and line:
                    # This could be an option or continuation of question
                    if line[0] in ['A', 'B', 'C', 'D'] and ') ' in line[:5]:
                        # This is an option
                        option_letter = line[0]
                        option_text = line.split(')', 1)[1].strip()
                        
                        current_question['options'].append({
                            'letter': option_letter,
                            'text': option_text
                        })
                    else:
                        # Continuation of question text
                        current_question['text'] += ' ' + line
            
            # For this example, just create mock answers (in production, these would be real)
            for q in questions:
                if q['options']:
                    answers.append({
                        'number': q['number'],
                        'answer': 'A',  # Just a placeholder - in reality, you'd have the actual answers
                        'explanation': 'Explanation would go here.'
                    })
                else:
                    # For open-ended questions
                    answers.append({
                        'number': q['number'],
                        'answer': 'Sample answer would go here.',
                        'explanation': 'Explanation would go here.'
                    })
            
            # Create the practice test
            practice_test = PracticeTest(
                complete_test_id=complete_test.id,
                test_type='reading',
                ielts_test_type=test['ielts_test_type'],
                section=1,
                title=f"{'Academic' if test['ielts_test_type'] == 'academic' else 'General Training'} Reading Test {test['test_number']}",
                description=f"Reading test with comprehension passages and various question types.",
                _questions=json.dumps({
                    'passage': reading_text,
                    'questions': questions
                }),
                _answers=json.dumps(answers),
                is_free=test['is_free'],
                time_limit=60  # 60 minutes for reading
            )
            db.session.add(practice_test)
    
    # Commit all changes
    db.session.commit()
    print("Reading tests initialized successfully!")

def init_test_repository():
    """Initialize the complete test repository with 16 unique academic and 16 unique general tests."""
    print("Initializing test repository...")
    
    # Initialize reading tests
    init_reading_tests()
    
    # TODO: Initialize listening tests when data is available
    # TODO: Initialize writing tests when data is available
    # TODO: Initialize speaking tests when data is available
    
    print("Test repository initialization complete!")

if __name__ == '__main__':
    # Create a minimal Flask app for database access
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/ielts_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        init_test_repository()