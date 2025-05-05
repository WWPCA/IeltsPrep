"""
Add General Training Writing Task 1 tests to the IELTS preparation app.
This script adds letter writing tasks for General Training candidates.
"""

import json
import os
from app import app, db
from models import PracticeTest

def add_general_writing_task1_tests():
    """Add General Training writing Task 1 letter tests."""
    
    # Define the test data for 16 letter writing tasks
    letter_tasks = [
        # Letter 1: College Accommodation
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: College Accommodation Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a college accommodation officer.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You live in a room in college which you share with another student. However, there are many problems with this arrangement and you find it very difficult to work.",
                    "instructions": "Write a letter to the accommodation officer at the college. In your letter:\n• describe the situation\n• explain your problems and why it is difficult to work\n• say what kind of accommodation you would prefer",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 2: Flight Delay
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Flight Delay Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to an airline about a delayed flight.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You recently traveled by airplane and your flight was delayed by over four hours, causing you significant problems.",
                    "instructions": "Write a letter to the airline. In your letter:\n• describe what happened and how it affected you\n• explain why this situation was unsatisfactory\n• say what you would like the airline to do",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 3: Store Complaint
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Store Complaint Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter of complaint to a store manager.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You bought a new laptop computer from a local store last week. When you got home, you discovered several problems with it.",
                    "instructions": "Write a letter to the store manager. In your letter:\n• provide details of your purchase\n• explain what problems you have experienced\n• state what action you would like the manager to take",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 4: Job Application
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Job Application Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a job application letter.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You saw an advertisement for a part-time job at a local hotel during the summer break.",
                    "instructions": "Write a letter to the hotel manager. In your letter:\n• state which job you are applying for and where you saw the advertisement\n• explain why you would be suitable for this job\n• say when you would be available for an interview",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 5: Library Resources
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Library Resources Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a librarian suggesting new resources.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are a regular user of your local public library but you think it needs more resources in a particular subject area.",
                    "instructions": "Write a letter to the chief librarian. In your letter:\n• explain how often you use the library and why\n• describe what subject resources you think the library needs more of\n• explain why these additional resources would be helpful",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 6: Friend's Visit
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Friend's Visit Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a friend about an upcoming visit.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "Your friend from overseas is coming to stay with you for a week. You need to change the arrangements you had made.",
                    "instructions": "Write a letter to your friend. In your letter:\n• apologize for changing the arrangements\n• explain why you need to make these changes\n• describe the new arrangements you have made",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear [name],"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 7: Lost Item
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Lost Item Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter about a lost item.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You left a valuable item on public transportation while traveling in a foreign city.",
                    "instructions": "Write a letter to the lost property office. In your letter:\n• describe the item you lost and where you left it\n• explain why this item is important to you\n• say what you would like them to do if they find it",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 8: Noisy Neighbor
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Noisy Neighbor Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to a neighbor about noise.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are having problems with noise from your neighbor's apartment, which is affecting your sleep and work.",
                    "instructions": "Write a letter to your neighbor. In your letter:\n• describe the noise problem and when it occurs\n• explain how it is affecting you\n• suggest what you would like your neighbor to do about it",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Neighbor,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 9: Community Event
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Community Event Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to organize a community event.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You would like to organize a community event in your local area and need permission to use a public space.",
                    "instructions": "Write a letter to the local council. In your letter:\n• describe the event you want to organize\n• explain why this event would be beneficial for the community\n• ask for permission and any specific arrangements you need",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 10: Course Inquiry
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Course Inquiry Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to inquire about a course.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are interested in taking a short course in photography at a local education center.",
                    "instructions": "Write a letter to the education center. In your letter:\n• explain what kind of photography you are interested in\n• ask about the details of the course (length, cost, etc.)\n• inquire about what equipment you would need to bring",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 11: Holiday Accommodation
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Holiday Accommodation Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter to inquire about holiday accommodation.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are planning a holiday and would like to rent a vacation property you saw advertised online.",
                    "instructions": "Write a letter to the property owner. In your letter:\n• say when you would like to rent the property and for how long\n• ask for more information about specific features of the accommodation\n• inquire about activities and attractions in the area",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 12: Service Feedback
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Service Feedback Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter providing feedback on a service.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You recently used a service (e.g., restaurant, hotel, transportation) and were very impressed with the quality.",
                    "instructions": "Write a letter to the manager. In your letter:\n• describe when you used the service\n• explain what you particularly liked about the service\n• recommend ways the service could be improved further",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 13: Job Recommendation
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Job Recommendation Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter recommending someone for a job.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "A friend has asked you to write a letter recommending them for a job at your workplace.",
                    "instructions": "Write a letter to your manager. In your letter:\n• explain who your friend is and how you know them\n• describe their relevant skills and qualities\n• explain why you think they would be suitable for the job",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear [Manager's Name],"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 14: Health Club Membership
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Health Club Membership Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter about a health club membership.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You have recently joined a health club, but you are dissatisfied with several aspects of the facilities and service.",
                    "instructions": "Write a letter to the manager of the health club. In your letter:\n• describe your membership details\n• explain what problems you have experienced\n• suggest what improvements you would like to see",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear Sir or Madam,"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 15: Housing Repair
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Housing Repair Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter about necessary repairs to rented accommodation.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are renting an apartment and have several maintenance issues that need to be fixed urgently.",
                    "instructions": "Write a letter to your landlord. In your letter:\n• describe the problems in detail\n• explain how these issues are affecting your daily life\n• request specific repairs and when you would like them completed",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear [Landlord's Name],"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        },
        
        # Letter 16: Project Deadline Extension
        {
            "test_type": "writing",
            "ielts_test_type": "general",
            "section": 1,  # Task 1
            "title": "General Training Writing Task 1: Project Deadline Extension Letter",
            "description": "IELTS General Training Writing Task 1 practice writing a letter requesting a project deadline extension.",
            "questions": [
                {
                    "task": "Task 1",
                    "description": "You are working on an important project and will not be able to meet the agreed deadline due to unexpected circumstances.",
                    "instructions": "Write a letter to your supervisor. In your letter:\n• explain what project you are working on\n• describe the unexpected circumstances that have arisen\n• request an extension and propose a new deadline",
                    "guidance": "You do NOT need to write any addresses.\nBegin your letter as follows:\nDear [Supervisor's Name],"
                }
            ],
            "answers": [
                "This is a sample model answer structure. Actual assessment will be done by AI."
            ]
        }
    ]
    
    # Add each letter test to the database
    with app.app_context():
        for i, letter_test in enumerate(letter_tasks, 1):
            # Check if this test already exists
            existing_test = PracticeTest.query.filter_by(
                test_type=letter_test["test_type"],
                ielts_test_type=letter_test["ielts_test_type"],
                section=letter_test["section"],
                title=letter_test["title"]
            ).first()
            
            if existing_test:
                print(f"Test {i} already exists: {letter_test['title']}")
                continue
            
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
        
        db.session.commit()
        print("All General Training Writing Task 1 letter tests added successfully!")

if __name__ == "__main__":
    add_general_writing_task1_tests()