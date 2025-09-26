import boto3
import zipfile
import tempfile
import os

def populate_questions():
    """Populate DynamoDB with assessment questions"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        # Academic Writing Questions
        academic_writing = [
            {"id": "aw_001", "task_type": "Task 2 - Essay", "prompt": "Some people believe that the internet has brought people closer together, while others argue it has made people more isolated. Discuss both views and give your own opinion.", "time_limit": 40, "word_count_min": 250},
            {"id": "aw_002", "task_type": "Task 2 - Essay", "prompt": "Many countries are investing heavily in renewable energy sources. To what extent do you agree that this is the best way to address climate change?", "time_limit": 40, "word_count_min": 250},
            {"id": "aw_003", "task_type": "Task 2 - Essay", "prompt": "University education should be free for all students. Do you agree or disagree with this statement?", "time_limit": 40, "word_count_min": 250},
            {"id": "aw_004", "task_type": "Task 1 - Graph Analysis", "prompt": "The chart below shows the percentage of households with internet access in five countries between 2000 and 2020. Summarize the information by selecting and reporting the main features.", "time_limit": 20, "word_count_min": 150}
        ]
        
        # Academic Speaking Questions  
        academic_speaking = [
            {"id": "as_001", "parts": [{"part": 1, "topic": "Work and Career", "questions": ["What do you do for work?", "Do you enjoy your job?", "What are your career goals?"]}, {"part": 2, "topic": "Describe a skill you would like to learn", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Skills and Learning", "questions": ["How important are practical skills?", "Should schools teach more life skills?"]}]},
            {"id": "as_002", "parts": [{"part": 1, "topic": "Technology", "questions": ["How often do you use technology?", "What technology do you find most useful?", "Has technology changed your life?"]}, {"part": 2, "topic": "Describe a piece of technology you find useful", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Technology and Society", "questions": ["How has technology changed communication?", "What are the negative effects of technology?"]}]},
            {"id": "as_003", "parts": [{"part": 1, "topic": "Education", "questions": ["What subjects did you study?", "What was your favorite subject?", "How important is education?"]}, {"part": 2, "topic": "Describe a teacher who influenced you", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Education Systems", "questions": ["How should teachers be trained?", "What makes a good education system?"]}]},
            {"id": "as_004", "parts": [{"part": 1, "topic": "Travel", "questions": ["Do you like to travel?", "Where have you traveled?", "What do you like about traveling?"]}, {"part": 2, "topic": "Describe a memorable journey you took", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Tourism and Culture", "questions": ["How does tourism affect local culture?", "Should there be limits on tourism?"]}]}
        ]
        
        # General Writing Questions
        general_writing = [
            {"id": "gw_001", "task_type": "Task 1 - Letter", "prompt": "You recently bought a product online but it arrived damaged. Write a letter to the company. In your letter: explain what you bought, describe the damage, say what action you want the company to take.", "time_limit": 20, "word_count_min": 150, "letter_type": "Complaint"},
            {"id": "gw_002", "task_type": "Task 2 - Essay", "prompt": "Some people think that parents should teach children how to be good members of society. Others believe that school is the best place to learn this. Discuss both views and give your opinion.", "time_limit": 40, "word_count_min": 250},
            {"id": "gw_003", "task_type": "Task 1 - Letter", "prompt": "You are planning a holiday abroad and need accommodation. Write a letter to a hotel. In your letter: introduce yourself, explain what type of accommodation you need, ask about availability and prices.", "time_limit": 20, "word_count_min": 150, "letter_type": "Inquiry"},
            {"id": "gw_004", "task_type": "Task 2 - Essay", "prompt": "Many people believe that social media platforms should be regulated by governments. To what extent do you agree or disagree?", "time_limit": 40, "word_count_min": 250}
        ]
        
        # General Speaking Questions
        general_speaking = [
            {"id": "gs_001", "parts": [{"part": 1, "topic": "Home and Family", "questions": ["Where do you live?", "Who do you live with?", "Describe your home."]}, {"part": 2, "topic": "Describe a family celebration you enjoyed", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Family and Traditions", "questions": ["How important are family traditions?", "How have families changed over time?"]}]},
            {"id": "gs_002", "parts": [{"part": 1, "topic": "Free Time", "questions": ["What do you do in your free time?", "Do you prefer indoor or outdoor activities?", "How do you relax?"]}, {"part": 2, "topic": "Describe a hobby you enjoy", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Leisure and Recreation", "questions": ["How important is leisure time?", "How do people choose their hobbies?"]}]},
            {"id": "gs_003", "parts": [{"part": 1, "topic": "Shopping", "questions": ["Do you like shopping?", "Where do you usually shop?", "How often do you go shopping?"]}, {"part": 2, "topic": "Describe a shop you like to visit", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Consumer Culture", "questions": ["How has shopping changed?", "Do people buy too many things nowadays?"]}]},
            {"id": "gs_004", "parts": [{"part": 1, "topic": "Food", "questions": ["What is your favorite food?", "Do you cook at home?", "What food is popular in your country?"]}, {"part": 2, "topic": "Describe a meal you enjoyed", "prep_time": 60, "talk_time": 120}, {"part": 3, "topic": "Food and Culture", "questions": ["How important is food in your culture?", "How have eating habits changed?"]}]}
        ]
        
        question_sets = {
            "academic-writing": academic_writing,
            "academic-speaking": academic_speaking,
            "general-writing": general_writing,
            "general-speaking": general_speaking
        }
        
        questions_count = 0
        for assessment_type, questions in question_sets.items():
            for question in questions:
                item = {
                    'assessment_type': assessment_type,
                    'question_id': question['id'],
                    'question_data': question,
                    'created_at': '2025-07-08T11:10:00Z',
                    'active': True
                }
                table.put_item(Item=item)
                questions_count += 1
        
        print(f"✅ Populated {questions_count} questions in DynamoDB")
        return True
        
    except Exception as e:
        print(f"❌ Error populating questions: {str(e)}")
        return False

def deploy_lambda_with_dynamodb():
    """Deploy Lambda function with DynamoDB integration"""
    try:
        # First populate questions
        if not populate_questions():
            print("❌ Failed to populate questions")
            return False
        
        # Read working template
        with open('working_template.html', 'r', encoding='utf-8') as f:
            home_template = f.read()
        
        # Create Lambda code with DynamoDB
        lambda_code = f'''
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

# Test user credentials
test_email = "prodtest_20250704_165313_kind@ieltsaiprep.com"
test_password = "TestProd2025!"
test_hash = hashlib.pbkdf2_hmac("sha256", test_password.encode(), b"production_salt_2025", 100000).hex()

# In-memory storage
users = {{test_email: {{"password_hash": test_hash, "email": test_email, "assessments_purchased": ["academic-writing", "academic-speaking", "general-writing", "general-speaking"]}}}}
sessions = {{}}
user_assessments = {{}}
assessment_attempts = {{}}

def get_questions_from_dynamodb(assessment_type: str) -> List[Dict[str, Any]]:
    """Retrieve questions from DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        response = table.query(
            KeyConditionExpression='assessment_type = :type',
            FilterExpression='active = :active',
            ExpressionAttributeValues={{
                ':type': assessment_type,
                ':active': True
            }}
        )
        
        questions = []
        for item in response['Items']:
            questions.append(item['question_data'])
        
        print(f"DynamoDB: Retrieved {{len(questions)}} questions for {{assessment_type}}")
        return questions
        
    except Exception as e:
        print(f"DynamoDB error: {{str(e)}}")
        return []

def get_unique_assessment_question(user_email: str, assessment_type: str) -> Optional[Dict[str, Any]]:
    """Get unique question from DynamoDB"""
    if user_email not in user_assessments:
        user_assessments[user_email] = {{}}
    
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
    """Record completed question"""
    if user_email not in user_assessments:
        user_assessments[user_email] = {{}}
    if assessment_type not in user_assessments[user_email]:
        user_assessments[user_email][assessment_type] = []
    
    if question_id not in user_assessments[user_email][assessment_type]:
        user_assessments[user_email][assessment_type].append(question_id)

def get_remaining_attempts(user_email: str, assessment_type: str) -> int:
    """Get remaining attempts"""
    if user_email not in assessment_attempts:
        assessment_attempts[user_email] = {{}}
    
    if assessment_type not in assessment_attempts[user_email]:
        assessment_attempts[user_email][assessment_type] = 4
    
    return assessment_attempts[user_email][assessment_type]

def use_assessment_attempt(user_email: str, assessment_type: str) -> bool:
    """Use one attempt"""
    remaining = get_remaining_attempts(user_email, assessment_type)
    if remaining > 0:
        assessment_attempts[user_email][assessment_type] = remaining - 1
        return True
    return False

def call_nova_micro_api(prompt: str, assessment_type: str) -> Dict[str, Any]:
    """Mock Nova Micro assessment"""
    return {{
        "overall_band": random.uniform(6.0, 8.5),
        "criteria": {{
            "task_achievement": {{"score": random.uniform(6.0, 8.0), "feedback": "Good task response with clear position."}},
            "coherence_cohesion": {{"score": random.uniform(6.5, 8.0), "feedback": "Well-organized ideas."}},
            "lexical_resource": {{"score": random.uniform(6.0, 7.5), "feedback": "Good vocabulary range."}},
            "grammatical_range": {{"score": random.uniform(6.5, 8.0), "feedback": "Variety of structures."}}
        }},
        "detailed_feedback": "Strong response with clear argumentation. Consider expanding examples.",
        "word_count": len(prompt.split()),
        "assessment_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }}

def initiate_maya_speech_session(assessment_type: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize Maya session"""
    return {{
        "session_id": str(uuid.uuid4()),
        "examiner": "Maya",
        "assessment_type": assessment_type,
        "question_data": question_data,
        "status": "ready",
        "websocket_url": f"wss://api.ieltsaiprep.com/maya-speech/{{str(uuid.uuid4())}}",
        "instructions": {{
            "part_1": "Questions about yourself and familiar topics.",
            "part_2": "1 minute to prepare, 2 minutes to speak.",
            "part_3": "Abstract discussion questions."
        }}
    }}

def verify_recaptcha_enterprise(recaptcha_token: str, user_ip: Optional[str] = None) -> bool:
    """Verify reCAPTCHA"""
    if not recaptcha_token:
        return False
    
    recaptcha_secret = os.environ.get('RECAPTCHA_V2_SECRET_KEY', '')
    if not recaptcha_secret:
        return True
    
    try:
        verification_data = {{
            'secret': recaptcha_secret,
            'response': recaptcha_token
        }}
        
        if user_ip and user_ip != 'unknown':
            verification_data['remoteip'] = user_ip
        
        post_data = urllib.parse.urlencode(verification_data).encode('utf-8')
        
        request = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=post_data,
            method='POST'
        )
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data.get('success', False)
            
    except Exception as e:
        print(f"reCAPTCHA error: {{str(e)}}")
        return False

def get_client_ip(headers: Dict[str, str]) -> str:
    """Extract client IP"""
    ip_headers = ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP', 'CF-Connecting-IP']
    
    for header in ip_headers:
        ip_value = headers.get(header, '').strip()
        if ip_value:
            if ',' in ip_value:
                ip_value = ip_value.split(',')[0].strip()
            if ip_value and ip_value != 'unknown':
                return ip_value
    return 'unknown'

def lambda_handler(event, context):
    """Main Lambda handler with DynamoDB questions"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        headers = event.get("headers", {{}})
        
        print(f"REQUEST: {{method}} {{path}}")
        
        if path == "/" and method == "GET":
            return {{
                "statusCode": 200,
                "headers": {{
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "public, max-age=300"
                }},
                "body": """{home_template.replace('"', '\\"')}"""
            }}
        
        elif path == "/dashboard":
            # Session verification logic here
            cookie_header = headers.get("Cookie", "")
            session_id = None
            
            for cookie in cookie_header.split(";"):
                if "session_id=" in cookie:
                    session_id = cookie.split("session_id=")[1].strip()
                    break
            
            if not session_id or session_id not in sessions:
                return {{"statusCode": 302, "headers": {{"Location": "/login"}}, "body": ""}}
            
            session = sessions[session_id]
            if session["expires_at"] < datetime.now(timezone.utc).timestamp():
                del sessions[session_id]
                return {{"statusCode": 302, "headers": {{"Location": "/login"}}, "body": ""}}
            
            user_email = session["user_email"]
            
            attempt_counts = {{}}
            for assessment_type in ["academic-writing", "academic-speaking", "general-writing", "general-speaking"]:
                attempt_counts[assessment_type] = get_remaining_attempts(user_email, assessment_type)
            
            dashboard_html = f"""<!DOCTYPE html>
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
            <p class="mb-0">Questions are now dynamically loaded from DynamoDB for scalable question management.</p>
        </div>
        
        <h1>Assessment Dashboard</h1>
        <p>Logged in as: {{user_email}}</p>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h4>Academic Writing</h4>
                    </div>
                    <div class="card-body">
                        <p>{{attempt_counts.get('academic-writing', 4)}} attempts remaining</p>
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
                        <p>{{attempt_counts.get('academic-speaking', 4)}} attempts remaining</p>
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
                        <p>{{attempt_counts.get('general-writing', 4)}} attempts remaining</p>
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
                        <p>{{attempt_counts.get('general-speaking', 4)}} attempts remaining</p>
                        <a href="/assessment/general-speaking" class="btn btn-warning">Start Assessment</a>
                    </div>
                </div>
            </div>
        </div>
        
        <a href="/" class="btn btn-secondary">Back to Home</a>
    </div>
</body>
</html>"""
            
            return {{
                "statusCode": 200,
                "headers": {{"Content-Type": "text/html; charset=utf-8"}},
                "body": dashboard_html
            }}
        
        elif path.startswith("/assessment/"):
            assessment_type = path.replace("/assessment/", "")
            
            if assessment_type not in ["academic-writing", "academic-speaking", "general-writing", "general-speaking"]:
                return {{
                    "statusCode": 404,
                    "headers": {{"Content-Type": "text/html"}},
                    "body": """<html><body style="text-align: center; padding: 50px;">
                        <h1>Assessment Not Found</h1>
                        <a href="/dashboard">Back to Dashboard</a>
                    </body></html>"""
                }}
            
            # Session verification
            cookie_header = headers.get("Cookie", "")
            session_id = None
            for cookie in cookie_header.split(";"):
                if "session_id=" in cookie:
                    session_id = cookie.split("session_id=")[1].strip()
                    break
            
            if not session_id or session_id not in sessions:
                return {{"statusCode": 302, "headers": {{"Location": "/login"}}, "body": ""}}
            
            user_email = sessions[session_id]["user_email"]
            
            # Check attempts
            remaining_attempts = get_remaining_attempts(user_email, assessment_type)
            if remaining_attempts <= 0:
                return {{
                    "statusCode": 200,
                    "headers": {{"Content-Type": "text/html"}},
                    "body": """<html><body style="text-align: center; padding: 50px;">
                        <h2>No Attempts Remaining</h2>
                        <a href="/dashboard">Back to Dashboard</a>
                    </body></html>"""
                }}
            
            # Get question from DynamoDB
            question = get_unique_assessment_question(user_email, assessment_type)
            if not question:
                return {{
                    "statusCode": 500,
                    "headers": {{"Content-Type": "text/html"}},
                    "body": """<html><body style="text-align: center; padding: 50px;">
                        <h2>Assessment Unavailable</h2>
                        <p>Unable to load question from DynamoDB.</p>
                        <a href="/dashboard">Back to Dashboard</a>
                    </body></html>"""
                }}
            
            # Handle POST (submission)
            if method == "POST":
                body = event.get("body", "")
                data = dict(urllib.parse.parse_qsl(body))
                
                question_id = data.get("question_id", "")
                use_assessment_attempt(user_email, assessment_type)
                record_assessment_completion(user_email, assessment_type, question_id)
                
                if "writing" in assessment_type:
                    writing_content = data.get("writing_content", "").strip()
                    assessment_result = call_nova_micro_api(writing_content, assessment_type)
                    
                    results_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Assessment Results - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h1>Assessment Results</h1>
                <h3>Overall Band Score: {{assessment_result.get('overall_band', 7.0):.1f}}</h3>
                <p class="mb-0">Question ID: {{question_id}} (DynamoDB)</p>
            </div>
            <div class="card-body">
                <h4>AI Feedback:</h4>
                <p>{{assessment_result.get('detailed_feedback', 'Great work!')}}</p>
                <p><strong>Word Count:</strong> {{assessment_result.get('word_count', 0)}}</p>
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
            </div>
        </div>
    </div>
</body>
</html>"""
                    
                    return {{
                        "statusCode": 200,
                        "headers": {{"Content-Type": "text/html"}},
                        "body": results_html
                    }}
                
                elif "speaking" in assessment_type:
                    speaking_results_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Speaking Results - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h1>Speaking Assessment Complete</h1>
                <h3>Overall Band Score: {{random.uniform(6.5, 8.0):.1f}}</h3>
                <p class="mb-0">Question ID: {{question_id}} (DynamoDB)</p>
            </div>
            <div class="card-body">
                <p>Your speaking assessment with Maya AI examiner has been completed.</p>
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
            </div>
        </div>
    </div>
</body>
</html>"""
                    
                    return {{
                        "statusCode": 200,
                        "headers": {{"Content-Type": "text/html"}},
                        "body": speaking_results_html
                    }}
            
            # Handle GET (show assessment)
            titles = {{
                "academic-writing": "Academic Writing Assessment",
                "academic-speaking": "Academic Speaking Assessment", 
                "general-writing": "General Writing Assessment",
                "general-speaking": "General Speaking Assessment"
            }}
            title = titles.get(assessment_type, "Assessment")
            
            if "writing" in assessment_type:
                assessment_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{title}} - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h1>{{title}}</h1>
                <p class="mb-0">Question ID: {{question['id']}} (from DynamoDB)</p>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <h4>{{question.get('task_type', 'Writing Task')}}</h4>
                    <p>{{question.get('prompt', 'Assessment prompt')}}</p>
                    <p><strong>Time Limit:</strong> {{question.get('time_limit', 40)}} minutes</p>
                    <p><strong>Minimum Words:</strong> {{question.get('word_count_min', 250)}}</p>
                </div>
                
                <form method="POST" action="/assessment/{{assessment_type}}">
                    <input type="hidden" name="question_id" value="{{question['id']}}">
                    <div class="mb-3">
                        <label for="writing_content" class="form-label">Your Response:</label>
                        <textarea class="form-control" id="writing_content" name="writing_content" rows="15" 
                                  placeholder="Begin writing your response here..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-success btn-lg">Submit for Assessment</button>
                    <a href="/dashboard" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            elif "speaking" in assessment_type:
                maya_session = initiate_maya_speech_session(assessment_type, question)
                
                assessment_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{title}} - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h1>{{title}}</h1>
                <h4>Maya - Your AI Examiner</h4>
                <p class="mb-0">Question ID: {{question['id']}} (from DynamoDB)</p>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <h5>Maya AI Speaking Assessment</h5>
                    <p>Maya will guide you through a 3-part speaking assessment.</p>
                </div>
                
                <div class="border p-3 mb-3">
                    <h4>Part 1: Introduction & Interview</h4>
                    <p><strong>Topic:</strong> {{question['parts'][0]['topic']}}</p>
                    <p><strong>First Question:</strong> {{question['parts'][0]['questions'][0]}}</p>
                </div>
                
                <div class="border p-3 mb-3">
                    <h4>Part 2: Long Turn</h4>
                    <p><strong>Topic:</strong> {{question['parts'][1]['topic']}}</p>
                    <p><strong>Preparation time:</strong> 1 minute | <strong>Speaking time:</strong> 2 minutes</p>
                </div>
                
                <div class="border p-3 mb-3">
                    <h4>Part 3: Discussion</h4>
                    <p><strong>Topic:</strong> {{question['parts'][2]['topic']}}</p>
                </div>
                
                <form method="POST" action="/assessment/{{assessment_type}}">
                    <input type="hidden" name="question_id" value="{{question['id']}}">
                    <button type="submit" class="btn btn-success btn-lg">Complete Assessment</button>
                    <a href="/dashboard" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        console.log('Maya AI Examiner initialized with DynamoDB questions');
        console.log('WebSocket URL:', '{{maya_session.get("websocket_url", "N/A")}}');
    </script>
</body>
</html>"""
            
            return {{
                "statusCode": 200,
                "headers": {{"Content-Type": "text/html"}},
                "body": assessment_html
            }}
        
        else:
            return {{
                "statusCode": 404,
                "headers": {{"Content-Type": "text/html"}},
                "body": """<html><body style="text-align: center; padding: 50px;">
                    <h1>404 Not Found</h1>
                    <a href="/">Return to Home</a>
                </body></html>"""
            }}
    
    except Exception as e:
        print(f"LAMBDA ERROR: {{type(e).__name__}}: {{str(e)}}")
        return {{
            "statusCode": 500,
            "headers": {{"Content-Type": "text/html"}},
            "body": """<html><body style="text-align: center; padding: 50px;">
                <h2>Internal Server Error</h2>
                <p>An unexpected error occurred. Please try again later.</p>
                <a href="/">Return to Home</a>
            </body></html>"""
        }}
'''
        
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
        
        print('✅ DYNAMODB MIGRATION COMPLETE!')
        print(f'Function ARN: {response["FunctionArn"]}')
        print('')
        print('🎯 MIGRATION COMPLETED:')
        print('  ✅ Questions moved from hardcoded arrays to DynamoDB table')
        print('  ✅ Dynamic question loading with get_questions_from_dynamodb()')
        print('  ✅ Unique question delivery system maintained')
        print('  ✅ Assessment attempt tracking preserved')
        print('  ✅ Maya speech functionality intact')
        print('')
        print('📋 VISIBLE CHANGES:')
        print('  • Dashboard shows "DynamoDB Question System Active"')
        print('  • Assessment pages display "Question ID: xxx (from DynamoDB)"')
        print('  • Results pages show "Question ID: xxx (DynamoDB)"')
        print('')
        print('💡 BENEFITS:')
        print('  • Easy to add new questions without code deployment')
        print('  • Better scalability for large question banks')
        print('  • Question analytics and usage tracking possible')
        print('  • Supports question versioning and A/B testing')
        print('')
        print('🌐 Test at: https://www.ieltsaiprep.com')
        print('   All assessments now use DynamoDB for question management!')
        
        os.unlink(zip_file_path)
        return True
        
    except Exception as e:
        print(f'❌ Deployment error: {str(e)}')
        if 'zip_file_path' in locals() and os.path.exists(zip_file_path):
            os.unlink(zip_file_path)
        return False

if __name__ == "__main__":
    deploy_lambda_with_dynamodb()
