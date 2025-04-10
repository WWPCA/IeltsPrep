"""
Pronunciation Coach Module
This module provides functionality for the pronunciation coach feature
without requiring AWS services.
"""

import json
import random
import os

def generate_pronunciation_exercises(difficulty='medium', category='general'):
    """
    Generate pronunciation exercises based on difficulty and category.
    
    Args:
        difficulty (str): 'easy', 'medium', or 'hard'
        category (str): Category of words to practice
        
    Returns:
        list: A list of pronunciation exercise items
    """
    # Static datasets of exercises based on difficulty and category
    exercises = {
        'easy': {
            'general': [
                {'text': 'Hello, how are you today?', 'focus': 'Basic greeting'},
                {'text': 'My name is David. Nice to meet you.', 'focus': 'Self-introduction'},
                {'text': 'I live in New York City.', 'focus': 'Simple statement'},
                {'text': 'Today is Monday, October fifth.', 'focus': 'Date pronunciation'},
                {'text': 'I enjoy watching movies and reading books.', 'focus': 'Hobbies'}
            ],
            'academic': [
                {'text': 'The professor explained the concept clearly.', 'focus': 'Academic vocabulary'},
                {'text': 'Students must submit their assignments on time.', 'focus': 'Academic rules'},
                {'text': 'The library is open until nine p.m.', 'focus': 'Time and places'},
                {'text': 'Please take notes during the lecture.', 'focus': 'Academic instructions'},
                {'text': 'The research paper is due next week.', 'focus': 'Academic deadlines'}
            ],
            'business': [
                {'text': 'We have a meeting at ten o\'clock.', 'focus': 'Business scheduling'},
                {'text': 'Please email me the report by Friday.', 'focus': 'Business requests'},
                {'text': 'Our company has offices in five countries.', 'focus': 'Company information'},
                {'text': 'The presentation went very well.', 'focus': 'Business evaluation'},
                {'text': 'I need to make a phone call to a client.', 'focus': 'Business communication'}
            ]
        },
        'medium': {
            'general': [
                {'text': 'The weather is quite unpredictable this time of year.', 'focus': 'Weather vocabulary'},
                {'text': 'I\'ve been learning English for approximately three years.', 'focus': 'Time expressions'},
                {'text': 'The restaurant we visited yesterday was extraordinary.', 'focus': 'Adjectives and adverbs'},
                {'text': 'Could you recommend a good place to visit in this city?', 'focus': 'Questions and recommendations'},
                {'text': 'Public transportation is very efficient in this area.', 'focus': 'Urban vocabulary'}
            ],
            'academic': [
                {'text': 'Statistical analysis reveals significant correlations between the variables.', 'focus': 'Academic terminology'},
                {'text': 'The methodology section describes the experimental procedure in detail.', 'focus': 'Research vocabulary'},
                {'text': 'Environmental factors contribute substantially to biodiversity loss.', 'focus': 'Scientific terminology'},
                {'text': 'The literature review synthesizes previous research on this topic.', 'focus': 'Academic writing terminology'},
                {'text': 'Students are required to participate in group discussions.', 'focus': 'Academic requirements'}
            ],
            'business': [
                {'text': 'Our quarterly financial report shows a twenty percent increase in revenue.', 'focus': 'Business reporting'},
                {'text': 'We need to analyze customer feedback to improve our services.', 'focus': 'Business analysis'},
                {'text': 'The project deadline has been extended to the end of the month.', 'focus': 'Project management'},
                {'text': 'Please schedule a meeting with the marketing department.', 'focus': 'Business coordination'},
                {'text': 'We should consider alternative strategies for market penetration.', 'focus': 'Business strategy'}
            ]
        },
        'hard': {
            'general': [
                {'text': 'Despite the inclement weather, the outdoor event was extraordinarily successful.', 'focus': 'Complex vocabulary and sentence structure'},
                {'text': 'The architectural magnificence of the cathedral left the tourists awestruck.', 'focus': 'Difficult pronunciation clusters'},
                {'text': 'The government announced unprecedented measures to stimulate economic growth.', 'focus': 'Political and economic vocabulary'},
                {'text': 'She meticulously organized her schedule to accommodate all her responsibilities.', 'focus': 'Adverbs and syllable stress'},
                {'text': 'The philanthropist anonymously donated substantial funds to various charitable organizations.', 'focus': 'Long multi-syllable words'}
            ],
            'academic': [
                {'text': 'The interdisciplinary research synthesizes methodologies from cognitive psychology and neurophysiology.', 'focus': 'Academic jargon'},
                {'text': 'The dissertation examines the socioeconomic implications of technological determinism in developing nations.', 'focus': 'Academic terminology'},
                {'text': 'Preliminary experimental results indicate a statistically significant correlation between the variables.', 'focus': 'Scientific reporting'},
                {'text': 'The epistemological foundations of qualitative research methodologies remain controversial.', 'focus': 'Philosophy of science vocabulary'},
                {'text': 'Researchers must acknowledge the inherent limitations of their methodological approach.', 'focus': 'Research ethics and considerations'}
            ],
            'business': [
                {'text': 'The conglomerate\'s acquisition strategy has resulted in unprecedented market capitalization growth.', 'focus': 'Business finance terminology'},
                {'text': 'Stakeholders expressed concern regarding the sustainability of the company\'s supply chain practices.', 'focus': 'Business ethics vocabulary'},
                {'text': 'The implementation of artificial intelligence solutions has revolutionized our operational efficiency.', 'focus': 'Technology business vocabulary'},
                {'text': 'Quarterly fluctuations notwithstanding, the annual revenue projections remain optimistic.', 'focus': 'Complex business expressions'},
                {'text': 'The strategic partnership aims to leverage synergies and establish competitive differentiation.', 'focus': 'Business strategy jargon'}
            ]
        }
    }
    
    # Get exercises for the requested difficulty and category
    if difficulty in exercises and category in exercises[difficulty]:
        return exercises[difficulty][category]
    else:
        # Default to medium/general if the requested combination doesn't exist
        return exercises['medium']['general']


def analyze_pronunciation(transcription, reference_text):
    """
    Analyze pronunciation by comparing transcribed speech to reference text
    without using AWS services.
    
    Args:
        transcription (str): Transcribed text from the user's speech
        reference_text (str): The reference text the user was trying to pronounce
        
    Returns:
        dict: Pronunciation analysis results
    """
    # Helper function to clean text
    def clean_text(text):
        return ''.join(c for c in text.lower() if c.isalnum() or c.isspace()).strip()
    
    # Clean both texts for comparison
    clean_reference = clean_text(reference_text)
    clean_transcription = clean_text(transcription)
    
    # Split into words
    reference_words = clean_reference.split()
    transcription_words = clean_transcription.split()
    
    # Count matching words
    matching_words = 0
    for word in transcription_words:
        if word in reference_words:
            matching_words += 1
    
    # Calculate basic metrics
    total_reference_words = len(reference_words)
    total_transcription_words = len(transcription_words)
    
    # Calculate accuracy percentage
    if total_reference_words > 0:
        accuracy = (matching_words / total_reference_words) * 100
    else:
        accuracy = 0
    
    # Determine IELTS-like score (0-9 scale)
    if accuracy >= 95:
        score = 9
    elif accuracy >= 90:
        score = 8
    elif accuracy >= 80:
        score = 7
    elif accuracy >= 70:
        score = 6
    elif accuracy >= 60:
        score = 5
    elif accuracy >= 50:
        score = 4
    elif accuracy >= 40:
        score = 3
    elif accuracy >= 30:
        score = 2
    elif accuracy > 0:
        score = 1
    else:
        score = 0
    
    # Generate feedback
    feedback_templates = [
        "Good pronunciation! Your speech was clear and accurate.",
        "Your pronunciation was mostly clear. Try to emphasize stressed syllables more.",
        "Work on the pronunciation of longer words. Breaking them into syllables can help.",
        "Practice the rhythm of English sentences. Try listening and repeating after native speakers.",
        "Focus on vowel sounds, which are important for clear English pronunciation.",
        "Work on linking words together smoothly in connected speech.",
        "Try slowing down your speech to improve clarity and accuracy."
    ]
    
    if score >= 7:
        feedback = random.choice(feedback_templates[:2])
    elif score >= 5:
        feedback = random.choice(feedback_templates[2:4])
    else:
        feedback = random.choice(feedback_templates[4:])
    
    # Return the analysis results
    return {
        'accuracy': accuracy,
        'score': score,
        'matching_words': matching_words,
        'total_words': total_reference_words,
        'feedback': feedback
    }


def mock_transcribe_audio(audio_path):
    """
    Mock function to simulate transcription when AWS services aren't available.
    In a real implementation, this would use speech-to-text services.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: Simulated transcription text
    """
    # Extract the filename without extension
    filename = os.path.basename(audio_path)
    base_name = os.path.splitext(filename)[0]
    
    # Generate a simplified "transcription" based on the file name
    # In a real implementation, this would use actual speech-to-text
    return "This is a simulated transcription for testing purposes. In a real application, this would contain the actual words spoken by the user."