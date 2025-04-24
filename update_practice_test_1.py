from main import app
from models import PracticeTest, CompletePracticeTest
from flask_sqlalchemy import SQLAlchemy
import json

def update_ielts_listening_test():
    """Update the first IELTS listening test to match the official format more precisely."""
    with app.app_context():
        # Find the first listening test
        test = PracticeTest.query.filter_by(
            test_type='listening',
            section=1
        ).first()
        
        if not test:
            print("No listening test found to update.")
            return
        
        # Update with more authentic IELTS format questions
        test.title = "IELTS Academic Listening - Test 1 Section 1"
        test.description = "Listen to a conversation between a student and an accommodation officer."
        
        # Create new question format with multiple choice questions as seen in the demo
        # This follows the official IELTS format and structure
        questions = [
            {
                "number": "1-5",
                "instructions": "Questions 1-5. Choose the correct letter, A, B or C.",
                "questions": [
                    {
                        "number": "1",
                        "text": "The student is looking for accommodation for",
                        "options": {
                            "A": "one semester",
                            "B": "one academic year",
                            "C": "the summer only"
                        }
                    },
                    {
                        "number": "2",
                        "text": "The student prefers to live",
                        "options": {
                            "A": "on campus",
                            "B": "near the city center",
                            "C": "in a quiet neighborhood"
                        }
                    },
                    {
                        "number": "3",
                        "text": "The maximum monthly budget for accommodation is",
                        "options": {
                            "A": "£500",
                            "B": "£600",
                            "C": "£700"
                        }
                    },
                    {
                        "number": "4",
                        "text": "The student needs to pay a deposit of",
                        "options": {
                            "A": "one month's rent",
                            "B": "£300",
                            "C": "£500"
                        }
                    },
                    {
                        "number": "5",
                        "text": "The student says they need a room that is",
                        "options": {
                            "A": "close to public transport",
                            "B": "fully furnished",
                            "C": "in a quiet environment"
                        }
                    }
                ]
            },
            {
                "number": "6-10",
                "instructions": "Questions 6-10. Complete the form below. Write NO MORE THAN THREE WORDS AND/OR A NUMBER for each answer.",
                "form_title": "STUDENT ACCOMMODATION REQUEST FORM",
                "form_fields": [
                    {"field": "Student name", "answer_key": "6"},
                    {"field": "Student ID", "answer_key": "7"},
                    {"field": "Course start date", "answer_key": "8"},
                    {"field": "Length of stay", "answer_key": "9"},
                    {"field": "Contact email", "answer_key": "10"}
                ]
            }
        ]
        
        # Update answers to match the new questions
        answers = {
            "1": "B",
            "2": "A",
            "3": "B",
            "4": "B",
            "5": "C",
            "6": "Sarah Johnson",
            "7": "BT5940728",
            "8": "September 15th",
            "9": "two semesters",
            "10": "sjohnson@email.edu"
        }
        
        # Update the test
        test.questions = json.dumps(questions)
        test.answers = json.dumps(answers)
        
        # Commit changes
        from app import db
        db.session.commit()
        
        print(f"Successfully updated listening test: {test.title}")
        
        # Check if we have a complete practice test with this listening test
        complete_test = CompletePracticeTest.query.filter_by(
            ielts_test_type='academic',
            test_number=1
        ).first()
        
        if not complete_test:
            print("No complete practice test found. Consider creating one.")
        else:
            print(f"This test belongs to complete test: {complete_test.title}")

if __name__ == "__main__":
    update_ielts_listening_test()