"""
Comprehensive IELTS Speaking Question Database
Authentic questions following official IELTS test patterns and timing.
"""

import random

class IELTSQuestionDatabase:
    """Database of authentic IELTS speaking questions organized by part and type"""
    
    PART_1_TOPICS = {
        'personal_info': [
            "Could you tell me your full name, please?",
            "What should I call you?",
            "Can you tell me where you're from?",
            "Do you work or are you a student?"
        ],
        'home_accommodation': [
            "Do you live in a house or an apartment?",
            "Can you describe the place where you live?",
            "How long have you lived there?",
            "What do you like most about where you live?",
            "Is there anything you would like to change about your home?"
        ],
        'hometown': [
            "Let's talk about your hometown. Where is it?",
            "What's your hometown like?",
            "What do you like most about your hometown?",
            "Has your hometown changed much over the years?",
            "Are there any problems with your hometown?"
        ],
        'work_study': [
            "What do you do for work?",
            "Why did you choose that job?",
            "What do you like most about your job?",
            "What are your responsibilities at work?",
            "Do you think you'll continue doing this job in the future?"
        ],
        'hobbies_interests': [
            "What do you like to do in your free time?",
            "How long have you been interested in that?",
            "Is this a popular hobby in your country?",
            "Do you think hobbies are important?",
            "Have your hobbies changed since you were a child?"
        ],
        'food': [
            "What's your favourite type of food?",
            "Do you like cooking?",
            "What did you eat when you were a child?",
            "Do you think it's important to eat healthy food?",
            "Have your eating habits changed over the years?"
        ]
    }
    
    PART_2_CUE_CARDS = {
        'academic': [
            {
                'topic': "Describe a subject you enjoyed studying at school",
                'points': [
                    "What the subject was",
                    "When you studied it",
                    "What you learned about it",
                    "And explain why you enjoyed studying this subject"
                ]
            },
            {
                'topic': "Describe a book that had a major influence on you",
                'points': [
                    "What the book was",
                    "When you read it",
                    "What it was about",
                    "And explain how it influenced you"
                ]
            },
            {
                'topic': "Describe a skill you would like to learn",
                'points': [
                    "What the skill is",
                    "How you would learn it",
                    "Where you would use this skill",
                    "And explain why you want to learn it"
                ]
            }
        ],
        'general': [
            {
                'topic': "Describe a person who has helped you",
                'points': [
                    "Who this person is",
                    "How you know them",
                    "How they helped you",
                    "And explain how you felt about their help"
                ]
            },
            {
                'topic': "Describe a place you like to visit",
                'points': [
                    "Where this place is",
                    "How often you go there",
                    "What you do there",
                    "And explain why you like this place"
                ]
            },
            {
                'topic': "Describe something you bought recently",
                'points': [
                    "What you bought",
                    "Where you bought it",
                    "Why you chose it",
                    "And explain how you feel about this purchase"
                ]
            }
        ]
    }
    
    PART_3_QUESTIONS = {
        'education_academic': [
            "How has education changed in your country over the past decade?",
            "What role should technology play in education?",
            "Do you think university education is necessary for everyone?",
            "How can we encourage more people to pursue higher education?",
            "What are the benefits and drawbacks of online learning?"
        ],
        'society_culture': [
            "How do you think social media has changed the way people communicate?",
            "What impact does globalization have on local cultures?",
            "How important is it to preserve traditional customs?",
            "What role should the government play in promoting culture?",
            "How do you see society changing in the next 20 years?"
        ],
        'environment': [
            "What are the most serious environmental problems facing the world today?",
            "How can individuals contribute to environmental protection?",
            "Do you think governments are doing enough to protect the environment?",
            "How has climate change affected your country?",
            "What role should businesses play in environmental conservation?"
        ],
        'technology': [
            "How has technology changed the way people work?",
            "What are the advantages and disadvantages of modern technology?",
            "Do you think people rely too much on technology today?",
            "How might technology develop in the future?",
            "What impact has the internet had on society?"
        ]
    }
    
    @classmethod
    def get_part1_questions(cls, topic_count=2):
        """Get Part 1 questions covering 2-3 topics"""
        selected_topics = random.sample(list(cls.PART_1_TOPICS.keys()), topic_count)
        questions = []
        
        for topic in selected_topics:
            topic_questions = cls.PART_1_TOPICS[topic]
            questions.extend(random.sample(topic_questions, min(3, len(topic_questions))))
        
        return questions
    
    @classmethod
    def get_part2_cue_card(cls, assessment_type='academic'):
        """Get a random Part 2 cue card"""
        cards = cls.PART_2_CUE_CARDS.get(assessment_type, cls.PART_2_CUE_CARDS['academic'])
        return random.choice(cards)
    
    @classmethod
    def get_part3_questions(cls, topic=None, count=5):
        """Get Part 3 follow-up questions"""
        if topic and topic in cls.PART_3_QUESTIONS:
            questions = cls.PART_3_QUESTIONS[topic]
        else:
            # Select random topic
            topic = random.choice(list(cls.PART_3_QUESTIONS.keys()))
            questions = cls.PART_3_QUESTIONS[topic]
        
        return random.sample(questions, min(count, len(questions)))
    
    @classmethod
    def build_examiner_script(cls, assessment_type, part):
        """Build complete examiner script with authentic questions"""
        
        if part == 1:
            questions = cls.get_part1_questions()
            script = """I'm Maya, your IELTS Speaking examiner. This is Part 1 of the speaking test.
            I'll ask you some questions about yourself and familiar topics. Let's begin.
            
            First, """ + questions[0]
            return script, questions[1:]  # Return opening + remaining questions
            
        elif part == 2:
            cue_card = cls.get_part2_cue_card(assessment_type)
            script = f"""Now we'll move to Part 2. I'm going to give you a topic and I'd like you to talk about it.
            You have one minute to think about what you're going to say, then speak for 1-2 minutes.
            
            Here's your topic: {cue_card['topic']}
            
            You should say:
            """ + "\n".join([f"• {point}" for point in cue_card['points']])
            
            return script, cue_card
            
        elif part == 3:
            questions = cls.get_part3_questions()
            script = """Now let's discuss some more general questions related to your Part 2 topic.
            These questions require more detailed answers with examples and explanations.
            
            """ + questions[0]
            return script, questions[1:]
        
        return "Let's begin the speaking assessment.", []