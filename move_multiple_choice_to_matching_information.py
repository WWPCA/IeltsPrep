"""
Move Multiple Choice questions to Matching Information section.
This script updates the General Training Reading tests from section 1 to section 3.
"""
from app import app, db
from models import PracticeTest

def move_multiple_choice_to_matching_information():
    """
    Move questions from Multiple Choice (section 1) to Matching Information (section 3).
    """
    with app.app_context():
        # Find all Multiple Choice tests (section 1)
        multiple_choice_tests = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=1
        ).all()
        
        # Update their section to Matching Information (section 3)
        for test in multiple_choice_tests:
            # Update the title and description to reflect the new question type
            test.title = test.title.replace("Multiple Choice", "Matching Information")
            test.description = test.description.replace("multiple choice", "matching information")
            # Update the section
            test.section = 3
            print(f"Updated test: {test.title}")
        
        # Commit changes
        db.session.commit()
        print(f"Successfully moved {len(multiple_choice_tests)} tests from Multiple Choice to Matching Information.")

if __name__ == "__main__":
    move_multiple_choice_to_matching_information()