"""
Update General Training Writing Task 1 tests with official questions.
This script updates the letter writing tasks with authentic content.
"""

import json
import os
from app import app, db
from models import PracticeTest

def update_general_writing_task1_tests():
    """Update General Training writing Task 1 letter tests with official content."""
    
    # Define the official letter tasks
    letter_tasks = [
        # Letter 1: Evening Course Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Evening Course Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a course coordinator about classroom environment issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are currently enrolled in an evening course at a local community center, but you are facing several issues with the classroom environment that make it challenging to focus and learn effectively.",
                    "instructions": "Write a letter to the course coordinator at the community center. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to learn\n• suggest what kind of classroom environment you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 2: Gym Facilities Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Gym Facilities Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a gym manager about facility issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a local gym to improve your fitness, but you are experiencing several issues with the gym facilities that make it difficult to exercise comfortably.",
                    "instructions": "Write a letter to the gym manager. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to exercise\n• suggest what kind of improvements or facilities you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 3: Shared Apartment Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Shared Apartment Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a housing coordinator about living arrangement challenges.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently moved into a shared apartment provided by your employer, but you are facing several challenges with the living arrangement that make it hard to relax and focus on your work.",
                    "instructions": "Write a letter to the housing coordinator at your company. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to relax and work\n• suggest what kind of living arrangement you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 4: University Library Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: University Library Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a head librarian about library environment issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently started using the library at your university to study, but you are encountering several issues with the library environment that make it difficult to concentrate and be productive.",
                    "instructions": "Write a letter to the head librarian at the university. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to study\n• suggest what kind of library environment you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 5: Community Art Class Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Community Art Class Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to an art class organizer about class setup issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a community art class to develop your creative skills, but you are facing several issues with the class setup that make it challenging to enjoy and focus on your artwork.",
                    "instructions": "Write a letter to the art class organizer at the community center. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to focus on your artwork\n• suggest what kind of class setup you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 6: Language Course Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Language Course Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a program director about classroom arrangement issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently started attending a language course at a local institute to improve your skills, but you are facing several issues with the classroom arrangement that make it difficult to learn effectively.",
                    "instructions": "Write a letter to the institute's program director. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to learn\n• suggest what kind of classroom arrangement you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 7: Fitness Center Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Fitness Center Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a fitness center manager about class schedule and environment issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a local fitness center to attend group exercise classes, but you are encountering several issues with the class schedule and environment that make it challenging to participate regularly.",
                    "instructions": "Write a letter to the fitness center manager. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to attend the classes\n• suggest what kind of schedule or environment you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 8: Community Kitchen Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Community Kitchen Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a community kitchen coordinator about kitchen setup and schedule issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently started volunteering at a local community kitchen, but you are facing several issues with the kitchen setup and schedule that make it difficult to contribute effectively.",
                    "instructions": "Write a letter to the community kitchen coordinator. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to volunteer\n• suggest what kind of kitchen setup or schedule you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 9: Photography Workshop Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Photography Workshop Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a workshop coordinator about facilities and timing issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently enrolled in a photography workshop at a local cultural center, but you are facing several issues with the workshop facilities and timing that make it difficult to fully engage in the learning process.",
                    "instructions": "Write a letter to the workshop coordinator at the cultural center. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to engage in the workshop\n• suggest what kind of facilities or timing you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 10: Book Club Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Book Club Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a library manager about book club meeting space and schedule issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a book club at your local library, but you are encountering several issues with the meeting space and schedule that make it difficult to participate and enjoy the discussions.",
                    "instructions": "Write a letter to the library manager. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to participate in the book club\n• suggest what kind of meeting space or schedule you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 11: Meditation Group Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Meditation Group Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a wellness center manager about meditation session environment and timing issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently started attending a weekly meditation group at a local wellness center, but you are facing several issues with the session environment and timing that make it challenging to relax and focus.",
                    "instructions": "Write a letter to the wellness center manager. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to meditate\n• suggest what kind of session environment or timing you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 12: Gardening Club Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Gardening Club Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a community garden organizer about garden facilities and meeting times issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a gardening club at a local community garden, but you are facing several issues with the garden facilities and meeting times that make it difficult to participate and enjoy the activities.",
                    "instructions": "Write a letter to the community garden organizer. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to participate in the gardening club\n• suggest what kind of facilities or meeting times you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 13: Dance Class Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Dance Class Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a recreation center supervisor about studio conditions and class schedule issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently enrolled in a dance class at a local recreation center, but you are facing several issues with the studio conditions and class schedule that make it difficult to practice and improve your skills.",
                    "instructions": "Write a letter to the recreation center supervisor. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to practice\n• suggest what kind of studio conditions or schedule you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 14: Cycling Group Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Cycling Group Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a cycling group coordinator about meeting locations and ride schedules issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a local cycling group to participate in group rides, but you are facing several issues with the meeting locations and ride schedules that make it challenging to join regularly and enjoy the experience.",
                    "instructions": "Write a letter to the cycling group coordinator. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to participate\n• suggest what kind of meeting locations or schedules you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 15: Coding Bootcamp Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Coding Bootcamp Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a bootcamp organizer about training room setup and class timings issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently enrolled in a coding bootcamp offered by a local tech hub, but you are facing several issues with the training room setup and class timings that make it difficult to focus and learn effectively.",
                    "instructions": "Write a letter to the bootcamp organizer at the tech hub. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to learn\n• suggest what kind of training room setup or timings you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 16: Pottery Workshop Issues
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Pottery Workshop Issues",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a workshop coordinator about workspace conditions and session schedules issues.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a pottery workshop at a local arts center, but you are facing several issues with the workspace conditions and session schedules that make it challenging to create and enjoy your work.",
                    "instructions": "Write a letter to the workshop coordinator at the arts center. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to create your work\n• suggest what kind of workspace conditions or schedules you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        }
    ]
    
    # Update or add each letter test to the database
    with app.app_context():
        # First, find all existing General Training Writing Task 1 tests
        existing_tests = PracticeTest.query.filter_by(
            test_type="writing",
            ielts_test_type="general",
            section=1
        ).all()
        
        # Create a mapping of test titles to test objects
        test_mapping = {test.title: test for test in existing_tests}
        
        for i, letter_test in enumerate(letter_tasks, 1):
            # Check if a test with this title exists
            existing_test = test_mapping.get(letter_test["title"])
            
            if existing_test:
                # Update the existing test
                existing_test.description = letter_test["description"]
                existing_test.questions = json.dumps(letter_test["questions"])
                existing_test.answers = json.dumps(letter_test["answers"])
                print(f"Updated test {i}: {letter_test['title']}")
            else:
                # Create a new test
                new_test = PracticeTest(
                    test_type=letter_test["test_type"],
                    ielts_test_type=letter_test["ielts_test_type"],
                    section=letter_test["section"],
                    title=letter_test["title"],
                    description=letter_test["description"],
                    questions=json.dumps(letter_test["questions"]),
                    answers=json.dumps(letter_test["answers"]),
                    is_free=False  # These are premium tests
                )
                db.session.add(new_test)
                print(f"Added test {i}: {letter_test['title']}")
        
        # Delete any existing General Training Writing Task 1 tests that were not in our official list
        official_titles = [test["title"] for test in letter_tasks]
        for title, test in test_mapping.items():
            if title not in official_titles:
                db.session.delete(test)
                print(f"Deleted non-official test: {title}")
        
        db.session.commit()
        print("All General Training Writing Task 1 letter tests updated successfully!")

if __name__ == "__main__":
    update_general_writing_task1_tests()