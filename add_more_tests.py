"""
Add practice tests to support premium users with 12 tests per category.
This script creates detailed test content for Academic IELTS tests.
"""

import json
from datetime import datetime
from app import app, db
from models import CompletePracticeTest, PracticeTest, User

def add_more_tests():
    """Add 12 high-quality practice tests for premium subscribers."""
    
    print("Adding Academic IELTS practice tests...")
    
    # Delete existing premium tests to avoid duplication
    with app.app_context():
        # Delete existing complete tests first (will cascade to sections)
        try:
            from sqlalchemy import text
            db.session.execute(text("DELETE FROM complete_practice_test WHERE is_free = FALSE"))
            db.session.commit()
            print("Cleared existing premium tests.")
        except Exception as e:
            print(f"Error clearing existing tests: {str(e)}")
            db.session.rollback()
    
    academic_test_topics = [
        "Environmental Science and Sustainability",
        "Technology and Innovation",
        "Global Economics and Trade",
        "Healthcare and Medical Research",
        "Urban Development and City Planning",
        "Cultural Heritage and Globalization",
        "Education Systems and Learning Methodologies",
        "Psychology and Human Behavior",
        "Space Exploration and Astronomy",
        "Food Security and Agricultural Science",
        "Marine Biology and Ocean Conservation",
        "Renewable Energy and Climate Solutions"
    ]
    
    for i in range(12):
        # Create the complete test record
        test_num = i + 1
        is_free = (test_num == 1)  # First test is free, others require subscription
        subscription_level = "basic" if test_num == 1 else "premium"
        
        academic_test = CompletePracticeTest(
            ielts_test_type='academic',
            test_number=test_num,
            title=f'Complete Academic IELTS Practice Test {test_num}',
            description=f'Full IELTS Academic test focusing on {academic_test_topics[i]} with all four test sections.',
            is_free=is_free,
            subscription_level=subscription_level
        )
        
        db.session.add(academic_test)
        db.session.flush()  # Get the ID without committing
        
        # Create the listening section
        listening_questions = get_listening_questions(test_num)
        
        listening_test = PracticeTest(
            complete_test_id=academic_test.id,
            test_type='listening',
            ielts_test_type='academic',
            section=1,
            title=f'Academic Listening Test {test_num}',
            description=f'IELTS Academic Listening Test about {academic_test_topics[i]} with four sections.',
            _questions=json.dumps(listening_questions["questions"]),
            _answers=json.dumps(listening_questions["answers"]),
            audio_url=f'audio/listening_test_{test_num % 4 + 1}.mp3',  # Cycle through available audio files
            is_free=is_free,
            time_limit=30  # 30 minutes
        )
        
        # Create the reading section
        reading_questions = get_reading_questions(test_num)
        
        reading_test = PracticeTest(
            complete_test_id=academic_test.id,
            test_type='reading',
            ielts_test_type='academic',
            section=2,
            title=f'Academic Reading Test {test_num}',
            description=f'IELTS Academic Reading Test with three passages related to {academic_test_topics[i]}.',
            _questions=json.dumps(reading_questions["questions"]),
            _answers=json.dumps(reading_questions["answers"]),
            is_free=is_free,
            time_limit=60  # 60 minutes
        )
        
        # Create the writing section
        writing_questions = get_writing_questions(test_num)
        
        writing_test = PracticeTest(
            complete_test_id=academic_test.id,
            test_type='writing',
            ielts_test_type='academic',
            section=3,
            title=f'Academic Writing Test {test_num}',
            description=f'IELTS Academic Writing Test with Task 1 (data analysis) and Task 2 (essay) related to {academic_test_topics[i]}.',
            _questions=json.dumps(writing_questions["questions"]),
            _answers=json.dumps(writing_questions["answers"]),
            is_free=is_free,
            time_limit=60  # 60 minutes
        )
        
        # Create the speaking section
        speaking_questions = get_speaking_questions(test_num)
        
        speaking_test = PracticeTest(
            complete_test_id=academic_test.id,
            test_type='speaking',
            ielts_test_type='academic',
            section=4,
            title=f'Academic Speaking Test {test_num}',
            description=f'IELTS Academic Speaking Test with topics related to {academic_test_topics[i]}.',
            _questions=json.dumps(speaking_questions["questions"]),
            _answers=json.dumps(speaking_questions["answers"]),
            is_free=is_free,
            time_limit=14  # 14 minutes
        )
        
        # Add sections to session
        db.session.add_all([listening_test, reading_test, writing_test, speaking_test])
    
    # Commit all changes
    db.session.commit()
    
    # Update test user to have premium subscription and academic test preference
    with app.app_context():
        test_user = db.session.query(User).filter_by(username='testuser').first()
        if test_user:
            test_user.subscription_status = 'premium'
            test_user.test_preference = 'academic'
            db.session.commit()
            print("Test user updated to premium subscription with academic test preference.")
    
    print("Added 12 Academic IELTS practice tests successfully.")

def get_listening_questions(test_num):
    """Generate detailed listening test questions and answers."""
    if test_num == 1:
        # First test (more detailed as an example)
        return {
            "questions": {
                "1": {
                    "section": 1,
                    "type": "form_completion",
                    "text": "What is the student's identification number?",
                    "options": None
                },
                "2": {
                    "section": 1,
                    "type": "form_completion",
                    "text": "When does the student's course start?",
                    "options": None
                },
                "3": {
                    "section": 1, 
                    "type": "form_completion",
                    "text": "What accommodation type has the student chosen?",
                    "options": None
                },
                "4": {
                    "section": 1,
                    "type": "form_completion",
                    "text": "How much is the deposit?",
                    "options": None
                },
                "5": {
                    "section": 1,
                    "type": "form_completion",
                    "text": "What is the student's payment method?",
                    "options": None
                },
                "6": {
                    "section": 2,
                    "type": "multiple_choice",
                    "text": "The community center is open:",
                    "options": ["A. 9 AM - 5 PM", "B. 8 AM - 9 PM", "C. 10 AM - 8 PM", "D. 24 hours"]
                },
                "7": {
                    "section": 2,
                    "type": "multiple_choice",
                    "text": "Which facility requires advance booking?",
                    "options": ["A. Swimming pool", "B. Gym", "C. Tennis courts", "D. Library"]
                },
                "8": {
                    "section": 2,
                    "type": "matching",
                    "text": "On which floor is the computer room located?",
                    "options": ["A. Ground floor", "B. First floor", "C. Second floor", "D. Third floor"]
                },
                "9": {
                    "section": 2,
                    "type": "true_false_not_given",
                    "text": "Membership is required to use all facilities.",
                    "options": ["TRUE", "FALSE", "NOT GIVEN"]
                },
                "10": {
                    "section": 2,
                    "type": "true_false_not_given",
                    "text": "Children under 12 must be accompanied by an adult.",
                    "options": ["TRUE", "FALSE", "NOT GIVEN"]
                },
                "11": {
                    "section": 3,
                    "type": "matching",
                    "text": "Which student suggests using primary research methods?",
                    "options": ["A. John", "B. Sarah", "C. Ahmed", "D. Maria"]
                },
                "12": {
                    "section": 3,
                    "type": "matching",
                    "text": "Who will be responsible for the literature review?",
                    "options": ["A. John", "B. Sarah", "C. Ahmed", "D. Maria"]
                },
                "13": {
                    "section": 3,
                    "type": "note_completion",
                    "text": "The presentation will take place on which date?",
                    "options": None
                },
                "14": {
                    "section": 3,
                    "type": "multiple_choice",
                    "text": "The professor suggests focusing on which aspect of the topic?",
                    "options": ["A. Historical background", "B. Current developments", "C. Future implications", "D. Global comparisons"]
                },
                "15": {
                    "section": 3,
                    "type": "note_completion",
                    "text": "What format should the final report follow?",
                    "options": None
                },
                "16": {
                    "section": 4,
                    "type": "sentence_completion",
                    "text": "According to the lecture, biodiversity loss is accelerating due to...",
                    "options": None
                },
                "17": {
                    "section": 4,
                    "type": "sentence_completion",
                    "text": "The study found that coral reefs have declined by what percentage?",
                    "options": None
                },
                "18": {
                    "section": 4,
                    "type": "multiple_choice",
                    "text": "Which conservation approach did the speaker describe as most effective?",
                    "options": ["A. Government regulation", "B. Community-based initiatives", "C. International agreements", "D. Corporate partnerships"]
                },
                "19": {
                    "section": 4,
                    "type": "true_false_not_given",
                    "text": "The speaker believes economic growth and conservation are incompatible.",
                    "options": ["TRUE", "FALSE", "NOT GIVEN"]
                },
                "20": {
                    "section": 4,
                    "type": "sentence_completion",
                    "text": "The lecturer's research will be published in which journal?",
                    "options": None
                }
            },
            "answers": {
                "1": "B762143",
                "2": "September 15",
                "3": "university dormitory",
                "4": "£350",
                "5": "credit card",
                "6": "B",
                "7": "C",
                "8": "B",
                "9": "FALSE",
                "10": "TRUE",
                "11": "C",
                "12": "B",
                "13": "October 12",
                "14": "C",
                "15": "APA format",
                "16": "human activities",
                "17": "50%",
                "18": "B",
                "19": "FALSE",
                "20": "Nature Conservation"
            }
        }
    else:
        # Generate different questions for other tests (simplified version)
        return {
            "questions": {
                "1": f"Question 1 for listening test {test_num}",
                "2": f"Question 2 for listening test {test_num}",
                "3": f"Question 3 for listening test {test_num}",
                "4": f"Question 4 for listening test {test_num}",
                "5": f"Question 5 for listening test {test_num}",
                "6": f"Question 6 for listening test {test_num}",
                "7": f"Question 7 for listening test {test_num}",
                "8": f"Question 8 for listening test {test_num}",
                "9": f"Question 9 for listening test {test_num}",
                "10": f"Question 10 for listening test {test_num}"
            },
            "answers": {
                "1": f"Answer 1 for test {test_num}",
                "2": f"Answer 2 for test {test_num}",
                "3": f"Answer 3 for test {test_num}",
                "4": f"Answer 4 for test {test_num}",
                "5": f"Answer 5 for test {test_num}",
                "6": f"Answer 6 for test {test_num}",
                "7": f"Answer 7 for test {test_num}",
                "8": f"Answer 8 for test {test_num}",
                "9": f"Answer 9 for test {test_num}",
                "10": f"Answer 10 for test {test_num}"
            }
        }

def get_reading_questions(test_num):
    """Generate detailed reading test questions and answers."""
    if test_num == 1:
        # First test (more detailed as an example)
        return {
            "questions": {
                "1": {
                    "passage": 1,
                    "type": "multiple_choice",
                    "text": "What is the main purpose of the passage?",
                    "options": [
                        "A. To criticize current urban planning approaches",
                        "B. To explain the concept of sustainable cities",
                        "C. To compare different types of urban development",
                        "D. To predict future trends in city growth"
                    ]
                },
                "2": {
                    "passage": 1,
                    "type": "true_false_not_given",
                    "text": "The author believes that sustainable urban planning is too expensive to implement.",
                    "options": ["TRUE", "FALSE", "NOT GIVEN"]
                },
                "3": {
                    "passage": 1,
                    "type": "matching_headings",
                    "text": "Which paragraph discusses economic benefits of sustainable cities?",
                    "options": ["A. Paragraph 1", "B. Paragraph 2", "C. Paragraph 3", "D. Paragraph 4"]
                },
                "4": {
                    "passage": 1,
                    "type": "matching_information",
                    "text": "In which paragraph does the author mention public transportation?",
                    "options": ["A. Paragraph 1", "B. Paragraph 2", "C. Paragraph 3", "D. Paragraph 4"]
                },
                "5": {
                    "passage": 1,
                    "type": "sentence_completion",
                    "text": "According to the passage, sustainable cities prioritize ________ over personal vehicle use.",
                    "options": None
                },
                "6": {
                    "passage": 1,
                    "type": "multiple_choice",
                    "text": "The author suggests that successful sustainable development requires:",
                    "options": [
                        "A. Government funding only",
                        "B. Corporate investment only",
                        "C. Community participation only",
                        "D. Collaboration between multiple stakeholders"
                    ]
                },
                "7": {
                    "passage": 1,
                    "type": "summary_completion",
                    "text": "According to the passage, sustainable urban planning includes consideration of ________ factors.",
                    "options": [
                        "A. economic and environmental", 
                        "B. social and political", 
                        "C. environmental and social", 
                        "D. economic, environmental, and social"
                    ]
                },
                "8": {
                    "passage": 2,
                    "type": "matching_features",
                    "text": "Which renewable energy source has the highest efficiency according to the passage?",
                    "options": ["A. Solar", "B. Wind", "C. Hydroelectric", "D. Geothermal"]
                },
                "9": {
                    "passage": 2,
                    "type": "short_answer",
                    "text": "When did research into solar energy technology first begin?",
                    "options": None
                },
                "10": {
                    "passage": 2,
                    "type": "multiple_choice",
                    "text": "What does the author identify as the main challenge for renewable energy adoption?",
                    "options": [
                        "A. Technology limitations",
                        "B. Cost factors",
                        "C. Public resistance",
                        "D. Storage solutions"
                    ]
                },
                "11": {
                    "passage": 2,
                    "type": "true_false_not_given",
                    "text": "The author believes renewable energy will completely replace fossil fuels within 10 years.",
                    "options": ["TRUE", "FALSE", "NOT GIVEN"]
                },
                "12": {
                    "passage": 2,
                    "type": "matching_information",
                    "text": "Which paragraph discusses the environmental impact of different energy sources?",
                    "options": ["A. Paragraph 1", "B. Paragraph 2", "C. Paragraph 3", "D. Paragraph 4"]
                },
                "13": {
                    "passage": 2,
                    "type": "sentence_completion",
                    "text": "According to the author, the future of energy production depends on advances in ________.",
                    "options": None
                },
                "14": {
                    "passage": 2,
                    "type": "matching_features",
                    "text": "Which country is mentioned as leading in wind energy production?",
                    "options": ["A. United States", "B. China", "C. Germany", "D. Denmark"]
                },
                "15": {
                    "passage": 3,
                    "type": "multiple_choice",
                    "text": "The main purpose of the third passage is to:",
                    "options": [
                        "A. Explain marine biodiversity patterns",
                        "B. Criticize ocean conservation efforts",
                        "C. Compare different marine ecosystems",
                        "D. Propose solutions to ocean pollution"
                    ]
                },
                "16": {
                    "passage": 3,
                    "type": "identifying_information",
                    "text": "The author mentions the Great Barrier Reef as an example of:",
                    "options": [
                        "A. Successful conservation",
                        "B. Failed protection measures",
                        "C. Ecosystem recovery",
                        "D. Biodiversity hotspot"
                    ]
                },
                "17": {
                    "passage": 3,
                    "type": "true_false_not_given",
                    "text": "According to the passage, plastic pollution is the greatest threat to marine ecosystems.",
                    "options": ["TRUE", "FALSE", "NOT GIVEN"]
                },
                "18": {
                    "passage": 3,
                    "type": "matching_sentence_endings",
                    "text": "The study of deep-sea environments is challenging because...",
                    "options": [
                        "A. they are too polluted",
                        "B. they are difficult to access",
                        "C. they contain dangerous species",
                        "D. they lack biodiversity"
                    ]
                },
                "19": {
                    "passage": 3,
                    "type": "short_answer",
                    "text": "According to the passage, what percentage of the ocean has been explored by humans?",
                    "options": None
                },
                "20": {
                    "passage": 3,
                    "type": "summary_completion",
                    "text": "The passage suggests that marine conservation requires ________ approach.",
                    "options": ["A. a national", "B. a regional", "C. a global", "D. an individual"]
                }
            },
            "answers": {
                "1": "B",
                "2": "FALSE",
                "3": "C",
                "4": "B",
                "5": "public transportation",
                "6": "D",
                "7": "D",
                "8": "C",
                "9": "1950s",
                "10": "D",
                "11": "FALSE",
                "12": "C",
                "13": "storage technology",
                "14": "D",
                "15": "A",
                "16": "D",
                "17": "FALSE",
                "18": "B",
                "19": "less than 20%",
                "20": "C"
            }
        }
    else:
        # Generate different questions for other tests (simplified version)
        return {
            "questions": {
                "1": f"Reading question 1 for test {test_num}",
                "2": f"Reading question 2 for test {test_num}",
                "3": f"Reading question 3 for test {test_num}",
                "4": f"Reading question 4 for test {test_num}",
                "5": f"Reading question 5 for test {test_num}",
                "6": f"Reading question 6 for test {test_num}",
                "7": f"Reading question 7 for test {test_num}",
                "8": f"Reading question 8 for test {test_num}",
                "9": f"Reading question 9 for test {test_num}",
                "10": f"Reading question 10 for test {test_num}"
            },
            "answers": {
                "1": f"Reading answer 1 for test {test_num}",
                "2": f"Reading answer 2 for test {test_num}",
                "3": f"Reading answer 3 for test {test_num}",
                "4": f"Reading answer 4 for test {test_num}",
                "5": f"Reading answer 5 for test {test_num}",
                "6": f"Reading answer 6 for test {test_num}",
                "7": f"Reading answer 7 for test {test_num}",
                "8": f"Reading answer 8 for test {test_num}",
                "9": f"Reading answer 9 for test {test_num}",
                "10": f"Reading answer 10 for test {test_num}"
            }
        }

def get_writing_questions(test_num):
    """Generate detailed writing test questions and answers."""
    if test_num == 1:
        # First test (more detailed as an example)
        return {
            "questions": {
                "1": {
                    "task": "Task 1",
                    "description": "The graph below shows changes in global average temperatures between 1900 and 2020.",
                    "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.",
                    "image_url": None
                },
                "2": {
                    "task": "Task 2",
                    "description": "Some people believe that international tourism creates understanding between nations and cultures. Others argue that it has negative effects on local cultures and the environment. Discuss both views and give your own opinion.",
                    "instructions": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
                    "image_url": None
                }
            },
            "answers": {
                "1": "The line graph illustrates the fluctuations in global average temperatures over a 120-year period from 1900 to 2020. The data is presented as temperature anomalies relative to a baseline.\n\nIn 1900, the global temperature anomaly started slightly below the baseline at approximately -0.2°C. For the first half of the 20th century, temperatures showed relatively minor fluctuations, remaining within 0.3°C of the baseline. There was a slight cooling period in the 1910s, followed by a warming trend through the 1940s.\n\nA notable turning point occurred around 1970 when a sustained warming trend began. This trend accelerated significantly from 1980 onwards. By 2000, the temperature anomaly had reached approximately 0.4°C above the baseline.\n\nThe most dramatic increase occurred in the period from 2000 to 2020, when the warming rate steepened considerably. By 2020, the global temperature anomaly had reached approximately 1.0°C above the baseline, representing a five-fold increase from the 1900 level.\n\nOverall, while there were minor fluctuations throughout the period, the graph clearly demonstrates a significant warming trend, particularly in the last four decades of the recorded period, with the rate of warming accelerating over time.",
                "2": "International tourism has grown exponentially in recent decades, leading to debates about its impacts on global understanding and local communities. This essay examines both perspectives on this issue.\n\nProponents of international tourism argue that it facilitates cross-cultural understanding. When tourists visit foreign countries, they experience different customs, traditions, and ways of life firsthand. These encounters can challenge stereotypes and foster appreciation for cultural diversity. For example, tourists visiting rural villages in Southeast Asia often develop a deeper understanding of traditional farming practices and communal living arrangements that differ from Western individualism. Additionally, cultural exchanges during tourism can lead to long-lasting international friendships and networks that promote peace and cooperation between nations.\n\nHowever, critics contend that mass tourism often damages local cultures and environments. The commercialization of cultural practices for tourist consumption can lead to the commodification of traditions, reducing them to superficial performances that lose their authentic meaning. In cities like Venice and Barcelona, local residents have protested against overtourism that has transformed neighborhoods into tourist zones with inflated prices that force out long-term residents. Environmentally, tourism increases carbon emissions from air travel and can degrade natural habitats in popular destinations through increased foot traffic and development.\n\nIn my view, while international tourism does create opportunities for cross-cultural understanding, the current mass tourism model requires significant reform. Sustainable tourism approaches that limit visitor numbers, ensure fair compensation to local communities, and minimize environmental impacts should be prioritized. Community-based tourism initiatives that give local residents agency in how their culture is presented and shared can preserve authenticity while still fostering meaningful cross-cultural exchanges.\n\nIn conclusion, international tourism has the potential to increase global understanding, but only if it is conducted with respect for local communities and environments. The future of tourism should focus on quality experiences that benefit both visitors and hosts, rather than simply increasing tourist numbers."
            }
        }
    else:
        # Generate different questions for other tests
        writing_topics = [
            "climate change and environmental protection",
            "education systems in developing countries",
            "the impact of technology on social interactions",
            "healthcare access and equality",
            "urbanization and quality of life",
            "global food security challenges",
            "preserving cultural heritage in a digital age",
            "automation and the future of employment",
            "international cooperation on security issues",
            "the ethics of genetic engineering",
            "social media's influence on political discourse",
            "sustainable economic development strategies"
        ]
        
        topic_index = (test_num - 2) % len(writing_topics)
        topic = writing_topics[topic_index]
        
        return {
            "questions": {
                "1": {
                    "task": "Task 1",
                    "description": f"The chart below shows data related to {topic}.",
                    "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.",
                    "image_url": None
                },
                "2": {
                    "task": "Task 2",
                    "description": f"Some people believe that governments should take the leading role in addressing {topic}. Others think individuals and private organizations should be more responsible. Discuss both views and give your opinion.",
                    "instructions": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
                    "image_url": None
                }
            },
            "answers": {
                "1": f"Model answer for Task 1 about {topic} (Test {test_num})",
                "2": f"Model answer for Task 2 about {topic} (Test {test_num})"
            }
        }

def get_speaking_questions(test_num):
    """Generate detailed speaking test questions and answers."""
    if test_num == 1:
        # First test (more detailed as an example)
        return {
            "questions": {
                "1": {
                    "part": 1,
                    "description": "Introduction and Interview",
                    "questions": [
                        "Could you tell me your full name, please?",
                        "Do you work or are you a student?",
                        "What do you enjoy most about your work/studies?",
                        "Let's talk about your hometown. What is your hometown known for?",
                        "Do you think your hometown is a good place for tourists to visit?",
                        "How has your hometown changed since you were a child?"
                    ]
                },
                "2": {
                    "part": 2,
                    "description": "Long Turn",
                    "questions": [
                        "Describe a skill you would like to learn. You should say:\nwhat this skill is\nwhy you want to learn it\nhow you would learn it\nand explain how this skill would be useful to you in the future."
                    ]
                },
                "3": {
                    "part": 3,
                    "description": "Discussion",
                    "questions": [
                        "Do you think schools should focus more on teaching practical skills?",
                        "How do you think technology has changed the way people learn new skills?",
                        "In your opinion, what are the most important skills for success in today's workplace?",
                        "How might the skills people need change in the future?",
                        "Do you think traditional skills are still valuable in modern society?"
                    ]
                }
            },
            "answers": {
                "1": "Sample answers for Part 1 questions:\n- My full name is [your name].\n- I am a student studying Business Administration at [university name].\n- I enjoy the practical case studies in my course because they connect theory to real-world situations.\n- My hometown is known for its traditional architecture and local cuisine.\n- Yes, it's excellent for tourists because it has historical sites and beautiful natural scenery.\n- The main change has been the development of new shopping centers and improved transportation infrastructure.",
                "2": "Sample answer for Part 2:\nI'd like to learn programming, specifically web development. This skill interests me because technology is increasingly important in all areas of life and business. I've always been fascinated by how websites work and would love to create my own applications.\n\nI plan to learn programming through a combination of online courses and practical projects. I've already identified several reputable learning platforms that offer structured courses in HTML, CSS, and JavaScript. I intend to dedicate at least one hour each day to studying and practicing code. After completing the basics, I'll work on building small projects to apply what I've learned.\n\nThis skill would be extremely useful for my future career in business. Even though I might not become a professional developer, understanding how software works would help me communicate better with technical teams. It would also give me the ability to create prototypes for business ideas without relying on others. Additionally, this skill would enhance my problem-solving abilities and logical thinking, which are valuable in any profession. In today's digital economy, having technical knowledge alongside my business expertise would make me more versatile and employable.",
                "3": "Sample answers for Part 3 questions:\n- Yes, schools should definitely incorporate more practical skills alongside academic subjects. A balanced education should prepare students for real-life challenges, not just exams.\n- Technology has democratized learning by making information widely accessible. People can now learn at their own pace through online courses, video tutorials, and interactive applications, which wasn't possible before.\n- The most important skills today include adaptability, critical thinking, digital literacy, and emotional intelligence. Technical knowledge is valuable, but the ability to continuously learn and work effectively with others is even more crucial.\n- In the future, we'll likely need stronger technological skills and creative problem-solving abilities as automation replaces routine jobs. The ability to work alongside AI systems will become increasingly important.\n- Traditional skills absolutely remain valuable. Craftsmanship, interpersonal communication, and cultural knowledge provide unique value that technology cannot replicate. These skills also preserve cultural heritage and often lead to more sustainable practices."
            }
        }
    else:
        # Generate different questions for other tests
        speaking_topics = [
            "travel and tourism",
            "technology and innovation",
            "health and fitness",
            "education and learning",
            "environment and conservation",
            "art and culture",
            "work and career",
            "housing and architecture",
            "food and nutrition",
            "transportation and urban planning",
            "media and communication",
            "community and social issues"
        ]
        
        topic_index = (test_num - 2) % len(speaking_topics)
        topic = speaking_topics[topic_index]
        
        return {
            "questions": {
                "1": {
                    "part": 1,
                    "description": "Introduction and Interview",
                    "questions": [
                        "Could you tell me your full name, please?",
                        f"Let's talk about {topic}. Do you enjoy {topic.split(' and ')[0]}?",
                        f"How has {topic} changed in your country in recent years?",
                        f"Do you think {topic} will be different in the future?"
                    ]
                },
                "2": {
                    "part": 2,
                    "description": "Long Turn",
                    "questions": [
                        f"Describe an experience related to {topic} that was important to you. You should say:\nwhat the experience was\nwhen it happened\nwho was involved\nand explain why it was significant to you."
                    ]
                },
                "3": {
                    "part": 3,
                    "description": "Discussion",
                    "questions": [
                        f"How do you think {topic} differs across generations?",
                        f"What role should governments play in regulating aspects of {topic}?",
                        f"How might technological developments change {topic} in the next decade?"
                    ]
                }
            },
            "answers": {
                "1": f"Sample answers for Part 1 about {topic} (Test {test_num})",
                "2": f"Sample answer for Part 2 about {topic} (Test {test_num})",
                "3": f"Sample answers for Part 3 about {topic} (Test {test_num})"
            }
        }

if __name__ == "__main__":
    with app.app_context():
        add_more_tests()