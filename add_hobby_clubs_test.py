"""
Add a new academic writing test with hobby clubs graph.
This is the 16th and final Academic Writing Task 1 test.
"""
import os
from app import app, db
from models import PracticeTest

def add_hobby_clubs_test():
    """Add a new academic writing test with hobby clubs graph."""
    with app.app_context():
        # Check if test already exists
        test_title = 'Academic Writing Task 1: Hobby Clubs Bar Chart'
        existing_test = PracticeTest.query.filter_by(
            test_type='writing',
            title=test_title
        ).first()
        
        action = "Creating new" if not existing_test else "Updating existing"
        print(f"{action} 'Hobby Clubs' writing test...")
        
        # Define the test data
        test_data = {
            "test_type": "writing",
            "ielts_test_type": "academic",
            "section": 1,  # Task 1
            "title": test_title,
            "description": "IELTS Academic Writing Task 1 practice with bar chart data comparing hobby clubs participation in 2019 and 2029.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "The chart below shows the number of adults participating in different hobby clubs in one area, in 2019 and 2029.",
                    "instructions": "Summarise the key trends in adult participation in these hobby clubs over the 10-year period and provide relevant comparisons between the two years.",
                    "image_url": "/static/images/writing_graphs/hobby_clubs_2019_2029.png"
                }
            ],
            "answers": [
                """The bar chart illustrates the changes in adult participation in five different hobby clubs between 2019 and 2029.

Overall, board game nights and model train building showed the most significant increases in participation over the decade, while stamp collecting experienced a notable decline. Astronomy groups saw moderate growth, and calligraphy classes remained relatively stable.

Board game nights demonstrated the most dramatic increase, more than doubling from approximately 15,000 participants in 2019 to 30,000 in 2029, making it the most popular hobby by the end of the decade. Similarly, model train building grew substantially from 20,000 to about 25,000 participants.

In contrast, stamp collecting declined from around 18,000 participants in 2019 to 14,000 by 2029. Calligraphy classes remained virtually unchanged with approximately 22,000 participants throughout the period. Astronomy groups, which had the lowest participation in 2019 with 10,000 members, increased modestly to about 13,000 participants by 2029."""
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
            print("Hobby Clubs writing test added/updated successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding writing test: {str(e)}")

if __name__ == "__main__":
    add_hobby_clubs_test()