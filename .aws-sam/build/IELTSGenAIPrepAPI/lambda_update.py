
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
