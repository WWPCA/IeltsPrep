"""
Create placeholder Multiple Choice tests for General Training Reading.
This script adds simple placeholder Multiple Choice tests to the database.
"""
import json
from app import app, db
from models import PracticeTest

def create_placeholder_multiple_choice():
    """Create placeholder Multiple Choice tests for General Training Reading."""
    
    # Create placeholder tests
    with app.app_context():
        # Create 4 placeholder tests
        for i in range(1, 5):
            title = f"Multiple Choice Reading {i}"
            passage = f"""
Multiple Choice Reading Test {i}

This is a placeholder text for the General Training Reading Multiple Choice test.
The actual test content will include a passage with multiple choice questions.

Multiple choice questions typically require you to select the best answer from several options.
These could be factual questions, inference questions, or questions about the meaning of words or phrases.
            """
            
            questions = [
                f"Question about the main idea in Multiple Choice Test {i}",
                f"Question about a specific detail in Multiple Choice Test {i}",
                f"Question about the author's purpose in Multiple Choice Test {i}",
                f"Question about the meaning of a specific term in Multiple Choice Test {i}",
                f"Question about an inference in Multiple Choice Test {i}",
                f"Question about the organization of Multiple Choice Test {i}"
            ]
            
            # Default answers for the placeholder
            answers = {
                "1": "A",
                "2": "B",
                "3": "C",
                "4": "B",
                "5": "A",
                "6": "C"
            }
            
            test = PracticeTest(
                title=f"General Training Reading: Multiple Choice {i}",
                description=f"Part 1: {title}. Choose the best answer from options A-D.",
                test_type="reading",
                ielts_test_type="general",
                section=1,  # Section 1 is for Multiple Choice
                _content=passage,
                _questions=json.dumps([f"Question {j+1}: {q}" for j, q in enumerate(questions)]),
                _answers=json.dumps(answers)
            )
            db.session.add(test)
            print(f"Added placeholder Multiple Choice test {i}")
        
        db.session.commit()
        print("Successfully added placeholder Multiple Choice tests.")

if __name__ == "__main__":
    create_placeholder_multiple_choice()