"""
Add a new academic writing test with outdoor adventure activities graph.
"""
import os
from app import app, db
from models import PracticeTest

def add_outdoor_adventure_test():
    """Add a new academic writing test with outdoor adventure activities graph."""
    with app.app_context():
        # Check if test already exists
        test_title = 'Academic Writing Task 1: Outdoor Adventure Activities Bar Chart'
        existing_test = PracticeTest.query.filter_by(
            test_type='writing',
            title=test_title
        ).first()
        
        action = "Creating new" if not existing_test else "Updating existing"
        print(f"{action} 'Outdoor Adventure Activities' writing test...")
        
        # Define the test data
        test_data = {
            "test_type": "writing",
            "ielts_test_type": "academic",
            "section": 1,  # Task 1
            "title": test_title,
            "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing outdoor adventure activities participation in 2021 and 2031.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "The chart below shows the number of adults participating in different outdoor adventure activities in one area, in 2021 and 2031.",
                    "instructions": "Summarise the key trends in adult participation in these outdoor adventure activities over the 10-year period and provide relevant comparisons between the two years.",
                    "image_url": "/static/images/writing_graphs/outdoor_adventure_activities_2021_2031.png"
                }
            ],
            "answers": [
                """The graph compares adult participation in five outdoor adventure activities in an area over a ten-year period from 2021 to 2031.

Overall, rock climbing and mountain biking saw substantial increases in participation over the decade, while kayaking experienced a notable decline. Zip lining remained relatively stable, and paragliding showed modest growth.

Rock climbing demonstrated the most significant growth, increasing from 25,000 participants in 2021 to 35,000 by 2031, representing a 40% rise. Similarly, mountain biking nearly doubled from 15,000 to 28,000 participants. In contrast, kayaking decreased considerably from 30,000 to 25,000 participants during this period.

Zip lining remained essentially unchanged with approximately 20,000 participants in both years. Meanwhile, paragliding showed a moderate increase from 10,000 to 14,000 participants. By 2031, rock climbing had become the most popular activity, whereas in 2021, kayaking had held that position."""
            ],
            "is_free": False,
            "time_limit": 20  # 20 minutes for Task 1
        }
        
        # Add or update the test in the database
        if existing_test:
            # Update existing test
            existing_test.ielts_test_type = test_data["ielts_test_type"]
            existing_test.section = test_data["section"]
            existing_test.description = test_data["description"]
            existing_test.questions = test_data["questions"]
            existing_test.answers = test_data["answers"]
            existing_test.is_free = test_data["is_free"]
            existing_test.time_limit = test_data["time_limit"]
        else:
            # Create new test
            new_test = PracticeTest(
                test_type=test_data["test_type"],
                ielts_test_type=test_data["ielts_test_type"],
                section=test_data["section"],
                title=test_data["title"],
                description=test_data["description"],
                questions=test_data["questions"],
                answers=test_data["answers"],
                is_free=test_data["is_free"],
                time_limit=test_data["time_limit"]
            )
            db.session.add(new_test)
        
        # Save to database
        try:
            db.session.commit()
            print("Outdoor Adventure Activities writing test added/updated successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding writing test: {str(e)}")

if __name__ == "__main__":
    add_outdoor_adventure_test()