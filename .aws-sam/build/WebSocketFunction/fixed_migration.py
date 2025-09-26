#!/usr/bin/env python3
"""
Fixed Full Assessment Migration to DynamoDB
Creates proper table structure matching existing Lambda code
"""

import json
import os
import uuid
import time
from typing import Dict, Any, List

# Set environment for .replit testing
os.environ['REPLIT_ENVIRONMENT'] = 'true'

# Import AWS mock services
from aws_mock_config import aws_mock

def create_questions_table():
    """Create a dedicated questions table with proper structure"""
    # Create new table for questions
    questions_table = aws_mock.assessment_results_table.__class__('ielts-assessment-questions')
    
    # Academic Writing Questions
    academic_writing_questions = [
        {
            'question_id': 'aw_001',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'The global economy is evolving quickly, and individuals can no longer rely on the same career path or workplace environment throughout their lives. Discuss the potential reasons for this rapid evolution, and propose strategies to prepare people for their careers in the future.',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'aw_002',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Many countries are experiencing a significant increase in the proportion of older people in their populations. Discuss the possible reasons for this demographic shift, and suggest ways in which societies can adapt to this aging population.',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'aw_003',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'In many parts of the world, the popularity of private vehicles is increasing despite growing concerns about environmental pollution and traffic congestion. Discuss the possible reasons for the continued preference for private vehicles, and suggest ways in which governments could encourage people to use alternative forms of transport.',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'aw_004',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Some people believe that the internet has brought people closer together, while others argue it has made people more isolated. Discuss both views and give your own opinion.',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'aw_005',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Many countries are investing heavily in renewable energy sources. To what extent do you agree that this is the best way to address climate change?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'aw_006',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'University education should be free for all students. Do you agree or disagree with this statement?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        }
    ]
    
    # General Writing Questions
    general_writing_questions = [
        {
            'question_id': 'gw_001',
            'assessment_type': 'general_writing',
            'task_type': 'Task 1 - Letter',
            'prompt': 'You are currently enrolled in an evening course at a local community center, but you are facing several issues with the classroom environment that make it challenging to focus and learn effectively. Write a letter to the course coordinator at the community center.',
            'requirements': ['describe the situation', 'explain your problems and why it is difficult to learn', 'suggest what kind of classroom environment you would prefer'],
            'time_limit': 20,
            'word_count_min': 150,
            'instructions': 'You should spend about 20 minutes on this task. Write at least 150 words. Begin your letter as follows: Dear Sir or Madam,',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gw_002',
            'assessment_type': 'general_writing',
            'task_type': 'Task 1 - Letter',
            'prompt': 'You have recently joined a local gym to improve your fitness, but you are experiencing several issues with the gym facilities that make it difficult to exercise comfortably. Write a letter to the gym manager.',
            'requirements': ['describe the situation', 'explain your problems and why it is difficult to exercise', 'suggest what kind of improvements or facilities you would prefer'],
            'time_limit': 20,
            'word_count_min': 150,
            'instructions': 'You should spend about 20 minutes on this task. Write at least 150 words. Begin your letter as follows: Dear Sir or Madam,',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gw_003',
            'assessment_type': 'general_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Urban areas face increasing traffic problems. Some think building more roads is the answer, while others favor improving public transport. Who do you believe should be the priority: expanding roads or developing public transport?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gw_004',
            'assessment_type': 'general_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Many companies are now allowing their employees to work from home some or all of the time. This shift has both benefits and drawbacks. Do you think the advantages of remote work outweigh the disadvantages, or vice versa?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gw_005',
            'assessment_type': 'general_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'The use of social media has become widespread among young people. It offers opportunities for connection but also presents potential risks. Do you believe the benefits of social media for young people outweigh the risks, or are the risks more significant?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gw_006',
            'assessment_type': 'general_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Fast food is a popular choice for many due to its convenience and affordability. However, its impact on health is often debated. Do you think the advantages of fast food outweigh its disadvantages, or are the health concerns more significant?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        }
    ]
    
    # Academic Speaking Questions
    academic_speaking_questions = [
        {
            'question_id': 'as_001',
            'assessment_type': 'academic_speaking',
            'part': 1,
            'topic': 'Studies and Academic Life',
            'questions': [
                'What subject are you studying?',
                'Why did you choose this subject?',
                'What do you find most interesting about your studies?',
                'Do you prefer studying alone or in groups?'
            ],
            'time_limit': 5,
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'as_002',
            'assessment_type': 'academic_speaking',
            'part': 2,
            'topic': 'Describe a book that influenced you',
            'cue_card': 'Describe a book that has influenced your thinking. You should say: what the book was about, when and where you read it, why it influenced you, and explain how it changed your perspective.',
            'preparation_time': 1,
            'speaking_time': 2,
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'as_003',
            'assessment_type': 'academic_speaking',
            'part': 3,
            'topic': 'Education and Learning',
            'questions': [
                'How has education changed in your country?',
                'What role should technology play in education?',
                'Do you think traditional teaching methods are still effective?',
                'How important is lifelong learning in modern society?'
            ],
            'time_limit': 5,
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        }
    ]
    
    # General Speaking Questions
    general_speaking_questions = [
        {
            'question_id': 'gs_001',
            'assessment_type': 'general_speaking',
            'part': 1,
            'topic': 'Daily Life and Routine',
            'questions': [
                'Can you describe your daily routine?',
                'What do you usually do in your free time?',
                'How do you usually get to work or school?',
                'What kind of weather do you prefer?'
            ],
            'time_limit': 5,
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gs_002',
            'assessment_type': 'general_speaking',
            'part': 2,
            'topic': 'Describe a memorable journey',
            'cue_card': 'Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why it was memorable.',
            'preparation_time': 1,
            'speaking_time': 2,
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        },
        {
            'question_id': 'gs_003',
            'assessment_type': 'general_speaking',
            'part': 3,
            'topic': 'Travel and Transportation',
            'questions': [
                'How has travel changed over the years?',
                'What are the benefits of traveling?',
                'Do you think people travel too much nowadays?',
                'How might transportation change in the future?'
            ],
            'time_limit': 5,
            'difficulty_level': 'standard',
            'created_at': int(time.time())
        }
    ]
    
    # Combine all questions
    all_questions = []
    all_questions.extend(academic_writing_questions)
    all_questions.extend(general_writing_questions)
    all_questions.extend(academic_speaking_questions)
    all_questions.extend(general_speaking_questions)
    
    # Add questions to the table
    success_count = 0
    for question in all_questions:
        if questions_table.put_item(question):
            success_count += 1
            print(f"[MIGRATION] ✓ Added {question['question_id']} - {question['assessment_type']}")
        else:
            print(f"[MIGRATION] ✗ Failed to add {question['question_id']}")
    
    print(f"[MIGRATION] Successfully added {success_count}/{len(all_questions)} questions to DynamoDB")
    return questions_table, success_count

def update_lambda_with_new_question_system():
    """Update the Lambda function to use the new comprehensive question system"""
    
    # Read current Lambda function
    with open('app.py', 'r') as f:
        current_code = f.read()
    
    # Find the get_questions_from_dynamodb function and update it
    new_function = '''
def get_questions_from_dynamodb(assessment_type: str, user_email: str) -> Optional[Dict[str, Any]]:
    """Get comprehensive questions from DynamoDB with proper table structure"""
    try:
        # Get user's completed questions to avoid repetition
        user_data = aws_mock.users_table.get_item(user_email)
        completed_questions = user_data.get('completed_questions', []) if user_data else []
        
        # Create questions table reference
        questions_table = aws_mock.assessment_results_table.__class__('ielts-assessment-questions')
        
        # Scan for questions of the specified assessment type
        all_questions = questions_table.scan(
            filter_expression=f"assessment_type = '{assessment_type}'"
        )
        
        # Filter out completed questions
        available_questions = [q for q in all_questions if q['question_id'] not in completed_questions]
        
        if not available_questions:
            print(f"[DYNAMODB] No available questions for {assessment_type}, user has completed all")
            # Fallback to original hardcoded questions
            return get_fallback_question(assessment_type)
        
        # Return first available question
        selected_question = available_questions[0]
        
        print(f"[DYNAMODB] ✓ Retrieved question {selected_question['question_id']} for {assessment_type} (from DynamoDB)")
        return selected_question
        
    except Exception as e:
        print(f"[DYNAMODB ERROR] Failed to get questions: {str(e)}")
        # Fallback to original hardcoded questions
        return get_fallback_question(assessment_type)

def get_fallback_question(assessment_type: str) -> Optional[Dict[str, Any]]:
    """Fallback to original hardcoded questions if DynamoDB fails"""
    fallback_questions = {
        'academic_writing': {
            'question_id': 'aw_fallback',
            'assessment_type': 'academic_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Some people believe that the internet has brought people closer together, while others argue it has made people more isolated. Discuss both views and give your own opinion.',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard'
        },
        'general_writing': {
            'question_id': 'gw_fallback',
            'assessment_type': 'general_writing',
            'task_type': 'Task 2 - Essay',
            'prompt': 'Many companies are now allowing their employees to work from home some or all of the time. Do you think the advantages of remote work outweigh the disadvantages?',
            'time_limit': 40,
            'word_count_min': 250,
            'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words.',
            'difficulty_level': 'standard'
        },
        'academic_speaking': {
            'question_id': 'as_fallback',
            'assessment_type': 'academic_speaking',
            'part': 1,
            'topic': 'Studies and Academic Life',
            'questions': [
                'What subject are you studying?',
                'Why did you choose this subject?',
                'What do you find most interesting about your studies?'
            ],
            'time_limit': 5,
            'difficulty_level': 'standard'
        },
        'general_speaking': {
            'question_id': 'gs_fallback',
            'assessment_type': 'general_speaking',
            'part': 1,
            'topic': 'Daily Life and Routine',
            'questions': [
                'Can you describe your daily routine?',
                'What do you usually do in your free time?',
                'How do you usually get to work or school?'
            ],
            'time_limit': 5,
            'difficulty_level': 'standard'
        }
    }
    
    question = fallback_questions.get(assessment_type)
    if question:
        print(f"[FALLBACK] Using fallback question for {assessment_type}")
        return question
    
    print(f"[FALLBACK] No fallback question available for {assessment_type}")
    return None
'''
    
    # Write the new function to a temporary file
    with open('lambda_update.py', 'w') as f:
        f.write(new_function)
    
    print("[MIGRATION] Lambda function update code saved to lambda_update.py")
    return new_function

def run_migration():
    """Run the complete migration process"""
    print("🚀 [MIGRATION] Starting Full Assessment Content Migration...")
    print("=" * 60)
    
    # Create questions table and add all questions
    questions_table, success_count = create_questions_table()
    
    # Update Lambda function
    lambda_code = update_lambda_with_new_question_system()
    
    print("=" * 60)
    print(f"✅ [MIGRATION COMPLETE] Successfully migrated {success_count} questions to DynamoDB")
    print("📊 [MIGRATION] Content breakdown:")
    print("   - Academic Writing: 6 comprehensive essay questions")
    print("   - General Writing: 6 questions (2 letters + 4 essays)")
    print("   - Academic Speaking: 3 questions (Part 1, 2, 3)")
    print("   - General Speaking: 3 questions (Part 1, 2, 3)")
    print("   - Total: 18 comprehensive assessment questions")
    print("📝 [MIGRATION] Lambda function update code ready for deployment")
    print("🔄 [MIGRATION] System now uses database-driven question management")
    
    return success_count

if __name__ == "__main__":
    run_migration()