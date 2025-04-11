"""
Initialize complete practice test data for the IELTS preparation app.
This script creates sample complete tests with all sections.
"""

import json
from datetime import datetime
from app import app, db
from models import CompletePracticeTest, PracticeTest

def init_complete_test_data():
    """Initialize the complete practice test data in the database."""
    
    print("Initializing complete practice test data...")
    
    # Create a complete academic test
    academic_test = CompletePracticeTest(
        ielts_test_type='academic',
        test_number=1,
        title='Complete Academic IELTS Practice Test 1',
        description='A full IELTS Academic test with all four sections: Listening, Reading, Writing, and Speaking.',
        is_free=True,
        subscription_level='basic'
    )
    
    db.session.add(academic_test)
    db.session.flush()  # Get the ID without committing
    
    # Create the listening section
    listening_test = PracticeTest(
        complete_test_id=academic_test.id,
        test_type='listening',
        ielts_test_type='academic',
        section=1,
        title='Academic Listening Test 1',
        description='IELTS Academic Listening Test with 40 questions in 4 sections.',
        _questions=json.dumps({
            "1": "What is the woman's name?",
            "2": "What is her student ID number?",
            "3": "What program is she enrolling in?",
            "4": "How many courses is she taking this semester?",
            "5": "What day does her first class start?",
        }),
        _answers=json.dumps({
            "1": "sarah johnson",
            "2": "j4586921",
            "3": "business administration",
            "4": "4",
            "5": "monday",
        }),
        audio_url='audio/accommodation_inquiry.mp3',
        is_free=True,
        time_limit=30  # 30 minutes
    )
    
    # Create the reading section
    reading_test = PracticeTest(
        complete_test_id=academic_test.id,
        test_type='reading',
        ielts_test_type='academic',
        section=2,
        title='Academic Reading Test 1',
        description='IELTS Academic Reading Test with 3 passages and 40 questions.',
        _questions=json.dumps({
            "1": "The title of the first passage is:",
            "2": "According to the passage, the main cause of coral reef destruction is:",
            "3": "The study was conducted over a period of:",
            "4": "The researchers concluded that coral reefs could recover if:",
            "5": "The term 'bleaching' in the passage refers to:",
        }),
        _answers=json.dumps({
            "1": "the decline of coral reefs",
            "2": "climate change",
            "3": "10 years",
            "4": "human impacts are reduced",
            "5": "loss of algae",
        }),
        is_free=True,
        time_limit=60  # 60 minutes
    )
    
    # Create the writing section
    writing_test = PracticeTest(
        complete_test_id=academic_test.id,
        test_type='writing',
        ielts_test_type='academic',
        section=3,
        title='Academic Writing Test 1',
        description='IELTS Academic Writing Test with Task 1 (chart/graph description) and Task 2 (essay).',
        _questions=json.dumps({
            "1": {
                "task": "Task 1",
                "description": "The graph below shows the percentage of people who used different types of transportation to commute to work in a European city between 1990 and 2020.",
                "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.",
                "image_url": None
            },
            "2": {
                "task": "Task 2",
                "description": "Some people believe that universities should focus on providing academic skills, while others think that universities should prepare students for their future careers. Discuss both views and give your opinion.",
                "instructions": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
                "image_url": None
            }
        }),
        _answers=json.dumps({
            "1": "model answer for task 1",
            "2": "model answer for task 2"
        }),
        is_free=True,
        time_limit=60  # 60 minutes
    )
    
    # Create the speaking section
    speaking_test = PracticeTest(
        complete_test_id=academic_test.id,
        test_type='speaking',
        ielts_test_type='academic',
        section=4,
        title='Academic Speaking Test 1',
        description='IELTS Speaking Test with three parts: Interview, Long Turn, and Discussion.',
        _questions=json.dumps({
            "1": {
                "part": 1,
                "description": "Introduction and Interview",
                "questions": [
                    "Could you tell me your full name, please?",
                    "Can I see your identification, please?",
                    "Do you work or study?",
                    "Let's talk about your hometown. What's it like?",
                    "What do you like most about living there?"
                ]
            },
            "2": {
                "part": 2,
                "description": "Long Turn",
                "questions": [
                    "Describe a skill that took you a long time to learn. You should say: what the skill is, when you learned it, why you learned it, and explain how you felt when you finally learned it."
                ]
            },
            "3": {
                "part": 3,
                "description": "Discussion",
                "questions": [
                    "How important do you think it is for people to learn new skills throughout their lives?",
                    "Do you think schools teach enough practical skills?",
                    "What kinds of skills do you think will be most important in the future?"
                ]
            }
        }),
        _answers=json.dumps({
            "1": "sample answers for part 1",
            "2": "sample answer for part 2",
            "3": "sample answers for part 3"
        }),
        is_free=True,
        time_limit=14  # 14 minutes
    )
    
    # Create a complete general training test
    general_test = CompletePracticeTest(
        ielts_test_type='general',
        test_number=1,
        title='Complete General Training IELTS Practice Test 1',
        description='A full IELTS General Training test with all four sections: Listening, Reading, Writing, and Speaking.',
        is_free=False,
        subscription_level='basic'
    )
    
    db.session.add(general_test)
    db.session.flush()  # Get the ID without committing
    
    # Create the general listening section (same as academic)
    general_listening_test = PracticeTest(
        complete_test_id=general_test.id,
        test_type='listening',
        ielts_test_type='general',
        section=1,
        title='General Training Listening Test 1',
        description='IELTS General Training Listening Test with 40 questions in 4 sections.',
        _questions=json.dumps({
            "1": "What is the woman's name?",
            "2": "What is her reference number?",
            "3": "What type of accommodation is she looking for?",
            "4": "What is her maximum budget?",
            "5": "How long does she want to stay?",
        }),
        _answers=json.dumps({
            "1": "emma wilson",
            "2": "a7429",
            "3": "apartment",
            "4": "800",
            "5": "6 months",
        }),
        audio_url='audio/accommodation_inquiry.mp3',
        is_free=False,
        time_limit=30  # 30 minutes
    )
    
    # Create the general reading section
    general_reading_test = PracticeTest(
        complete_test_id=general_test.id,
        test_type='reading',
        ielts_test_type='general',
        section=2,
        title='General Training Reading Test 1',
        description='IELTS General Training Reading Test with 3 sections and 40 questions.',
        _questions=json.dumps({
            "1": "According to the brochure, the community center opens at:",
            "2": "How many days a week is the swimming pool open?",
            "3": "What activity is available on Thursday evenings?",
            "4": "Children under what age must be accompanied by an adult?",
            "5": "The annual membership fee for adults is:",
        }),
        _answers=json.dumps({
            "1": "9am",
            "2": "7",
            "3": "yoga",
            "4": "12",
            "5": "£45",
        }),
        is_free=False,
        time_limit=60  # 60 minutes
    )
    
    # Create the general writing section
    general_writing_test = PracticeTest(
        complete_test_id=general_test.id,
        test_type='writing',
        ielts_test_type='general',
        section=3,
        title='General Training Writing Test 1',
        description='IELTS General Training Writing Test with Task 1 (letter) and Task 2 (essay).',
        _questions=json.dumps({
            "1": {
                "task": "Task 1",
                "description": "You have just moved into a new apartment and have some issues that need to be addressed. Write a letter to your landlord describing the problems and requesting repairs.",
                "instructions": "You should write at least 150 words. You do NOT need to write any addresses. Begin your letter as follows: Dear Mr./Ms. Smith,",
                "image_url": None
            },
            "2": {
                "task": "Task 2",
                "description": "Some people believe that children should be allowed to watch whatever TV programs they want without parental control. Others think parents should strictly monitor what their children watch. Discuss both views and give your opinion.",
                "instructions": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
                "image_url": None
            }
        }),
        _answers=json.dumps({
            "1": "model letter answer",
            "2": "model essay answer"
        }),
        is_free=False,
        time_limit=60  # 60 minutes
    )
    
    # Create the general speaking section (same as academic)
    general_speaking_test = PracticeTest(
        complete_test_id=general_test.id,
        test_type='speaking',
        ielts_test_type='general',
        section=4,
        title='General Training Speaking Test 1',
        description='IELTS Speaking Test with three parts: Introduction, Long Turn, and Discussion.',
        _questions=json.dumps({
            "1": {
                "part": 1,
                "description": "Introduction and Interview",
                "questions": [
                    "Could you tell me your full name, please?",
                    "Can I see your identification, please?",
                    "Do you work or study?",
                    "Let's talk about your hometown. What's it like?",
                    "What do you like most about living there?"
                ]
            },
            "2": {
                "part": 2,
                "description": "Long Turn",
                "questions": [
                    "Describe an interesting journey you have taken. You should say: where you went, how you traveled, who you were with, and explain why this journey was interesting."
                ]
            },
            "3": {
                "part": 3,
                "description": "Discussion",
                "questions": [
                    "Do you think traveling is a good way to learn about different cultures?",
                    "How has transportation changed in your country in the last few decades?",
                    "Do you think people will travel more or less in the future?"
                ]
            }
        }),
        _answers=json.dumps({
            "1": "sample answers for part 1",
            "2": "sample answer for part 2",
            "3": "sample answers for part 3"
        }),
        is_free=False,
        time_limit=14  # 14 minutes
    )
    
    # Add all tests to the session
    db.session.add_all([
        listening_test, reading_test, writing_test, speaking_test,
        general_listening_test, general_reading_test, general_writing_test, general_speaking_test
    ])
    
    # Commit all changes
    db.session.commit()
    
    print("Complete practice test data initialized successfully.")

if __name__ == "__main__":
    with app.app_context():
        init_complete_test_data()