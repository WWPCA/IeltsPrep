"""
Add a new academic writing test with health and wellness activities graph.
"""
import os
from app import app, db
from models import PracticeTest

def add_health_wellness_test():
    """Add a new academic writing test with health and wellness activities graph."""
    with app.app_context():
        # Check if test already exists
        test_title = 'Academic Writing Task 1: Health and Wellness Activities Bar Chart'
        existing_test = PracticeTest.query.filter_by(
            test_type='writing',
            title=test_title
        ).first()
        
        action = "Creating new" if not existing_test else "Updating existing"
        print(f"{action} 'Health and Wellness Activities' writing test...")
        
        # Define the test data
        test_data = {
            "test_type": "writing",
            "ielts_test_type": "academic",
            "section": 1,  # Task 1
            "title": test_title,
            "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing health and wellness activities participation in 2020 and 2030.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "The chart below shows the number of adults participating in different health and wellness activities in one area, in 2020 and 2030.",
                    "instructions": "Summarise the key trends in adult participation in these health and wellness activities over the 10-year period and provide relevant comparisons between the two years.",
                    "image_url": "/static/images/writing_graphs/health_wellness_activities_2020_2030.png"
                }
            ],
            "answers": [
                """The bar chart illustrates the changes in adult participation across five health and wellness activities between 2020 and 2030.

Overall, meditation sessions and tai chi classes experienced substantial growth in participation, while fitness bootcamps saw a considerable decline. Both nutrition workshops and spa retreats showed modest increases over the decade.

In 2020, fitness bootcamps were the most popular activity with approximately 35,000 participants, but this number decreased significantly to around 30,000 by 2030. Conversely, meditation sessions grew from about 27,000 to 33,000 participants, making it the most popular activity by 2030.

Tai chi classes demonstrated the most dramatic increase, more than doubling from roughly 12,000 participants in 2020 to 25,000 in 2030. Nutrition workshops remained relatively stable at around 20,000 participants in both years, while spa retreats showed a moderate increase from 15,000 to 18,000 participants over the ten-year period."""
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
            print("Health and Wellness Activities writing test added/updated successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding writing test: {str(e)}")

if __name__ == "__main__":
    add_health_wellness_test()