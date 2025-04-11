"""
Add more practice tests to support premium users with 12 tests.
"""

import json
from datetime import datetime
from app import app, db
from models import CompletePracticeTest, PracticeTest

def add_more_tests():
    """Add more practice tests for premium subscribers."""
    
    print("Adding more practice tests...")
    
    test_types = ['academic', 'general', 'ukvi', 'life_skills']
    subscription_levels = ['basic', 'intermediate', 'premium']
    
    # Create 3 tests of each type (12 total)
    for test_type in test_types:
        # Academic tests (3)
        if test_type == 'academic':
            # Test 1 (Free) was already created
            # Create Test 2 (Intermediate)
            academic_test2 = CompletePracticeTest(
                ielts_test_type='academic',
                test_number=2,
                title='Complete Academic IELTS Practice Test 2',
                description='A full IELTS Academic test with all four sections, including more complex topics and questions.',
                is_free=False,
                subscription_level='intermediate'
            )
            
            db.session.add(academic_test2)
            db.session.flush()  # Get the ID without committing
            
            # Create the listening section
            listening_test = PracticeTest(
                complete_test_id=academic_test2.id,
                test_type='listening',
                ielts_test_type='academic',
                section=1,
                title='Academic Listening Test 2',
                description='IELTS Academic Listening Test with challenging vocabulary and quick exchanges.',
                _questions=json.dumps({
                    "1": "What is the project deadline?",
                    "2": "How many team members are needed?",
                    "3": "What is the budget constraint?",
                    "4": "Which department is funding the research?",
                    "5": "What special equipment is required?",
                }),
                _answers=json.dumps({
                    "1": "march 15",
                    "2": "6",
                    "3": "50000",
                    "4": "engineering",
                    "5": "spectrometer",
                }),
                audio_url='audio/biodiversity_project.mp3',
                is_free=False,
                time_limit=30  # 30 minutes
            )
            
            # Create the reading section
            reading_test = PracticeTest(
                complete_test_id=academic_test2.id,
                test_type='reading',
                ielts_test_type='academic',
                section=2,
                title='Academic Reading Test 2',
                description='Advanced reading passages with scientific terminology and complex arguments.',
                _questions=json.dumps({
                    "1": "According to the article, which species is most affected by climate change?",
                    "2": "The research was conducted in what year?",
                    "3": "What was the sample size used in the study?",
                    "4": "What methodology was used to collect data?",
                    "5": "Which country funded the majority of the research?",
                }),
                _answers=json.dumps({
                    "1": "polar bears",
                    "2": "2022",
                    "3": "2500",
                    "4": "field observation",
                    "5": "canada",
                }),
                is_free=False,
                time_limit=60  # 60 minutes
            )
            
            # Create the writing section
            writing_test = PracticeTest(
                complete_test_id=academic_test2.id,
                test_type='writing',
                ielts_test_type='academic',
                section=3,
                title='Academic Writing Test 2',
                description='Challenging writing tasks requiring sophisticated analysis and language use.',
                _questions=json.dumps({
                    "1": {
                        "task": "Task 1",
                        "description": "The table below shows electricity generation (in terawatt hours) from different sources in five countries in 2020.",
                        "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.",
                        "image_url": None
                    },
                    "2": {
                        "task": "Task 2",
                        "description": "Some people believe that governments should invest more in scientific research to solve environmental problems, while others think changing individual behavior is more important. Discuss both views and give your opinion.",
                        "instructions": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
                        "image_url": None
                    }
                }),
                _answers=json.dumps({
                    "1": "model answer for task 1",
                    "2": "model answer for task 2"
                }),
                is_free=False,
                time_limit=60  # 60 minutes
            )
            
            # Create the speaking section
            speaking_test = PracticeTest(
                complete_test_id=academic_test2.id,
                test_type='speaking',
                ielts_test_type='academic',
                section=4,
                title='Academic Speaking Test 2',
                description='Advanced speaking topics requiring nuanced opinions and detailed explanations.',
                _questions=json.dumps({
                    "1": {
                        "part": 1,
                        "description": "Introduction and Interview",
                        "questions": [
                            "Could you tell me your full name, please?",
                            "What do you enjoy about your studies or work?",
                            "Do you think your field will change in the future?",
                            "Let's talk about technology. How has technology changed education in your country?",
                            "Do you think artificial intelligence will improve learning? Why or why not?"
                        ]
                    },
                    "2": {
                        "part": 2,
                        "description": "Long Turn",
                        "questions": [
                            "Describe a significant scientific discovery or technological innovation. You should say: what it was, when it was developed, how it has affected society, and explain why you think it is important."
                        ]
                    },
                    "3": {
                        "part": 3,
                        "description": "Discussion",
                        "questions": [
                            "How do scientific advances affect ordinary people's lives?",
                            "Should governments regulate technological development? Why or why not?",
                            "In what ways might technology create problems as well as solve them?"
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
            
            # Create Test 3 (Premium)
            academic_test3 = CompletePracticeTest(
                ielts_test_type='academic',
                test_number=3,
                title='Complete Academic IELTS Practice Test 3',
                description='Our most advanced Academic IELTS practice test, with university-level content and expert-verified questions.',
                is_free=False,
                subscription_level='premium'
            )
            
            db.session.add(academic_test3)
            db.session.flush()  # Get the ID without committing
            
            # Create the listening section
            listening_test3 = PracticeTest(
                complete_test_id=academic_test3.id,
                test_type='listening',
                ielts_test_type='academic',
                section=1,
                title='Academic Listening Test 3',
                description='Premium academic listening test with complex lectures and detailed note-taking requirements.',
                _questions=json.dumps({
                    "1": "What is the main focus of the urban planning lecture?",
                    "2": "How many case studies were presented?",
                    "3": "What year was the first smart city project implemented?",
                    "4": "Which city pioneered the transportation solution?",
                    "5": "What percentage reduction in emissions was achieved?",
                }),
                _answers=json.dumps({
                    "1": "sustainable development",
                    "2": "3",
                    "3": "2015",
                    "4": "singapore",
                    "5": "35",
                }),
                audio_url='audio/urban_planning_lecture.mp3',
                is_free=False,
                time_limit=30  # 30 minutes
            )
            
            # Create the reading section
            reading_test3 = PracticeTest(
                complete_test_id=academic_test3.id,
                test_type='reading',
                ielts_test_type='academic',
                section=2,
                title='Academic Reading Test 3',
                description='Premium reading passages with academic journal-level content and sophisticated vocabulary.',
                _questions=json.dumps({
                    "1": "The research on neuroplasticity suggests that the brain:",
                    "2": "According to the study, how long does it take to form new neural pathways?",
                    "3": "The author suggests that the implications for education are primarily related to:",
                    "4": "Which demographic showed the most significant improvements?",
                    "5": "The longitudinal study was conducted over a period of:",
                }),
                _answers=json.dumps({
                    "1": "continues to develop throughout life",
                    "2": "6 weeks",
                    "3": "personalized learning",
                    "4": "older adults",
                    "5": "12 years",
                }),
                is_free=False,
                time_limit=60  # 60 minutes
            )
            
            # Create the writing section
            writing_test3 = PracticeTest(
                complete_test_id=academic_test3.id,
                test_type='writing',
                ielts_test_type='academic',
                section=3,
                title='Academic Writing Test 3',
                description='Premium writing tasks requiring sophisticated analysis and precise academic language.',
                _questions=json.dumps({
                    "1": {
                        "task": "Task 1",
                        "description": "The diagrams below show the process of photosynthesis and how it relates to the carbon cycle.",
                        "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.",
                        "image_url": None
                    },
                    "2": {
                        "task": "Task 2",
                        "description": "Some researchers believe that it is more important to focus on applied scientific research to solve immediate problems, while others argue that theoretical research has greater long-term benefits. Discuss both perspectives and give your own opinion.",
                        "instructions": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
                        "image_url": None
                    }
                }),
                _answers=json.dumps({
                    "1": "model answer for task 1",
                    "2": "model answer for task 2"
                }),
                is_free=False,
                time_limit=60  # 60 minutes
            )
            
            # Create the speaking section
            speaking_test3 = PracticeTest(
                complete_test_id=academic_test3.id,
                test_type='speaking',
                ielts_test_type='academic',
                section=4,
                title='Academic Speaking Test 3',
                description='Premium speaking assessment requiring sophisticated vocabulary and complex topic analysis.',
                _questions=json.dumps({
                    "1": {
                        "part": 1,
                        "description": "Introduction and Interview",
                        "questions": [
                            "Could you tell me your full name, please?",
                            "What field of study or work are you most interested in?",
                            "How has education changed in your country in recent years?",
                            "Do you think traditional teaching methods still have value today?",
                            "How important is continuous learning in your culture?"
                        ]
                    },
                    "2": {
                        "part": 2,
                        "description": "Long Turn",
                        "questions": [
                            "Describe an important ethical dilemma facing society today. You should say: what the ethical issue is, why it has become important now, how it affects different groups of people, and explain how you think it might be resolved."
                        ]
                    },
                    "3": {
                        "part": 3,
                        "description": "Discussion",
                        "questions": [
                            "How do ethical standards vary between different professions?",
                            "Should ethical education be a mandatory part of university curricula?",
                            "How might advances in technology create new ethical challenges in the future?"
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
            
            # Add tests to session
            db.session.add_all([
                listening_test, reading_test, writing_test, speaking_test,
                listening_test3, reading_test3, writing_test3, speaking_test3
            ])
            
        # Add General Training tests - test 2 and 3
        if test_type == 'general':
            # Test 1 was already created
            # Create Test 2 (Intermediate)
            general_test2 = CompletePracticeTest(
                ielts_test_type='general',
                test_number=2,
                title='Complete General Training IELTS Practice Test 2',
                description='An intermediate-level General Training IELTS test focusing on workplace and everyday communication.',
                is_free=False,
                subscription_level='intermediate'
            )
            
            db.session.add(general_test2)
            db.session.flush()
            
            # Create sections for general_test2 (similar structure to above, abbreviated for brevity)
            general_listening2 = PracticeTest(
                complete_test_id=general_test2.id,
                test_type='listening',
                ielts_test_type='general',
                section=1,
                title='General Training Listening Test 2',
                description='Intermediate workplace and social situation dialogues.',
                _questions=json.dumps({"1": "Sample question 1", "2": "Sample question 2"}),
                _answers=json.dumps({"1": "sample answer 1", "2": "sample answer 2"}),
                audio_url='audio/community_center.mp3',
                is_free=False,
                time_limit=30
            )
            
            # Create Test 3 (Premium)
            general_test3 = CompletePracticeTest(
                ielts_test_type='general',
                test_number=3,
                title='Complete General Training IELTS Practice Test 3',
                description='Advanced General Training test with complex workplace scenarios and sophisticated practical writing tasks.',
                is_free=False,
                subscription_level='premium'
            )
            
            db.session.add(general_test3)
            db.session.flush()
            
            # Create sections for general_test3 (similar structure)
            general_listening3 = PracticeTest(
                complete_test_id=general_test3.id,
                test_type='listening',
                ielts_test_type='general',
                section=1,
                title='General Training Listening Test 3',
                description='Premium workplace and training scenarios.',
                _questions=json.dumps({"1": "Sample question 1", "2": "Sample question 2"}),
                _answers=json.dumps({"1": "sample answer 1", "2": "sample answer 2"}),
                audio_url='audio/community_center.mp3',
                is_free=False,
                time_limit=30
            )
            
            # Add test sections to session
            db.session.add_all([general_listening2, general_listening3])
        
        # Add UKVI tests - all 3
        if test_type == 'ukvi':
            for i in range(1, 4):
                subscription = 'basic' if i == 1 else 'intermediate' if i == 2 else 'premium'
                is_free = (i == 1)
                
                ukvi_test = CompletePracticeTest(
                    ielts_test_type='ukvi',
                    test_number=i,
                    title=f'Complete UKVI IELTS Practice Test {i}',
                    description=f'IELTS for UK Visas and Immigration test designed to prepare for UK visa requirements.',
                    is_free=is_free,
                    subscription_level=subscription
                )
                
                db.session.add(ukvi_test)
                db.session.flush()
                
                # Create basic section for each test
                ukvi_listening = PracticeTest(
                    complete_test_id=ukvi_test.id,
                    test_type='listening',
                    ielts_test_type='ukvi',
                    section=1,
                    title=f'UKVI Listening Test {i}',
                    description='UKVI-specific listening scenarios including UK-related conversations.',
                    _questions=json.dumps({"1": "Sample question 1", "2": "Sample question 2"}),
                    _answers=json.dumps({"1": "sample answer 1", "2": "sample answer 2"}),
                    audio_url='audio/accommodation_inquiry.mp3',
                    is_free=is_free,
                    time_limit=30
                )
                
                db.session.add(ukvi_listening)
        
        # Add Life Skills tests - all 3
        if test_type == 'life_skills':
            for i in range(1, 4):
                subscription = 'basic' if i == 1 else 'intermediate' if i == 2 else 'premium'
                is_free = (i == 1)
                
                life_test = CompletePracticeTest(
                    ielts_test_type='life_skills',
                    test_number=i,
                    title=f'Complete IELTS Life Skills Test {i}',
                    description=f'IELTS Life Skills test focused on speaking and listening for everyday communication.',
                    is_free=is_free,
                    subscription_level=subscription
                )
                
                db.session.add(life_test)
                db.session.flush()
                
                # Create basic section for each test
                life_listening = PracticeTest(
                    complete_test_id=life_test.id,
                    test_type='listening',
                    ielts_test_type='life_skills',
                    section=1,
                    title=f'Life Skills Listening Test {i}',
                    description='Everyday communication scenarios in English-speaking environments.',
                    _questions=json.dumps({"1": "Sample question 1", "2": "Sample question 2"}),
                    _answers=json.dumps({"1": "sample answer 1", "2": "sample answer 2"}),
                    audio_url='audio/accommodation_inquiry.mp3',
                    is_free=is_free,
                    time_limit=20
                )
                
                db.session.add(life_listening)
    
    # Commit all changes
    db.session.commit()
    
    print("Added more practice tests successfully.")

if __name__ == "__main__":
    with app.app_context():
        add_more_tests()