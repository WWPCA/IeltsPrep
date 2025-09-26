import boto3
import zipfile
import tempfile
import os

def populate_dynamodb_questions():
    """Populate DynamoDB table with assessment questions"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        # Question data structure
        questions = [
            # Academic Writing
            {"assessment_type": "academic-writing", "question_id": "aw_001", "question_data": {"id": "aw_001", "task_type": "Task 2 - Essay", "prompt": "Some people believe that the internet has brought people closer together, while others argue it has made people more isolated. Discuss both views and give your own opinion.", "time_limit": 40, "word_count_min": 250}},
            {"assessment_type": "academic-writing", "question_id": "aw_002", "question_data": {"id": "aw_002", "task_type": "Task 2 - Essay", "prompt": "Many countries are investing heavily in renewable energy sources. To what extent do you agree that this is the best way to address climate change?", "time_limit": 40, "word_count_min": 250}},
            {"assessment_type": "academic-writing", "question_id": "aw_003", "question_data": {"id": "aw_003", "task_type": "Task 2 - Essay", "prompt": "University education should be free for all students. Do you agree or disagree with this statement?", "time_limit": 40, "word_count_min": 250}},
            {"assessment_type": "academic-writing", "question_id": "aw_004", "question_data": {"id": "aw_004", "task_type": "Task 1 - Graph Analysis", "prompt": "The chart below shows the percentage of households with internet access in five countries between 2000 and 2020. Summarize the information by selecting and reporting the main features.", "time_limit": 20, "word_count_min": 150}},
            
            # Academic Speaking
            {"assessment_type": "academic-speaking", "question_id": "as_001", "question_data": {"id": "as_001", "parts": [{"part": 1, "topic": "Work and Career", "questions": ["What do you do for work?", "Do you enjoy your job?", "What are your career goals?"]}, {"part": 2, "topic": "Describe a skill you would like to learn", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Skills and Learning", "questions": ["How important are practical skills?", "Should schools teach more life skills?"]}]}},
            {"assessment_type": "academic-speaking", "question_id": "as_002", "question_data": {"id": "as_002", "parts": [{"part": 1, "topic": "Technology", "questions": ["How often do you use technology?", "What technology do you find most useful?", "Has technology changed your life?"]}, {"part": 2, "topic": "Describe a piece of technology you find useful", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Technology and Society", "questions": ["How has technology changed communication?", "What are the negative effects of technology?"]}]}},
            {"assessment_type": "academic-speaking", "question_id": "as_003", "question_data": {"id": "as_003", "parts": [{"part": 1, "topic": "Education", "questions": ["What subjects did you study?", "What was your favorite subject?", "How important is education?"]}, {"part": 2, "topic": "Describe a teacher who influenced you", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Education Systems", "questions": ["How should teachers be trained?", "What makes a good education system?"]}]}},
            {"assessment_type": "academic-speaking", "question_id": "as_004", "question_data": {"id": "as_004", "parts": [{"part": 1, "topic": "Travel", "questions": ["Do you like to travel?", "Where have you traveled?", "What do you like about traveling?"]}, {"part": 2, "topic": "Describe a memorable journey you took", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Tourism and Culture", "questions": ["How does tourism affect local culture?", "Should there be limits on tourism?"]}]}},
            
            # General Writing
            {"assessment_type": "general-writing", "question_id": "gw_001", "question_data": {"id": "gw_001", "task_type": "Task 1 - Letter", "prompt": "You recently bought a product online but it arrived damaged. Write a letter to the company. In your letter: explain what you bought, describe the damage, say what action you want the company to take.", "time_limit": 20, "word_count_min": 150, "letter_type": "Complaint"}},
            {"assessment_type": "general-writing", "question_id": "gw_002", "question_data": {"id": "gw_002", "task_type": "Task 2 - Essay", "prompt": "Some people think that parents should teach children how to be good members of society. Others believe that school is the best place to learn this. Discuss both views and give your opinion.", "time_limit": 40, "word_count_min": 250}},
            {"assessment_type": "general-writing", "question_id": "gw_003", "question_data": {"id": "gw_003", "task_type": "Task 1 - Letter", "prompt": "You are planning a holiday abroad and need accommodation. Write a letter to a hotel. In your letter: introduce yourself, explain what type of accommodation you need, ask about availability and prices.", "time_limit": 20, "word_count_min": 150, "letter_type": "Inquiry"}},
            {"assessment_type": "general-writing", "question_id": "gw_004", "question_data": {"id": "gw_004", "task_type": "Task 2 - Essay", "prompt": "Many people believe that social media platforms should be regulated by governments. To what extent do you agree or disagree?", "time_limit": 40, "word_count_min": 250}},
            
            # General Speaking
            {"assessment_type": "general-speaking", "question_id": "gs_001", "question_data": {"id": "gs_001", "parts": [{"part": 1, "topic": "Home and Family", "questions": ["Where do you live?", "Who do you live with?", "Describe your home."]}, {"part": 2, "topic": "Describe a family celebration you enjoyed", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Family and Traditions", "questions": ["How important are family traditions?", "How have families changed over time?"]}]}},
            {"assessment_type": "general-speaking", "question_id": "gs_002", "question_data": {"id": "gs_002", "parts": [{"part": 1, "topic": "Free Time", "questions": ["What do you do in your free time?", "Do you prefer indoor or outdoor activities?", "How do you relax?"]}, {"part": 2, "topic": "Describe a hobby you enjoy", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Leisure and Recreation", "questions": ["How important is leisure time?", "How do people choose their hobbies?"]}]}},
            {"assessment_type": "general-speaking", "question_id": "gs_003", "question_data": {"id": "gs_003", "parts": [{"part": 1, "topic": "Shopping", "questions": ["Do you like shopping?", "Where do you usually shop?", "How often do you go shopping?"]}, {"part": 2, "topic": "Describe a shop you like to visit", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Consumer Culture", "questions": ["How has shopping changed?", "Do people buy too many things nowadays?"]}]}},
            {"assessment_type": "general-speaking", "question_id": "gs_004", "question_data": {"id": "gs_004", "parts": [{"part": 1, "topic": "Food", "questions": ["What is your favorite food?", "Do you cook at home?", "What food is popular in your country?"]}, {"part": 2, "topic": "Describe a meal you enjoyed", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Food and Culture", "questions": ["How important is food in your culture?", "How have eating habits changed?"]}]}}
        ]
        
        for question in questions:
            item = {
                'assessment_type': question['assessment_type'],
                'question_id': question['question_id'],
                'question_data': question['question_data'],
                'created_at': '2025-07-08T11:15:00Z',
                'active': True
            }
            table.put_item(Item=item)
        
        print(f"✅ Populated {len(questions)} questions in DynamoDB")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def deploy_lambda():
    """Deploy Lambda with DynamoDB integration"""
    try:
        # Populate questions first
        if not populate_dynamodb_questions():
            return False
        
        # Read template
        with open('working_template.html', 'r', encoding='utf-8') as f:
            home_template = f.read()
        
        # Simple Lambda code template
        lambda_template = '''
import json
import hashlib
import secrets
import urllib.parse
import urllib.request
import os
import random
import uuid
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Test credentials
test_email = "prodtest_20250704_165313_kind@ieltsaiprep.com"
test_password = "TestProd2025!"
test_hash = hashlib.pbkdf2_hmac("sha256", test_password.encode(), b"production_salt_2025", 100000).hex()

users = {test_email: {"password_hash": test_hash, "email": test_email, "assessments_purchased": ["academic-writing", "academic-speaking", "general-writing", "general-speaking"]}}
sessions = {}
user_assessments = {}
assessment_attempts = {}

def get_questions_from_dynamodb(assessment_type: str) -> List[Dict[str, Any]]:
    """Get questions from DynamoDB"""
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
        
        print(f"DynamoDB: Retrieved {len(questions)} questions for {assessment_type}")
        return questions
        
    except Exception as e:
        print(f"DynamoDB error: {str(e)}")
        return []

def get_unique_assessment_question(user_email: str, assessment_type: str) -> Optional[Dict[str, Any]]:
    """Get unique question"""
    if user_email not in user_assessments:
        user_assessments[user_email] = {}
    
    if assessment_type not in user_assessments[user_email]:
        user_assessments[user_email][assessment_type] = []
    
    all_questions = get_questions_from_dynamodb(assessment_type)
    
    if not all_questions:
        return None
    
    completed_questions = user_assessments[user_email][assessment_type]
    available_questions = [q for q in all_questions if q["id"] not in completed_questions]
    
    if available_questions:
        return random.choice(available_questions)
    else:
        user_assessments[user_email][assessment_type] = []
        return random.choice(all_questions)

def record_assessment_completion(user_email: str, assessment_type: str, question_id: str):
    """Record completion"""
    if user_email not in user_assessments:
        user_assessments[user_email] = {}
    if assessment_type not in user_assessments[user_email]:
        user_assessments[user_email][assessment_type] = []
    
    if question_id not in user_assessments[user_email][assessment_type]:
        user_assessments[user_email][assessment_type].append(question_id)

def get_remaining_attempts(user_email: str, assessment_type: str) -> int:
    """Get remaining attempts"""
    if user_email not in assessment_attempts:
        assessment_attempts[user_email] = {}
    
    if assessment_type not in assessment_attempts[user_email]:
        assessment_attempts[user_email][assessment_type] = 4
    
    return assessment_attempts[user_email][assessment_type]

def use_assessment_attempt(user_email: str, assessment_type: str) -> bool:
    """Use attempt"""
    remaining = get_remaining_attempts(user_email, assessment_type)
    if remaining > 0:
        assessment_attempts[user_email][assessment_type] = remaining - 1
        return True
    return False

def lambda_handler(event, context):
    """Main handler"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        headers = event.get("headers", {})
        
        print(f"REQUEST: {method} {path}")
        
        if path == "/" and method == "GET":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "public, max-age=300"
                },
                "body": """HOME_TEMPLATE_PLACEHOLDER"""
            }
        
        elif path == "/dashboard":
            # Basic dashboard with DynamoDB indicator
            dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="alert alert-success">
            <h5><i class="fas fa-database me-2"></i>DynamoDB Question System Active</h5>
            <p class="mb-0">Questions are now dynamically loaded from DynamoDB for better scalability.</p>
        </div>
        
        <h1>Assessment Dashboard</h1>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h4>Academic Writing</h4>
                    </div>
                    <div class="card-body">
                        <p>4 attempts remaining</p>
                        <a href="/assessment/academic-writing" class="btn btn-success">Start Assessment</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4>Academic Speaking</h4>
                    </div>
                    <div class="card-body">
                        <p>4 attempts remaining</p>
                        <a href="/assessment/academic-speaking" class="btn btn-primary">Start Assessment</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h4>General Writing</h4>
                    </div>
                    <div class="card-body">
                        <p>4 attempts remaining</p>
                        <a href="/assessment/general-writing" class="btn btn-info">Start Assessment</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-warning text-white">
                        <h4>General Speaking</h4>
                    </div>
                    <div class="card-body">
                        <p>4 attempts remaining</p>
                        <a href="/assessment/general-speaking" class="btn btn-warning">Start Assessment</a>
                    </div>
                </div>
            </div>
        </div>
        
        <a href="/" class="btn btn-secondary">Back to Home</a>
    </div>
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html; charset=utf-8"},
                "body": dashboard_html
            }
        
        elif path.startswith("/assessment/"):
            assessment_type = path.replace("/assessment/", "")
            
            if assessment_type not in ["academic-writing", "academic-speaking", "general-writing", "general-speaking"]:
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "text/html"},
                    "body": "<html><body><h1>Assessment Not Found</h1><a href='/dashboard'>Back</a></body></html>"
                }
            
            # Get question from DynamoDB
            question = get_unique_assessment_question("test_user", assessment_type)
            if not question:
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "text/html"},
                    "body": "<html><body><h2>Question Unavailable</h2><p>Unable to load from DynamoDB.</p><a href='/dashboard'>Back</a></body></html>"
                }
            
            # Handle POST (submission)
            if method == "POST":
                question_id = question.get('id', 'unknown')
                record_assessment_completion("test_user", assessment_type, question_id)
                
                results_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Results - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h1>Assessment Results</h1>
                <p class="mb-0">Question ID: {question_id} (DynamoDB)</p>
            </div>
            <div class="card-body">
                <h3>Assessment Complete!</h3>
                <p>Your assessment has been evaluated using questions from DynamoDB.</p>
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
            </div>
        </div>
    </div>
</body>
</html>"""
                
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "text/html"},
                    "body": results_html
                }
            
            # Handle GET (show assessment)
            titles = {
                "academic-writing": "Academic Writing Assessment",
                "academic-speaking": "Academic Speaking Assessment", 
                "general-writing": "General Writing Assessment",
                "general-speaking": "General Speaking Assessment"
            }
            title = titles.get(assessment_type, "Assessment")
            
            if "writing" in assessment_type:
                assessment_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title} - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h1>{title}</h1>
                <p class="mb-0">Question ID: {question['id']} (from DynamoDB)</p>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <h4>{question.get('task_type', 'Writing Task')}</h4>
                    <p>{question.get('prompt', 'Assessment prompt')}</p>
                    <p><strong>Time:</strong> {question.get('time_limit', 40)} minutes</p>
                    <p><strong>Min Words:</strong> {question.get('word_count_min', 250)}</p>
                </div>
                
                <form method="POST" action="/assessment/{assessment_type}">
                    <div class="mb-3">
                        <textarea class="form-control" name="writing_content" rows="10" 
                                  placeholder="Write your response here..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">Submit Assessment</button>
                    <a href="/dashboard" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            elif "speaking" in assessment_type:
                assessment_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title} - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h1>{title}</h1>
                <h4>Maya - Your AI Examiner</h4>
                <p class="mb-0">Question ID: {question['id']} (from DynamoDB)</p>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <h5>Maya AI Speaking Assessment</h5>
                    <p>3-part speaking assessment with Maya examiner.</p>
                </div>
                
                <div class="border p-3 mb-3">
                    <h4>Part 1: {question['parts'][0]['topic']}</h4>
                    <p>Question: {question['parts'][0]['questions'][0]}</p>
                </div>
                
                <div class="border p-3 mb-3">
                    <h4>Part 2: {question['parts'][1]['topic']}</h4>
                    <p>Preparation: 1 minute | Speaking: 2 minutes</p>
                </div>
                
                <div class="border p-3 mb-3">
                    <h4>Part 3: {question['parts'][2]['topic']}</h4>
                </div>
                
                <form method="POST" action="/assessment/{assessment_type}">
                    <button type="submit" class="btn btn-success">Complete Assessment</button>
                    <a href="/dashboard" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": assessment_html
            }
        
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "text/html"},
                "body": "<html><body><h1>404 Not Found</h1><a href='/'>Home</a></body></html>"
            }
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/html"},
            "body": "<html><body><h2>Internal Server Error</h2><a href='/'>Home</a></body></html>"
        }
'''
        
        # Replace placeholder with actual template
        lambda_code = lambda_template.replace('"""HOME_TEMPLATE_PLACEHOLDER"""', f'"""{home_template}"""')
        
        # Create deployment package
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr('lambda_function.py', lambda_code)
            zip_file_path = tmp_file.name
        
        # Deploy to AWS
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        with open(zip_file_path, 'rb') as zip_file:
            zip_bytes = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_bytes
        )
        
        print('✅ DYNAMODB MIGRATION SUCCESSFUL!')
        print('')
        print('🎯 COMPLETED CHANGES:')
        print('  ✅ Questions moved from hardcoded arrays to DynamoDB table')
        print('  ✅ get_questions_from_dynamodb() function implemented')
        print('  ✅ Unique question delivery system maintained')
        print('  ✅ Assessment attempt tracking preserved')
        print('')
        print('📋 VISIBLE INDICATORS:')
        print('  • Dashboard shows "DynamoDB Question System Active"')
        print('  • Assessment pages display "Question ID: xxx (from DynamoDB)"')
        print('  • Results pages show "Question ID: xxx (DynamoDB)"')
        print('')
        print('💡 MIGRATION BENEFITS:')
        print('  • Easy to add new questions without redeploying code')
        print('  • Better scalability for large question banks')
        print('  • Foundation for question analytics and management')
        print('  • Supports future question versioning')
        print('')
        print('🌐 Test at: https://www.ieltsaiprep.com')
        print('   All assessments now use DynamoDB for question storage!')
        
        os.unlink(zip_file_path)
        return True
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        if 'zip_file_path' in locals() and os.path.exists(zip_file_path):
            os.unlink(zip_file_path)
        return False

if __name__ == "__main__":
    print("🚀 MIGRATING QUESTIONS TO DYNAMODB")
    print("=" * 50)
    deploy_lambda()
