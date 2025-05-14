"""
Create a structure for General Training Reading tests with 7 question types.
"""
from app import app, db
from models import PracticeTest, CompletePracticeTest
import json

def create_general_reading_structure():
    """Create a structure for General Training Reading tests with specified question types."""
    
    # Define the 7 question types
    question_types = [
        "multiple_choice",
        "true_false_not_given",
        "matching_information",
        "matching_features",
        "summary_completion",
        "note_completion",
        "sentence_completion"
    ]
    
    # Define a template for each question type
    question_templates = {
        "multiple_choice": {
            "type": "multiple_choice",
            "section_title": "Multiple Choice",
            "description": "Choose the correct option from A, B, C, or D.",
            "passage": "", # Will be filled with the actual passage text
            "questions": [] # Will contain actual questions with options
        },
        "true_false_not_given": {
            "type": "true_false_not_given",
            "section_title": "True / False / Not Given",
            "description": "Decide if the statements are True, False, or Not Given based on the passage.",
            "passage": "", # Will be filled with the actual passage text
            "questions": [] # Will contain statements to evaluate
        },
        "matching_information": {
            "type": "matching_information",
            "section_title": "Matching Information",
            "description": "Match each statement with the correct paragraph (A-G) from the passage.",
            "passage": "", # Will be filled with actual passage with labeled paragraphs
            "paragraphs": [], # Will contain paragraphs labeled A-G
            "questions": [] # Will contain statements to match
        },
        "matching_features": {
            "type": "matching_features",
            "section_title": "Matching Features",
            "description": "Match each description with the correct item from the list.",
            "passage": "", # Will be filled with the actual passage text
            "features": [], # Will contain features to match (e.g., people, places)
            "questions": [] # Will contain descriptions to match
        },
        "summary_completion": {
            "type": "summary_completion",
            "section_title": "Summary Completion",
            "description": "Complete the summary using words from the passage.",
            "passage": "", # Will be filled with the actual passage text
            "summary": "", # Will contain summary with gaps to fill
            "word_list": [], # Optional: may contain a list of words to choose from
            "questions": [] # Will contain gaps to fill
        },
        "note_completion": {
            "type": "note_completion",
            "section_title": "Note Completion",
            "description": "Complete the notes using words from the passage.",
            "passage": "", # Will be filled with the actual passage text
            "notes": "", # Will contain notes with gaps to fill
            "word_limit": 0, # Maximum number of words for each answer
            "questions": [] # Will contain gaps to fill
        },
        "sentence_completion": {
            "type": "sentence_completion",
            "section_title": "Sentence Completion",
            "description": "Complete each sentence using information from the passage.",
            "passage": "", # Will be filled with the actual passage text
            "questions": [] # Will contain sentences with gaps to fill
        }
    }
    
    with app.app_context():
        print("Creating structure for General Training Reading tests...")
        
        # First, check if a complete test exists for General Training
        complete_test = CompletePracticeTest.query.filter_by(
            ielts_test_type="general",
            title="General Training Complete Test 1"
        ).first()
        
        if not complete_test:
            # Create a complete test if it doesn't exist
            complete_test = CompletePracticeTest(
                ielts_test_type="general",
                test_number=1,
                title="General Training Complete Test 1",
                description="A complete General Training IELTS test with all sections.",
                is_free=False,
                subscription_level="premium"
            )
            db.session.add(complete_test)
            db.session.flush()  # Get the ID without committing
            print(f"Created new complete test with ID: {complete_test.id}")
        else:
            print(f"Using existing complete test with ID: {complete_test.id}")
        
        # Create a placeholder test for each question type
        for i, q_type in enumerate(question_types):
            # Create the practice test
            section_num = i + 1
            title = f"General Training Reading: {question_templates[q_type]['section_title']}"
            
            practice_test = PracticeTest(
                complete_test_id=complete_test.id,
                test_type="reading",
                ielts_test_type="general",
                section=section_num,
                title=title,
                description=question_templates[q_type]['description'],
                _questions=json.dumps([]),  # Empty questions array to be filled later
                _answers=json.dumps({}),    # Empty answers object to be filled later
                is_free=False,
                time_limit=60  # Standard time for reading section
            )
            
            db.session.add(practice_test)
            print(f"Created placeholder for {title}")
        
        # Commit all changes
        try:
            db.session.commit()
            print("Successfully created General Training Reading test structure.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating test structure: {str(e)}")

if __name__ == "__main__":
    create_general_reading_structure()