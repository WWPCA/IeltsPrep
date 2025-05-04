"""
Add writing tests with graphs to the IELTS preparation app.
This script adds the academic writing Task 1 tests with their associated graph images.
"""

import json
import os
from app import app, db
from models import PracticeTest

def add_academic_writing_test_with_graph():
    """Add an academic writing test with a bar graph."""
    
    # Define the test data
    academic_writing_test = {
        "test_type": "writing",
        "ielts_test_type": "academic",
        "section": 1,  # Task 1
        "title": "Academic Writing Task 1: Cultural Activities Bar Chart",
        "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing cultural activities participation in 2010 and 2020.",
        "questions": [
            {
                "task": "Task 1",
                "description": "The chart below shows the number of adults participating in different cultural activities in one area, in 2010 and 2020.",
                "instructions": "Summarise the key trends in adult participation in these cultural activities over the 10-year period and provide relevant comparisons between the two years.",
                "image_url": "/static/images/writing_graphs/cultural_activities_2010_2020.png"
            }
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by AI."
        ],
        "is_free": True,
        "time_limit": 60  # 60 minutes
    }
    
    # Check if the test already exists
    existing_test = PracticeTest.query.filter_by(
        test_type="writing",
        ielts_test_type="academic",
        section=1,
        title=academic_writing_test["title"]
    ).first()
    
    if existing_test:
        print(f"Test '{academic_writing_test['title']}' already exists. Updating...")
        
        # Update the existing test
        existing_test.description = academic_writing_test["description"]
        existing_test.questions = academic_writing_test["questions"]
        existing_test.answers = academic_writing_test["answers"]
        existing_test.is_free = academic_writing_test["is_free"]
        existing_test.time_limit = academic_writing_test["time_limit"]
    else:
        print(f"Creating new test: '{academic_writing_test['title']}'")
        
        # Create a new test
        new_test = PracticeTest(
            test_type=academic_writing_test["test_type"],
            ielts_test_type=academic_writing_test["ielts_test_type"],
            section=academic_writing_test["section"],
            title=academic_writing_test["title"],
            description=academic_writing_test["description"],
            _questions=json.dumps(academic_writing_test["questions"]),
            _answers=json.dumps(academic_writing_test["answers"]),
            is_free=academic_writing_test["is_free"],
            time_limit=academic_writing_test["time_limit"]
        )
        db.session.add(new_test)
    
    # Commit the changes
    try:
        db.session.commit()
        print("Writing test with graph added/updated successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding writing test: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        add_academic_writing_test_with_graph()