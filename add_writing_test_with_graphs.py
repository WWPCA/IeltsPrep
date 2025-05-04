"""
Add writing tests with graphs to the IELTS preparation app.
This script adds the academic writing Task 1 tests with their associated graph images.
"""

import json
import os
from app import app, db
from models import PracticeTest

def add_academic_writing_tests_with_graphs():
    """Add academic writing tests with bar graphs."""
    
    # Define the test data for the first test (Cultural Activities)
    test_1 = {
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
    
    # Define the test data for the second test (Outdoor Activities)
    test_2 = {
        "test_type": "writing",
        "ielts_test_type": "academic",
        "section": 1,  # Task 1
        "title": "Academic Writing Task 1: Outdoor Activities Bar Chart",
        "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing outdoor activities participation in 2012 and 2022.",
        "questions": [
            {
                "task": "Task 1",
                "description": "The chart below shows the participation of adults in various outdoor activities in 2012 and 2022.",
                "instructions": "Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
                "image_url": "/static/images/writing_graphs/outdoor_activities_2012_2022.png"
            }
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by AI."
        ],
        "is_free": True,
        "time_limit": 60  # 60 minutes
    }
    
    # Define the test data for the third test (Community Activities)
    test_3 = {
        "test_type": "writing",
        "ielts_test_type": "academic",
        "section": 1,  # Task 1
        "title": "Academic Writing Task 1: Community Activities Bar Chart",
        "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing community activities participation in 2015 and 2025.",
        "questions": [
            {
                "task": "Task 1",
                "description": "The chart below shows the number of adults participating in different community activities in one area, in 2015 and 2025.",
                "instructions": "Summarise the key trends in adult participation in these community activities over the 10-year period and provide relevant comparisons between the two years.",
                "image_url": "/static/images/writing_graphs/community_activities_2015_2025.png"
            }
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by AI."
        ],
        "is_free": True,
        "time_limit": 60  # 60 minutes
    }

    # Define the test data for the fourth test (Fitness Activities)
    test_4 = {
        "test_type": "writing",
        "ielts_test_type": "academic",
        "section": 1,  # Task 1
        "title": "Academic Writing Task 1: Fitness Activities Bar Chart",
        "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing fitness activities participation in 2018 and 2028.",
        "questions": [
            {
                "task": "Task 1",
                "description": "The chart below shows the number of adults participating in different fitness activities in one area, in 2018 and 2028.",
                "instructions": "Summarise the key trends in adult participation in these fitness activities over the 10-year period and provide relevant comparisons between the two years.",
                "image_url": "/static/images/writing_graphs/fitness_activities_2018_2028.png"
            }
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by AI."
        ],
        "is_free": True,
        "time_limit": 60  # 60 minutes
    }

    # List of tests to add
    tests = [test_1, test_2, test_3, test_4]
    
    # Add each test
    for test_data in tests:
        # Check if the test already exists
        existing_test = PracticeTest.query.filter_by(
            test_type="writing",
            ielts_test_type="academic",
            section=1,
            title=test_data["title"]
        ).first()
        
        if existing_test:
            print(f"Test '{test_data['title']}' already exists. Updating...")
            
            # Update the existing test
            existing_test.description = test_data["description"]
            existing_test.questions = test_data["questions"]
            existing_test.answers = test_data["answers"]
            existing_test.is_free = test_data["is_free"]
            existing_test.time_limit = test_data["time_limit"]
        else:
            print(f"Creating new test: '{test_data['title']}'")
            
            # Create a new test
            new_test = PracticeTest(
                test_type=test_data["test_type"],
                ielts_test_type=test_data["ielts_test_type"],
                section=test_data["section"],
                title=test_data["title"],
                description=test_data["description"],
                _questions=json.dumps(test_data["questions"]),
                _answers=json.dumps(test_data["answers"]),
                is_free=test_data["is_free"],
                time_limit=test_data["time_limit"]
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
        add_academic_writing_tests_with_graphs()