import boto3
import json
from datetime import datetime

# Assessment questions data
ASSESSMENT_QUESTIONS = {
    "academic-writing": [
        {
            "id": "aw_001",
            "task_type": "Task 2 - Essay",
            "prompt": "Some people believe that the internet has brought people closer together, while others argue it has made people more isolated. Discuss both views and give your own opinion.",
            "time_limit": 40,
            "word_count_min": 250
        },
        {
            "id": "aw_002", 
            "task_type": "Task 2 - Essay",
            "prompt": "Many countries are investing heavily in renewable energy sources. To what extent do you agree that this is the best way to address climate change?",
            "time_limit": 40,
            "word_count_min": 250
        },
        {
            "id": "aw_003",
            "task_type": "Task 2 - Essay", 
            "prompt": "University education should be free for all students. Do you agree or disagree with this statement?",
            "time_limit": 40,
            "word_count_min": 250
        },
        {
            "id": "aw_004",
            "task_type": "Task 1 - Graph Analysis",
            "prompt": "The chart below shows the percentage of households with internet access in five countries between 2000 and 2020. Summarize the information by selecting and reporting the main features.",
            "time_limit": 20,
            "word_count_min": 150
        }
    ],
    "academic-speaking": [
        {
            "id": "as_001",
            "parts": [
                {"part": 1, "topic": "Work and Career", "questions": ["What do you do for work?", "Do you enjoy your job?", "What are your career goals?"]},
                {"part": 2, "topic": "Describe a skill you would like to learn", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Skills and Learning", "questions": ["How important are practical skills?", "Should schools teach more life skills?"]}
            ]
        },
        {
            "id": "as_002",
            "parts": [
                {"part": 1, "topic": "Technology", "questions": ["How often do you use technology?", "What technology do you find most useful?", "Has technology changed your life?"]},
                {"part": 2, "topic": "Describe a piece of technology you find useful", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Technology and Society", "questions": ["How has technology changed communication?", "What are the negative effects of technology?"]}
            ]
        },
        {
            "id": "as_003",
            "parts": [
                {"part": 1, "topic": "Education", "questions": ["What subjects did you study?", "What was your favorite subject?", "How important is education?"]},
                {"part": 2, "topic": "Describe a teacher who influenced you", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Education Systems", "questions": ["How should teachers be trained?", "What makes a good education system?"]}
            ]
        },
        {
            "id": "as_004",
            "parts": [
                {"part": 1, "topic": "Travel", "questions": ["Do you like to travel?", "Where have you traveled?", "What do you like about traveling?"]},
                {"part": 2, "topic": "Describe a memorable journey you took", "prep_time": 60, "talk_time": 120}, 
                {"part": 3, "topic": "Tourism and Culture", "questions": ["How does tourism affect local culture?", "Should there be limits on tourism?"]}
            ]
        }
    ],
    "general-writing": [
        {
            "id": "gw_001",
            "task_type": "Task 1 - Letter",
            "prompt": "You recently bought a product online but it arrived damaged. Write a letter to the company. In your letter: explain what you bought, describe the damage, say what action you want the company to take.",
            "time_limit": 20,
            "word_count_min": 150,
            "letter_type": "Complaint"
        },
        {
            "id": "gw_002",
            "task_type": "Task 2 - Essay", 
            "prompt": "Some people think that parents should teach children how to be good members of society. Others believe that school is the best place to learn this. Discuss both views and give your opinion.",
            "time_limit": 40,
            "word_count_min": 250
        },
        {
            "id": "gw_003",
            "task_type": "Task 1 - Letter",
            "prompt": "You are planning a holiday abroad and need accommodation. Write a letter to a hotel. In your letter: introduce yourself, explain what type of accommodation you need, ask about availability and prices.",
            "time_limit": 20, 
            "word_count_min": 150,
            "letter_type": "Inquiry"
        },
        {
            "id": "gw_004",
            "task_type": "Task 2 - Essay",
            "prompt": "Many people believe that social media platforms should be regulated by governments. To what extent do you agree or disagree?",
            "time_limit": 40,
            "word_count_min": 250
        }
    ],
    "general-speaking": [
        {
            "id": "gs_001", 
            "parts": [
                {"part": 1, "topic": "Home and Family", "questions": ["Where do you live?", "Who do you live with?", "Describe your home."]},
                {"part": 2, "topic": "Describe a family celebration you enjoyed", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Family and Traditions", "questions": ["How important are family traditions?", "How have families changed over time?"]}
            ]
        },
        {
            "id": "gs_002",
            "parts": [
                {"part": 1, "topic": "Free Time", "questions": ["What do you do in your free time?", "Do you prefer indoor or outdoor activities?", "How do you relax?"]},
                {"part": 2, "topic": "Describe a hobby you enjoy", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Leisure and Recreation", "questions": ["How important is leisure time?", "How do people choose their hobbies?"]}
            ]
        },
        {
            "id": "gs_003",
            "parts": [
                {"part": 1, "topic": "Shopping", "questions": ["Do you like shopping?", "Where do you usually shop?", "How often do you go shopping?"]},
                {"part": 2, "topic": "Describe a shop you like to visit", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Consumer Culture", "questions": ["How has shopping changed?", "Do people buy too many things nowadays?"]}
            ]
        },
        {
            "id": "gs_004",
            "parts": [
                {"part": 1, "topic": "Food", "questions": ["What is your favorite food?", "Do you cook at home?", "What food is popular in your country?"]},
                {"part": 2, "topic": "Describe a meal you enjoyed", "prep_time": 60, "talk_time": 120},
                {"part": 3, "topic": "Food and Culture", "questions": ["How important is food in your culture?", "How have eating habits changed?"]}
            ]
        }
    ]
}

def create_questions_table():
    """Create DynamoDB table for assessment questions"""
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        # Create table
        table_config = {
            'TableName': 'ielts-assessment-questions',
            'KeySchema': [
                {'AttributeName': 'assessment_type', 'KeyType': 'HASH'},
                {'AttributeName': 'question_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'assessment_type', 'AttributeType': 'S'},
                {'AttributeName': 'question_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'Tags': [
                {'Key': 'Project', 'Value': 'IELTS-GenAI-Prep'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        }
        
        response = dynamodb.create_table(**table_config)
        print(f"✅ Created DynamoDB table: ielts-assessment-questions")
        print(f"   Table ARN: {response['TableDescription']['TableArn']}")
        
        # Wait for table to be active
        waiter = dynamodb.get_waiter('table_exists')
        print("   Waiting for table to become active...")
        waiter.wait(TableName='ielts-assessment-questions')
        print("   ✅ Table is now active")
        
        return True
        
    except dynamodb.exceptions.ResourceInUseException:
        print("✅ Table 'ielts-assessment-questions' already exists")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        return False

def populate_questions_table():
    """Populate DynamoDB table with assessment questions"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        questions_inserted = 0
        
        for assessment_type, questions in ASSESSMENT_QUESTIONS.items():
            for question in questions:
                # Prepare item for DynamoDB
                item = {
                    'assessment_type': assessment_type,
                    'question_id': question['id'],
                    'question_data': question,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'active': True
                }
                
                # Insert into DynamoDB
                table.put_item(Item=item)
                questions_inserted += 1
                print(f"   ✅ Inserted {question['id']} ({assessment_type})")
        
        print(f"✅ Successfully inserted {questions_inserted} questions into DynamoDB")
        return True
        
    except Exception as e:
        print(f"❌ Error populating questions: {str(e)}")
        return False

def verify_questions_data():
    """Verify questions are properly stored in DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        print("\n🔍 VERIFYING QUESTIONS IN DYNAMODB:")
        print("=" * 50)
        
        for assessment_type in ASSESSMENT_QUESTIONS.keys():
            response = table.query(
                KeyConditionExpression='assessment_type = :type',
                ExpressionAttributeValues={':type': assessment_type}
            )
            
            questions_count = len(response['Items'])
            print(f"✅ {assessment_type}: {questions_count} questions stored")
            
            # Show sample question
            if response['Items']:
                sample = response['Items'][0]
                print(f"   Sample: {sample['question_id']} - {sample['question_data'].get('task_type', 'Speaking')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying questions: {str(e)}")
        return False

def generate_updated_lambda_code():
    """Generate Lambda code that reads questions from DynamoDB"""
    
    lambda_code_snippet = '''
# DynamoDB Question Management Functions
def get_questions_from_dynamodb(assessment_type: str) -> List[Dict[str, Any]]:
    """Retrieve questions from DynamoDB for specific assessment type"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        response = table.query(
            KeyConditionExpression='assessment_type = :type',
            FilterExpression='active = :active',
            ExpressionAttributeValues={
                ':type': assessment_type,
                ':active': True
            }
        )
        
        questions = []
        for item in response['Items']:
            questions.append(item['question_data'])
        
        print(f"Retrieved {len(questions)} questions for {assessment_type}")
        return questions
        
    except Exception as e:
        print(f"DynamoDB error retrieving questions: {str(e)}")
        # Fallback to empty list - could also implement local cache
        return []

def get_unique_assessment_question(user_email: str, assessment_type: str) -> Optional[Dict[str, Any]]:
    """Get a unique question from DynamoDB that the user hasn't seen before"""
    if user_email not in user_assessments:
        user_assessments[user_email] = {}
    
    if assessment_type not in user_assessments[user_email]:
        user_assessments[user_email][assessment_type] = []
    
    # Get questions from DynamoDB
    all_questions = get_questions_from_dynamodb(assessment_type)
    
    if not all_questions:
        print(f"No questions found in DynamoDB for {assessment_type}")
        return None
    
    completed_questions = user_assessments[user_email][assessment_type]
    available_questions = [q for q in all_questions if q["id"] not in completed_questions]
    
    if available_questions:
        return random.choice(available_questions)
    else:
        # All questions used - reset or provide variation
        print(f"All questions used for {assessment_type}, resetting for {user_email}")
        user_assessments[user_email][assessment_type] = []
        return random.choice(all_questions)

def add_new_question_to_dynamodb(assessment_type: str, question_data: Dict[str, Any]) -> bool:
    """Add new question to DynamoDB (for future content management)"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        item = {
            'assessment_type': assessment_type,
            'question_id': question_data['id'],
            'question_data': question_data,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'active': True
        }
        
        table.put_item(Item=item)
        print(f"Added new question {question_data['id']} to {assessment_type}")
        return True
        
    except Exception as e:
        print(f"Error adding question to DynamoDB: {str(e)}")
        return False
'''
    
    print("\n📋 UPDATED LAMBDA CODE FUNCTIONS:")
    print("=" * 50)
    print("✅ get_questions_from_dynamodb() - Retrieves questions from DynamoDB")
    print("✅ get_unique_assessment_question() - Modified to use DynamoDB")
    print("✅ add_new_question_to_dynamodb() - Allows adding new questions")
    print("\n💡 Benefits of DynamoDB storage:")
    print("   • Easy to add new questions without code deployment")
    print("   • Better scalability for large question banks")
    print("   • Can implement question analytics and usage tracking")
    print("   • Supports question versioning and A/B testing")
    
    return lambda_code_snippet

if __name__ == "__main__":
    print("🚀 MIGRATING ASSESSMENT QUESTIONS TO DYNAMODB")
    print("=" * 60)
    
    # Step 1: Create DynamoDB table
    if create_questions_table():
        # Step 2: Populate with questions
        if populate_questions_table():
            # Step 3: Verify data
            if verify_questions_data():
                # Step 4: Generate updated Lambda code
                updated_code = generate_updated_lambda_code()
                print("\n✅ MIGRATION COMPLETE!")
                print("   Questions are now stored in DynamoDB table: ielts-assessment-questions")
                print("   Next step: Update Lambda function to use DynamoDB instead of hardcoded questions")
            else:
                print("❌ Verification failed")
        else:
            print("❌ Population failed")
    else:
        print("❌ Table creation failed")
